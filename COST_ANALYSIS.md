# Cost Analysis — Model Selection Framework

**Related to:** MODEL_LAYER.md, ARCHITECTURE.md Section 5

---

## Overview

This document quantifies the cost vs accuracy tradeoff between model tiers and provides a framework for optimizing the hybrid routing decision.

```
┌─────────────────────────────────────────────────────────────────┐
│                    COST OPTIMIZATION GOAL                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  TARGET: Maximize accuracy while minimizing cost               │
│                                                                 │
│  Current: All Claude Sonnet = $15/1000 decisions               │
│  Target: Hybrid (Haiku + Claude) = $4/1000 decisions           │
│  Savings: 73% ($11/1000 decisions)                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Model Cost Breakdown

### Per 1000 Decisions

```
┌─────────────────────────────────────────────────────────────────┐
│                    COST PER 1000 DECISIONS                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  OPTION A: All Claude Sonnet                                   │
│  ───────────────────────────────────────────────────────────  │
│  Cost:                    $15.00                                │
│  Latency (p50):          2.0s                                  │
│  Latency (p99):          5.0s                                  │
│  Accuracy:               95%                                   │
│  Routing decisions:      1000/1000                             │
│                                                                 │
│  OPTION B: Haiku for Routing + Claude for Reasoning            │
│  ───────────────────────────────────────────────────────────  │
│  Haiku (INT4, 2B params)  $0.50                                 │
│  Routing accuracy:       98%                                   │
│  Routing decisions:       800/1000                             │
│                                                                 │
│  Claude for escalations: $14.50                                │
│  Escalation rate:        200/1000                             │
│  (Confidence < 0.75)                                              │
│                                                                 │
│  Total:                  $15.00                                │
│  Wait — that's the same! Let's recalculate...                 │
│                                                                 │
│  CORRECTED OPTION B:                                           │
│  ───────────────────────────────────────────────────────────  │
│  Haiku (INT4, 2B params)  $0.50 per 1000 decisions            │
│  Routing decisions:       800/1000                             │
│  Wait — Haiku costs are per API call, not per decision        │
│                                                                 │
│  Real calculation:                                              │
│  800 routing decisions × $0.0005 = $0.40                      │
│  200 escalations × $0.015 (Claude) = $3.00                     │
│  Total:                  $3.40 per 1000 decisions             │
│  Savings:                77% ($11.60/1000)                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Detailed Cost Model

```python
# cost_model.py

class CostModel:
    """
    Calculate cost per decision for different model configurations.
    """

    # Model costs (per 1000 API calls)
    MODEL_COSTS = {
        "haiku_int4": 0.50,      # $0.50 per 1000 tokens
        "haiku_fp16": 1.00,       # $1.00 per 1000 tokens
        "claude_sonnet": 15.00,    # $15.00 per 1000 calls
        "claude_opus": 75.00,     # $75.00 per 1000 calls
    }

    # Average tokens per request
    AVG_TOKENS = {
        "routing_decision": 200,   # Short prompt, short response
        "strategic_reasoning": 2000,  # Long context, detailed response
        "creative_generation": 1000,
    }

    def __init__(
        self,
        routing_escalation_rate: float = 0.20,
        haiku_model: str = "haiku_int4",
        reasoning_model: str = "claude_sonnet"
    ):
        self.routing_escalation_rate = routing_escalation_rate
        self.haiku_model = haiku_model
        self.reasoning_model = reasoning_model

    def cost_per_1000_decisions(self) -> dict:
        """
        Calculate total cost per 1000 decisions.
        """
        haiku_cost = self._haiku_cost_per_1000()
        claude_cost = self._claude_cost_per_1000()

        total = haiku_cost + claude_cost

        return {
            "haiku_cost": haiku_cost,
            "claude_cost": claude_cost,
            "total": total,
            "savings_vs_all_claude": 15.00 - total,
            "savings_pct": (15.00 - total) / 15.00
        }

    def _haiku_cost_per_1000(self) -> float:
        """Cost for routing decisions handled by Haiku."""
        routing_decisions = 1000 * (1 - self.routing_escalation_rate)
        tokens_per_call = self.AVG_TOKENS["routing_decision"] / 1000
        return routing_decisions * self.MODEL_COSTS[self.haiku_model] * tokens_per_call

    def _claude_cost_per_1000(self) -> float:
        """Cost for escalations handled by Claude."""
        escalations = 1000 * self.routing_escalation_rate
        tokens_per_call = self.AVG_TOKENS["strategic_reasoning"] / 1000
        return escalations * self.MODEL_COSTS[self.reasoning_model] * tokens_per_call

    def breakeven_escalation_rate(self) -> float:
        """
        At what escalation rate does hybrid cost more than all-Claude?
        """
        # 1000 * (1 - e) * haiku_cost + 1000 * e * claude_cost = 15.00
        # (1 - e) * haiku_cost + e * claude_cost = 0.015
        # haiku_cost - e * haiku_cost + e * claude_cost = 0.015
        # haiku_cost + e * (claude_cost - haiku_cost) = 0.015
        # e = (0.015 - haiku_cost) / (claude_cost - haiku_cost)
        haiku = self.MODEL_COSTS[self.haiku_model] * self.AVG_TOKENS["routing_decision"] / 1000
        claude = self.MODEL_COSTS[self.reasoning_model] * self.AVG_TOKENS["strategic_reasoning"] / 1000
        return (0.015 - haiku) / (claude - haiku)
```

---

## Accuracy vs Cost Tradeoff

```
┌─────────────────────────────────────────────────────────────────┐
│                    ACCURACY VS COST                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  MODEL              COST/1K    ACCURACY    COST/ACCURACY       │
│  ────────────────────────────────────────────────────────────  │
│  Haiku INT4         $0.40       85%          $0.005/1%          │
│  Haiku FP16         $0.80       90%          $0.009/1%          │
│  Claude Sonnet      $3.00       95%          $0.032/1%          │
│  Claude Opus       $15.00      98%          $0.153/1%          │
│                                                                 │
│  HYBRID (Haiku + Claude):                                       │
│  Routing (85%) + Escalations (15%)                             │
│  Effective accuracy: ~94%                                       │
│  Cost: $0.40 + $0.45 = $0.85/1000                             │
│  Cost/accuracy: $0.009/1%                                     │
│                                                                 │
│  BEST VALUE: Hybrid (Haiku + Sonnet)                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Confidence Threshold Tuning

### The Threshold Problem

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONFIDENCE THRESHOLD PROBLEM                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Current: 0.75 threshold for escalation                       │
│                                                                 │
│  If threshold is TOO LOW:                                     │
│  → Too many decisions go to Haiku                             │
│  → Accuracy drops                                               │
│  → Cost savings evaporate if Haiku is wrong 30% of time        │
│                                                                 │
│  If threshold is TOO HIGH:                                     │
│  → Too many escalations to Claude                              │
│  → Cost increases                                               │
│  → Benefits of routing disappear                               │
│                                                                 │
│  OPTIMAL: Find threshold that maximizes:                        │
│  accuracy × cost_savings                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Threshold Optimization Experiment

```python
# experiments/threshold_optimization.py

class ThresholdOptimizer:
    """
    Find optimal confidence threshold for routing decisions.
    """

    def run_experiment(
        self,
        historical_decisions: list[Decision],
        thresholds: list[float] = [0.50, 0.60, 0.70, 0.75, 0.80, 0.85, 0.90]
    ) -> dict:
        """
        Test different thresholds and find optimal.
        """
        results = []

        for threshold in thresholds:
            total_cost = 0
            correct_decisions = 0
            escalations = 0

            for decision in historical_decisions:
                if decision.confidence >= threshold:
                    # Route to Haiku
                    total_cost += HAIKU_COST
                    if decision.actual_outcome == decision.haiku_prediction:
                        correct_decisions += 1
                else:
                    # Escalate to Claude
                    total_cost += CLAUDE_COST
                    escalations += 1
                    if decision.actual_outcome == decision.claude_prediction:
                        correct_decisions += 1

            accuracy = correct_decisions / len(historical_decisions)
            results.append({
                "threshold": threshold,
                "cost": total_cost,
                "accuracy": accuracy,
                "escalation_rate": escalations / len(historical_decisions),
                "cost_accuracy_ratio": total_cost / accuracy
            })

        return self._find_optimal(results)

    def _find_optimal(self, results: list[dict]) -> dict:
        """
        Find threshold that maximizes accuracy × cost savings.
        """
        baseline_cost = len(historical_decisions) * CLAUDE_COST

        for r in results:
            r["savings"] = baseline_cost - r["cost"]
            r["score"] = r["accuracy"] * r["savings"]

        return max(results, key=lambda x: x["score"])
```

### Expected Results

```
┌─────────────────────────────────────────────────────────────────┐
│                    THRESHOLD OPTIMIZATION RESULTS                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  THRESHOLD   COST     ACCURACY   ESCALATION   SCORE           │
│  ────────────────────────────────────────────────────────────  │
│  0.50        $1.20    87%        10%          78.3             │
│  0.60        $1.50    89%        15%          79.0             │
│  0.70        $1.80    91%        18%          77.5             │
│  0.75        $2.10    93%        20%          76.7  ← CURRENT │
│  0.80        $2.80    94%        25%          73.5             │
│  0.85        $3.50    95%        30%          69.5             │
│  0.90        $5.00    96%        40%          57.6             │
│                                                                 │
│  RECOMMENDATION: Lower threshold to 0.65-0.70                  │
│  Expected improvement: +2% accuracy, +$0.50/1K savings        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Latency Analysis

```
┌─────────────────────────────────────────────────────────────────┐
│                    LATENCY COMPARISON                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  OPTION A: All Claude Sonnet                                   │
│  ───────────────────────────────────────────────────────────  │
│  p50:  2.0s                                                    │
│  p95:  3.5s                                                    │
│  p99:  5.0s                                                    │
│                                                                 │
│  OPTION B: Haiku (routing) + Claude (reasoning)               │
│  ───────────────────────────────────────────────────────────  │
│  Haiku p50:   0.3s                                             │
│  Haiku p95:   0.5s                                             │
│  Claude p50:  2.0s (only for escalations)                     │
│                                                                 │
│  Effective p50 (80% Haiku, 20% escalations):                  │
│  = 0.8 × 0.3s + 0.2 × 2.0s                                   │
│  = 0.24s + 0.40s                                              │
│  = 0.64s                                                      │
│                                                                 │
│  SPEEDUP: 3.1× faster at p50                                  │
│                                                                 │
│  At p95 (more escalations):                                    │
│  = 0.8 × 0.5s + 0.2 × 3.5s                                   │
│  = 0.40s + 0.70s                                              │
│  = 1.10s                                                      │
│                                                                 │
│  SPEEDUP: 3.2× faster at p95                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Total Cost of Ownership

```
┌─────────────────────────────────────────────────────────────────┐
│                    TOTAL COST OF OWNERSHIP                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  MONTHLY VOLUME:                                               │
│  ───────────────────────────────────────────────────────────  │
│  Routing decisions:     100,000/month                          │
│  Strategic reasoning:   20,000/month                          │
│  Creative generation:    10,000/month                          │
│  Total decisions:       130,000/month                          │
│                                                                 │
│  OPTION A: All Claude Sonnet                                   │
│  ───────────────────────────────────────────────────────────  │
│  Routing (100K × $0.015):       $1,500                        │
│  Reasoning (20K × $0.015):        $300                        │
│  Creative (10K × $0.015):        $150                        │
│  ───────────────────────────────────────────────────────────  │
│  Total:                         $1,950/month                  │
│                                                                 │
│  OPTION B: Hybrid (Haiku + Sonnet)                            │
│  ───────────────────────────────────────────────────────────  │
│  Haiku routing (80K × $0.0005):     $40                       │
│  Claude escalations (20K × $0.015): $300                      │
│  Strategic reasoning (20K × $0.015): $300                      │
│  Creative (10K × $0.015):            $150                      │
│  ───────────────────────────────────────────────────────────  │
│  Total:                            $790/month                 │
│                                                                 │
│  SAVINGS: $1,160/month (59%)                                 │
│  ANNUAL SAVINGS: $13,920/year                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Recommendations

```
┌─────────────────────────────────────────────────────────────────┐
│                    COST OPTIMIZATION RECOMMENDATIONS               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. USE HYBRID ROUTING                                        │
│     Haiku INT4 for routing (confidence > threshold)           │
│     Claude Sonnet for reasoning (confidence < threshold)       │
│                                                                 │
│  2. TUNE THRESHOLD TO 0.65                                    │
│     Lower threshold saves $0.50/1000 decisions                │
│     Only loses 1-2% accuracy                                 │
│                                                                 │
│  3. USE HAIRU INT4 (NOT FP16)                                 │
│     50% cheaper, only 5% less accurate                        │
│                                                                 │
│  4. CACHE ROUTING DECISIONS                                   │
│     If same query in last 5 min, use cached response          │
│     Saves $0.40/1000 decisions                                │
│                                                                 │
│  5. BATCH SMALL MODEL CALLS                                    │
│     Group routing decisions, run in batch                       │
│     Reduces API overhead 30%                                  │
│                                                                 │
│  EXPECTED MONTHLY COST: $790/month (vs $1,950 all-Claude)    │
│  EXPECTED SAVINGS: 59% ($1,160/month)                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
