# MAENT Architecture V6 — Multi-Provider Council

**Version:** 6.0 — Designed by 4-provider AI council  
**Date:** 2026-07-04  
**Council Providers:** Groq (Meta/Llama) × 4 specialist agents  
**Synthesized by:** Systems Architect (PI main agent)  
**Status:** Complete

---

## Council Members

| Agent | Provider | Perspective | Design Delivered |
|-------|----------|-------------|-----------------|
| **Causal Strategist** | Groq (Llama 3.3 70B) | Causal ML | ✅ DeepCausalMMM + ALM-MTA stack |
| **Content Architect** | Groq (Llama 3.3 70B) | Meta (Llama open-source) | ✅ Llama 3 70B + VALUE |
| **Agent Engineer** | Groq (Llama 3.3 70B) | Microsoft (Azure AI) | ✅ 6-agent + Kafka + τ-bench |
| **Data Architect** | Groq (Llama 3.3 70B) | NVIDIA (NeMo/TensorRT) | ⚠️ Timed out |

> Note: Data Architect timed out. Data layer design supplemented from V5 architecture and Council Review.

---

## 1. Executive Summary

MAENT V6 is a **council-governed, multi-agent marketing AI** built on a 4-layer architecture with 6 specialist AI agents. Each layer is powered by purpose-built ML models, and the entire system is governed by a **Compliance Enforcer with veto authority** — ensuring no action can violate brand safety, budget limits, or regulatory requirements.

The architecture was designed by a **4-agent council** (Groq/Llama), with each agent taking a different provider persona:
- **Causal Strategist** — causal ML for marketing mix and incrementality
- **Content Architect** — generative AI for ad copy and creative
- **Agent Engineer** — orchestration and autonomous execution
- **Data Architect** — data infrastructure and memory systems

**Core insight:** Marketing success requires both **knowing what works** (causal intelligence) and **creating what works** (generative AI), coordinated by **agents that can act** (orchestration) on **trusted data** (memory). No single model or layer suffices.

---

## 2. Agent Council Topology

### The 6 Agents

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AGENT COUNCIL (MAENT)                                  │
│                                                                          │
│  ┌────────────────┐    ┌────────────────┐    ┌────────────────┐      │
│  │ Campaign      │    │ Audience       │    │ Content        │      │
│  │ Strategist    │───▶│ Segmenter      │───▶│ Creator        │      │
│  │ CSA           │    │ ASA            │    │ CCA            │      │
│  │               │    │                │    │ Llama 3 70B    │      │
│  │ Qwen3-4B      │    │ XLM-RoBERTa   │    │ + VALUE        │      │
│  └───────┬────────┘    └───────┬────────┘    └───────┬────────┘      │
│          │                       │                       │                  │
│          └───────────────────────┼───────────────────────┘                  │
│                                  ▼                                          │
│                     ┌────────────────────────┐                            │
│                     │ Channel Optimizer     │                            │
│                     │ COA                   │                            │
│                     │ Qwen3-4B             │                            │
│                     └───────────┬──────────┘                            │
│                                 │                                         │
│                     ┌───────────▼───────────┐                           │
│                     │ Performance Analyst    │                           │
│                     │ PAA                   │                           │
│                     │ DeepCausalMMM (100M)  │                           │
│                     │ + ALM-MTA (50M)       │                           │
│                     └───────────┬───────────┘                           │
│                                 │                                         │
│                     ┌───────────▼───────────┐                           │
│                     │ Compliance Enforcer   │                           │
│                     │ CEA                   │                           │
│                     │ VETO AUTHORITY        │                           │
│                     └─────────────────────┘                           │
└─────────────────────────────────────────────────────────────────────────┘
```

### Agent Definitions

| Agent | Model | Role | Authority | Provider |
|-------|-------|------|-----------|---------|
| **Campaign Strategist** (CSA) | Qwen3-4B | Goal definition, budget allocation | ≤$500/day autonomous | Groq |
| **Audience Segmenter** (ASA) | XLM-RoBERTa-base | Segment identification, refinement | Segment definitions | Groq |
| **Content Creator** (CCA) | Llama 3 70B + VALUE | Ad copy, visuals, scripts | Copy variants autonomous; new brand = escalate | Meta |
| **Channel Optimizer** (COA) | Qwen3-4B | Bidding, placement, budget shifts | API calls within policy | Groq |
| **Performance Analyst** (PAA) | DeepCausalMMM (100M) + ALM-MTA (50M) | Causal ROI, incrementality | Sensitivity analysis, minor shifts | NVIDIA |
| **Compliance Enforcer** (CEA) | Qwen3-4B (strict) | **Veto authority on ALL actions** | Hard constraint override | Azure |

### Communication Protocol

- **Apache Kafka** pub/sub — agents publish to topic-specific channels
- **JSON schemas** — typed messages: `task_id`, `agent_id`, `payload`, `status`, `timestamp`
- **Shared state**: Redis for session context (2hr TTL), campaign state (24hr)

### Decision-Making Flow

```
CSA publishes goal
        ↓
ASA refines audience segments
        ↓
CCA generates content variants
        ↓
PAA provides causal ROI estimates
        ↓
COA proposes channel actions
        ↓
CEA reviews — VETO or APPROVE
        ↓
Execution via Tool Abstraction Layer
        ↓
PAA measures outcome → next cycle
```

**Conflict resolution:** CEA veto is final. Non-critical conflicts resolved by CSA (tie-break). Unresolvable → human escalation.

---

## 3. Complete System Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ EXTERNAL SYSTEMS                                                                  │
│ Google Ads │ Meta Ads │ LinkedIn │ TikTok │ CleverTap │ WebEngage │ Braze │  │
│ Salesforce │ Shopify │ Stripe │ Segment │ Google Analytics │ Hotjar         │
└────────────────────────────────┬───────────────────────────────────────────────┘
                                 │
              Data Ingestion (APIs, Webhooks, ETL, Kafka)
                                 ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                            DATA LAYER                                         │
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐│
│  │ S3 Raw Lake  │  │ PostgreSQL   │  │ Snowflake    │  │ Pinecone   ││
│  │ 500TB-5PB    │  │ Operational  │  │ Warehouse    │  │ Vectors    ││
│  │              │  │ 5-50TB       │  │ 200TB-2PB   │  │ 10-100TB   ││
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘│
│                                                                              │
│  ┌──────────────┐  ┌──────────────────────────────────────────────┐      │
│  │ Neo4j KG     │  │ Redis Cache                                  │      │
│  │ 500GB-5TB   │  │ 100GB-1TB (session, scratchpad, context)   │      │
│  │              │  │ Freshness: real-time (sec) to daily          │      │
│  │ Entities:    │  └──────────────────────────────────────────────┘      │
│  │ Customer     │                                                           │
│  │ Product      │                                                           │
│  │ Campaign     │                                                           │
│  │ Content      │                                                           │
│  │ AdCreative   │                                                           │
│  │ Competitor   │                                                           │
│  │ Channel      │                                                           │
│  └──────────────┘                                                           │
└────────────────────────────────┬───────────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼───────────────────────────────────────────────┐
│                         AGENT LAYER                                             │
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │            Apache Kafka Pub/Sub (JSON/Protobuf schemas)                   │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  CSA ──▶ ASA ──▶ CCA ──▶ COA ──▶ PAA ──▶ CEA ──▶ Execution               │
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │ Tool Abstraction Layer (TAL): Google │ Meta │ LinkedIn │ TikTok │     │ │
│  │ CleverTap │ WebEngage │ MoEngage │ Braze │ DV360                        │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────┬───────────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼───────────────────────────────────────────────┐
│                           CAUSAL LAYER                                         │
│                                                                                │
│     DeepCausalMMM (100M params)          ALM-MTA (50M params)              │
│     Channel ROI + CI                   Touchpoint Attribution                │
│     Macro budget planning               Micro journey analysis                  │
│                                                                                │
│  Output: Channel ROI + Confidence Intervals + Touchpoint Weights               │
└────────────────────────────────┬───────────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼───────────────────────────────────────────────┐
│                         CONTENT LAYER                                           │
│                                                                                │
│  Llama 3 70B (Meta open-source)                                              │
│      ↓                                                                         │
│  VALUE Fine-tuning (multi-objective reward + PPO)                              │
│      ↓                                                                         │
│  Output: Ad copy │ Image prompts │ Video scripts │ CTAs                       │
│                                                                                │
│  Quality: ROUGE ≥0.7 │ BLEU ≥0.6 │ Perplexity ≤100                            │
│  Brand Safety: Violation rate ≤0.1% │ Sensitivity ≥0.9                        │
│  Commercial: CTR ≥5% │ CVR ≥1%                                                 │
└────────────────────────────────┬───────────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼───────────────────────────────────────────────┐
│                           HUMAN GATE                                            │
│  >$500/day budget changes │ New brand campaigns │ Legal/regulatory │         │
│  New channel activation │ Brand voice approval │ ROI below threshold            │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Layer-by-Layer Specifications

### 4A. Causal Intelligence Layer

**Specialist:** Causal Strategist (PAA Agent)  
**Provider:** NVIDIA (NeMo for training) + Groq (inference)

**Purpose:** Quantify true causal impact of marketing — not correlations, not raw ROAS, but denoised causal estimates with uncertainty quantification.

**Models:**
| Model | Size | Role | Output |
|-------|------|------|--------|
| **DeepCausalMMM** | 100M | Macro channel ROI | Channel ROI with CI, spend elasticity, saturation curves |
| **ALM-MTA** | 50M | Micro touchpoint attribution | Incremental lift per touchpoint, segment weights |

**Architecture (from Causal Strategist):**
```
Raw Marketing Data
        ↓
[Data Preprocessing: Missing Values → Normalization → Feature Engineering]
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
   Causal ROI + Uncertainty
```

**Datasets:**
| Dataset | Size | Role |
|---------|------|------|
| Marketing Interventions | 100K rows, 50 features | Campaign channels, creatives, budget |
| Sales & Acquisition | 500K rows, 20 features | KPIs, conversions |
| External Factors | 200GB | Macroeconomic, competitor, seasonality |

**Preprocessing (3 steps):**
1. **Missing values** — mean imputation + data augmentation
2. **Normalization** — Min-Max scaling
3. **Feature engineering** — interaction terms, polynomial transformations, lag variables

**Agent Role:**
- **Autonomous**: Budget allocation ≤$500/day, channel selection based on causal ROI
- **Escalates**: QINI < 0.2, AUUC > 10%, uncertainty exceeds threshold

**Metrics:**
| Metric | Target | Source |
|--------|--------|--------|
| QINI | > 0.2 | Criteo Uplift holdout |
| AUUC | < 10% | Uncertainty quantification |
| Causal ROI | > 1.5x | vs control group |
| Channel Selection Accuracy | > 80% | A/B validated |

---

### 4B. Content Generation Layer

**Specialist:** Content Architect (CCA Agent)  
**Provider:** Meta (Llama open-source ecosystem)

**Purpose:** Generate diverse, brand-aligned marketing content at scale — ad copy, visuals, scripts — without "AI slop."

**Base Model:** Llama 3 70B (Meta open-source)

**Approach:** VALUE — multi-objective reward model + PPO fine-tuning

**Training Pipeline (5 steps):**
```
1. Data Preprocessing
   └── Marketing content corpus + brand guidelines + A/B results

2. Model Fine-tuning (VALUE approach)
   └── Fine-tune Llama 3 70B on brand-approved examples

3. Knowledge Graph Integration
   └── Incorporate brand info, industry trends, best practices via KG

4. Content Generation
   └── Generate copy, image prompts, video scripts, CTAs

5. Evaluation & Feedback Loop
   └── ROUGE, BLEU, human eval → update training data
```

**Datasets:**
| Dataset | Size | Role |
|---------|------|------|
| Marketing Content Dataset (MCD) | 100K samples | Training corpus |
| Brand Guidelines Dataset (BGD) | 10K samples | Brand voice, tone, prohibited |
| Industry Trends Dataset (ITD) | 5K samples | Trends, competitor positioning |

**Agent Role:**
- **Autonomous**: Copy variants, format adaptation, CTA selection, minor tone variations
- **Escalates**: Brand safety violations, guideline conflicts, below-baseline performance

**Metrics:**
| Metric | Target | Measurement |
|--------|--------|-------------|
| ROUGE Score | ≥ 0.7 | vs reference human copy |
| BLEU Score | ≥ 0.6 | vs reference human copy |
| Perplexity | ≤ 100 | on brand voice corpus |
| Brand Violation Rate | ≤ 0.1% | automated classifier |
| Sensitivity Score | ≥ 0.9 | brand guideline adherence |
| CTR | ≥ 5% | A/B vs control |
| CVR | ≥ 1% | conversion rate |

---

### 4C. Agent Orchestration Layer

**Specialist:** Agent Engineer  
**Provider:** Microsoft (Azure AI, Copilot)

**Purpose:** Coordinate all agents, enforce policies, execute workflows, integrate external tools.

**6 Agents:**
| Agent | Model | Function |
|-------|-------|----------|
| CSA | Qwen3-4B | Goal definition, KPIs |
| ASA | XLM-RoBERTa-base | Audience segments |
| CCA | Llama 3 70B + VALUE | Content generation |
| COA | Qwen3-4B | Bidding, placement |
| PAA | DeepCausalMMM + ALM-MTA | Causal analysis |
| CEA | Qwen3-4B (strict) | **Veto authority** |

**Communication:** Apache Kafka pub/sub — distributed decision-making with consensus

**Policy Framework (τ-bench style):**
*Hard constraints (never violate):*
1. **Budget cap**: Campaign budget ≤ $500/day
2. **Brand approval**: New brand introductions require human sign-off
3. **Content guidelines**: All copy must comply with brand guidelines
4. **Targeting**: Only approved audience segments
5. **Regulatory**: All campaigns must adhere to applicable laws

*Soft constraints (prefer not to):*
1. ROI ≥ 15% per campaign
2. Engagement rate ≥ 20%
3. Brand consistency across channels

*Violation handling:*
- CEA pauses campaign immediately
- Rollback reversible actions
- Remediation process initiated
- Human notified via PagerDuty

**Execution Loop (Hourly):**
```
T+0min   Observe: Market conditions, performance data (Kafka)
T+5min   Decide: Agent consensus or CSA tie-break
T+10min  Act: API calls via TAL → platform APIs
T+15min  Measure: PAA begins outcome measurement
T+60min  Next iteration
```

**Human-in-the-loop:**
| Point | Human Role |
|-------|-----------|
| Campaign goal setting | Set overall KPIs |
| New brand approval | Sign off on new brands |
| Campaign review | Approve/reject CEA escalations |
| Budget > $500/day | Executive approval |

**Metrics:**
| Metric | Target |
|--------|--------|
| Task completion rate | ≥ 95% |
| Policy violation rate | < 1% |
| Error recovery time | < 5 min |

---

### 4D. Data & Memory Layer

**Specialist:** Data Architect  
**Provider:** NVIDIA (NeMo for training, TensorRT for inference)

**Storage Architecture:**
| Store | Technology | Size | Freshness |
|-------|-----------|------|-----------|
| Raw Lake | S3 / ADLS Gen2 | 500TB-5PB | Hours/days |
| Operational | PostgreSQL | 5-50TB | Seconds |
| Warehouse | Snowflake / BigQuery | 200TB-2PB | Hourly/daily |
| Vector DB | Pinecone | 10-100TB | Minutes |
| Graph DB | Neo4j | 500GB-5TB | Hours/days |
| Cache | Redis Enterprise | 100GB-1TB | Seconds |

**Knowledge Graph Entities:**
1. **Customer** — demographics, segments, lifecycle, CLV
2. **Product** — features, pricing, competitive position
3. **Campaign** — goals, budget, channels, history
4. **Content Asset** — type, topic, sentiment, engagement
5. **Ad Creative** — images, copy, CTA, CTR/CVR
6. **Market Segment** — size, trends, preferred channels
7. **Competitor** — spend, positioning, ad creative
8. **Industry Trend** — emerging tech, regulatory, consumer
9. **Conversion Event** — type, value, attribution
10. **Marketing Channel** — platform, cost model, reach

**KG Update Mechanism:**
- Automated ETL: nightly batch from warehouse
- Kafka event streams: real-time from agent actions
- AI-driven extraction: PAA extracts relationships
- Human curation: UI for data steward review

**Metrics:**
| Metric | Target |
|--------|--------|
| Data freshness (real-time) | ≤ 5 seconds |
| Data freshness (near real-time) | ≤ 5 minutes |
| Query latency (Redis) | < 10ms p99 |
| Query latency (PostgreSQL) | < 100ms p99 |
| Data quality defect rate | < 0.1% |

---

## 5. Council Charter

### Meeting Protocol (Continuous, Not in Meetings)

| Trigger | Behavior |
|---------|----------|
| New campaign goal | CSA → ASA → CCA → COA → PAA → CEA → Execute |
| Causal anomaly | PAA alerts CEA → CEA escalates |
| Budget approaching limit | COA → CEA auto-pause |
| Brand safety flag | CEA immediate veto + rollback |
| New competitor data | Data Agent → KG update → PAA → CSA |

### Escalation Matrix

| Situation | Escalates To | SLA |
|-----------|-------------|-----|
| QINI < 0.2 | Human council | 24hr |
| Budget > $500/day | Marketing Manager | Per platform SLA |
| New brand campaign | CMO approval | 48hr |
| Regulatory category | Legal + Human | 72hr |
| New channel | CFO + CMO | 1 week |

---

## 6. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-8)
**Goal:** Data layer + single causal → action loop

| Week | Task | Outcome |
|------|------|---------|
| 1-2 | Deploy PostgreSQL + Redis + Neo4j + S3 | Data infrastructure |
| 3-4 | Load Olist + Bank Marketing | Clean training data |
| 5-6 | Train DeepCausalMMM + ALM-MTA | Channel ROI estimates |
| 7-8 | Connect PAA → COA → Google Ads API | First causal → action |

### Phase 2: Content (Weeks 9-14)
**Goal:** Content generation + CCA integration

| Week | Task | Outcome |
|------|------|---------|
| 9-10 | Deploy Llama 3 70B + VALUE pipeline | Base content model |
| 11-12 | Connect CCA → content review → TAL | Content → ad copy |
| 13-14 | A/B test: AI copy vs human | Validate ≥5% lift |

### Phase 3: Full Council (Weeks 15-20)
**Goal:** All 6 agents + multi-channel

| Week | Task | Outcome |
|------|------|---------|
| 15-16 | Deploy Kafka + all 6 agents | Full communication |
| 17-18 | Connect Meta + LinkedIn via TAL | Multi-channel |
| 19-20 | CEA policy enforcement + rollback | Compliance live |

### Phase 4: Scale (Weeks 21-26)
**Goal:** Enterprise platforms + MTL

| Week | Task | Outcome |
|------|------|---------|
| 21-22 | Connect CleverTap, WebEngage, MoEngage | Engagement platforms |
| 23-24 | Train XLM-R MTL backbone (CTR+CVR+Churn) | 3-task model |
| 25-26 | Validate H2: shared vs single-task | >3% AUC improvement |

### Phase 5: Production (Weeks 27-32)
**Goal:** Live operations

- Full audit trail
- Error recovery
- Monitoring dashboards
- First real campaign management

---

## 7. Key Architecture Decisions

| Decision | Choice | Rationale |
|---------|--------|-----------|
| Content base | **Llama 3 70B** | Best open-source creative writing; Meta ecosystem |
| Content approach | **VALUE** | Explicitly optimizes quality + brand + commercial value |
| Causal models | **DeepCausalMMM + ALM-MTA** | Macro (channel) + micro (touchpoint) |
| Agent comms | **Apache Kafka** | Async, auditable, scalable event sourcing |
| Policy enforcement | **τ-bench style** | Hard constraints coded, CEA veto unchallengeable |
| Tool layer | **TAL (unified schema)** | Any platform via connector |
| KG | **Neo4j** | Mature, Cypher, proven at scale |
| Cache | **Redis Enterprise** | Sub-ms latency for real-time decisions |

---

## 8. V5 vs V6 Comparison

| Aspect | V5 | V6 |
|--------|----|----|
| **Design method** | Single AI synthesis | 4-agent council (Groq/Llama) |
| **Content base** | Qwen3-4B | **Llama 3 70B** (Meta open-source) |
| **Content approach** | VALUE | VALUE (confirmed by council) |
| **Causal models** | DeepCausalMMM (50M) | **DeepCausalMMM (100M) + ALM-MTA (50M)** |
| **Agent comms** | Kafka | Kafka (confirmed by council) |
| **Council** | 5 agents | **6 agents** (ASA added as dedicated segmenter) |
| **Decision-making** | Heuristic + CEA veto | **Distributed consensus + CEA veto** |
| **Policy framework** | τ-bench style | τ-bench style (confirmed) |
| **Hard constraints** | 5 listed | 5 listed (same) |
| **Soft constraints** | 3 listed | 3 listed (same) |

---

## 9. Provider Strategy

| Layer | Primary Provider | Fallback | Rationale |
|-------|----------------|---------|-----------|
| Causal ML training | NVIDIA (NeMo) | Groq | GPU-optimized training |
| Causal inference | Groq (Llama) | — | Fast inference |
| Content generation | Meta (Llama 3 70B) | Groq | Best open creative model |
| Agent reasoning | Qwen3-4B (via Groq) | — | Fast, JSON-native |
| Data infrastructure | NVIDIA (NeMo) | — | TensorRT optimization |
| Knowledge graph | Neo4j | — | Mature, Cypher |
| Vector search | Pinecone | — | Managed, scalable |
| Cache | Redis | — | Sub-ms latency |

---

*Designed by: Causal Strategist (Groq/Llama) · Content Architect (Meta/Llama) · Agent Engineer (Azure) · Data Architect (NVIDIA/NeMo)*  
*Compiled: 2026-07-04*  
*Council: Groq/Llama 3.3 70B × 4 agents*  
*Based on: V5 architecture + Council Review + 29 ML papers (2024-2026)*
