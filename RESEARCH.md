# Research — Foundation and Inspirations

**Related to:** ARCHITECTURE.md Section 10

---

## Overview

MAIS is built on top of research from multiple domains: autonomous agents, marketing intelligence, statistical learning, and organizational design. This document captures the key research areas and their influence on the architecture.

```
┌─────────────────────────────────────────────────────────────────┐
│                    RESEARCH FOUNDATIONS                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ AUTONOMOUS AGENTS                                         │  │
│  │ • Autoquant (Karpathy) — 135 agents in parallel loop     │  │
│  │ • KARL — RL knowledge agent beats Claude Opus            │  │
│  │ • Hermes Agent — Memory-growth over time                  │  │
│  │ • A-Evolve — LLM-driven evolution (79.4% MCP-Atlas)      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↑                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ MARKETING INTELLIGENCE                                    │  │
│  │ • Helena — Autonomous marketer (competitor → ads)        │  │
│  │ • Vibe Marketing 4 levels                                │  │
│  │ • GEO — $80B+ opportunity (a16z)                         │  │
│  │ • Knowledge Graphs > Vectors for agents                  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↑                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ STATISTICAL LEARNING                                       │  │
│  │ • Causal inference before RL                              │  │
│  │ • Bayesian optimization with uncertainty                  │  │
│  │ • SPC monitoring for anomaly detection                   │  │
│  │ • Benjamini-Hochberg for multiple comparisons             │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↑                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ ORCHESTRATION PATTERNS                                     │  │
│  │ • Two-Loop Autoresearch (Orchestra Research)             │  │
│  │ • n8n + Claude feedback loops                             │  │
│  │ • TMLPD — RouteLLM cost-quality routing                   │  │
│  │ • RadixAttention prefix caching                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Autonomous Agents Research

### 1.1 Autoquant — Karpathy's Autoreasearch Loop

**Source:** Karpathy's autoreasearch framework
**Key Metric:** 135 agents operating in parallel loop

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUTOQUANT ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ HYPOTHESIS GENERATOR                                       │  │
│  │  • Takes experiment results                               │  │
│  │  • Generates new testable hypotheses                      │  │
│  │  • 135 parallel agents explore hypothesis space          │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ EXPERIMENT RUNNER                                          │  │
│  │  • Runs experiments in parallel                           │  │
│  │  • Collects metrics                                       │  │
│  │  • Feeds results back to generator                        │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ RESULT AGGREGATOR                                         │  │
│  │  • Synthesizes experiment outcomes                        │  │
│  │  • Updates hypothesis confidence                           │  │
│  │  • Prunes failed hypotheses                               │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Relevance to MAIS:**
- Inner loop hypothesis generation (135 parallel agents → scaled down to marketing context)
- Parallel experiment evaluation for hypothesis validation
- Learning loop with result aggregation

### 1.2 KARL — RL Knowledge Agent

**Source:** Knowledge-augmented Reinforcement Learning agent
**Key Finding:** RL-trained knowledge agent beats Claude Opus 4.6 and GPT-5.2 on knowledge tasks

**Key Insights:**
1. **Knowledge graph integration** improves agent reasoning significantly
2. **RL from knowledge feedback** is more stable than RL from raw metrics
3. **Uncertainty quantification** is critical for knowledge claims

**Relevance to MAIS:**
- Knowledge graph is primary memory (not vector store)
- Reward signal comes from knowledge consistency, not just outcomes
- Uncertainty-aware reasoning prevents hallucination

### 1.3 Hermes Agent

**Source:** Open-source agent with memory growth
**Key Feature:** Agent grows and improves over time with accumulated experience

**Architecture:**
```
Session Memory → Long-term Memory → Policy Update
     ↓                ↓                ↓
  Immediate        Accumulated      Weight
  context          experiences      adjustment
```

**Relevance to MAIS:**
- Episodic memory for session logging
- Knowledge graph for accumulated marketing knowledge
- Model weight updates driven by accumulated evidence

### 1.4 A-Evolve — LLM-Driven Evolution

**Source:** Orchestra Research AI-Research-SKILLs
**Key Metric:** 79.4% on MCP-Atlas, 76.8% on SWE-bench

**Evolution Loop:**
1. Generate mutation candidates from current best
2. Evaluate candidates using LLM as judge
3. Select top candidates
4. Repeat

**Relevance to MAIS:**
- Hypothesis mutation in inner loop
- LLM-as-judge for creative quality assessment
- Evolution over fixed optimization

---

## 2. Marketing Intelligence Research

### 2.1 Helena — Autonomous Marketer

**Source:** World's first autonomous AI marketer
**Key Workflow:**
```
Competitor Ads Analysis → Trend Detection → Creative Generation → Ad Deployment
         ↓                    ↓                  ↓                ↓
    [Source of        [What themes        [What angles       [TikTok/UGC/
     truth]            are working]        resonate]          static ads]
```

**Key Insights:**
- Competitor intelligence drives creative strategy
- Multiple output formats (TikTok, UGC, static)
- Human review for brand safety

**Relevance to MAIS:**
- Competitive intelligence as strategic input
- Multi-format creative generation
- Human review gate for brand risk

### 2.2 Vibe Marketing Framework

**Source:** boringmarketer.com
**Key Framework:** Four levels of AI marketing maturity

```
Level 1: AI User
──────────────
• Uses ChatGPT for copy ideas
• Manual prompt engineering
• No systematic learning

Level 2: AI-Augmented Marketer
──────────────────────────────
• Integrates AI into workflow
• Some automated processes
• Basic analytics

Level 3: AI-First Marketer
───────────────────────────
• AI designs campaigns
• Automated execution
• Data-driven optimization

Level 4: Autonomous Marketing Agent
──────────────────────────────────
• Agent operates independently
• Continuous learning
• Strategic human oversight
```

**MAIS Target:** Level 4 with human oversight

### 2.3 Generative Engine Optimization (GEO)

**Source:** a16z $80B+ thesis
**Key Insight:** As AI search increases, optimizing for AI becomes as important as SEO

**GEO Techniques:**
- Structured data (JSON-LD, schema.org)
- FAQ content
- Citation-optimized writing
- llms.txt generation
- Entity-centric content

**Relevance to MAIS:**
- GEO transform middleware
- Content enhancement for AI discoverability
- Competitive advantage as AI search grows

### 2.4 Knowledge Graphs vs Vectors for Agents

**Source:** @swyx tweet (56.1 score)
**Key Quote:** "Knowledge graphs are infinitely better than vector search for agents"

**Why Knowledge Graphs Win for Agents:**
1. **Interpretability** — Can trace reasoning path
2. **Relationships** — Knows HOW things connect
3. **Updates** — Can modify specific nodes
4. **Causal inference** — Can do path traversal

**Relevance to MAIS:**
- Knowledge graph as PRIMARY memory
- Vector store for semantic retrieval
- Graph + Vector hybrid approach

---

## 3. Statistical Learning Research

### 3.1 Causal Inference Before RL

**Key Principle:** Never apply RL directly to confounded marketing metrics.

**Problem:**
```
Raw ROAS = Treatment Effect + Confounders
                    ↑
        day-of-week, seasonality,
        competitor actions, budget changes
```

**Solution:** Causal inference to isolate true effect:
1. Bayesian structural time-series
2. Difference-in-differences
3. Synthetic control

**Relevance to MAIS:**
- Reward denoising layer BEFORE learning
- Confound detection in validation pipeline
- Only denoised metrics drive model updates

### 3.2 Bayesian Optimization

**Key Properties:**
- Quantifies uncertainty
- Sample-efficient
- Globale optiization with local exploitation
- Works well with noisy data

**GP Regression:**
```python
# Uncertainty quantification
prediction, std_dev = gp.predict(x)
uncertainty_bonus = exploration_weight * std_dev
acquisition = prediction + uncertainty_bonus
```

**Relevance to MAIS:**
- Learning mechanism for hypothesis optimization
- Uncertainty-aware budget allocation
- Safe exploration with conservative updates

### 3.3 SPC Monitoring

**Statistical Process Control:**
- EWMA charts for smooth trend detection
- Western Electric rules for anomaly signaling
- σ thresholds for escalation

**Relevance to MAIS:**
- Inner loop daily monitoring
- Anomaly detection before hypothesis generation
- Automated alerting on SPC signals

---

## 4. Orchestration Patterns

### 4.1 Two-Loop Autoresearch (Orchestra Research)

**Source:** Orchestra Research AI-Research-SKILLs

```
┌─────────────────────────────────────────────────────────────────┐
│                    TWO-LOOP AUTORESEARCH                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  INNER LOOP (Fast — minutes to hours)                          │
│  ─────────────────────────────────────────────────────────────  │
│  • Rapid hypothesis generation                                 │
│  • Quick experiment iteration                                  │
│  • No model updates                                           │
│  • Queue findings for outer loop                               │
│                                                                 │
│  OUTER LOOP (Slow — days to weeks)                            │
│  ─────────────────────────────────────────────────────────────  │
│  • Synthesize inner loop findings                             │
│  • Validate hypotheses statistically                           │
│  • Make strategic changes                                      │
│  • Update model weights                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Relevance to MAIS:**
- Direct inspiration for two-loop architecture
- Inner loop: daily observation
- Outer loop: monthly synthesis

### 4.2 n8n + Claude Feedback Loops

**Source:** OpenOutreach (50.99 score)
**Key Pattern:** n8n executes → Claude reviews → n8n adjusts

```
n8n Campaign Deployment
        ↓
Claude Performance Review
        ↓
n8n Budget Adjustment
        ↓
Claude Quality Check
        ↓
...
```

**Relevance to MAIS:**
- n8n as execution layer (inspired by OpenOutreach)
- MAIAgent reviews and decides
- Clear handoff boundary

### 4.3 TMLPD — RouteLLM Cost-Quality Routing

**Source:** TMLPD (arXiv research)
**Key Papers:**
- RouteLLM (2404.06035) — Learned cost-quality routing
- RadixAttention (2312.07104) — 5-10x speedup via prefix caching
- Medusa (2401.10774) — 2-3x faster generation

**Relevance to MAIS:**
- Hybrid model routing (small for routing, Claude for reasoning)
- Cost optimization across model tiers
- Prefix caching for repeated queries

---

## 5. Key Architecture Decisions from Research

```
┌─────────────────────────────────────────────────────────────────┐
│                    RESEARCH → ARCHITECTURE MAPPING                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  RESEARCH FINDING                  →  ARCHITECTURE DECISION      │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  Autoquant (135 parallel agents)    →  Inner loop parallel      │
│                                        hypothesis generation      │
│                                                                 │
│  KARL (KG > vectors for agents)    →  Knowledge graph primary   │
│                                        memory                    │
│                                                                 │
│  Causal inference before RL         →  Reward denoising layer     │
│                                                                 │
│  Bayesian optimization              →  Learning mechanism        │
│                                        (BO over A-Evolve)        │
│                                                                 │
│  Hermes (memory growth)             →  Episodic memory store      │
│                                        + model update logging     │
│                                                                 │
│  GEO $80B thesis                   →  GEO as middleware transform │
│                                                                 │
│  Vibe Marketing Level 4            →  Autonomous with human      │
│                                        oversight                  │
│                                                                 │
│  Two-Loop Autoresearch             →  Inner (daily) + Outer      │
│                                        (monthly) loops            │
│                                                                 │
│  n8n + Claude feedback             →  n8n executes, MAIAgent     │
│                                        decides                    │
│                                                                 │
│  TMLPD routing                     →  Small model for routing,  │
│                                        Claude for reasoning       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Future Research Areas

### 6.1 A-Evolve Integration

**Potential:** Use LLM-driven evolution for creative hypothesis generation while BO handles tactical optimization.

**Plan:**
1. Validate BO as primary mechanism first
2. If creative tasks underperform, plug in A-Evolve
3. Architecture supports both (from Council condition)

### 6.2 Multi-Agent Marketing Orchestra

**Potential:** Multiple specialized agents (Creative Agent, Audience Agent, Budget Agent) coordinated by MAIAgent.

**Inspiration:** Autoquant's parallel agent architecture

**Plan:** Phase 2 after single-agent validates

### 6.3 Real-Time Market Intelligence

**Potential:** Continuous monitoring of competitor ads, market trends, and customer sentiment.

**Inspiration:** Helena's competitor → ad pipeline

**Plan:** MCP integration for real-time data feeds

---

## 7. References

### Core Papers

1. **RouteLLM** — arXiv:2404.06035 — Learned cost-quality routing for LLMs
2. **RadixAttention** — arXiv:2312.07104 — Prefix caching for LLM serving
3. **Medusa** — arXiv:2401.10774 — Multi-head speculative decoding

### Open Source Projects

1. **Orchestra Research AI-Research-SKILLs** — 98 skills, 23 categories, 10K+ stars
2. **n8n** — Workflow automation with MCP integration
3. **Autoquant** — Karpathy's autoreasearch framework
4. **Hermes Agent** — Memory-growth agent

### Industry Analysis

1. **a16z GEO Thesis** — $80B+ Generative Engine Optimization
2. **Helena** — World's first autonomous AI marketer
3. **BoringMarketer** — Vibe Marketing Framework
4. **KARL** — RL knowledge agent research

---

## 8. Appendix: Research Log

```
DATE        SOURCE              KEY FINDING                          INFLUENCE
──────────  ──────────────────  ───────────────────────────────────  ──────────
2024-01-10  Autoquant           135 parallel agents for hypothesis   Inner loop
                             generation                             parallelization

2024-01-10  KARL               KG + RL > pure RL for knowledge      KG primary
             paper              reasoning

2024-01-11  Helena              Competitor → Creative pipeline       Competitive
                                                                 intelligence

2024-01-11  boringmarketer      4 levels of AI marketing maturity   Target L4

2024-01-12  a16z GEO            $80B+ GEO opportunity                GEO transform

2024-01-12  @swyx tweet         KG > vectors for agents              KG primary

2024-01-13  Orchestra Research  Two-loop autoresearch               Two-loop arch

2024-01-13  OpenOutreach        n8n + Claude feedback loop           n8n boundary

2024-01-14  TMLPD               RouteLLM cost-quality routing        Hybrid routing

2024-01-15  Agent Council       Multiple concerns raised             Conditions on
             Review             (see AGENT_COUNCIL_REPORT.md)        all decisions
```
