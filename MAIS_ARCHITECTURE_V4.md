# MAIS Architecture V4 — Council-Designed

**Version:** 4.0 — Designed by 4-agent council  
**Date:** 2026-07-04  
**Council:** Causal Strategist · Content Architect · Agent Engineer · Data Architect  
**Synthesized from:** MAIS_RESEARCH_VISION.md + COUNCIL_REVIEW.md + 29 papers + 150+ datasets

---

## Council Summary

### Causal Strategist
The causal layer should be **simplified to a single unified model** — DeepCausalMMM — rather than chaining multiple causal estimators. The output is a calibrated channel ROI with uncertainty intervals, not raw ROAS. A dedicated Causal Agent interprets these estimates and recommends channel-level budget shifts. Key insight: causal truth comes from incrementality tests, everything else is estimation.

### Content Architect
Content generation should use **FTPO (Final Token Preference Optimization)** as the RLHF backbone — more mature than OPERA (2026 preprint), achieves 90% slop reduction, maintains creative quality. Base model: Qwen3-4B (already in stack). Training: supervised fine-tune → FTPO → constitutional safety layer. A Content Agent handles copy generation requests, conditioned on Causal Agent's recommendations.

### Agent Engineer
The agent layer is a **3-agent team with explicit roles and a policy-constrained execution layer**. Agents: Router Agent (fast triage), Campaign Agent (execution), Safety Agent (veto). Decisions made by simple majority or Safety Agent veto. Based on τ-bench principles: policy constraints enforced at tool-call level, not prompt level. Hard budget limits and brand safety rules are non-negotiable.

### Data Architect
Data layer uses a **dual-store architecture**: PostgreSQL for structured campaign data + Redis for real-time features + Neo4j for knowledge graph + Qdrant for semantic search. A Data Agent manages data quality, pipeline health, and serves as the interface between layers. All agent memory is time-boxed (72hr working context, permanent episodic logs).

---

## Part 1: Agent Council Topology

### The 4 AI Agents

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENT COUNCIL                              │
│                                                             │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌─────────┐ │
│  │ CAUSAL   │   │ CONTENT  │   │AGENT     │   │ DATA    │ │
│  │ AGENT    │◄──┤ AGENT    │◄──┤ ENGINEER │◄──┤ ARCHITECT│ │
│  │          │   │          │   │          │   │         │ │
│  │ "Oracle" │   │ "Artist" │   │ "Exec"   │   │ "Librarian"│ │
│  └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬────┘ │
│       │              │              │              │        │
│       └──────────────┴──────────────┴──────────────┘        │
│                         │                                   │
│                    Shared Memory                             │
│               (72hr context + permanent log)                 │
└─────────────────────────────────────────────────────────────┘
```

### Agent Definitions

| Agent | Model | Role | Authority | Escalates To |
|-------|-------|------|-----------|--------------|
| **Causal Agent** | XLM-RoBERTa-base + LightGBM | Interprets causal data, recommends channel budget | Budget reallocation <$500/day autonomously | Human for >$500 |
| **Content Agent** | Qwen3-4B + FTPO | Generates ad copy, conditioned by Causal Agent | Content creation & A/B copy variants | Human for brand/risk |
| **Campaign Agent** | Qwen3-4B (fast) | Executes campaign changes via APIs | API calls within policy constraints | Safety Agent veto |
| **Data Agent** | XLM-RoBERTa-base | Manages data quality, knowledge graph, serving | Data pipeline changes | Human for schema changes |
| **Safety Agent** | Qwen3-4B (strict) | Vetoes unsafe actions, enforces policy | Final word on brand/legal safety | Human (final override) |

### Communication Protocol

```
Every decision cycle (daily):
1. Data Agent → updates knowledge graph, signals data freshness
2. Causal Agent → reads KG, produces channel ROI estimates
3. Content Agent → reads Causal output, generates/updates ad copy
4. Campaign Agent → proposes campaign changes based on Causal recommendations
5. Safety Agent → reviews Campaign Agent proposals, vetoes violations
6. Council vote (if needed) → majority or Safety veto wins
7. Human approval → for high-stakes decisions (>$500, new brands, new channels)
```

### Conflict Resolution

| Conflict | Resolution |
|----------|------------|
| Causal vs Content on channel | Causal wins (budget is truth) |
| Campaign vs Safety on action | Safety wins (no override) |
| Content generation vs brand safety | Safety Agent vetoes copy |
| Data Agent vs Causal on data quality | Data Agent wins (quality gate) |

---

## Part 2: Complete System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                     HUMAN GATE (High-Stakes)                         │
│              >$500 budget changes, new brands, legal risk            │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────┐
│                    AGENT COUNCIL LAYER                               │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │  Causal      │  │  Content     │  │  Campaign    │               │
│  │  Agent       │  │  Agent       │  │  Agent       │               │
│  │              │  │              │  │              │               │
│  │ • Channel ROI│  │ • Copy gen   │  │ • API calls  │               │
│  │ • Budget rec │  │ • A/B copy   │  │ • Campaign   │               │
│  │ • Increment. │  │ • Brand voice│  │   changes    │               │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘               │
│         │                 │                 │                       │
│         └─────────────────┼─────────────────┘                       │
│                           │                                          │
│                    ┌──────▼──────┐                                  │
│                    │ Safety      │ ← Policy constraints (τ-bench)    │
│                    │ Agent       │ ← Veto, brand safety, legal       │
│                    └──────┬──────┘                                  │
│                           │                                          │
│         ┌─────────────────┼─────────────────┐                        │
│         │    DATA AGENT   │ (Knowledge Graph + Serving)               │
│         └─────────────────┼─────────────────┘                        │
└─────────────────────────────┼────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────┐
│                    KNOWLEDGE GRAPH LAYER                             │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │ Neo4j        │  │ Qdrant       │  │ PostgreSQL   │               │
│  │ (Entities)   │  │ (Embeddings) │  │ (Campaigns)  │               │
│  │              │  │              │  │              │               │
│  │ • Channels   │  │ • Ad copy    │  │ • Spend      │               │
│  │ • Brands     │  │ • Keywords   │  │ • Results    │               │
│  │ • Campaigns  │  │ • Competitors│  │ • A/B tests  │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
└─────────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────┐
│                    ML ENGINE LAYER                                   │
│                                                                       │
│  ┌─────────────────────────┐  ┌────────────────────────────────┐    │
│  │ CAUSAL MODELS           │  │ PREDICTION MODELS               │    │
│  │                         │  │                                 │    │
│  │ DeepCausalMMM           │  │ Shared Backbone (XLM-R-base)    │    │
│  │ (channel ROI, Bayesian) │  │ ├── CTR Head                   │    │
│  │                         │  │ ├── CVR Head                   │    │
│  │ Output:                 │  │ ├── Churn Head                │    │
│  │ • Channel contribution  │  │ ├── CLV Head                   │    │
│  │ • Uncertainty intervals │  │ └── Uplift Head                │    │
│  │ • Incrementality signal│  │                                 │    │
│  └─────────────────────────┘  └────────────────────────────────┘    │
│                                                                       │
│  ┌─────────────────────────┐  ┌────────────────────────────────┐    │
│  │ CONTENT MODELS          │  │ DATA PIPELINE                   │    │
│  │                         │  │                                 │    │
│  │ Qwen3-4B (base)         │  │ Airflow DAGs                   │    │
│  │ → SFT                   │  │ ├── Daily spend sync            │    │
│  │ → FTPO (90% slop ↓)    │  │ ├── Hourly metrics refresh      │    │
│  │ → Constitutional AI     │  │ ├── Weekly knowledge graph update│    │
│  │ (brand safety)          │  │ └── Real-time feature store      │    │
│  │                         │  │                                 │    │
│  │ VALUE steering (opt.)   │  │ Redis (features)                │    │
│  └─────────────────────────┘  └────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────┐
│                    TOOL/EXECUTION LAYER                              │
│                                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ Google   │  │ Meta Ads │  │ LinkedIn │  │ n8n      │           │
│  │ Ads API  │  │ API      │  │ Ads API  │  │ Workflow │           │
│  │          │  │          │  │          │  │ Engine   │           │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
│                                                                       │
│  Policy constraints enforced at THIS layer (not prompt level)          │
└───────────────────────────────────────────────────────────────────────┘
```

---

## Part 3: Layer-by-Layer Specifications

### Layer 1: Causal Intelligence (The "Oracle")

**What it does:** Converts raw marketing spend data into calibrated channel ROI estimates with uncertainty.

**Architecture:**
```
Raw Spend Data → DeepCausalMMM (GRU + DAG + Hill) → Channel ROI + CI
                                       ↑
                        Incrementality Tests (calibration anchor)
```

**Models:**
- DeepCausalMMM (JOSS, 2026) — open-source, Bayesian channel attribution
- Adstock: GRU-based temporal decay
- Saturation: Hill equation (diminishing returns)
- Calibration: Sparse RCT incrementality tests

**Datasets:**
- Bank Marketing (UCI, 45K) — initial training
- A/B Testing 588K (GitHub) — incrementality ground truth
- Criteo Attribution (672MB) — scaled validation

**Causal Agent decisions:**
| Budget Change | Authority |
|--------------|-----------|
| < $100/day/channel | Autonomous |
| $100-500/day | Content Agent co-sign |
| > $500/day | Human approval required |
| New channel | Human approval required |

**Metrics:**
- QINI coefficient on uplift holdout
- Calibration error vs incrementality tests
- Forecast vs actual spend fit (R² > 0.7)

---

### Layer 2: Multi-Task Prediction (The "Sensor Array")

**What it does:** Predicts CTR, CVR, Churn, CLV, and Uplift from customer journey data.

**Architecture:**
```
Customer Journey Data → XLM-RoBERTa-base (shared backbone)
                              │
          ┌──────────┬────────┴────────┬──────────┐
          ▼          ▼                  ▼          ▼
      CTR Head    CVR Head         Churn Head  CLV Head
     (binary)    (binary)         (survival)  (regression)
```

**Models:**
- Base: XLM-RoBERTa-base (278M params) — multilingual, robust
- Heads: LightGBM on top of embeddings (faster than fine-tuning)
- Alternative: Qwen3-4B for complex sequences

**Datasets:**
- Olist E-Commerce (45K orders) — full journey
- E-Comm Behavior 4.6GB — session-level
- Telco Churn (7K) — survival analysis

**Metrics:**
- AUC-ROC per head (target: > 0.75)
- QINI for uplift head
- C-index for churn (survival)

---

### Layer 3: Content Generation (The "Artist")

**What it does:** Generates brand-aligned ad copy conditioned on causal recommendations.

**Architecture:**
```
Causal Recommendation → {channel, tone, offer}
                            │
                    Qwen3-4B (base)
                            │
                    Supervised Fine-Tune (brand examples)
                            │
                    FTPO (90% slop reduction)
                            │
                    Constitutional AI (brand safety)
                            │
                    Output: 3 copy variants (A/B/C)
```

**Why FTPO over OPERA:**
- FTPO is from Antislop (2025) — more mature, peer-reviewed
- OPERA is 2026 preprint — unproven outside its domain
- FTPO achieves 90% slop reduction, DPO causes quality degradation

**Base model:** Qwen3-4B (2.5GB, native tool support, reliable JSON)

**FTPO training:**
1. SFT on 10K brand-approved examples
2. Construct preference pairs (original vs slop)
3. FTPO token-level preference optimization
4. Constitutional AI safety fine-tune

**Datasets:**
- UltraFeedback (187K) — quality signal
- Amazon Reviews (1.26M) — customer language
- Ad Creative (HF, 7K) — brand-safe examples
- Custom brand copy (internal, once available)

**Content Agent decisions:**
- A/B copy variants: Autonomous (3 variants generated)
- Copy for new brand: Human approval
- Copy that Safety Agent flagged: Human review

**Metrics:**
- Lexical diversity (type-token ratio)
- Perplexity on brand voice corpus
- Human eval: relevance, creativity, brand fit (1-5)
- Slop rate: < 5%

---

### Layer 4: Agent Orchestration (The "Executive")

**What it does:** Executes campaign changes through APIs, constrained by policy.

**Architecture:**
```
┌─────────────────────────────────────────────────────┐
│              CAMPAIGN AGENT                          │
│                                                      │
│  Input: Causal recommendation + copy variants        │
│                                                      │
│  Action Planning:                                     │
│  1. Identify affected campaigns                      │
│  2. Calculate required API calls                     │
│  3. Check policy constraints                         │
│  4. Execute (or propose if > authority)              │
│                                                      │
│  Tools: Google Ads API, Meta Ads API, LinkedIn API   │
│  Execution: n8n workflows                           │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│              SAFETY AGENT (Veto Layer)                │
│                                                      │
│  Hard constraints:                                   │
│  - Never exceed daily budget cap per channel         │
│  - Never target prohibited demographics              │
│  - Never run brand-unsafe content categories         │
│  - Never make > 10 API calls/minute                 │
│                                                      │
│  Soft constraints (prefer not to):                  │
│  - Avoid > 20% daily budget swings                   │
│  - Prefer gradual changes over sharp pivots          │
│                                                      │
│  Enforcement: Policy-as-code (not prompt-based)       │
│  Implementation: n8n if/then rules + Safety API check │
└─────────────────────────────────────────────────────┘
```

**τ-bench Principles:**
- Policy is explicit, coded, enforceable
- No "jailbreak" possible through prompt injection
- Safety overrides are hardware-level (not soft)

**Execution Loop:**
```
Daily Cycle:
T+0min:   Data Agent refreshes feature store
T+5min:   Causal Agent produces channel ROI estimates
T+10min:  Content Agent generates copy updates
T+15min:  Campaign Agent proposes changes
T+20min:  Safety Agent reviews (auto-approved or flagged)
T+25min:  Low-risk changes execute autonomously
          High-risk changes → Human review queue
T+30min:  Human reviews approved/rejected
T+35min:  Execution confirmed
```

**Human-in-the-loop:**
| Action | Human Required? |
|--------|---------------|
| Budget < $100/day | No |
| Budget $100-500/day | Yes (async) |
| Budget > $500/day | Yes (sync) |
| New channel launch | Yes |
| Copy for new brand | Yes |
| API credentials change | Yes |
| Policy rule change | Yes |

**Metrics:**
- pass@k: Campaign Agent completes k tasks autonomously
- Violation rate: < 0.1% of actions
- Mean time to execution: < 30 min for autonomous actions

---

### Layer 5: Data & Memory (The "Librarian")

**Storage Architecture:**
```
┌────────────────────────────────────────────────────────┐
│                  REAL-TIME (ms latency)                  │
│  Redis Feature Store                                    │
│  - Current campaign spend                               │
│  - Live CTR/CVR metrics                                │
│  - A/B test results                                    │
└────────────────────────────────────────────────────────┘
                           │
┌────────────────────────────────────────────────────────┐
│                  OPERATIONAL (minute latency)           │
│  PostgreSQL                                            │
│  - Campaign definitions                                │
│  - Historical spend + results                          │
│  - A/B test metadata                                   │
│  - Agent decision logs                                 │
└────────────────────────────────────────────────────────┘
                           │
┌────────────────────────────────────────────────────────┐
│                  ANALYTICAL (hour latency)              │
│  Neo4j Knowledge Graph                                  │
│  - Brand entities + relationships                      │
│  - Channel performance hierarchies                     │
│  - Competitor positioning                              │
│                                                          │
│  Qdrant Vector Store                                   │
│  - Ad copy embeddings (semantic search)                │
│  - Customer journey embeddings                         │
│  - Competitor ad embeddings                            │
└────────────────────────────────────────────────────────┘
                           │
┌────────────────────────────────────────────────────────┐
│                  ARCHIVAL (permanent)                  │
│  S3 / GCS Object Storage                              │
│  - All raw data backups                               │
│  - Model checkpoints                                  │
│  - Agent decision audit trail                         │
│  - Compliance logs (GDPR, CCPA)                      │
└────────────────────────────────────────────────────────┘
```

**Data Agent responsibilities:**
- Data quality: freshness checks, schema validation
- Pipeline health: Airflow DAG monitoring
- KG updates: weekly entity reconciliation
- Serving: low-latency queries for other agents

**Memory System for Agents:**
```
Working Context (72hr):
- Recent causal outputs
- Active campaign states
- Pending decisions
- Conversation history

Permanent Episodic Memory:
- All decisions with full evidence + approver
- Outcomes (what happened after each decision)
- Lessons learned (what worked, what didn't)

Knowledge Base (neo4j):
- Brands, channels, campaigns, metrics
- Relationships (brand → channel → performance)
- Competitor benchmarks
```

---

## Part 4: Implementation Priority

### Phase 1: Foundation (Weeks 1-6)
**Goal:** Get a working causal → prediction loop

| Week | Task | Outcome |
|------|------|---------|
| 1 | Set up data stack (PostgreSQL + Redis + Neo4j) | Data pipelines running |
| 2 | Load Olist dataset (45K orders) into PostgreSQL | Clean training data |
| 3 | Train shared backbone (CTR + CVR heads) on Olist | Working MTL model |
| 4 | Add Churn head (Telco dataset) | 3-task model validated |
| 5 | Load Bank Marketing, train DeepCausalMMM | Causal ROI estimates |
| 6 | Connect Causal → Prediction → Content (no agents yet) | E2E pipeline |

### Phase 2: Content (Weeks 7-10)
**Goal:** Working content generation

| Week | Task | Outcome |
|------|------|---------|
| 7 | SFT Qwen3-4B on brand copy examples | Base content model |
| 8 | Implement FTPO training pipeline | 90% slop reduction |
| 9 | Add Constitutional AI safety layer | Brand-safe output |
| 10 | A/B test: AI copy vs human copy | Validate quality |

### Phase 3: Agent Council (Weeks 11-14)
**Goal:** Autonomous decision-making

| Week | Task | Outcome |
|------|------|---------|
| 11 | Implement Campaign Agent (API orchestration) | Can execute changes |
| 12 | Implement Safety Agent (policy-as-code) | Veto layer working |
| 13 | Implement Causal Agent + Content Agent | Full council running |
| 14 | Human-in-the-loop gates + approval flow | Compliance ready |

### Phase 4: Polish & Launch (Weeks 15-16)
**Goal:** Production-ready

- Full audit trail
- Error recovery procedures
- Monitoring dashboards
- Run first real campaign

---

## Part 5: Open Questions (Require Human Decision)

1. **Which channel first?** SEM (Google) is easiest to API-control and measure. Facebook is highest volume but more complex. What's the priority?

2. **Human approval latency?** If the human gate has a 48hr SLA, autonomous actions can proceed. What's the acceptable delay for approvals?

3. **Budget responsibility?** Who owns the $500/day autonomous threshold? The marketing manager? The CFO? This is a legal/compliance question.

4. **Brand voice ownership?** Who approves the "brand voice" that Content Agent learns from? Legal? Brand team? This determines who signs off on FTPO training data.

5. **Incumbent system integration?** Is there an existing marketing platform (HubSpot, Salesforce) that must be integrated? This changes the tool layer significantly.

---

## Appendix: Model Choices Summary

| Component | Model | Size | Why |
|-----------|-------|------|-----|
| Base backbone | XLM-RoBERTa-base | 278M | Multilingual, robust, fast |
| Fast routing | Qwen3-4B | 2.5GB | Native tool support, JSON |
| Causal MMM | DeepCausalMMM | — | Open-source, Bayesian |
| Content gen | Qwen3-4B + FTPO | 2.5GB | Slop-resistant, brand-safe |
| Vector search | Qdrant | — | Fast, Kubernetes-ready |
| KG | Neo4j | — | Mature, Cypher queries |
| Pipeline | Airflow | — | Industry standard |
| Execution | n8n | — | Visual workflow, API-first |

---

*Designed by: Causal Strategist · Content Architect · Agent Engineer · Data Architect agents*  
*Synthesized: 2026-07-04*  
*Based on: 29 ML papers (2024-2026) + 150+ datasets + Council Review*
