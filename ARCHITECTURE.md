# MAIAgent Architecture — Full Technical Specification

**Version:** 2.0  
**Status:** Architecture Complete, Implementation Pending  
**Last Updated:** 2026-07-02

---

## Table of Contents

1. [Overview](#1-overview)
2. [The Learning Mechanism](#2-the-learning-mechanism)
3. [Two-Loop Architecture](#3-two-loop-architecture)
4. [Memory Architecture](#4-memory-architecture)
5. [Model Layer](#5-model-layer)
6. [Tool + Execution Layer](#6-tool--execution-layer)
7. [Skills Architecture](#7-skills-architecture)
8. [Validation Pipeline](#8-validation-pipeline)
9. [Human Oversight](#9-human-oversight)
10. [Open Questions](#10-open-questions)

---

## 1. Overview

### 1.1 Design Principles (Non-Negotiable)

```
┌─────────────────────────────────────────────────────────────────┐
│                    CORE PRINCIPLES                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. NO RAW RL                                                   │
│     - Always denoise rewards before learning                     │
│     - Always use statistical significance gate                    │
│     - Always require replication across segments/time             │
│                                                                 │
│  2. HUMAN-IN-THE-LOOP (Non-Negotiable)                       │
│     - >$1000 budget changes → Human required                   │
│     - Content posting → Human required                          │
│     - Model updates → Human required                             │
│     - Brand/legal risk → Human required                        │
│                                                                 │
│  3. VALIDATE ONE THING BEFORE SCALING                         │
│     - Prove learning mechanism on 1 campaign type first         │
│     - Then scale to 2, then 5, then all                        │
│                                                                 │
│  4. MARKETING TIMESCALES                                        │
│     - Inner loop: Daily + Weekly (observe, flag, hypothesize)   │
│     - Outer loop: Monthly (synthesize, validate, update)      │
│     - Patience: Minimum 14-day observation windows               │
│                                                                 │
│  5. HYBRID EVERYWHERE                                          │
│     - Memory: Graph + Vector + Episodic                        │
│     - Model: Small (routing) + Claude (reasoning)             │
│     - Tool: n8n (execution) + MAIAgent (decisions)            │
│     - Skills: Code + Docs + Tests + Interface Contract         │
│                                                                 │
│  6. AUDIT TRAIL (Everything Logged)                            │
│     - All model updates with evidence + approver                 │
│     - All rollbacks with reason + trigger                      │
│     - Retention: Permanent for model updates, 2 years for logs  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        HUMAN IN THE LOOP (Gate)                            │
│         High-stakes decisions (>$1000, content posting, brand risk)          │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────────────┐
│                 OUTER LOOP (Monthly/Quarterly)                              │
│  ─── Strategy synthesis ─── Statistical significance gate ─── Model update │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────────────┐
│                 INNER LOOP (Daily + Weekly)                                  │
│  ─── Daily: SPC monitoring, quick hypotheses (06:00 UTC)                    │
│  ─── Weekly: Deep analysis, segment patterns, competitor moves (Monday)      │
│  ─── NO model updates ─ Queue for outer loop review                         │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────────────┐
│              LEARNING MECHANISM (Bayesian + SFT Hybrid)                     │
│  ─── Reward denoising layer (causal impact analysis)                       │
│  ─── Bayesian optimization (noise-tolerant GP regression)                   │
│  ─── Supervised fine-tuning on validated (query → outcome) pairs            │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────────────┐
│                         MEMORY ARCHITECTURE                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │Knowledge     │◄─►│Vector        │  │SQLite/      │                  │
│  │Graph         │  │Store         │  │Episodic     │                  │
│  │(Reasoning)   │  │(Retrieval)   │  │(Audit)      │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────────────┐
│                    MODEL LAYER (Hybrid)                                     │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐           │
│  │Small Model    │─────►│Claude-class  │─────►│Human Review │           │
│  │(Routing/     │      │(Strategic    │      │(High-       │           │
│  │Classification)│      │Reasoning)    │      │Stakes)      │           │
│  └──────────────┘      └──────────────┘      └──────────────┘           │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────────────┐
│                    TOOL + EXECUTION LAYER                                 │
│  ┌──────────────┐      ┌──────────────┐                                  │
│  │MAIAgent      │─────►│n8n           │                                  │
│  │(Decisions)    │      │(Execution)   │                                  │
│  └──────────────┘      └──────────────┘                                  │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────────────┐
│                    SKILLS LAYER                                            │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │ Each skill: SKILL.md + skill.py + skill_test.py + config.py     │    │
│  │ SkillRegistry: Dependency injection, circuit breakers             │    │
│  └──────────────────────────────────────────────────────────────────┘    │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────────────┐
│                    VALIDATION PIPELINE                                     │
│  ─── Data quality ─── Confound detection ─── Significance ─── Replication  │
│  ─── Human review ─── Shadow deploy (7d) ─── Canary deploy (14d)         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. The Learning Mechanism

**The Core Problem:** Marketing metrics are HIGH VARIANCE. ROAS swings 20-40% daily due to seasonality, competitor actions, audience fatigue. Raw RL amplifies this noise → false patterns → catastrophic strategy shifts.

**The Solution:** Bayesian Optimization + Supervised Fine-tuning on Validated Pairs.

### 2.1 Reward Denoising Layer (Required First)

```
Raw Signal ──► Confounder Detection ──► Denoised Reward ──► Learning

CONFOUNDERS HANDLED:
- Day-of-week effects (Mon ≠ Fri for e-commerce)
- Seasonality (Black Friday ≠ random Tuesday)
- Audience fatigue (repeated exposure decay)
- Competitor confounds (rival sale, PR crisis)
- Budget confounds (spend changes during measurement window)

METHOD: Causal impact analysis (Bayesian structural time-series)
OUTPUT: Denoised ROAS with confidence interval
```

### 2.2 Bayesian Optimization (Weekly)

```
For each tunable parameter (bid, audience segment weights, creative mix):
  1. Fit Gaussian Process regression
     - Input: parameter values
     - Output: denoised ROAS
     - Kernel: RBF + linear drift
  2. Acquisition function: Expected Improvement with uncertainty penalty
  3. Propose next parameter setting
  4. Run for minimum 14 days OR until GP fit R² > 0.3
  5. IF R² < 0.1 after 30 days → FLAG as not learnable
```

### 2.3 Supervised Fine-tuning (Monthly)

```
CRITERIA FOR VALIDATION:
- Denoised ROAS improvement is statistically significant
- Effect replicates across at least 2 distinct audience segments
- Effect persists for minimum 7 days post-observation
- No confounding variables correlated with treatment

TRAINING DATA CONSTRUCTION:
- Positive pairs: (query_context, recommended_action, outcome) where outcome > baseline
- Negative pairs: (query_context, recommended_action, outcome) where outcome < baseline
- Mix ratio: 3:1 positive:negative

BASE MODEL: Claude Haiku (or equivalent small model)
TRAINING: LoRA on validated pairs only (max 1000 pairs to avoid overfitting)
```

---

## 3. Two-Loop Architecture

### 3.1 Inner Loop (Daily + Weekly)

The inner loop operates at **two timescales**: fast daily monitoring and deeper weekly analysis.

```
┌─────────────────────────────────────────────────────────────────┐
│                 INNER LOOP (Daily 06:00 UTC)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  DAILY (06:00 UTC)                                             │
│  1. Ingests yesterday's performance data                         │
│  2. Runs statistical process control (EWMA chart on ROAS)      │
│     - Flag if ROAS deviates > 2σ from rolling mean            │
│  3. Generates quick hypothesis candidates (NOT model updates)  │
│  4. Scores hypothesis confidence (Bayesian A/B test)           │
│  5. Queues promising hypotheses (p < 0.2) for outer loop       │
│                                                                 │
│  WEEKLY (Monday 06:00 UTC)                                     │
│  1. Collects week's data                                        │
│  2. Week-over-week trend analysis                              │
│  3. Segment-level deep dive (winners/losers)                   │
│  4. Creative fatigue detection (CTR decay patterns)             │
│  5. Competitor movement analysis (new ads, positioning)         │
│  6. Strategic hypothesis generation                              │
│  7. Publishes weekly brief                                       │
│                                                                 │
│  WHAT IT CANNOT DO:                                            │
│  - ANY model weight changes                                    │
│  - ANY parameter updates                                       │
│  - ANY automated budget reallocation >$100                     │
│  - ANY content posting                                         │
│                                                                 │
│  OUTPUT: Daily brief + Weekly brief + prioritized hypothesis queue│
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Outer Loop (Monthly)

```
┌─────────────────────────────────────────────────────────────────┐
│                 OUTER LOOP (First Monday Monthly)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  WHAT IT DOES:                                                 │
│  1. Synthesizes accumulated hypotheses into strategic themes    │
│  2. Runs full statistical significance validation              │
│  3. Authorizes model updates (ONLY if gate criteria met)      │
│  4. Reviews and approves/rejects A/B test portfolio           │
│  5. Updates knowledge graph with validated causal relationships │
│                                                                 │
│  WHAT IT CAN ONLY DO WITH HUMAN REVIEW:                        │
│  - Model weight updates to production router                    │
│  - Budget reallocation > $1000/month cumulative               │
│  - New audience segment targeting                              │
│  - Creative strategy pivots                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 Statistical Significance Gate

```
GATE CRITERIA (ALL must pass):
┌─────────────────────────────────────────────────────────────────┐
│  1. Effect Size: |denoised_ROAS_improvement| > 5%             │
│  2. Statistical Test: T-test on denoised ROAS distributions  │
│  3. P-value threshold: p < 0.05 (BH-corrected)              │
│  4. Minimum Sample: 1000 impressions per variant              │
│  5. Effect Persistence: 7 consecutive days                    │
│  6. No Confound: Correlation with confounders < 0.2          │
└─────────────────────────────────────────────────────────────────┘

FAIL ANY → NO MODEL UPDATE. Log and continue monitoring.
```

---

## 4. Memory Architecture

### 4.1 Knowledge Graph (Explicit, Structured, Auditable)

```
NODES:
- Campaign (id, name, start_date, end_date, status, budget)
- AudienceSegment (id, name, demographics, interests)
- CreativeAsset (id, type, url, performance_history)
- Channel (id, platform, cost_model)
- OutcomeMetric (id, type, value, timestamp)

RELATIONSHIPS:
- Campaign → TARGETS → AudienceSegment
- Campaign → USES → CreativeAsset
- Campaign → RUNS_ON → Channel
- Campaign → PRODUCES → OutcomeMetric
- AudienceSegment → SIMILAR_TO → AudienceSegment (similarity score)
- CreativeAsset → A_B_TESTED_WITH → CreativeAsset (head-to-head results)

ENTITY RESOLUTION:
- Canonical name table: "Meta" = "Facebook" = "FB" = "Facebook Ads"
- Fuzzy matching via embedding similarity at ingestion time
- Human-in-the-loop for new entity merge suggestions
- Versioned entity IDs (entity_v2 when merged)
```

### 4.2 Vector Store (Retrieval, Similarity)

```
WHAT STORES HERE:
- Campaign descriptions (unstructured text)
- Creative copy and messaging
- Audience segment natural language descriptions
- Strategy documents and rationales

EMBEDDING MODEL: sentence-transformers/all-MiniLM-L6-v2

INDEX STRATEGY:
- Separate indices per entity type
- Hybrid search: vector similarity + metadata filter
- Re-rank with cross-encoder for final results

QUERY PATTERNS:
- "Find campaigns similar to this one"
- "What worked for automotive clients before?"
- "Find creative angle that resonated with Gen Z"
```

### 4.3 Episodic Store / SQLite (Session Logs, Raw Feedback)

```
TABLES:
- session_log (id, timestamp, agent_id, query, response, latency_ms)
- hypothesis (id, created_at, description, confidence, status)
- experiment_run (id, hypothesis_id, start_date, end_date, result)
- feedback (id, session_id, is_positive, feedback_text)
- model_update_log (id, timestamp, what_changed, approved_by, p_value)

RETENTION:
- Session logs: 90 days
- Hypotheses: Until resolved or archived
- Experiments: Permanent
- Model updates: Permanent (audit trail)
```

### 4.4 How They Interact

```
NEW CAMPAIGN CREATED:
- Parse structured fields → Knowledge Graph
- Embed description → Vector Store (with KG node ID reference)
- Log session → Episodic Store

QUERY: "What worked for DTC brands?"
- Embed query → Vector Store
- For each result, fetch from KG (full structured context)
- Fuse: "Campaign X worked because [KG] + similar to [vector]"

ENTITY RESOLUTION: "Meta" seen for first time
- Embed "Meta" → Vector Store
- Find most similar entity (similarity > 0.85?)
- If match → propose merge (Human reviews)
- If no match → create new entity
```

---

## 5. Model Layer

### 5.1 Decision Tree for Model Selection

```
┌─────────────────────────────────────────────────────────────────┐
│          IS THIS HIGH-STAKES? (> $1000, brand, content)       │
│                            │                                    │
│          YES ──────────────┼─────────────── NO                │
│                            │                      │             │
│                            ▼                      ▼             │
│                   ┌─────────────┐      IS ROUTING?            │
│                   │HUMAN REVIEW │      (channel, segment,     │
│                   │ REQUIRED    │       bid tier, format)      │
│                   └─────────────┘              │             │
│                                          YES ─┼── NO         │
│                                               │    │         │
│                                               ▼    ▼         │
│                                          ┌─────┐ ┌─────┐   │
│                                          │SMALL│ │CLAUDE│  │
│                                          │MODEL│ │CLASS │   │
│                                          └─────┘ └─────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Task Assignment

```
ROUTING TASKS (→ Small Model, auto if confidence > 0.75):
- Channel selection (Facebook vs Google vs TikTok)
- Audience segment classification
- Bid tier assignment
- Creative format selection (image vs video vs carousel)
- Placement selection (feed vs story vs search)
- Dayparting recommendations

REASONING TASKS (→ Claude-class, always):
- Campaign strategy formulation
- Creative concept development
- Audience strategy deep-dive
- Competitive positioning analysis
- Budget allocation strategy across campaigns
- Performance diagnosis (why did ROAS drop?)

HIGH-STAKES TASKS (→ Human + Claude):
- Budget reallocation > $1000
- New campaign launch (brand risk)
- Content that mentions competitors
- Legal/prohibited content categories
- Crisis response
```

### 5.3 Small Model Router

```
MODEL: Claude Haiku (or Mistral-7B-Instruct quantized)
METHOD: LoRA fine-tuned on historical routing decisions
TASK: Multi-class classification (5-10 channel/audience classes)

OUTPUT FORMAT:
{
  "recommended_channel": "google",
  "confidence": 0.82,
  "alternatives": [
    {"channel": "meta", "score": 0.71},
    {"channel": "tiktok", "score": 0.45}
  ],
  "requires_review": false  // auto-true if confidence < 0.75
}

GUARDRAILS:
- Confidence < 0.75 → Flag for human review
- Any class probability > 0.95 → Warning (overconfidence)
- Distribution shift detected → flag
```

---

## 6. Tool + Execution Layer

### 6.1 Boundary Definition

```
MAIAgent (Decision Engine):
┌─────────────────────────────────────────────────────────────────┐
│ WHAT IT DOES:                                                 │
│ - Analyzes marketing data                                       │
│ - Generates recommendations                                      │
│ - Makes low-stakes routing decisions (confidence > 0.75)        │
│ - Escalates high-stakes to human                               │
│ - Learns from feedback (via learning mechanism)                 │
│                                                                 │
│ WHAT IT CANNOT DO:                                             │
│ - Execute anything directly (no direct API calls to ad platforms)│
│ - Post content without human approval                          │
│ - Change budget > $100 without human review                    │
│ - Make strategic decisions without human review                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ (Approved action + approval token)
                              ▼
n8n (Execution Engine):
┌─────────────────────────────────────────────────────────────────┐
│ WHAT IT DOES:                                                 │
│ - Executes human-approved actions                              │
│ - Handles webhook triggers from ad platforms                   │
│ - Manages scheduled reporting jobs                             │
│ - Sends notifications (Slack, email)                           │
│                                                                 │
│ WHAT IT CANNOT DO:                                            │
│ - Make decisions (only executes pre-approved actions)           │
│ - Learn or adapt (no model updates)                           │
│ - Override human decisions                                    │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 Action Approval Flow

```
1. MAIAgent generates recommendation

2. IF high-stakes (>$100, content, brand risk):
   - Send to Human Review Queue (Slack notification)
   - Human: Approve / Reject / Modify
   - IF approved → Forward to n8n with approval token
   - IF rejected → Log and close

3. IF low-stakes (confidence > 0.75):
   - Execute directly via n8n

4. n8n receives action:
   - Validates approval token (reject if missing/invalid)
   - Executes action on ad platform API
   - Logs execution result
   - Sends confirmation back to MAIAgent

5. MAIAgent logs outcome for learning mechanism
```

### 6.3 MCP Integration

```
MCP SERVERS (MAIAgent calls - read/recommend):
- Google Ads (read/write)
- Meta Ads (read/write)
- Analytics (read only)

MCP SERVERS (n8n calls - execute after approval):
- Google Ads (write only after approval)
- Meta Ads (write only after approval)
- Slack (notify)

FRAGILITY MITIGATION:
- Versioned MCP schemas (lock to major version)
- Graceful degradation: if MCP fails → human decision
- Circuit breaker: after 3 failures → pause and alert
- Health checks before any action
```

---

## 7. Skills Architecture

### 7.1 Directory Structure

```
skills/
├── my-skill/
│   ├── SKILL.md           ← Documentation (what, when, input, output)
│   ├── skill.py           ← Implementation
│   ├── skill_test.py       ← Unit tests (required)
│   ├── skill_config.py     ← Configuration schema
│   └── examples/
│       ├── example1.yaml
│       └── example2.yaml
└── another-skill/
    └── ...
```

### 7.2 Interface Contract

```
ALL skills MUST implement:
1. execute(input: InputSchema) → OutputSchema
2. validate_input(raw: dict) → InputSchema (raises on invalid)
3. get_schema() → (InputSchema, OutputSchema)

Skills CAN call other skills via SkillRegistry:
  result = await self.registry.call('another-skill', input_data)

SkillRegistry handles:
- Dependency injection
- Error propagation
- Timeout management
- Circuit breaking (if callee fails 3x → skip)
```

### 7.3 Common Reusable Skills

```
skill: get_campaign_data
  input: {campaign_id, date_range, metrics_needed}
  output: {campaign_data, data_quality_score}
  used_by: diagnosis, performance_review, budget_analysis

skill: calculate_denoised_roas
  input: {raw_metrics, confounders, control_series}
  output: {denoised_roas, ci_width, is_learnable}
  used_by: hypothesis_generation, model_update_validation

skill: format_for_human
  input: {data, context, human_readable_goal}
  output: {formatted_text, summary, key_metrics}
  used_by: approval_requests, reports, alerts
```

---

## 8. Validation Pipeline

### 8.1 Pre-Update Validation Stages

```
STEP 1: DATA QUALITY CHECK
- Missing data < 10%? (if not → flag, use imputation)
- Outliers within 4σ? (if not → cap at 4σ)
- Control group size adequate? (n > 100 per variant)
- Time series stationarity? (ADF test, p > 0.05)
FAIL → Abort

STEP 2: CONFOUND DETECTION
- Day-of-week correlation < 0.3
- Seasonality adjustment applied
- Competitor activity flagged
- Budget changes during window flagged
FAIL → Flag as confounded, do not use for update

STEP 3: STATISTICAL SIGNIFICANCE
- Two-sample t-test (or Mann-Whitney U if non-normal)
- Benjamini-Hochberg correction for multiple comparisons
- Effect size (Cohen's d) > 0.2
- 95% CI on effect size does not include 0
FAIL ANY → NO MODEL UPDATE

STEP 4: REPLICATION CHECK
- Effect replicates across at least 2 distinct audience segments
- Effect replicates across at least 2 different time periods
EXCEPTION: Large effect (d > 0.8) requires only 1 segment + 1 period
FAIL → Require more data

STEP 5: HUMAN REVIEW
- Submit: what changed, evidence (p-value, effect size, CI), risks, rollback procedure
- Human must explicitly approve (digital signature logged)
FAIL → NO MODEL UPDATE

STEP 6: SHADOW DEPLOY (7 days)
- New model runs IN PARALLEL with production
- Compare shadow vs production predictions (should match > 95%)
- If shadow degrades > 2% → auto-rollback

STEP 7: CANARY DEPLOY (14 days)
- Route 10% of traffic to new model
- Monitor: Denoised ROAS >= baseline, error rate < 1%, latency < 500ms p95
- If ALL pass for 14 days → Full rollout
- If ANY degrades → Rollback
```

### 8.2 Rollback Triggers

```
AUTO-ROLLBACK (No human needed):
- Canary ROAS drops > 5% vs baseline for 3 consecutive days
- Error rate > 5% (vs baseline < 1%)
- Latency p99 > 2000ms
- Shadow prediction mismatch > 10%

MANUAL REVIEW (Human decides):
- Canary ROAS drops 2-5% vs baseline for 7 days
- High variance in metrics
- Negative user feedback
```

---

## 9. Human Oversight

### 9.1 Decision Authority Matrix

```
ACTION                          AUTOMATIC    HUMAN REQUIRED
─────────────────────────────────────────────────────────
Channel selection (confidence > 0.75)    ✓
Channel selection (confidence < 0.75)                ✓
Bid tier assignment (confidence > 0.75)    ✓
Bid tier (confidence < 0.75)                       ✓
Budget change < $100                      ✓
Budget change $100-$1000                             ✓
Budget change > $1000                                 ✓
Ad copy variation (low stakes)             ✓
Ad copy mentioning competitor                          ✓
New audience segment                               ✓
Model weight update                                 ✓
Creative strategy pivot                              ✓
Crisis response                                     ✓
```

### 9.2 Human Review UX

```
When human review is required:
1. Notification sent to Slack (#mais-approvals channel)
2. Message includes:
   - Recommendation with full reasoning chain
   - Confidence score
   - What could go wrong
   - Rollback procedure
   - [Approve] [Reject] [Modify] buttons
3. Escalation: If no response in 4 hours → alert manager
4. All approvals logged permanently
```

---

## 10. Open Questions

These will be resolved during Phase 1 validation:

```
1. CAUSAL MODEL CHOICE
   - BSTS vs CausalImpact vs DoWhy?
   - Need to benchmark on actual marketing data

2. GP KERNEL SELECTION
   - RBF+linear drift vs Mattern?
   - Need to test on marketing parameter landscapes

3. SFT DATASET SIZE CAP
   - 1000 pairs is estimate
   - May need adjustment based on model capacity

4. CONFIDENCE THRESHOLD FOR AUTO-ROUTING
   - 0.75 is starting point
   - Need to calibrate based on review queue depth and error rate

5. ENTITY RESOLUTION THRESHOLD
   - 0.85 similarity for merge suggestion
   - May need adjustment based on false positive/negative rates
```

---

## Appendix: File Map

| Document | Purpose |
|----------|---------|
| ARCHITECTURE.md | This file — full technical spec |
| LEARNING_MECHANISM.md | Reward denoising + Bayesian optimization |
| TWO_LOOP_ARCHITECTURE.md | Inner/outer loop design |
| MEMORY_ARCHITECTURE.md | Knowledge graph + vector + episodic |
| MODEL_LAYER.md | Small model + Claude + routing |
| TOOL_LAYER.md | MAIAgent + n8n + MCP |
| SKILLS_ARCHITECTURE.md | Code + docs + tests structure |
| VALIDATION_PIPELINE.md | Pre-update validation + rollback |
| AGENT_COUNCIL_REPORT.md | Skeptical review by 6 agents |
| RESEARCH.md | Competitive landscape + vault research |
