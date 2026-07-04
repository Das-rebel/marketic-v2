# Literature Survey — MAIS 3.0

## Causal Inference for Marketing (10 papers)

### CHAUN + RA-IPS (2026)
- arXiv:2606.27114
- Cross-head attention uplift network with Robust Adversarial IPS for unobserved confounders
- +25.6% QINI improvement over SOTA on CRITEO-UPLIFT and LAZADA
- **Relevance**: Core uplift-modeling engine for MAIS Layer 1

### UpliftBench (2026)
- arXiv:2604.06123
- Benchmark: S-Learner (LightGBM) wins on 13.98M Criteo records
- Top 20% ranked customers capture 77.7% of incremental conversions (3.9x lift)
- **Relevance**: Estimator selection guide for production

### Orthogonal Uplift Learning (2026)
- arXiv:2602.19851
- Permutation-invariant treatment representations for combinatorial treatments
- **Relevance**: Multi-creative/multi-channel treatment combinations

### ALM-MTA (ICLR 2026)
- arXiv:2605.08881
- Front-door causal identification with adversarially learned mediator
- Deployed 400M DAU, 30B samples
- **Relevance**: Gold-standard causal multi-touch attribution

### Amazon Ads MTA (2025)
- arXiv:2508.08209
- Hybrid RCT + ML: randomized trials as causal anchors
- **Relevance**: Pragmatic production pattern

### DeepCausalMMM (2026)
- arXiv:2510.13087
- GRU adstock + DAG structure + Hill saturation + budget optimization
- **Relevance**: Open-source end-to-end MMM for channel planning

### IMA (2026)
- arXiv:2606.16878
- Unifies MMM (coarse) with Bayesian MTA (granular)
- **Relevance**: Bridges MMM↔MTA gap

### DICE-MMM (2026)
- arXiv:2606.12687
- Diagnoses attribution bypass in neural MMM
- **Relevance**: Validity warning — neural MMM must pass stress tests

### TikTok Cannibalization (ADKDD 2026)
- arXiv:2606.26690
- Experiment-calibrated daily incrementality from sparse RCTs
- -15pt cannibalization globally
- **Relevance**: Attribution vs incrementality mismatch solution

### DICE-DML (2026)
- arXiv:2603.02359
- Deepfake-informed double ML for creative attribute causal effects
- 73-97% RMSE reduction vs standard DML
- **Relevance**: Creative-level causal optimization

---

## RLHF & Content Generation (11 papers)

### VALUE (Alibaba, 2025)
- arXiv:2504.05321
- Value-aware LLM token steering via Weighted Trie
- Production-deployed since Oct 2024 (Alibaba Double Eleven)
- **Relevance**: Integrates commercial value into token probabilities

### GR4AD (Kuaishou, 2026)
- arXiv:2602.22732
- Ranking-Guided Softmax Preference Optimization (RSPO)
- +4.2% ad revenue, deployed 400M+ users
- **Relevance**: List-wise RL for generative ad recommenders

### OPERA (2026)
- arXiv:2606.25757
- Objective Perplexity-based Reinforcement Learning
- Replaces LLM-as-judge with intrinsic perplexity-dynamics rewards
- **Relevance**: Solves "no ground truth for creative quality"

### FTPO/Antislop (2025)
- arXiv:2510.15061
- Final Token Preference Optimization
- 90% slop reduction while maintaining creative quality
- **Relevance**: DPO alternative for creative content

### SuperWriter (2025)
- arXiv:2506.04180
- Hierarchical DPO using MCTS for quality propagation
- **Relevance**: Long-form content quality

### GRPO Style Transfer (CoNLL 2026)
- arXiv:2512.05747
- GRPO with authorship-verification-calibrated reward
- **Relevance**: Style adaptation for brand voice

### Follow-Your-Preference++ (2026)
- arXiv:2606.03216
- Calibrated ensemble of reward models
- **Relevance**: Mitigates reward hacking

### G-Zero (2026)
- arXiv:2605.09959
- Verifier-free Hint-δ intrinsic reward
- **Relevance**: Scaling creative generation without external judges

### AI vs Human Brand Safety (ICCV 2025)
- arXiv:2508.05527
- Benchmarks MLLMs on multilingual brand-safety dataset
- **Relevance**: Brand safety classification for ads

### Reverse Constitutional AI (2026)
- arXiv:2604.17769
- Inverts constitution for adversarial red-team data generation
- **Relevance**: Safety testing automation

### SCHEMA Compliance Trap (2026)
- arXiv:2605.02398
- Constitutional AI shows near-perfect immunity to compliance traps
- **Relevance**: Robust brand safety

---

## Tool-Use Agents (4 papers)

### τ-bench (2024)
- arXiv:2406.12045
- Multi-turn benchmark with domain-specific APIs + policy guidelines
- Retail and airline customer-service domains
- **Relevance**: Template for policy-constrained marketing agents

### ToolBench/ToolLLM (ICLR 2024)
- arXiv:2307.16789
- 16,000+ REST APIs with DFSDT reasoning
- **Relevance**: Multi-API marketing orchestration

### ToolACE (Salesforce, 2024)
- arXiv:2409.00920
- Multi-agent collaboration for authentic function-calling data
- **Relevance**: Synthetic function-calling data generation

### WebShop (NeurIPS 2022)
- arXiv:2207.01296
- Interactive shopping environment
- **Relevance**: E-commerce agent training

---

## Multi-Task Marketing Prediction (4 papers)

### Multi-Task Budget Allocation (2025)
- arXiv:2506.00959
- Hidden representation clustering + multi-task representation learning
- **Relevance**: Large-scale marketing optimization

### Joint CTR+CVR Residual (2024)
- DOI:10.1007/s00521-024-10617-0
- Residual connections for joint CTR/CVR prediction
- **Relevance**: Unified CTR/CVR architecture

### LSTM+Transformer Multi-Task (2025)
- DOI:10.55214/25768484.v9i3.5256
- +15% AUC purchase, +35% CTR, +28% CVR on 1.5M interactions
- **Relevance**: Multi-output marketing prediction

### Survival Analysis Churn (2025)
- DOI:10.1109/iccct63501.2025.11020381
- Deep learning + survival models for churn
- **Relevance**: Churn prediction with time-to-event
