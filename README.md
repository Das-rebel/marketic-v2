# MAIS — Marketing Autonomous Intelligence System

**A self-improving autonomous marketing intelligence system that learns from every campaign, reasons with transparency, and operates with human oversight.**

> "Not a marketing tool. An intelligence that studies the market 24/7, learns from every result, and gets smarter over time — while explaining every decision it makes."

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Planning](https://img.shields.io/badge/Status-Planning-blue.svg)]()

---

## The Killer Demo

```bash
# Launch a competitor counter-campaign analysis
mais analyze-competitor --brand notion --budget 10000 --platforms meta,linkedin

# What happens:
# [1] Research Brain scrapes 90 days of Notion's ads (GoMarble + Meta Ad Library)
# [2] AI identifies 8 positioning gaps with reasoning chains
# [3] Generates 47 ad variants, each tagged with: gap exploited, confidence %, rationale
# [4] Human reviews top 5 variants (high-stakes approval gate)
# [5] Top 5 auto-launched via n8n workflow
# [6] ROAS tracked daily → Denoised ROAS computed → Bayesian optimization
# [7] Learning: "Engineering persona gap + aggressive tone = 3.2x ROAS"

# Total time: 20 minutes for first campaign
# Total time for 10th campaign: 5 minutes (system has learned your market)
```

---

## The Core Philosophy

**Not a marketing tool. An intelligence system.**

Most "AI marketing tools" are sophisticated scripts: they execute predefined workflows and return results. MAIAgent is fundamentally different:

| Aspect | Other Tools | MAIS |
|---------|-------------|------|
| **Learning** | Static (same output every time) | Self-improving (learns from every campaign) |
| **Reasoning** | Black box ("here's an ad") | White box ("here's WHY we think this ad will work") |
| **Confidence** | None | Every recommendation has a confidence score |
| **Mistakes** | Repeated | Corrected via feedback loop |
| **Human control** | Either full-auto or fully-manual | Graduated: low-stakes auto, high-stakes approved |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    HUMAN IN THE LOOP (Gate)                       │
│         High-stakes decisions (>$1000, content posting, brand)     │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                 OUTER LOOP (Monthly)                              │
│  ─── Strategy synthesis  ─── Statistical significance gate       │
│  ─── Human-authorized model updates                             │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                 INNER LOOP (Daily + Weekly)                        │
│  ─── Daily: SPC monitoring, quick hypotheses (06:00 UTC)          │
│  ─── Weekly: Deep analysis, segment patterns (Monday)             │
│  ─── Hypothesis generation (NO model updates)                     │
│  ─── Queue for outer loop review                                │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│              LEARNING MECHANISM (Bayesian + SFT)                 │
│  ─── Reward denoising (causal impact analysis)                   │
│  ─── Bayesian optimization (noise-tolerant GP)                   │
│  ─── Supervised fine-tuning on validated pairs                   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                      MEMORY ARCHITECTURE                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Knowledge     │◄─►│Vector        │  │SQLite/      │      │
│  │Graph         │  │Store         │  │Episodic     │      │
│  │(Reasoning)   │  │(Retrieval)   │  │(Audit)      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                    MODEL LAYER (Hybrid)                          │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │Small Model    │─────►│Claude-class  │─────►│Human Review │ │
│  │(Routing/     │      │(Strategic    │      │(High-       │ │
│  │Classification)│      │Reasoning)    │      │Stakes)      │ │
│  └──────────────┘      └──────────────┘      └──────────────┘ │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                  TOOL + EXECUTION LAYER                         │
│  ┌──────────────┐      ┌──────────────┐                       │
│  │MAIAgent      │─────►│n8n           │                       │
│  │(Decisions)   │      │(Execution)   │                       │
│  └──────────────┘      └──────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Differentiators

### 1. White-Box Reasoning (vs. Black-Box AI Tools)

Every recommendation includes the reasoning chain:

```
GAP IDENTIFIED: "Engineering persona underserved by Notion"
CONFIDENCE: 0.87
REASONING CHAIN:
  1. Notion's LinkedIn ads (last 90 days) target "Operations teams" (73% of spend)
  2. Notion's engineering-focused content has 2.1% CTR vs 4.7% for Ops content
  3. 3 competitor ads (Linear, Plane, Height) are aggressively targeting engineers
  4. Engineering persona has 34% longer sales cycle but 2.3x LTV
  5. Gap: No major player owns "ease of setup" messaging for engineering teams
VARIANTS GENERATED: 47
EXPECTED ROAS: 3.2x (based on similar campaigns in vertical)
```

This is the opposite of Icon AI CMO or Okara AI, which produce results with no audit trail.

### 2. Self-Improving via Validated Learning

Not "set it and forget it." The system learns from every campaign outcome:

```
DAY 1: Campaign launches with "aggressive tone + feature comparison"
DAY 7: ROAS = 2.1x (below 3.2x expected)
DAY 14: Denoted ROAS = 2.3x (after removing competitor confounds)
DAY 21: Still underperforming. System flags: "aggressive tone not resonating"
DAY 30: Hypothesis generated: "enterprise persona + data-driven tone > aggressive"
DAY 60: New variant tests "data-driven tone" → ROAS = 4.1x
DAY 90: Model updated. System now prefers "data-driven" for enterprise.
         This learning persists for all future campaigns.
```

### 3. Human-in-the-Loop for High-Stakes Decisions

The system doesn't spend $10K without human approval:

```
Budget change > $1000     → Human approval required
Content posting            → Human approval required  
Brand risk decisions       → Human approval required
New audience segments     → Human approval required
Model weight updates      → Human approval required

Low-stakes routing (channel selection, bid tiers) → Automatic if confidence > 0.75
```

### 4. Statistical Rigor

Marketing metrics are noisy. ROAS swings 20-40% daily due to seasonality, competitor actions, audience fatigue. The system doesn't learn from noise:

```
WRONG: "ROAS was 3.2x this week, let's do more of that"
RIGHT: "After removing day-of-week effects, competitor confounds, and audience
        fatigue, denoised ROAS = 3.1x ± 0.3x. This is statistically 
        significant (p = 0.003, replicates in 2 segments, persists for 7 days)"
```

---

## Project Status

**Phase: Architecture Planning (Complete)**

See [ARCHITECTURE.md](ARCHITECTURE.md) for full technical specification.

### Documentation Map

| File | Purpose |
|------|---------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Full technical architecture |
| [LEARNING_MECHANISM.md](LEARNING_MECHANISM.md) | Bayesian optimization + reward denoising |
| [TWO_LOOP_ARCHITECTURE.md](TWO_LOOP_ARCHITECTURE.md) | Inner/outer loop design |
| [MEMORY_ARCHITECTURE.md](MEMORY_ARCHITECTURE.md) | Knowledge graph + vector + episodic |
| [MODEL_LAYER.md](MODEL_LAYER.md) | Small model routing + Claude reasoning |
| [TOOL_LAYER.md](TOOL_LAYER.md) | MAIAgent + n8n boundary |
| [SKILLS_ARCHITECTURE.md](SKILLS_ARCHITECTURE.md) | Code + docs + tests structure |
| [VALIDATION_PIPELINE.md](VALIDATION_PIPELINE.md) | Pre-update validation + rollback |
| [AGENT_COUNCIL_REPORT.md](AGENT_COUNCIL_REPORT.md) | Skeptical review by 6 agents |
| [RESEARCH.md](RESEARCH.md) | Competitive landscape + vault research |

---

## Why Build This?

**The problem with current marketing AI:**
- Black boxes: No reasoning, no audit trail
- No learning: Same output every time
- Fragile: Breaks when competitors change strategy
- Expensive: Claude API calls for every decision

**MAIS solves this:**
- Transparent reasoning chains on every decision
- Self-improving: Learns from every campaign outcome
- Robust: Bayesian optimization handles noisy data
- Cost-efficient: Small model for routing, Claude only for strategic reasoning

---

## License

MIT © Subhajit
