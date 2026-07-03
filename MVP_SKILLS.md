# MVP Skills — Prioritized Implementation Order

**Related to:** SKILLS_ARCHITECTURE.md Section 5

---

## Overview

This document specifies which skills to implement first and in what order. Skills are ordered by dependency — you need the foundational ones before building on top.

**Total MVP: 6 skills over 4 weeks**

```
┌─────────────────────────────────────────────────────────────────┐
│                    MVP SKILL DEPENDENCY GRAPH                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  WEEK 1-2: DATA FOUNDATION                                     │
│  ───────────────────────────────────────────────────────────  │
│                                                                 │
│    get_campaign_data ──────┐                                    │
│           │                │                                    │
│           ▼                │                                    │
│  calculate_denoised_roas ◄─┘                                    │
│                                                                 │
│  WEEK 3: LEARNING FOUNDATION                                   │
│  ───────────────────────────────────────────────────────────  │
│                                                                 │
│    hypothesis_generator ◄── SPCMonitor (internal)               │
│           │                                                   │
│           ▼                                                   │
│    validate_hypothesis                                         │
│                                                                 │
│  WEEK 4: END-TO-END LOOP                                      │
│  ───────────────────────────────────────────────────────────  │
│                                                                 │
│    copy_generator                                             │
│           │                                                   │
│           ▼                                                   │
│    budget_allocator (simple v1)                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Week 1-2: Data Foundation

### Skill 1: get_campaign_data

**Priority:** HIGHEST — everything depends on this

```python
# skills/get_campaign_data/skill.py

class GetCampaignDataSkill(Skill):
    """
    Fetches campaign performance data from MCP ad platform connections.
    """

    name = "get_campaign_data"
    description = "Fetch daily ROAS, spend, conversions from ad platforms"
    version = "1.0.0"

    class Input(SkillInput):
        campaign_id: str = Field(..., description="Campaign ID")
        start_date: date = Field(..., description="Start date (inclusive)")
        end_date: date = Field(..., description="End date (inclusive)")
        metrics: list[str] = Field(
            default=["roas", "spend", "conversions", "impressions", "ctr"],
            description="Metrics to fetch"
        )

    class Output(SkillOutput):
        daily_metrics: list[dict] | None = None
        data_quality_score: float | None = None
        last_updated: datetime | None = None

    class Config(SkillConfig):
        timeout_seconds: int = 60
        cache_ttl_seconds: int = 3600  # Cache for 1 hour
        retry_attempts: int = 3

    async def execute(self, input_data: Input) -> Output:
        # 1. Fetch from MCP
        raw_data = await self.mcp.fetch(
            platform=self._get_platform(input_data.campaign_id),
            endpoint="getCampaignMetrics",
            params={
                "campaign_id": input_data.campaign_id,
                "start_date": input_data.start_date,
                "end_date": input_data.end_date,
                "metrics": input_data.metrics
            }
        )

        # 2. Validate data quality
        quality_score = self._calculate_quality_score(raw_data)

        # 3. Transform to standard format
        daily_metrics = self._transform(raw_data)

        # 4. Cache results
        await self.cache.set(
            key=f"campaign_data:{input_data.campaign_id}",
            value=daily_metrics,
            ttl=self.config.cache_ttl_seconds
        )

        return Output(
            success=True,
            data={
                "daily_metrics": daily_metrics,
                "data_quality_score": quality_score,
                "last_updated": datetime.utcnow()
            }
        )
```

**Test Cases:**

```python
# skills/get_campaign_data/skill_test.py

@pytest.mark.asyncio
async def test_fetches_30_days_of_data(skill):
    output = await skill.execute(skill.validate_input({
        "campaign_id": "test-123",
        "start_date": "2024-01-01",
        "end_date": "2024-01-30"
    }))
    assert output.success
    assert len(output.data["daily_metrics"]) == 30

@pytest.mark.asyncio
async def test_calculates_quality_score(skill):
    output = await skill.execute(...)
    assert 0 <= output.data["data_quality_score"] <= 1

@pytest.mark.asyncio
async def test_handles_missing_data_gracefully(skill):
    # When MCP returns partial data
    output = await skill.execute(...)
    assert output.data["data_quality_score"] < 1.0
```

---

### Skill 2: calculate_denoised_roas

**Priority:** HIGHEST — core of the learning mechanism

```python
# skills/calculate_denoised_roas/skill.py

class CalculateDenoisedRoasSkill(Skill):
    """
    Applies causal inference to isolate true ROAS from confounds.
    """

    name = "calculate_denoised_roas"
    description = "Denoise raw ROAS using BSTS causal inference"
    version = "1.0.0"

    class Input(SkillInput):
        raw_metrics: list[dict] = Field(
            ...,
            description="Raw daily metrics from get_campaign_data"
        )
        control_series: list[float] | None = Field(
            default=None,
            description="Optional control series (market index)"
        )

    class Output(SkillOutput):
        denoised_roas: list[float] | None = None
        ci_lower: list[float] | None = None
        ci_upper: list[float] | None = None
        confound_flags: dict | None = None
        is_learnable: bool | None = None

    async def execute(self, input_data: Input) -> Output:
        # 1. Fit BSTS model
        bsts = BSTSModel()
        result = bsts.denoise(pd.DataFrame(input_data.raw_metrics))

        # 2. Check if effect is learnable
        # (CI width < 30% of mean = learnable)
        ci_width = np.array(result.ci_upper) - np.array(result.ci_lower)
        mean_roas = np.mean(result.denoised_roas)
        is_learnable = (ci_width / mean_roas).mean() < 0.30

        return Output(
            success=True,
            data={
                "denoised_roas": result.denoised_roas.tolist(),
                "ci_lower": result.ci_lower.tolist(),
                "ci_upper": result.ci_upper.tolist(),
                "confound_flags": result.confound_flags,
                "is_learnable": is_learnable
            }
        )
```

**Test Cases:**

```python
# skills/calculate_denoised_roas/skill_test.py

@pytest.mark.asyncio
async def test_removes_day_of_week_effect(skill):
    # Input: 30 days with known +30% weekend effect
    input_data = create_test_data_with_weekend_effect()
    output = await skill.execute(skill.validate_input({
        "raw_metrics": input_data
    }))
    # Denoised should have weekends same as weekdays
    assert output.success
    assert output.data["confound_flags"]["day_of_week"] is True

@pytest.mark.asyncio
async def test_identifies_unlearnable_campaign(skill):
    # Input: High variance campaign
    input_data = create_high_variance_test_data()
    output = await skill.execute(...)
    assert output.data["is_learnable"] is False

@pytest.mark.asyncio
async def test_ci_coverage(skill):
    # 95% CI should contain true value ~95% of time
    ...
```

---

## Week 3: Learning Foundation

### Skill 3: hypothesis_generator

**Priority:** HIGH — drives the inner loop

```python
# skills/hypothesis_generator/skill.py

class HypothesisGeneratorSkill(Skill):
    """
    Generates testable hypotheses from SPC anomaly flags.
    """

    name = "hypothesis_generator"
    description = "Generate candidate explanations for ROAS anomalies"
    version = "1.0.0"

    class Input(SkillInput):
        anomaly_flags: list[str] = Field(
            ...,
            description="Flags from SPCMonitor"
        )
        campaign_context: dict = Field(
            ...,
            description="Campaign metadata (platform, audience, budget)"
        )
        denoised_roas: list[float] = Field(
            ...,
            description="Denoised ROAS time series"
        )

    class Output(SkillOutput):
        hypotheses: list[dict] | None = None
        queue_recommendation: str | None = None

    async def execute(self, input_data: Input) -> Output:
        # Build prompt for Claude
        prompt = self._build_prompt(input_data)

        # Generate with Claude
        response = await self.claude.generate(prompt)

        # Parse structured output
        hypotheses = self._parse_hypotheses(response)

        # Score confidence for each
        for h in hypotheses:
            h["confidence"] = self._score_confidence(h, input_data)

        # Recommend queue action
        queue_rec = "queue" if any(h["confidence"] > 0.6 for h in hypotheses) else "ignore"

        return Output(
            success=True,
            data={
                "hypotheses": hypotheses,
                "queue_recommendation": queue_rec
            }
        )
```

**Output Format:**

```json
{
  "hypotheses": [
    {
      "id": "hyp-001",
      "description": "Weekend audiences have higher intent — increase bid multiplier by 15%",
      "candidate_explanations": [
        {
          "explanation": "Weekend users are more likely to convert",
          "confidence": 0.72,
          "how_to_validate": "A/B test: weekend vs weekday bid multipliers"
        },
        {
          "explanation": "Competitor backing off on weekends",
          "confidence": 0.31,
          "how_to_validate": "Monitor competitor spend patterns"
        }
      ],
      "confidence": 0.72,
      "expected_effect_size": 0.15,
      "priority": "high"
    }
  ],
  "queue_recommendation": "queue"
}
```

---

### Skill 4: validate_hypothesis

**Priority:** HIGH — gates what gets to outer loop

```python
# skills/validate_hypothesis/skill.py

class ValidateHypothesisSkill(Skill):
    """
    Runs statistical tests on a hypothesis.
    Returns passes_all_gates boolean.
    """

    name = "validate_hypothesis"
    description = "Validate hypothesis against statistical gates"
    version = "1.0.0"

    class Input(SkillInput):
        hypothesis: dict = Field(..., description="Hypothesis to validate")
        historical_data: list[dict] = Field(
            ...,
            description="Historical campaign data"
        )

    class Output(SkillOutput):
        passes_all_gates: bool | None = None
        gate_results: dict | None = None
        recommended_action: str | None = None

    # Gate definitions (from VALIDATION_PIPELINE.md)
    GATES = {
        "data_quality": {"min_score": 0.85},
        "confounds": {"max_confounds": 1},
        "significance": {"max_p_value": 0.05},
        "effect_size": {"min_cohens_d": 0.05},
        "replication": {"min_segments": 2}
    }

    async def execute(self, input_data: Input) -> Output:
        gate_results = {}

        # Gate 1: Data Quality
        gate_results["data_quality"] = self._check_data_quality(
            input_data.historical_data
        )

        # Gate 2: Confounds
        gate_results["confounds"] = self._check_confounds(
            input_data.hypothesis,
            input_data.historical_data
        )

        # Gate 3: Statistical Significance
        gate_results["significance"] = self._check_significance(
            input_data.hypothesis,
            input_data.historical_data
        )

        # Gate 4: Effect Size
        gate_results["effect_size"] = self._check_effect_size(
            input_data.hypothesis,
            input_data.historical_data
        )

        # Gate 5: Replication
        gate_results["replication"] = self._check_replication(
            input_data.hypothesis,
            input_data.historical_data
        )

        # All gates must pass
        passes_all = all(
            gate_results[g]["passed"]
            for g in self.GATES.keys()
        )

        rec = "queue_for_outer_loop" if passes_all else "reject"

        return Output(
            success=True,
            data={
                "passes_all_gates": passes_all,
                "gate_results": gate_results,
                "recommended_action": rec
            }
        )
```

---

## Week 4: End-to-End Loop

### Skill 5: copy_generator

**Priority:** MEDIUM — demonstrates full loop

```python
# skills/copy_generator/skill.py

class CopyGeneratorSkill(Skill):
    """
    Generates ad copy variants using AI.
    Phase 1: Uses Claude only (no routing decision needed yet).
    """

    name = "copy_generator"
    description = "Generate ad copy variants for campaigns"
    version = "1.0.0"

    class Input(SkillInput):
        campaign_id: str = Field(..., description="Campaign ID")
        product_description: str = Field(..., description="Product description")
        audience_segment: str = Field(..., description="Target audience")
        tone: str = Field(default="professional")
        num_variants: int = Field(default=3, ge=1, le=10)
        platform: str = Field(..., description="google | meta | tiktok")

    class Output(SkillOutput):
        variants: list[dict] | None = None

    async def execute(self, input_data: Input) -> Output:
        # Fetch campaign context
        kg = MarketingKnowledgeGraph()
        campaign = kg.get_campaign(input_data.campaign_id)

        # Generate with Claude
        prompt = f"""Generate {input_data.num_variants} ad copy variants for:
Product: {input_data.product_description}
Audience: {input_data.audience_segment}
Tone: {input_data.tone}
Platform: {input_data.platform}

Return JSON array with: headline, description, call_to_action"""

        response = await self.claude.generate(prompt)
        variants = json.loads(response.content)

        return Output(
            success=True,
            data={"variants": variants}
        )
```

---

### Skill 6: budget_allocator

**Priority:** MEDIUM — shows learning → action

**Version 1 (MVP): Simple proportional allocation**

```python
# skills/budget_allocator/skill.py

class BudgetAllocatorSkill(Skill):
    """
    Allocates budget across segments based on ROAS.
    Version 1: Simple proportional to denoised ROAS.
    """

    name = "budget_allocator"
    description = "Allocate budget across audience segments"
    version = "1.0.0"

    class Input(SkillInput):
        campaign_id: str = Field(..., description="Campaign ID")
        total_budget: float = Field(..., description="Total budget to allocate")
        segment_metrics: list[dict] = Field(
            ...,
            description="Denoised ROAS per segment"
        )
        min_allocation_pct: float = Field(
            default=0.05,
            description="Minimum 5% per segment"
        )

    class Output(SkillOutput):
        allocations: list[dict] | None = None
        expected_roas_change: float | None = None

    async def execute(self, input_data: Input) -> Output:
        # 1. Calculate weights based on ROAS
        weights = self._calculate_weights(input_data.segment_metrics)

        # 2. Apply min allocation constraint
        allocations = self._apply_min_constraints(
            weights,
            input_data.total_budget,
            input_data.min_allocation_pct
        )

        # 3. Calculate expected ROAS change
        current_roas = np.mean([s["roas"] for s in input_data.segment_metrics])
        expected_roas = np.sum([
            a["pct"] * s["roas"]
            for a, s in zip(allocations, input_data.segment_metrics)
        ])
        expected_change = (expected_roas / current_roas) - 1

        return Output(
            success=True,
            data={
                "allocations": allocations,
                "expected_roas_change": expected_change
            }
        )

    def _calculate_weights(self, segment_metrics: list[dict]) -> list[float]:
        """
        Proportional allocation based on ROAS.
        Higher ROAS = higher weight.
        """
        roas_values = np.array([s["roas"] for s in segment_metrics])
        # Softmax-like normalization
        weights = roas_values / roas_values.sum()
        return weights.tolist()
```

---

## Post-MVP Skills (Phase 2+)

```
┌─────────────────────────────────────────────────────────────────┐
│                    POST-MVP SKILLS                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PHASE 2: COMPETITIVE + CREATIVE                               │
│  ───────────────────────────────────────────────────────────  │
│                                                                 │
│  7. competitor_monitor                                          │
│     → Weekly scrape of competitor ad libraries                 │
│     → New ad detection, theme extraction                       │
│                                                                 │
│  8. creative_optimizer                                         │
│     → A/B test result analysis                                │
│     → CTR/CVR optimization                                     │
│                                                                 │
│  9. headline_tester                                           │
│     → Sequential testing for headlines                         │
│     → Multi-armed bandit for allocation                        │
│                                                                 │
│  PHASE 3: ADVANCED LEARNING                                   │
│  ───────────────────────────────────────────────────────────  │
│                                                                 │
│  10. pattern_learner                                           │
│      → Cross-campaign pattern detection                       │
│      → Transfer learning between campaigns                     │
│                                                                 │
│  11. budget_optimizer (v2)                                     │
│      → Bayesian optimization for multi-campaign              │
│      → Uncertainty-aware exploration                         │
│                                                                 │
│  12. attribution_modeler                                      │
│      → Data-driven attribution                                │
│      → Shapley values for channel contribution               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Skill Implementation Order

```
WEEK 1:
├── Day 1-2: get_campaign_data
│   └── MCP connection setup, basic fetch
├── Day 3-4: get_campaign_data tests
│   └── Unit + integration tests
└── Day 5: calculate_denoised_roas
    └── BSTS integration

WEEK 2:
├── Day 1-2: calculate_denoised_roas tests + refine
├── Day 3-4: hypothesis_generator
│   └── Claude prompt engineering
└── Day 5: hypothesis_generator tests

WEEK 3:
├── Day 1-2: validate_hypothesis
│   └── All 5 gates implemented
├── Day 3-4: validate_hypothesis tests
│   └── Edge cases, false positives
└── Day 5: End-to-end integration test

WEEK 4:
├── Day 1-2: copy_generator
│   └── Claude-only (no routing yet)
├── Day 3-4: budget_allocator v1
│   └── Simple proportional
└── Day 5: MVP Demo + retrospective
```
