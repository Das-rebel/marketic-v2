# Implementation Roadmap — MAIS 2.0

**Related to:** ARCHITECTURE.md Section 10

---

## Overview

This roadmap converts architecture into actionable phases with concrete success criteria, team requirements, and rollback triggers. **Every phase must pass its success criteria before proceeding to the next.**

```
┌─────────────────────────────────────────────────────────────────┐
│                    IMPLEMENTATION PHASES                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PHASE 0: Infrastructure (Weeks 1-2)                          │
│  ───────────────────────────────────────────────────────────  │
│  Goal: Get MAIAgent talking to real ad platforms               │
│  Success: Can read 30 days of campaign data from 1 account    │
│                                                                 │
│  PHASE 1: Single Campaign Learning Loop (Weeks 3-8)           │
│  ───────────────────────────────────────────────────────────  │
│  Goal: Validate learning mechanism on 1 campaign               │
│  Success: Denoised ROAS within 10% of ground truth            │
│                                                                 │
│  PHASE 2: Multi-Campaign Orchestration (Weeks 9-16)          │
│  ───────────────────────────────────────────────────────────  │
│  Goal: Scale to 5 campaigns with shared learning              │
│  Success: Cross-campaign pattern detection works                │
│                                                                 │
│  PHASE 3: Autonomous Operation (Weeks 17+)                    │
│  ───────────────────────────────────────────────────────────  │
│  Goal: Full autonomous operation with human oversight          │
│  Success: 1 model update/month with < 10% rollback rate        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 0: Infrastructure (Weeks 1-2)

**Goal:** Get MAIAgent talking to real ad platforms. No learning yet — just data ingestion and storage.

### Team Requirements
- 1 backend engineer (MCP setup, API integrations)
- 1 data engineer (schema design, data pipelines)

### Tasks

```
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 0 TASK CHECKLIST                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  WEEK 1                                                         │
│  ───────────────────────────────────────────────────────────  │
│  [ ] Set up development environment                            │
│      - Python 3.11+, Node 18+                                 │
│      - Docker + docker-compose                                │
│      - Local Neo4j (or cloud if team prefers)                  │
│      - ChromaDB for vector store                              │
│      - SQLite for episodic store                              │
│                                                                 │
│  [ ] MCP server setup                                         │
│      - Google Ads MCP connection                              │
│      - Meta Ads MCP connection                                 │
│      - Test read operations for both platforms                 │
│      - Document API rate limits and quotas                    │
│                                                                 │
│  [ ] Knowledge Graph schema implementation                     │
│      - CampaignNode, AudienceSegmentNode, CreativeAssetNode    │
│      - ChannelNode, OutcomeMetricNode                         │
│      - Relationship types (TARGETS, USES, RUNS_ON, PRODUCES)  │
│      - Indexes for common query patterns                      │
│                                                                 │
│  WEEK 2                                                         │
│  ───────────────────────────────────────────────────────────  │
│  [ ] Vector store setup                                       │
│      - ChromaDB with all-MiniLM-L6-v2 embeddings              │
│      - Collections: campaigns, audiences, creatives           │
│      - Hybrid search implementation                           │
│                                                                 │
│  [ ] Episodic store setup                                     │
│      - SQLite with SessionLog, Hypothesis, ExperimentRun tables │
│      - ModelUpdate table with full audit schema               │
│      - Retention policies configured                          │
│                                                                 │
│  [ ] Slack integration                                       │
│      - Webhook for daily briefs                              │
│      - Approval workflow bot (Slash commands)                 │
│      - Alert channels configured                              │
│                                                                 │
│  [ ] End-to-end data ingestion test                           │
│      - Pull 30 days of historical data from 1 campaign       │
│      - Ingest into KG, vector store, episodic store          │
│      - Verify relationships are correct                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Success Criteria

| Metric | Target | How to Measure |
|--------|--------|----------------|
| MCP connection uptime | > 99% | Heartbeat monitoring |
| Data freshness | < 4 hours | Last-updated timestamp |
| KG node count | > 100 nodes ingested | KG query count |
| Vector store documents | > 100 indexed | ChromaDB count |
| Data quality score | > 0.85 | Automated quality checks |
| Slack notifications | All sending | Integration tests |

### Phase 0 Exit Gate

```
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 0 EXIT GATE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  BEFORE PROCEEDING TO PHASE 1, VERIFY:                         │
│                                                                 │
│  □ Can read 30 days of real campaign data from 1 account        │
│  □ KG has campaign + audience + creative + channel nodes        │
│  □ KG has outcome metrics with daily granularity                │
│  □ KG relationships (TARGETS, USES, RUNS_ON) are correct      │
│  □ Vector store indexes 100+ documents                         │
│  □ Episodic store logs are being written                       │
│  □ Slack receives daily brief notifications                     │
│  □ All integrations pass smoke tests                           │
│                                                                 │
│  If ANY criterion fails → Do not proceed to Phase 1            │
│  Document failure, fix, then re-verify                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Single Campaign Learning Loop (Weeks 3-8)

**Goal:** Validate the learning mechanism on 1 campaign. Run 2 outer loop cycles. Prove we can learn without breaking.

### Team Requirements
- 1 backend engineer (continuing)
- 1 ML engineer (causal inference, Bayesian optimization)
- 1 data scientist (statistical validation, A/B test design)

### Tasks

```
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 1 TASK CHECKLIST                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  WEEK 3: Data Foundation                                       │
│  ───────────────────────────────────────────────────────────  │
│  [ ] Implement get_campaign_data skill                         │
│      - Fetch 14+ days of ROAS, spend, conversions             │
│      - Output: DailyMetrics with confidence intervals           │
│      - Data quality scoring                                    │
│                                                                 │
│  [ ] Implement calculate_denoised_roas skill                   │
│      - Apply BSTS causal model                                │
│      - Output: denoised_roas, ci_95, confound_flags           │
│      - Validation: compare to ground truth (known effects)     │
│                                                                 │
│  WEEK 4: Learning Foundation                                   │
│  ───────────────────────────────────────────────────────────  │
│  [ ] Implement SPCMonitor (EWMA chart)                         │
│      - Daily ROAS monitoring                                   │
│      - Anomaly flagging                                       │
│      - Alert on deviation > 2σ                                │
│                                                                 │
│  [ ] Implement hypothesis_generator skill                       │
│      - Takes anomaly flags from SPC                            │
│      - Outputs: 3-5 candidate explanations with confidence      │
│      - Claude reasoning for candidate generation               │
│                                                                 │
│  WEEK 5: Validation Pipeline                                   │
│  ───────────────────────────────────────────────────────────  │
│  [ ] Implement DataQualityGate (Stage 1)                       │
│      - Missing data < 5% check                                │
│      - Outlier detection                                      │
│      - Source agreement                                       │
│                                                                 │
│  [ ] Implement ConfoundDetector (Stage 2)                      │
│      - Day-of-week effect detection                            │
│      - Seasonality detection                                   │
│      - Competitor activity flagging                            │
│      - Budget change detection                                 │
│                                                                 │
│  [ ] Implement SignificanceChecker (Stage 3)                   │
│      - T-test with Welch's correction                         │
│      - Benjamini-Hochberg multiple comparison correction        │
│      - Effect size (Cohen's d) check                          │
│                                                                 │
│  WEEK 6: Replication + Human Review                             │
│  ───────────────────────────────────────────────────────────  │
│  [ ] Implement ReplicationChecker (Stage 4)                    │
│      - 2+ segments check                                      │
│      - 2+ time periods check                                  │
│                                                                 │
│  [ ] Implement HumanReviewGate (Stage 5)                       │
│      - Slack approval workflow                                │
│      - Timeout handling (4h tactical, 24h strategic)           │
│      - Escalation path                                        │
│                                                                 │
│  WEEK 7: Shadow + Canary Deploy                               │
│  ───────────────────────────────────────────────────────────  │
│  [ ] Implement ShadowDeploy (Stage 6)                         │
│      - 7-day shadow mode                                     │
│      - Error rate, latency monitoring                         │
│      - Auto-rollback on thresholds                            │
│                                                                 │
│  [ ] Implement CanaryDeploy (Stage 7)                        │
│      - 14-day canary at 10% traffic                          │
│      - ROAS drop detection                                    │
│      - Auto-rollback on -5% ROAS                             │
│                                                                 │
│  WEEK 8: First Outer Loop Cycle                               │
│  ───────────────────────────────────────────────────────────  │
│  [ ] Run complete inner → outer → deploy cycle               │
│  [ ] Measure: Denoised ROAS accuracy vs ground truth          │
│  [ ] Document: All failures, edge cases, surprises             │
│  [ ] Phase 1 retrospective                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Success Criteria

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Denoised ROAS accuracy | Within 10% of ground truth | Compare to known effects |
| Hypothesis queue processing | 100% processed within 48h | Queue timestamps |
| Validation gate pass rate | > 30% pass to human review | Gate statistics |
| Human approval time | < 4 hours (tactical) | Approval log |
| Shadow deploy success | 100% no errors | Shadow monitoring |
| Canary ROAS maintenance | Within -2% of baseline | Canary vs baseline |
| Rollback rate | < 20% of canaries | Canary results |

### Phase 1 Exit Gate

```
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 1 EXIT GATE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  BEFORE PROCEEDING TO PHASE 2, VERIFY:                         │
│                                                                 │
│  □ Completed 2 full outer loop cycles                           │
│  □ Denoised ROAS within 10% of ground truth for BOTH cycles   │
│  □ At least 1 hypothesis passed ALL 7 validation stages       │
│  □ Human approval workflow tested and functional               │
│  □ Shadow deploy completed successfully (7 days)               │
│  □ Canary deploy completed successfully (14 days)              │
│  □ No silent failures — all edge cases logged                 │
│  □ Rollback tested at least once (if applicable)              │
│                                                                 │
│  If ANY criterion fails → Extend Phase 1 by 2 weeks           │
│  Fix issues, re-verify, then proceed                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 2: Multi-Campaign Orchestration (Weeks 9-16)

**Goal:** Scale to 5 campaigns with shared learning. Prove cross-campaign pattern detection works.

### Team Requirements
- 1 backend engineer
- 1 ML engineer
- 1 data scientist
- 1 product manager (defining success metrics)

### Tasks

```
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 2 TASK CHECKLIST                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  WEEK 9-10: Multi-Campaign Data Layer                          │
│  ───────────────────────────────────────────────────────────  │
│  [ ] Scale MCP connections to 5 campaigns                     │
│  [ ] Implement cross-campaign entity resolution                │
│      - Brand name canonicalization                             │
│      - Audience segment matching across platforms               │
│      - Creative asset deduplication                            │
│  [ ] Knowledge Graph: Cross-campaign relationships            │
│      - SimilarTo relationships                                │
│      - Competitor relationships                               │
│  [ ] Vector store: Cross-campaign index                       │
│                                                                 │
│  WEEK 11-12: Shared Learning                                  │
│  ───────────────────────────────────────────────────────────  │
│  [ ] HypothesisGenerator: Cross-campaign patterns             │
│      - "This audience works on campaign X — will it on Y?"   │
│      - Segment effectiveness transfer                          │
│  [ ] Bayesian Optimization: Multi-campaign allocation          │
│      - Budget optimization across campaigns                   │
│      - Uncertainty-aware exploration                          │
│  [ ] PatternLearner: Cross-campaign insights                  │
│      - What works for DTC brands?                             │
│      - What works for B2B?                                   │
│                                                                 │
│  WEEK 13-14: orchestration                                    │
│  ───────────────────────────────────────────────────────────  │
│  [ ] Inner Loop: Multi-campaign coordination                 │
│      - Unified dashboard                                      │
│      - Cross-campaign SPC monitoring                          │
│  [ ] Outer Loop: Shared hypothesis queue                     │
│      - Prioritization across campaigns                        │
│      - Resource allocation decisions                         │
│  [ ] Conflict resolution                                     │
│      - What if Campaign A and B have conflicting signals?     │
│      - Priority rules for budget reallocation                 │
│                                                                 │
│  WEEK 15-16: Scale Validation                                 │
│  ───────────────────────────────────────────────────────────  │
│  [ ] Run 2 outer loop cycles with 5 campaigns                │
│  [ ] Measure: Cross-campaign pattern accuracy                 │
│  [ ] Measure: Budget allocation efficiency                    │
│  [ ] Phase 2 retrospective                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Success Criteria

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Cross-campaign pattern accuracy | > 70% accuracy | Validated patterns |
| Budget reallocation efficiency | > 5% ROAS improvement | Pre/post comparison |
| Entity resolution accuracy | > 90% correct matches | Manual audit sample |
| Queue processing time | < 24 hours | Queue timestamps |
| Conflict resolution time | < 1 hour | Conflict log |
| System scalability | < 2x latency vs single campaign | Load test |

### Phase 2 Exit Gate

```
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 2 EXIT GATE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  BEFORE PROCEEDING TO PHASE 3, VERIFY:                         │
│                                                                 │
│  □ Completed 2 outer loop cycles with 5 campaigns              │
│  □ Cross-campaign patterns validated with > 70% accuracy       │
│  □ Entity resolution accuracy > 90%                            │
│  □ Budget reallocation shows > 5% ROAS improvement            │
│  □ Conflict resolution working without human intervention       │
│  □ No cascading failures across campaigns                      │
│  □ Latency acceptable with 5 campaigns (< 2x single campaign)  │
│                                                                 │
│  If ANY criterion fails → Extend Phase 2 by 2 weeks           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 3: Autonomous Operation (Weeks 17+)

**Goal:** Full autonomous operation with human oversight. Target: 1 model update/month with < 10% rollback rate.

### Team Requirements
- 1 backend engineer (part-time maintenance)
- 1 ML engineer (part-time optimization)
- 1 operations engineer (monitoring, alerting)
- 1 marketing manager (human approval owner)

### Tasks

```
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 3 TASK CHECKLIST                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ONGOING: Daily Operations                                     │
│  ───────────────────────────────────────────────────────────  │
│  [ ] Inner loop running automatically (daily + weekly)         │
│  [ ] Slack briefs delivered to #mais-daily                     │
│  [ ] Anomalies flagged and queued                              │
│  [ ] Data fresh within 4 hours                                 │
│                                                                 │
│  ONGOING: Weekly Operations                                    │
│  ───────────────────────────────────────────────────────────  │
│  [ ] Monday weekly brief delivered                             │
│  [ ] Segment deep-dive completed                              │
│  [ ] Creative fatigue report generated                        │
│  [ ] Competitor movement summary                               │
│                                                                 │
│  ONGOING: Monthly Outer Loop                                  │
│  ───────────────────────────────────────────────────────────  │
│  [ ] Hypothesis synthesis completed                            │
│  [ ] Validation pipeline executed                              │
│  [ ] Human approvals within SLA                               │
│  [ ] Shadow + canary deploy executed                          │
│  [ ] Model update (if approved) deployed                       │
│                                                                 │
│  CONTINUOUS IMPROVEMENT                                       │
│  ───────────────────────────────────────────────────────────  │
│  [ ] Quarterly model review                                    │
│  [ ] Causal inference model retraining                        │
│  [ ] Bayesian optimization tuning                             │
│  [ ] Skill additions based on failures                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Success Criteria

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Model update frequency | 1-2 per month | Update log |
| Rollback rate | < 10% of canaries | Canary results |
| Human approval SLA | 100% within 24h | Approval log |
| System uptime | > 99.5% | Monitoring |
| False positive anomaly rate | < 5% | SPC statistics |
| Cost per decision | < $0.01 | Cost tracking |

---

## Team Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                    TEAM STRUCTURE                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PHASE 0-1 (Weeks 1-8)                                         │
│  ───────────────────────────────────────────────────────────  │
│  Backend Engineer (1)                                           │
│    → MCP integrations, API contracts, data pipelines            │
│                                                                 │
│  Data Engineer (1)                                              │
│    → KG schema, vector store, episodic store                   │
│                                                                 │
│  ML Engineer (1) — Join Week 3                                 │
│    → Causal inference, Bayesian optimization                   │
│                                                                 │
│  Data Scientist (1) — Join Week 3                              │
│    → Statistical validation, A/B test design                   │
│                                                                 │
│  PHASE 2-3 (Weeks 9+)                                          │
│  ───────────────────────────────────────────────────────────  │
│  Backend Engineer (1) — Ongoing                                │
│  ML Engineer (1) — Ongoing                                     │
│  Operations Engineer (1) — Join Phase 3                       │
│  Marketing Manager (0.5) — Human approval owner                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Rollback Triggers

```
┌─────────────────────────────────────────────────────────────────┐
│                    ROLLBACK TRIGGERS                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  IMMEDIATE ROLLBACK (Stop Phase, Escalate):                     │
│  ───────────────────────────────────────────────────────────  │
│  • Denoised ROAS accuracy < 50% (vs ground truth)              │
│  • Validation pipeline produces false positives > 30%          │
│  • Data breach or PII exposure                                 │
│  • Unauthorized budget change                                   │
│                                                                 │
│  PAUSE AND REVIEW:                                             │
│  ───────────────────────────────────────────────────────────  │
│  • Rollback rate > 20% in Phase 1/2                          │
│  • Human approval SLA miss > 10%                             │
│  • System uptime < 99% in any week                           │
│  • Latency 3x above baseline                                  │
│                                                                 │
│  EXTEND PHASE:                                                │
│  ───────────────────────────────────────────────────────────  │
│  • Phase exit gate not met                                    │
│  • > 3 critical bugs in any week                             │
│  • Cost per decision > 2x budget                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Budget

```
┌─────────────────────────────────────────────────────────────────┐
│                    BUDGET ESTIMATE                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PHASE 0-1 (8 weeks)                                           │
│  ───────────────────────────────────────────────────────────  │
│  Engineering (2 FTEs × 8 weeks)              $80,000           │
│  Cloud infrastructure (Neo4j, ChromaDB)        $2,000/month   │
│  API costs (Google, Meta)                          $500/month   │
│  Slack/G-Suite integration                         $100/month   │
│  Phase 0-1 subtotal:                              ~$86,400     │
│                                                                 │
│  PHASE 2 (8 weeks)                                             │
│  ───────────────────────────────────────────────────────────  │
│  Engineering (3 FTEs × 8 weeks)              $120,000           │
│  Infrastructure (same + scaling)                   $3,000/month  │
│  Phase 2 subtotal:                               ~$126,000      │
│                                                                 │
│  PHASE 3 (Ongoing, monthly)                                    │
│  ───────────────────────────────────────────────────────────  │
│  Engineering (2 PTEs × month)                  $20,000/month   │
│  Infrastructure                                  $3,000/month  │
│  API costs (higher volume)                            $2,000/month  │
│  Phase 3 subtotal:                               ~$25,000/month  │
│                                                                 │
│  TOTAL ESTIMATED (Phases 0-2)                  ~$212,400        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
