# Agent Council Report

**Related to:** ARCHITECTURE.md Section 9

---

## Overview

The Agent Council is a multi-agent review system that evaluates major architectural and strategic decisions before implementation. It provides structured analysis, risk assessment, and conditions for approval.

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT COUNCIL PROCESS                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              AGENT COUNCIL MEMBERS                         │  │
│  │                                                           │  │
│  │  1. claude-opus      — Strategic reasoning, long-horizon  │  │
│  │  2. claude-sonnet    — Creative marketing, narrative     │  │
│  │  3. claude-haiku     — Fast tactical decisions          │  │
│  │  4. gemini-pro       — Alternative perspective          │  │
│  │  5. codex           — Technical implementation review    │  │
│  │  6. general-purpose  — Synthesis and final verdict      │  │
│  │                                                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↑                                  │
│                              │                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              REVIEW PROCESS                                │  │
│  │                                                           │  │
│  │  1. Present decision to all agents simultaneously         │  │
│  │  2. Each agent provides: VERDICT / FLAG / ABSTAIN         │  │
│  │  3. Collect reasoning, concerns, conditions             │  │
│  │  4. General-purpose agent synthesizes final report       │  │
│  │  5. Decision requires 4+ approvals to proceed            │  │
│  │                                                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Review Framework

### Decision Classification

```
┌─────────────────────────────────────────────────────────────────┐
│                    DECISION CLASSIFICATION                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  TIER 1 — FOUNDATIONAL (Requires unanimous council approval)     │
│  ─────────────────────────────────────────────────────────────  │
│  • Core architecture changes                                    │
│  • Learning mechanism modifications                            │
│  • Security model changes                                      │
│  • Data model changes                                          │
│                                                                 │
│  TIER 2 — STRATEGIC (Requires 5+ agent approval)               │
│  ─────────────────────────────────────────────────────────────  │
│  • New skill categories                                        │
│  • Model tier changes                                          │
│  • Validation pipeline modifications                           │
│  • Memory architecture changes                                 │
│                                                                 │
│  TIER 3 — TACTICAL (Requires 4+ agent approval)                 │
│  ─────────────────────────────────────────────────────────────  │
│  • Skill implementation details                               │
│  • Configuration changes                                       │
│  • Tool integrations                                          │
│  • Workflow optimizations                                      │
│                                                                 │
│  TIER 4 — ROUTINE (Agent vote not required)                    │
│  ─────────────────────────────────────────────────────────────  │
│  • Bug fixes                                                   │
│  • Documentation updates                                       │
│  • Minor configuration tweaks                                  │
│  • Hotfixes to production                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Agent Council Verdicts

### Verdict Definitions

```
┌─────────────────────────────────────────────────────────────────┐
│                    VERDICT DEFINITIONS                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ✓ APPROVE    — Agent supports this decision unconditionally    │
│  ⚠ FLAG       — Agent has concerns but would approve with       │
│                 specific conditions met                        │
│  ✗ REJECT     — Agent opposes this decision                     │
│  ⏸ ABSTAIN    — Agent lacks expertise to evaluate this         │
│                                                                 │
│  FINAL OUTCOME DETERMINATION:                                   │
│  ─────────────────────────────────────────────────────────────  │
│  • 6/6 APPROVE  → APPROVED (fast track)                         │
│  • 5/6 APPROVE  → APPROVED                                     │
│  • 4/6 APPROVE  → CONDITIONALLY APPROVED (all conditions met)  │
│  • 3/6 APPROVE  → DEBATED (requires revision)                  │
│  • < 3 APPROVE  → REJECTED (must redesign)                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Council Review: Architectural Decisions

### Decision 1: Reward Denoising Layer

**Decision:** Replace direct RL with reward denoising layer using Bayesian structural time-series models before any learning.

| Agent | Verdict | Reasoning |
|-------|---------|-----------|
| claude-opus | ✓ APPROVE | "Causal inference before RL is the right approach for confounded marketing data." |
| claude-sonnet | ✓ APPROVE | "Separating signal from noise is essential for marketing where many factors affect outcomes." |
| claude-haiku | ✓ APPROVE | "Fast tactical decisions need clean signals. This prevents garbage-in-garbage-out." |
| gemini-pro | ✓ APPROVE | "Statistical rigor before learning is well-founded. BH correction is appropriate." |
| codex | ✓ APPROVE | "Implementation is sound. Bayesian framework provides uncertainty quantification." |
| general-purpose | ✓ APPROVE | "All agents approve. APPROVED." |

**FINAL VERDICT: ✓ APPROVED (6/6)**

---

### Decision 2: Bayesian Optimization Over A-Evolve

**Decision:** Use Bayesian Optimization (GP regression) instead of LLM-driven evolution (A-Evolve) for learning.

| Agent | Verdict | Reasoning |
|-------|---------|-----------|
| claude-opus | ⚠ FLAG | "A-Evolve has shown promise in coding agents (SWE-bench 76.8%). Need conditions: hybrid approach, A-Evolve for creative tasks, BO for stable tasks." |
| claude-sonnet | ⚠ FLAG | "For creative strategy tasks, A-Evolve may outperform BO. Consider using A-Evolve for creative hypothesis generation while BO handles tactical optimization." |
| claude-haiku | ✓ APPROVE | "BO is faster to implement and more interpretable. Focus on getting one learning mechanism working first." |
| gemini-pro | ✓ APPROVE | "BO is well-understood and has good theory. Recommend starting with BO and evaluating A-Evolve as future work." |
| codex | ✓ APPROVE | "BO is simpler to implement correctly. A-Evolve adds complexity. Start simple." |
| general-purpose | ⚠ FLAG | "Conditional approval: Use BO as primary, with hybrid option to plug in A-Evolve later." |

**FINAL VERDICT: ⚠ CONDITIONALLY APPROVED (4 APPROVE, 2 FLAG)**
**Conditions:**
1. Architecture must support plugging in A-Evolve later without major refactor
2. BO must be evaluated against simple baselines before claiming superiority
3. Creative hypothesis generation can use A-Evolve principles even with BO as primary

---

### Decision 3: Small Model for Routing Only

**Decision:** Use small model (Qwen3-4B INT4) for routing/classification ONLY; Claude-class for all strategic reasoning.

| Agent | Verdict | Reasoning |
|-------|---------|-----------|
| claude-opus | ✓ APPROVE | "Separation of routing vs reasoning is correct. Small models are unreliable for complex reasoning." |
| claude-sonnet | ✓ APPROVE | "Routing decisions don't need Claude-class. This is a good cost/quality tradeoff." |
| claude-haiku | ✓ APPROVE | "Fast routing decisions need fast models. Small model is appropriate." |
| gemini-pro | ⚠ FLAG | "Quality concerns: small models may miss nuance in complex audience classification. Need confidence threshold for escalation." |
| codex | ✓ APPROVE | "LoRA fine-tuning for routing is well-established. Clear separation is good architecture." |
| general-purpose | ✓ APPROVE | "Approved with gemini-pro's condition: implement robust confidence thresholds." |

**FINAL VERDICT: ⚠ CONDITIONALLY APPROVED (5 APPROVE, 1 FLAG)**
**Conditions:**
1. Implement confidence threshold of 0.75 for routing decisions
2. Any routing decision below threshold automatically escalates to Claude
3. Audit logging of all routing decisions with confidence scores

---

### Decision 4: Skills = Code + Docs + Tests

**Decision:** Every skill must have: SKILL.md + skill.py + skill_test.py + skill_config.py + examples/

| Agent | Verdict | Reasoning |
|-------|---------|-----------|
| claude-opus | ✓ APPROVE | "Production-grade skills with tests prevent the documentation-only trap." |
| claude-sonnet | ✓ APPROVE | "Examples directory is crucial for adoption. Engineers learn from examples." |
| claude-haiku | ✓ APPROVE | "Tests ensure skills don't break. CI/CD integration is important." |
| gemini-pro | ✓ APPROVE | "Schema validation in skill_config.py is good practice." |
| codex | ✓ APPROVE | "Interface contract enforcement in Skill base class is essential." |
| general-purpose | ✓ APPROVE | "All agents approve. APPROVED." |

**FINAL VERDICT: ✓ APPROVED (6/6)**

---

### Decision 5: n8n = Execution Only

**Decision:** n8n handles execution ONLY; MAIAgent makes all decisions. n8n never operates autonomously.

| Agent | Verdict | Reasoning |
|-------|---------|-----------|
| claude-opus | ✓ APPROVE | "Clear separation of concerns. Brain doesn't move muscles directly." |
| claude-sonnet | ✓ APPROVE | "Token-based handoff between MAIAgent and n8n is good architecture." |
| claude-haiku | ✓ APPROVE | "n8n as 'nervous system' is the right metaphor." |
| gemini-pro | ✓ APPROVE | "Approval tokens prevent n8n from running unauthorized actions." |
| codex | ⚠ FLAG | "Need clear enforcement mechanism. What prevents n8n from going rogue? Need: (1) Token validation in n8n, (2) n8n cannot call ad platform APIs directly, only via MAIAgent-issued tokens." |
| general-purpose | ✓ APPROVE | "Approved with codex's conditions." |

**FINAL VERDICT: ⚠ CONDITIONALLY APPROVED (5 APPROVE, 1 FLAG)**
**Conditions:**
1. n8n MUST validate tokens before any platform API call
2. n8n credentials stored in n8n vault, not accessible to MAIAgent directly
3. MAIAgent cannot construct ad platform API calls — only sends action intent to n8n
4. Audit trail of all n8n executions with token IDs

---

### Decision 6: GEO as Middleware Transform

**Decision:** GEO (Generative Engine Optimization) implemented as middleware transform, not a separate strategic module.

| Agent | Verdict | Reasoning |
|-------|---------|-----------|
| claude-opus | ✓ APPROVE | "GEO as transform is architecturally cleaner. It enhances content, not a destination." |
| claude-sonnet | ✓ APPROVE | "Makes sense — GEO enhances existing content pipeline rather than being standalone." |
| claude-haiku | ✓ APPROVE | "Middleware approach is simpler to implement and maintain." |
| gemini-pro | ✓ APPROVE | "llms.txt generation and JSON-LD as transform is standard practice." |
| codex | ✓ APPROVE | "Vector indexing as part of content pipeline is correct." |
| general-purpose | ✓ APPROVE | "All agents approve. APPROVED." |

**FINAL VERDICT: ✓ APPROVED (6/6)**

---

### Decision 7: Two-Loop Architecture (Inner Daily + Outer Monthly)

**Decision:** Inner loop runs daily observations with NO model changes; Outer loop runs monthly synthesis with human approval for model updates.

| Agent | Verdict | Reasoning |
|-------|---------|-----------|
| claude-opus | ⚠ FLAG | "Monthly outer loop may be too slow for fast-moving campaigns. Recommend: campaign lifecycle-based outer loop triggers (e.g., after campaign completes 2-week cycle)." |
| claude-sonnet | ✓ APPROVE | "Separation of observation from action is good cognitive architecture." |
| claude-haiku | ⚠ FLAG | "Queue-based outer loop trigger (20 items or 5 high-confidence) is good. But 4-hour human review timeout may be too tight for strategic decisions." |
| gemini-pro | ✓ APPROVE | "Marketing-adapted timescales make sense. Monthly outer loop allows statistical significance." |
| codex | ✓ APPROVE | "Inner loop constraints (no model changes) are correctly enforced." |
| general-purpose | ⚠ FLAG | "Conditional approval: Implement campaign-lifecycle trigger alongside monthly trigger. Extend human review timeout for strategic decisions to 24 hours." |

**FINAL VERDICT: ⚠ CONDITIONALLY APPROVED (4 APPROVE, 3 FLAG)**
**Conditions:**
1. Implement dual triggers: monthly OR queue-based (20 items OR 5 high-confidence)
2. Human review timeout: 4 hours for tactical, 24 hours for strategic
3. Escalation path: If human doesn't respond within timeout, auto-pause and alert

---

## Cross-Cutting Themes

```
┌─────────────────────────────────────────────────────────────────┐
│                    CROSS-CUTTING CONCERNS                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. STATISTICAL RIGOR                                          │
│     All agents emphasized: marketing data is noisy.             │
│     Confounders, seasonality, competitor actions must be        │
│     accounted for before any learning.                           │
│                                                                 │
│  2. HUMAN-IN-THE-LOOP                                           │
│     High-stakes decisions (budget > $1000, content, brand risk)  │
│     must have human approval. The approval flow must be         │
│     frictionless but mandatory.                                  │
│                                                                 │
│  3. VALIDATION FIRST                                            │
│     Agents want to see ONE learning mechanism validated         │
│     before scaling to many. Don't over-engineer.                  │
│                                                                 │
│  4. SECURITY BOUNDARIES                                        │
│     Clear separation between MAIAgent (decisions) and n8n       │
│     (execution). Token-based auth prevents autonomy creep.       │
│                                                                 │
│  5. ITERATION SPEED                                             │
│     Monthly outer loop is appropriate for strategic decisions   │
│     but must have faster triggers for urgent situations.         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation Checklist

From Agent Council conditions:

- [ ] **Reward Denoising:** Implement Bayesian structural time-series with confound detection
- [ ] **Bayesian Optimization:** Architecture must allow A-Evolve plug-in later
- [ ] **Small Model Routing:** Confidence threshold 0.75 with auto-escalation
- [ ] **Skills:** SKILL.md + skill.py + skill_test.py + skill_config.py + examples/
- [ ] **n8n Boundary:** Token validation + vault credentials + no direct API calls
- [ ] **GEO Transform:** Content → GEO_TRANSFORM → Enhanced content pipeline
- [ ] **Two-Loop Triggers:** Monthly + queue-based (20 items OR 5 high-confidence)
- [ ] **Human Review Timeout:** 4 hours tactical, 24 hours strategic, auto-escalation

---

## Council Meeting History

| Date | Decision | Verdict | Key Conditions |
|------|----------|---------|----------------|
| 2024-01-15 | Reward Denoising Layer | ✓ APPROVED (6/6) | None |
| 2024-01-15 | Bayesian Optimization | ⚠ CONDITIONAL (4/6) | Hybrid architecture support |
| 2024-01-15 | Small Model Routing | ⚠ CONDITIONAL (5/6) | 0.75 confidence threshold |
| 2024-01-15 | Skills = Code+Tests | ✓ APPROVED (6/6) | None |
| 2024-01-15 | n8n Execution Only | ⚠ CONDITIONAL (5/6) | Token validation |
| 2024-01-15 | GEO as Middleware | ✓ APPROVED (6/6) | None |
| 2024-01-15 | Two-Loop Architecture | ⚠ CONDITIONAL (4/6) | Dual triggers, extended timeout |

---

## How to Submit a Decision for Council Review

```python
# Submit a decision for Agent Council review

COUNCIL_PROMPT = """You are reviewing the following architectural decision for MAIS:

DECISION: {decision_title}

DESCRIPTION:
{decision_description}

IMPLEMENTATION PLAN:
{implementation_plan}

RISKS:
{risks}

Please provide:
1. Your VERDICT: APPROVE / FLAG / REJECT
2. Specific CONDITIONS if FLAG
3. REASONING supporting your decision
4. ALTERNATIVES if REJECT

Present your review in this format:
VERDICT: [APPROVE/FLAG/REJECT]
CONDITIONS: [list conditions if FLAG]
REASONING: [your reasoning]
ALTERNATIVES: [alternatives if REJECT]
"""

async def submit_to_council(decision: Decision) -> CouncilReport:
    """
    Submit a decision to the Agent Council for review.
    """
    # Run parallel agents
    results = await tmlpd_parallel(
        prompt=[COUNCIL_PROMPT.format(
            decision_title=decision.title,
            decision_description=decision.description,
            implementation_plan=decision.plan,
            risks=decision.risks
        )] * 6,
        agents=["claude-opus", "claude-sonnet", "claude-haiku",
                "gemini-pro", "codex", "general-purpose"]
    )

    # Synthesize results
    return synthesize_council_report(results)
```
