# Model Layer — Hybrid Architecture

**Related to:** ARCHITECTURE.md Section 5

---

## Overview

MAIS uses three tiers of model capability, each matched to the appropriate task complexity:

```
┌─────────────────────────────────────────────────────────────────┐
│                    MODEL LAYER                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              HIGH-STAKES → HUMAN + CLAUDE                  │  │
│  │  Budget > $1000, content, brand risk, legal              │  │
│  │  → Always involves Claude-class + human review            │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↑                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              STRATEGIC REASONING → CLAUDE-CLASS           │  │
│  │  Campaign strategy, creative concepts, positioning,         │  │
│  │  budget allocation, performance diagnosis                  │  │
│  │  → Always Claude-class (Opus/Sonnet/Gemini-Pro)          │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↑                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              ROUTING → SMALL MODEL (Auto)                  │  │
│  │  Channel selection, audience classification, bid tier,       │  │
│  │  creative format, placement, dayparting                    │  │
│  │  → Small model if confidence > 0.75, else human review     │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Decision Flow

```python
class ModelRouter:
    """
    Decides which model tier handles each request.
    """

    def __init__(
        self,
        small_model: SmallModelRouter,
        claude_client: ClaudeClient,
        human_gate: HumanApprovalGate
    ):
        self.small_model = small_model
        self.claude = claude_client
        self.human_gate = human_gate

    async def route(self, request: MarketingRequest) -> RoutingDecision:
        """
        Main routing logic.
        """
        # 1. Classify task type
        task_type = self._classify(request)
        stakes_level = self._assess_stakes(request)

        # 2. Route decision tree
        if stakes_level == "high":
            return await self._route_high_stakes(request)

        elif stakes_level == "medium":
            return await self._route_medium_stakes(request)

        elif task_type in ROUTING_TASKS and request.confidence_requirement < 0.75:
            return await self._route_low_stakes(request)

        else:
            return await self._route_reasoning(request)

    def _classify(self, request: MarketingRequest) -> TaskType:
        """Classify task into routing vs reasoning category."""
        routing_keywords = [
            "which channel", "select platform", "bid tier",
            "audience segment", "placement", "format",
            "allocate budget percentage", "dayparting"
        ]
        reasoning_keywords = [
            "why did", "strategy for", "positioning",
            "concept for", "analyze competitor", "diagnose",
            "recommend overall", "budget allocation across"
        ]

        # Use lightweight classification
        if any(kw in request.query.lower() for kw in routing_keywords):
            return TaskType.ROUTING
        if any(kw in request.query.lower() for kw in reasoning_keywords):
            return TaskType.REASONING
        return TaskType.MIXED
```

---

## 2. Small Model Router

### 2.1 What It Does

```
┌─────────────────────────────────────────────────────────────────┐
│                    SMALL MODEL ROUTER                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  TASK TYPES:                                                   │
│  ─────────────────────────────────────────────────────────  │
│  Channel Selection    → Multi-class (google | meta | tiktok | linkedin | other)  │
│  Audience Segment    → Multi-label (tech_buyer | enterprise | smb | startup | etc.) │
│  Bid Tier           → Ordinal (1-10)                        │
│  Creative Format    → Multi-class (image | video | carousel | text)  │
│  Placement          → Multi-label (feed | story | search | discovery)  │
│  Dayparting        → Ordinal per 6-hr block (0.0-1.0 weight)  │
│                                                                 │
│  OUTPUT:                                                       │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ {                                                      │  │
│  │   "recommended": "google",                          │  │
│  │   "confidence": 0.82,                                │  │
│  │   "alternatives": [                                   │  │
│  │     {"channel": "meta", "score": 0.71},            │  │
│  │     {"channel": "tiktok", "score": 0.45}           │  │
│  │   ],                                                  │  │
│  │   "requires_review": false,                           │  │
│  │   "reasoning_chain": "Google search intent higher..."  │  │
│  │ }                                                      │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                                 │
│  GUARDRAILS:                                                  │
│  - confidence < 0.75 → requires_review = true              │
│  - Any prob > 0.95 → warning: overconfident               │
│  - OOD detected → requires_review = true                     │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Implementation

```python
class SmallModelRouter:
    """
    Fine-tuned small model for classification/routing tasks.
    Base: Claude Haiku or Mistral-7B-Instruct quantized.
    """

    def __init__(
        self,
        model_path: str = "models/router-lora",
        confidence_threshold: float = 0.75,
        calibration_temp: float = 1.2
    ):
        self.model = load_quantized_model(model_path)
        self.confidence_threshold = confidence_threshold
        self.calibration_temp = calibration_temp

        # Load LoRA weights
        self.model = load_lora(self.model, f"{model_path}/lora")

    async def classify(
        self,
        request: RoutingRequest
    ) -> RoutingDecision:
        """
        Main classification entry point.
        """
        # 1. Classify
        logits = await self.model.predict(
            input_ids=request.encoded,
            task_type=request.task_type
        )

        # 2. Apply temperature scaling (calibration)
        scaled_logits = logits / self.calibration_temp

        # 3. Get probabilities
        probs = softmax(scaled_logits)
        top_idx = np.argmax(probs)
        top_prob = probs[top_idx]

        # 4. Build alternatives
        alternatives = self._build_alternatives(probs, top_idx)

        # 5. Check guardrails
        requires_review = (
            top_prob < self.confidence_threshold or
            top_prob > 0.95 or  # Overconfidence warning
            self._is_out_of_distribution(request)
        )

        return RoutingDecision(
            recommended=CLASS_LABELS[request.task_type][top_idx],
            confidence=float(top_prob),
            alternatives=alternatives,
            requires_review=requires_review,
            model="small-router",
            latency_ms=self._last_latency()
        )

    def _is_out_of_distribution(self, request: RoutingRequest) -> bool:
        """
        Detect if input is far from training distribution.
        Uses embedding distance from centroid of training set.
        """
        embedding = self.model.get_embedding(request.encoded)
        centroid_dist = cosine_distance(embedding, self.training_centroid)

        # Flag if > 2 standard deviations from training centroid
        return centroid_dist > (self.centroid_mean + 2 * self.centroid_std)
```

### 2.3 Training Data Construction

```python
class RouterTrainingDataBuilder:
    """
    Builds (query → routing_decision) pairs from historical data.
    IMPORTANT: We use EXPERT-LABELED decisions, not outcomes.
    Outcomes are confounded by execution quality.
    """

    def build_training_pairs(self, historical_campaigns: list) -> list:
        """
        Build training pairs from historical routing decisions.
        Uses expert-labeled ground truth, not outcome-based labels.
        """
        pairs = []

        for campaign in historical_campaigns:
            # What was the routing decision?
            decision = {
                "channel": campaign.chosen_channel,
                "audience": campaign.audience_segment,
                "bid_tier": campaign.bid_tier,
                "format": campaign.creative_format,
                "placement": campaign.placements,
            }

            # Context that led to the decision
            context = {
                "brand": campaign.brand_name,
                "vertical": campaign.vertical,
                "objective": campaign.objective,
                "competitor": campaign.primary_competitor,
                "budget": campaign.budget,
                "audience_description": campaign.audience_description,
                "seasonality": campaign.season,
                "platform_capability": campaign.platform_capabilities,
            }

            # REJECT: Don't use outcomes as labels
            # campaign.roas is confounded by creative quality, competitor
            # actions, budget level, and many other factors

            pairs.append({
                "input": self._format_context(context),
                "output": self._format_decision(decision),
                "label_source": "expert_annotation",
                "campaign_id": campaign.id
            })

        return pairs
```

---

## 3. Claude-Class Reasoning

### 3.1 What It Does

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLAUDE-CLASS REASONING                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  TASK TYPES:                                                   │
│  ─────────────────────────────────────────────────────────  │
│  Campaign Strategy      → Full funnel, objectives, positioning  │
│  Creative Concepts     → Themes, angles, emotional triggers    │
│  Positioning Analysis  → Competitive gap identification         │
│  Budget Allocation    → Cross-campaign optimization           │
│  Performance Diagnosis → Root cause analysis                 │
│  Audience Strategy    → Deep segmentation, unmet needs        │
│                                                                 │
│  ALWAYS INCLUDES:                                             │
│  ─────────────────────────────────────────────────────────  │
│  Reasoning chain with every output                           │
│  Confidence score (calibrated)                              │
│  Alternative options with tradeoffs                           │
│  Risk assessment                                            │
│  Audit trail (stored in episodic memory)                    │
│                                                                 │
│  OUTPUT FORMAT:                                              │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Reasoning Chain:                                      │  │
│  │ 1. [Observation] Notion targets Ops teams...        │  │
│  │ 2. [Inference] Engineering teams underserved...      │  │
│  │ 3. [Hypothesis] Target engineering persona...      │  │
│  │                                                       │  │
│  │ Recommendation: [What to do]                          │  │
│  │ Confidence: 0.87 ± 0.08                             │  │
│  │                                                       │  │
│  │ Alternatives:                                        │  │
│  │  A: [Option A] — Pros/Cons                        │  │
│  │  B: [Option B] — Pros/Cons                        │  │
│  │                                                       │  │
│  │ Risk Assessment: [What could go wrong]              │  │
│  │ Evidence: [Citations from knowledge graph]         │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Implementation

```python
class ClaudeReasoningEngine:
    """
    Claude-class reasoning for strategic marketing decisions.
    Always produces reasoning chains with confidence scores.
    """

    SYSTEM_PROMPT = """You are MAIAgent, a strategic marketing reasoning engine.

For every recommendation you make, you MUST provide:
1. REASONING CHAIN: Step-by-step logic from observation to conclusion
2. CONFIDENCE SCORE: Calibrated 0-1, with uncertainty band
3. ALTERNATIVES: At least 2 other options with tradeoffs
4. RISK ASSESSMENT: What could go wrong and how to mitigate
5. EVIDENCE: Cite specific data from the knowledge graph

You NEVER guess. You ALWAYS show your reasoning.
If you don't have enough information, you say so.

Confidence calibration guidelines:
- 0.95+: Virtually certain, direct evidence
- 0.80-0.94: High confidence, strong evidence
- 0.65-0.79: Moderate confidence, some extrapolation
- 0.50-0.64: Low confidence, significant uncertainty
- < 0.50: Too uncertain to recommend, escalate to human
"""

    async def reason(
        self,
        request: ReasoningRequest,
        context: ReasoningContext
    ) -> ReasoningResult:
        """
        Main reasoning entry point.
        Always produces structured output with reasoning chain.
        """
        # 1. Fetch relevant knowledge from all memory systems
        kg_context = await self._fetch_knowledge_graph(request)
        vector_context = await self._fetch_vector_store(request)
        episodic_context = await self._fetch_episodic(request)

        # 2. Build enriched prompt
        prompt = self._build_prompt(request, {
            "knowledge_graph": kg_context,
            "vector_store": vector_context,
            "episodic": episodic_context
        })

        # 3. Generate with Claude
        response = await self.claude.generate(
            system=self.SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # Low temp for consistent reasoning
            max_tokens=2000
        )

        # 4. Parse structured output
        parsed = self._parse_reasoning_response(response)

        # 5. Calibrate confidence
        calibrated_confidence = self._calibrate_confidence(
            parsed.confidence,
            context.quality_score
        )

        # 6. Log to episodic store
        await self._log_reasoning(request, parsed, calibrated_confidence)

        return ReasoningResult(
            reasoning_chain=parsed.chain,
            recommendation=parsed.recommendation,
            confidence=calibrated_confidence,
            confidence_band=parsed.confidence_band,
            alternatives=parsed.alternatives,
            risk_assessment=parsed.risks,
            evidence=parsed.evidence,
            model="claude-reasoning",
            latency_ms=response.latency_ms
        )

    def _fetch_knowledge_graph(self, request: ReasoningRequest) -> dict:
        """
        Fetch relevant causal chains from knowledge graph.
        """
        chain = self.kg.get_causal_chain(request.campaign_id)
        return {
            "campaign": chain["campaign"],
            "outcomes": chain["outcomes"],
            "similar_campaigns": chain["similar_campaigns"],
            "competitor_analysis": self._analyze_competitors(
                chain["campaign"].brand_id
            )
        }
```

---

## 4. Human Approval Gate

```python
class HumanApprovalGate:
    """
    Routes high-stakes decisions to human reviewers.
    Non-negotiable for budget, content, brand risk.
    """

    HIGH_STAKES_THRESHOLDS = {
        "budget_change_usd": 1000,
        "content_posting": True,  # Any content → human
        "competitor_mention": True,
        "new_audience_segment": True,
        "brand_risk_categories": ["politics", "religion", "health", "finance"],
    }

    async def requires_approval(self, decision: RoutingDecision) -> bool:
        """
        Check if decision requires human approval.
        """
        # Budget threshold
        if decision.budget_change and decision.budget_change > self.HIGH_STAKES_THRESHOLDS["budget_change_usd"]:
            return True

        # Content posting
        if (decision.action_type == "content_post" and
            self.HIGH_STAKES_THRESHOLDS["content_posting"]):
            return True

        # Competitor mention
        if decision.mentions_competitor and self.HIGH_STAKES_THRESHOLDS["competitor_mention"]:
            return True

        # Brand risk categories
        if any(cat in decision.content_category
               for cat in self.HIGH_STAKES_THRESHOLDS["brand_risk_categories"]):
            return True

        # Low confidence
        if decision.confidence < 0.65:
            return True

        return False

    async def submit_for_review(
        self,
        decision: RoutingDecision,
        context: ReasoningContext
    ) -> ApprovalRequest:
        """
        Submit decision for human review.
        """
        approval = ApprovalRequest(
            id=generate_uuid(),
            decision=decision,
            context=context,
            submitted_at=datetime.utcnow(),
            urgency=self._assess_urgency(decision),
            approval_deadline=datetime.utcnow() + timedelta(hours=4)
        )

        await self._send_slack_notification(approval)
        await self._log_submission(approval)

        return approval
```

---

## 5. Confidence Calibration

```python
class ConfidenceCalibrator:
    """
    Calibrates model confidence to match actual accuracy.
    Prevents overconfident and underconfident outputs.
    """

    def calibrate(
        self,
        raw_confidence: float,
        context: ContextMetadata
    ) -> CalibratedConfidence:
        """
        Apply calibration adjustments based on context quality.
        """
        adjustments = []

        # Reduce confidence for data quality issues
        if context.data_quality_score < 0.8:
            adjustments.append(-0.1)
        if context.data_quality_score < 0.6:
            adjustments.append(-0.15)

        # Reduce confidence for short history
        if context.campaign_history_days < 14:
            adjustments.append(-0.1)

        # Reduce confidence for novel context
        if context.is_novel_audience:
            adjustments.append(-0.15)
        if context.is_novel_competitor:
            adjustments.append(-0.1)

        # Reduce confidence for high variance
        if context.outcome_variance > 0.3:
            adjustments.append(-0.1)

        # Apply adjustments
        calibrated = raw_confidence + sum(adjustments)
        calibrated = max(0.1, min(0.99, calibrated))  # Clamp

        # Calculate uncertainty band
        uncertainty_band = (
            0.05 +  # Base uncertainty
            0.05 * (1 - context.data_quality_score) +
            0.10 * (1 - context.campaign_history_days / 90)  # Cap at 90 days
        )

        return CalibratedConfidence(
            value=calibrated,
            lower=max(0.0, calibrated - uncertainty_band),
            upper=min(1.0, calibrated + uncertainty_band),
            adjustments=adjustments
        )
```
