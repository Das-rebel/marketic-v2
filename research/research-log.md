# Research Log — MAIS 3.0

## 2026-07-04: Bootstrap Complete

### Literature Survey Completed
- 29 ML papers surveyed across 4 domains (causal inference, RLHF, tool-use agents, multi-task marketing)
- Key finding: 2024-2026 literature converges on layered causal architecture for marketing
- Key finding: DPO is suboptimal for creative content — OPERA/FTPO are SOTA
- Key finding: τ-bench is the most relevant agent benchmark (policy-constrained API orchestration)

### Dataset Mapping Completed
- 150+ datasets mapped to 4 architecture layers
- All datasets publicly available (no proprietary data needed)
- Tier 1 critical datasets identified (15 datasets)

### Architecture Redesign
- MAIS 3.0 = 4-layer architecture:
  1. Causal Foundation (MMM + MTA + Uplift + Incrementality)
  2. Multi-Task Prediction (shared backbone, 5 heads)
  3. Content Generation (OPERA + VALUE + Constitutional AI)
  4. Agent Orchestration (τ-bench + ToolBench + n8n)

### 5 Hypotheses Formed
- H1: Causal reward denoising (>15% improvement)
- H2: Multi-task backbone (>3% AUC over single-task)
- H3: OPERA > DPO for ad copy
- H4: VALUE steering >10% CTR
- H5: Policy constraints >90% violation reduction

### Next Steps
- Download Tier 1 datasets
- Set up evaluation harness
- Begin Phase 1: Causal Foundation (H1)
