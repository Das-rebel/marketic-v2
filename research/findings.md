# Findings — MAIS 3.0

## Current Understanding

The 2024-2026 ML literature provides a clear blueprint for building SOTA marketing AI:

1. **Causal Layer is Non-Optional**: Raw ROAS is noisy. The causal stack (MMM → MTA → Uplift → Incrementality) denoises marketing signals before any model training.

2. **DPO is Wrong for Creative Content**: Vanilla DPO causes quality degradation. SOTA uses intrinsic rewards (OPERA), value-aware steering (VALUE), or token-level preferences (FTPO).

3. **Multi-Task Sharing Works**: A shared Transformer backbone with task-specific heads (CTR, CVR, Churn, CLV, Uplift) outperforms separate models.

4. **Policy-Constrained Agents are Production-Ready**: τ-bench proves that agents can autonomously orchestrate APIs while respecting business policies.

## Patterns and Insights

- **Layered causality**: Channel ROI (MMM) → touchpoint credit (MTA) → individual targeting (uplift) → ground truth calibration (incrementality)
- **Intrinsic over extrinsic rewards**: For creative content, perplexity-based rewards (OPERA) avoid reward hacking
- **Value-aware generation**: Integrating commercial value signals into token probabilities (VALUE) bridges the gap between language and business outcomes

## Lessons and Constraints

- DPO degrades creative diversity — don't use it for ad copy
- Raw ROAS is too noisy for direct RL — must denoise causally first
- Unobserved confounders in ad data require RA-IPS (CHAUN) or front-door identification (ALM-MTA)

## Open Questions

- Can OPERA rewards transfer from general content to marketing-specific creative?
- How do multi-task heads interact when tasks have different optimal learning rates?
- What policy constraints are needed for autonomous campaign management?
