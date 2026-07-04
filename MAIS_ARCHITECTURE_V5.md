# MAENT Architecture V5 — Council-Designed

**Version:** 5.0 — Designed by 4-agent specialist council  
**Date:** 2026-07-04  
**Council:** Causal Strategist · Content Architect · Agent Engineer · Data Architect · Systems Architect  
**Status:** Complete — Ready for Implementation

---

## 1. Executive Summary

MAENT (Marketing AI Engine for Next-gen Transformation) is a **council-governed, multi-agent marketing AI system** that combines causal intelligence, generative content, and autonomous orchestration.

The architecture is built on **4 specialist layers** governed by **6 AI agents** communicating via Apache Kafka. Each layer has a dedicated specialist agent that owns its domain. The Agent Council meets continuously — no weekly human meetings required.

**Core differentiator:** Unlike traditional marketing automation (rule-based), MAENT uses **causal AI** to distinguish correlation from causation, **generative AI** for infinite content variation, and **multi-agent orchestration** for autonomous campaign management within hard policy constraints.

---

## 2. Agent Council Topology

### The 6 Agents

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AGENT COUNCIL                                      │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │ Campaign     │  │ Audience     │  │ Content     │            │
│  │ Strategist   │→ │ Segmenter    │→ │ Creator     │            │
│  │ CSA          │  │ ASA          │  │ CCA         │            │
│  │              │  │              │  │ Llama 3 70B │            │
│  │ Qwen3-4B     │  │ XLM-R-base  │  │ + VALUE     │            │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘            │
│         │                 │                 │                       │
│         └─────────────────┼─────────────────┘                       │
│                           ▼                                          │
│              ┌────────────────────────┐                            │
│              │ Channel Optimizer      │                            │
│              │ COA                    │                            │
│              │ Qwen3-4B              │                            │
│              └──────────┬───────────┘                            │
│                         │                                            │
│              ┌──────────▼───────────┐                             │
│              │ Performance Analyst    │                             │
│              │ PAA                   │                             │
│              │ DeepCausalMMM +      │                             │
│              │ ALM-MTA               │                             │
│              └──────────┬───────────┘                             │
│                         │                                            │
│              ┌──────────▼───────────┐                             │
│              │ Compliance Enforcer  │                             │
│              │ CEA                  │                             │
│              │ VETO AUTHORITY       │                             │
│              └──────────────────────┘                             │
└─────────────────────────────────────────────────────────────────────┘
```

### Agent Definitions

| Agent | Abbrev | Model | Role | Authority |
|-------|--------|-------|------|-----------|
| **Campaign Strategist** | CSA | Qwen3-4B | Defines goals, KPIs, budget allocation | Budget ≤$500/day autonomously |
| **Audience Segmenter** | ASA | XLM-RoBERTa-base | Identifies/refines target segments | Segment definitions |
| **Content Creator** | CCA | Llama 3 70B + VALUE | Generates ad copy, visuals, scripts | Copy variants autonomous; brand approval for new brands |
| **Channel Optimizer** | COA | Qwen3-4B | Budget allocation, bidding, placement | API calls within policy constraints |
| **Performance Analyst** | PAA | DeepCausalMMM + ALM-MTA | Quantifies causal impact, ROI | Sensitivity analysis, minor budget shifts |
| **Compliance Enforcer** | CEA | Qwen3-4B (strict) | **Veto authority** on all actions | Hard constraint override |

### Communication Protocol

- **Apache Kafka** pub/sub — all agents publish to topic-specific channels
- **JSON/Protobuf schemas** — typed messages: `task_id`, `agent_id`, `payload`, `status`, `timestamp`
- **Shared state**: Redis for session context (2hr TTL), campaign optimization (24-48hr)

### Decision-Making Protocol

```
1. CSA publishes strategic goal (e.g., "Increase CLV in Segment X by 10%")
2. ASA publishes refined audience segments
3. CCA generates content variants conditioned on segments
4. COA proposes channel budget allocations based on PAA causal insights
5. PAA provides causal ROI estimates per channel
6. CEA reviews all proposals — VETOES violations
7. Orchestration Layer executes approved actions
8. PAA measures outcome → feeds back into next cycle
```

**Conflict resolution:** CEA veto is final. Heuristic resolution for non-critical conflicts (e.g., prioritize higher ROI channel). Unresolvable conflicts → human council notification.

---

## 3. Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SYSTEMS                                           │
│  Salesforce │ Google Ads API │ Meta Ads API │ LinkedIn │ OpenAI │        │
│  CleverTap │ WebEngage │ MoEngage │ Braze │ Hootsuite │ GA4 │           │
└──────────────────────────────────┬────────────────────────────────────────┘
                                   │
                    Data Ingestion (APIs, Webhooks, ETL)
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                                           │
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │ S3 Raw Lake │  │ PostgreSQL  │  │ Snowflake   │  │ Pinecone    │   │
│  │ 500TB-5PB    │  │ Operational │  │ Warehouse   │  │ Vectors     │   │
│  │              │  │ 5-50TB      │  │ 200TB-2PB   │  │ 10-100TB    │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
│                                                                             │
│  ┌─────────────┐  ┌─────────────────────────────────────────────┐       │
│  │ Neo4j KG    │  │ Redis Cache                               │       │
│  │ 500GB-5TB   │  │ 100GB-1TB (session, scratchpad, context) │       │
│  │ Entities:   │  │ Freshness: real-time (sec) to daily       │       │
│  │ Customer    │  └─────────────────────────────────────────────┘       │
│  │ Product     │                                                           │
│  │ Campaign    │                                                           │
│  │ Content     │                                                           │
│  │ AdCreative  │                                                           │
│  │ Competitor  │                                                           │
│  │ Channel     │                                                           │
│  └─────────────┘                                                           │
└──────────────────────────────────┬────────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼────────────────────────────────────────┐
│                      AGENT LAYER (Orchestration)                           │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────┐     │
│  │         Apache Kafka Pub/Sub (JSON/Protobuf schemas)             │     │
│  └─────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│  CSA ──► ASA ──► CCA ──► COA ──► PAA ──► CEA ──► Execution            │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────┐     │
│  │ Tool Abstraction Layer (TAL): Google │ Meta │ LinkedIn │       │     │
│  │ CleverTap │ WebEngage │ MoEngage │ Braze │ DV360              │     │
│  └─────────────────────────────────────────────────────────────────┘     │
└──────────────────────────────────┬────────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼────────────────────────────────────────┐
│                         CAUSAL LAYER                                      │
│                                                                             │
│  DeepCausalMMM (50M params)  ←→  ALM-MTA (10M params)                   │
│  Channel ROI + elasticity          Touchpoint-level attribution            │
│  Macro planning                   Micro journey analysis                     │
│                                                                             │
│  Output: Channel ROI + CI, Touchpoint weights, Incrementality signal        │
└──────────────────────────────────┬────────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼────────────────────────────────────────┐
│                      CONTENT LAYER                                         │
│                                                                             │
│  Llama 3 70B (base)                                                       │
│      ↓                                                                     │
│  VALUE Fine-tuning (multi-objective reward model + PPO)                    │
│      ↓                                                                     │
│  Output: Ad copy, Image prompts, Video scripts, CTAs                       │
│                                                                             │
│  Quality: >4.5/5 brand alignment │ Toxicity <0.03 │ A/B lift >5%           │
└──────────────────────────────────┬────────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼────────────────────────────────────────┐
│                         HUMAN GATE                                          │
│  >$500/day budget changes │ New brand campaigns │ Legal/regulatory │      │
│  New channel activation │ Brand voice approval                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Layer-by-Layer Specifications

### 4A. Causal Intelligence Layer

**Specialist:** Causal Strategist (PAA agent)

**Purpose:** Quantify the TRUE causal impact of marketing — not correlations, not raw ROAS, but denoised causal estimates with uncertainty.

**Models:**
| Model | Size | Role | Output |
|-------|------|------|--------|
| **DeepCausalMMM** | 50M | Macro channel ROI | Channel ROI with confidence intervals, spend elasticity, saturation curves |
| **ALM-MTA** | 10M | Micro touchpoint attribution | Incremental lift per touchpoint, segment-specific weights |

**Composition:**
```
Raw Marketing Data
        ↓
[Data Harmonization → Feature Engineering → Causal Graph Construction]
        ↓
   ┌────┴────┐
   ▼         ▼
DeepCausalMMM  ALM-MTA
   │              │
   ▼              ▼
Channel ROI   Touchpoint
+ CI           Attribution
   │              │
   └──────┬───────┘
          ▼
   Causal Estimates
   (ROI + Uncertainty)
```

**Datasets:**
| Dataset | Size | Role |
|---------|------|------|
| Marketing_Spend_Log | 1TB | Daily spend by channel/campaign/creative |
| Customer_Journey_Events | 2TB | Timestamped touchpoint sequences |
| Conversion_Metrics | 500GB | KPIs linked to customer IDs |
| External_Factors | 200GB | Macroeconomic, competitor, seasonality |

**Preprocessing:**
1. **Harmonization** — standardize formats, clean missing values, aggregate to appropriate granularity
2. **Feature Engineering** — lagged variables, Fourier seasonality terms, control variables
3. **Causal Graph Construction** — DAG for confounders, propensity score matching, IPW adjustment

**Metrics:**
- QINI coefficient > 0.3 on holdout uplift
- AUUC uplift > 15% vs random targeting
- Calibration error < 5% vs incrementality tests

---

### 4B. Content Generation Layer

**Specialist:** Content Architect (CCA agent)

**Purpose:** Generate diverse, brand-aligned marketing content at scale — without the "slop" problem.

**Base Model:** Llama 3 70B

**Approach:** VALUE (Value-Aligned Utility Learning) — multi-objective reward model + PPO fine-tuning

**Why VALUE over OPERA or FTPO:**
- OPERA is a 2026 preprint (unproven outside its domain)
- FTPO is for eliminating bad patterns, not optimizing good content
- VALUE explicitly optimizes the trifecta: quality + brand safety + commercial value

**Training Pipeline:**
```
1. Data Collection
   └── Curated marketing corpus (800GB) + brand guidelines (120GB) + A/B results (350GB)

2. Value Function Definition
   └── Multi-objective: brand adherence + persuasiveness + predicted CTR

3. Human Preference Labeling
   └── 250K samples scored by evaluators (1-5 scale per dimension)

4. Reward Model Training
   └── Smaller neural network predicting human preference scores

5. RL Fine-tuning (PPO)
   └── Llama 3 70B fine-tuned to maximize reward model scores

6. Iterative Refinement
   └── A/B testing → update labels → retrain (continuous)
```

**Datasets:**
| Dataset | Size | Role |
|---------|------|------|
| MAENT-MarketingCorpus | 800GB | High-performing marketing copy |
| MAENT-BrandGuidelines | 120GB | Brand voice, tone, prohibited terms |
| MAENT-PerformanceFeedback | 350GB | A/B test results linked to content |
| MAENT-HumanPreference | 250K samples | Preference labels per content piece |

**Metrics:**
| Metric | Target | Measurement |
|--------|--------|-------------|
| Brand Alignment Score | >4.5/5 | Human Likert scale |
| A/B Conversion Lift | >5% | vs human-written control |
| Toxicity Score | <0.03 | Perspective API |
| Guideline Violation Rate | <0.5% | Automated classifier |
| BLEU vs human reference | >0.5 | Against held-out human copy |

---

### 4C. Agent Orchestration Layer

**Specialist:** Agent Engineer (Orchestration Layer)

**Purpose:** Coordinate all agents, enforce policies, execute workflows, integrate tools.

**Tool Abstraction Layer (TAL):**
All external platforms are connectors on a unified Campaign Action Schema:
```json
{
  "action": "adjust_budget",
  "channel": "google_ads",
  "campaign_id": "xyz",
  "delta_usd": 150,
  "reason": "causal_roi_12pct_above_mean",
  "agent_id": "COA",
  "timestamp": "..."
}
```

**Supported Platforms:**
| Platform | Type | API Status |
|----------|------|------------|
| Google Ads | SEM | ✅ Full API |
| Meta Ads | Social | ✅ Full API |
| LinkedIn Ads | B2B | ✅ Full API |
| TikTok Ads | Video | ✅ Full API |
| CleverTap | Engagement | ✅ REST API |
| WebEngage | Engagement | ✅ REST API |
| MoEngage | Engagement | ✅ REST API |
| Braze | Engagement | ✅ REST API |
| DV360 | Programmatic | ✅ API |

**Policy Framework (τ-bench style):**

*Hard constraints (NEVER violate):*
1. **GDPR/CCPA** — no PII processing without consent
2. **Brand Safety** — sentiment score ≥ -0.8 (Google Cloud NL API), no prohibited content
3. **Budget Adherence** — never exceed campaign budget by >0.5% in any 24hr period
4. **Ad Platform TOS** — never violate Google/Meta/LinkedIn terms of service
5. **Regulatory** — no pharmaceutical/financial/gambling without documented legal review

*Soft constraints (prefer not to):*
1. ≤3 social posts/day/channel (avoid audience fatigue)
2. A/B test new creatives before allocating >20% of daily budget
3. Maintain brand sentiment score >0.6 (measured continuously)

*Violation handling:*
- **Hard violation** → immediate halt + automatic rollback + PagerDuty alert + full audit log
- **Soft violation** → log + flag + automated adjustment + repeated violations → human notification

**Execution Loop (Daily Cycle):**
```
T+0min    Data Agent refreshes feature store (Redis)
T+5min    PAA produces channel ROI estimates (DeepCausalMMM + ALM-MTA)
T+10min   CSA defines campaign goals for the day
T+15min   ASA refines audience segments
T+20min   CCA generates content variants (Llama 3 70B + VALUE)
T+25min   COA proposes channel budget adjustments
T+30min   CEA reviews all proposals (veto or approve)
T+35min   Approved actions execute via TAL → platform APIs
           >$500/day or new brand → Human Gate queue
T+40min   PAA begins measuring outcome
T+24hr    PAA produces full causal report
```

---

### 4D. Data & Memory Layer

**Specialist:** Data Architect (Data Agent)

**Storage Architecture:**
| Store | Technology | Size | Freshness | Purpose |
|-------|-----------|------|-----------|---------|
| Raw Lake | S3 / ADLS Gen2 | 500TB-5PB | Hours/days | Immutable source of truth |
| Operational | PostgreSQL | 5-50TB | Seconds | Transactional, session state |
| Warehouse | Snowflake / BigQuery | 200TB-2PB | Hourly/daily | Analytics, ML features |
| Vector DB | Pinecone / Weaviate | 10-100TB | Minutes | Semantic search, embeddings |
| Graph DB | Neo4j / Neptune | 500GB-5TB | Hours/days | Knowledge graph entities |
| Cache | Redis Enterprise | 100GB-1TB | Seconds | Working memory, TTL |

**Knowledge Graph Entities:**
1. **Customer** — demographics, segments, lifecycle stage, CLV
2. **Product** — features, pricing, competitive positioning
3. **Campaign** — goals, budget, channels, performance history
4. **Content Asset** — type, topic, sentiment, engagement metrics
5. **Ad Creative** — images, copy, CTA, CTR/CVR
6. **Market Segment** — size, trends, preferred channels
7. **Competitor** — spend, positioning, ad creative
8. **Industry Trend** — emerging tech, regulatory, consumer shifts
9. **Conversion Event** — type, value, attribution model
10. **Marketing Channel** — platform, cost model, audience reach

**KG Update Mechanism:**
- **Automated ETL** — nightly batch from warehouse updates nodes/edges
- **Kafka event streams** — real-time updates from agent actions
- **AI-driven extraction** — PAA extracts new relationships from causal analysis
- **Human curation** — UI for data steward review of KG quality

**Memory System:**
| Type | TTL | Storage | Content |
|------|-----|---------|---------|
| Session Context | 2hr | Redis | Active user queries, preferences |
| Campaign Optimization | 24-48hr | Redis | Budget state, performance snapshot |
| Reasoning Scratchpad | 30min | Redis | Intermediate causal outputs |
| Episodic (Permanent) | Forever | S3 + PostgreSQL | All decisions, evidence, outcomes |

**Metrics:**
- Data freshness SLA: real-time ≤5s, near-real-time ≤5min, batch ≤1hr
- Query latency p99: Redis <10ms, PostgreSQL <100ms, GraphQL <200ms
- Data quality defect rate: <0.1%

---

## 5. Council Charter

### Meeting Protocol

The council operates **continuously, not in meetings**:

| Trigger | Behavior |
|---------|----------|
| New campaign goal | CSA initiates → ASA → CCA → COA → PAA → CEA → Execute |
| Causal anomaly detected | PAA alerts CEA → CEA escalates to human |
| Budget approaching limit | COA → CEA auto-pause |
| Brand safety flag | CEA immediate veto + rollback |
| New competitor data | Data Agent → KG update → PAA → CSA strategy review |

### Escalation Matrix

| Situation | Escalates To | SLA |
|-----------|-------------|-----|
| Unobserved confounders affecting causal validity | Human council | 24hr |
| DeepCausalMMM vs ALM-MTA conflicting | CEA + Human | 48hr |
| Budget reallocation >$500/day | Human gate | Per platform SLA |
| New brand campaign launch | CMO approval | 48hr |
| Regulatory category (pharma/finance) | Legal + Human | 72hr |
| New channel activation | CFO + CMO | 1 week |

---

## 6. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-8)
**Goal:** Data layer + single campaign loop

| Week | Tasks | Outcome |
|------|-------|---------|
| 1-2 | Deploy PostgreSQL + Redis + Neo4j + S3 | Data infrastructure running |
| 3-4 | Load Olist (45K orders) + Bank Marketing (45K) into warehouse | Clean training data |
| 5-6 | Train DeepCausalMMM on Bank Marketing | Channel ROI estimates |
| 7-8 | Connect PAA → COA → Google Ads API (single channel) | First causal → action loop |

### Phase 2: Content (Weeks 9-14)
**Goal:** Content generation + CCA integration

| Week | Tasks | Outcome |
|------|-------|---------|
| 9-10 | Deploy Llama 3 70B + VALUE fine-tuning pipeline | Base content model |
| 11-12 | Connect CCA → Content review queue → TAL | Content → ad copy |
| 13-14 | A/B test: AI copy vs human control | Validate >5% lift |

### Phase 3: Full Council (Weeks 15-20)
**Goal:** All 6 agents running + multi-channel

| Week | Tasks | Outcome |
|------|-------|---------|
| 15-16 | Deploy Kafka pub/sub, connect all 6 agents | Full agent communication |
| 17-18 | Connect Meta + LinkedIn via TAL | Multi-channel coverage |
| 19-20 | Connect CEA → policy enforcement → rollback | Compliance layer live |

### Phase 4: Causal MTL (Weeks 21-26)
**Goal:** Multi-task prediction

| Week | Tasks | Outcome |
|------|-------|---------|
| 21-22 | Add ALM-MTA for touchpoint attribution | Micro-level causality |
| 23-24 | Train XLM-R MTL backbone (CTR + CVR + Churn) | 3-task model |
| 25-26 | Validate H2: shared backbone vs single-task | >3% AUC improvement |

### Phase 5: Scale & Polish (Weeks 27-32)
**Goal:** Production-ready

- Connect CleverTap, WebEngage, MoEngage, Braze
- Full audit trail
- Error recovery procedures
- Monitoring dashboards
- First real campaign management

---

## 7. Key Decisions & Open Questions

### Decisions Made by Council

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Llama 3 70B base for content | Best open-weight model for creative writing at 70B scale |
| 2 | VALUE over OPERA/FTPO | Explicitly optimizes quality + brand + commercial value |
| 3 | DeepCausalMMM + ALM-MTA in parallel | Macro (channel) + micro (touchpoint) — both needed |
| 4 | Kafka over direct API calls | Async, scalable, audit-friendly |
| 5 | CEA has veto authority | Safety must be unchallengeable |
| 6 | Redis for working memory | Speed is non-negotiable for real-time decisions |

### Open Questions (Require Human Decision)

| # | Question | Recommendation |
|---|----------|----------------|
| 1 | **First campaign budget?** | Start with $10K/month minimum for statistically significant results |
| 2 | **Onboarding brand size?** | SMB (5-50 employees) as first target — fastest iteration cycle |
| 3 | **Human approval for copy variations?** | Yes for first 3 months; autonomous after if CEA violation rate <0.1% |
| 4 | **Multi-brand support?** | Yes from day 1 — brand isolation via KG namespaces |
| 5 | **Real money vs sandbox?** | Sandbox first (4 weeks), then real money with $5K limit |

---

## Appendix: Model & Tech Choices

| Component | Choice | Size | Why |
|-----------|--------|------|-----|
| Content base | **Llama 3 70B** | 70B | Best open creative writing model |
| MTL backbone | **XLM-RoBERTa-base** | 278M | Multilingual, fast, robust |
| Causal MMM | **DeepCausalMMM** | 50M | Open-source, Bayesian, GRUs |
| Causal MTA | **ALM-MTA** | 10M | Front-door, adversarial mediator |
| Fast routing | **Qwen3-4B** | 4B | Native JSON, tool use, fast |
| KG | **Neo4j** | — | Mature, Cypher, proven |
| Vector DB | **Pinecone** | — | Managed, scalable, fast |
| Warehouse | **Snowflake** | — | Cloud-native, ELT-friendly |
| Cache | **Redis Enterprise** | — | Sub-ms latency, TTL support |
| Message bus | **Apache Kafka** | — | Event sourcing, audit trail |
| Pipeline | **Airflow** | — | Industry standard |
| Execution | **n8n** | — | Visual workflow, API-first |
| Monitoring | **Prometheus + Grafana** | — | Metrics + alerting |
| Secrets | **HashiCorp Vault** | — | Dynamic credentials |

---

*Designed by: Causal Strategist · Content Architect · Agent Engineer · Data Architect agents*  
*Compiled: 2026-07-04*  
*Based on: 29 ML papers (2024-2026) + 150+ datasets + Council Review + user requirements*
