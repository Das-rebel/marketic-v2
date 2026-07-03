# Learning Mechanism — Reward Denoising + Bayesian Optimization

**Related to:** ARCHITECTURE.md Section 2

---

## The Core Problem

Marketing metrics are **high variance**. ROAS swings 20-40% daily due to:

- Seasonality (weekday vs weekend, holiday vs non-holiday)
- Competitor actions (rival sale, PR crisis, ad spend changes)
- Audience fatigue (repeated exposure decay)
- Budget confounds (spend changes during measurement window)
- Market conditions (economic news, industry events)

**Raw RL on marketing metrics = bias amplification engine.** The system learns noise as signal and compounds errors.

---

## The Solution: Three-Stage Learning

```
┌─────────────────────────────────────────────────────────────────┐
│                    STAGE 1: Reward Denoising (Daily)             │
│  Raw ROAS ──► Causal Impact Analysis ──► Denoised ROAS        │
│  Apply Bayesian structural time-series model                    │
│  Remove: day-of-week, seasonality, competitor, fatigue effects  │
│  Output: Denoised ROAS with confidence interval                │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌────────────────────────────────▼─────────────────────────────────┐
│                    STAGE 2: Bayesian Optimization (Weekly)         │
│  GP regression on denoised ROAS vs parameters                  │
│  Expected Improvement acquisition function                      │
│  Propose next parameter setting                               │
│  Minimum 14-day observation window                            │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌────────────────────────────────▼─────────────────────────────────┐
│                    STAGE 3: Supervised Fine-tuning (Monthly)     │
│  Only on VALIDATED pairs (query, action, outcome)              │
│  Statistical significance gate required                         │
│  Replication across 2+ segments required                       │
│  Human approval required                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Stage 1: Reward Denoising

### 1.1 Confounders and Their Handling

| Confounder | Detection Method | Handling |
|------------|----------------|---------|
| Day-of-week | Fourier terms in BSTS model | Remove weekly seasonality component |
| Seasonality | STL decomposition + trend extraction | Detrend before analysis |
| Competitor confounds | News/event correlation analysis | Flag if ROAS change correlates with competitor events |
| Audience fatigue | Exposure decay curve modeling | Model decay, remove from ROAS |
| Budget changes | Spend rate change detection | Normalize to per-dollar basis |

### 1.2 Bayesian Structural Time-Series Model

```python
class CausalImpactAnalyzer:
    """
    Uses Bayesian structural time-series to decompose ROAS into:
    - Trend component (underlying performance)
    - Seasonality component (day-of-week, weekly, monthly)
    - Control component (market index, competitor activity)
    - Residual (experimental effect)
    """

    def __init__(self):
        self.priors = {
            'trend_strength': Normal(0, 1),
            'seasonality_strength': Normal(0, 0.5),
            'control_strength': Normal(0, 0.5),
        }

    def fit(self, y, control_series, dates):
        """
        y: raw ROAS time series
        control_series: market/competitor index
        dates: timestamps for alignment
        """
        # Local level model + seasonality + regression component
        model =bsts(
            y ~ trend(level) + seasonality(weekly) + regression(control_series),
            data = {y, control_series, dates},
            priors = self.priors
        )
        return model

    def denoise(self, model, y):
        """
        Returns: denoised_roas, ci_width, is_learnable
        """
        # Extract posterior distribution
        # Subtract control contribution
        # Return mean and credible interval
        denoised = posterior_mean - control_contribution
        ci_95 = posterior_ci_95()
        ci_width = ci_95[1] - ci_95[0]

        # Flag if too noisy to learn from
        is_learnable = (ci_width / abs(denoised)) < 0.3

        return {
            'denoised_roas': denoised,
            'ci_width': ci_width,
            'ci_lower': ci_95[0],
            'ci_upper': ci_95[1],
            'is_learnable': is_learnable
        }
```

### 1.3 Daily Denoised ROAS Computation

```python
async def compute_daily_denoised_roas(campaign_id: str, date: date) -> dict:
    """
    Runs daily. Produces denoised ROAS for a single campaign/day.
    """
    # 1. Fetch raw metrics
    raw_metrics = await fetch_campaign_metrics(campaign_id, window=14)
    market_index = await fetch_market_index(window=14)  # control series

    # 2. Fit BSTS model
    analyzer = CausalImpactAnalyzer()
    model = analyzer.fit(
        y=raw_metrics['roas_series'],
        control_series=market_index,
        dates=raw_metrics['dates']
    )

    # 3. Extract denoised ROAS
    result = analyzer.denoise(model, raw_metrics['roas_series'])

    # 4. Log for audit trail
    await log_to_episodic(
        table='daily_denoised_roas',
        campaign_id=campaign_id,
        date=date,
        raw_roas=raw_metrics['latest_roas'],
        denoised_roas=result['denoised_roas'],
        ci_width=result['ci_width'],
        is_learnable=result['is_learnable']
    )

    return result
```

---

## Stage 2: Bayesian Optimization

### 2.1 What Gets Optimized

| Parameter | Range | Resolution | Notes |
|-----------|-------|------------|-------|
| Bid multiplier | 0.5x - 2.0x | 0.05 | Applied to base bid |
| Audience segment weights | 0.0 - 1.0 | 0.1 | Allocation across segments |
| Creative mix (img/vid/car) | 0% - 100% | 10% | Budget allocation |
| Dayparting (hour weights) | 0.0 - 1.0 | 0.25 | 6-hour blocks |
| Placements | 0.0 - 1.0 | 0.1 | Feed vs story vs search |

### 2.2 GP Regression

```python
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel, ConstantKernel

class BayesianOptimizer:
    """
    Gaussian Process regression for noisy marketing parameters.
    """

    def __init__(self):
        kernel = (
            ConstantKernel(1.0) * RBF(length_scale=[0.2]*N_params) +
            WhiteKernel(noise_level=0.1)
        )
        self.gp = GaussianProcessRegressor(
            kernel=kernel,
            n_restarts_optimizer=5,
            normalize_y=True
        )

    def fit(self, params_list, denoised_roas_list):
        """
        params_list: list of parameter dicts
        denoised_roas_list: corresponding denoised ROAS values
        """
        X = self._params_to_array(params_list)
        y = np.array(denoised_roas_list)
        self.gp.fit(X, y)

        # Compute R² for fitness check
        y_pred = self.gp.predict(X)
        r_squared = r2_score(y, y_pred)
        return r_squared

    def suggest_next(self, bounds):
        """
        Expected Improvement acquisition function.
        """
        # Generate candidate points
        candidates = self._generate_candidates(bounds, n=1000)

        # Compute EI for each candidate
        ei = self._expected_improvement(candidates)

        # Return best candidate
        best_idx = np.argmax(ei)
        return self._array_to_params(candidates[best_idx])

    def _expected_improvement(self, X_candidates):
        """
        EI = (μ(x) - f_best) * Φ(z) + σ(x) * φ(z)
        where z = (μ(x) - f_best) / σ(x)
        """
        mu, sigma = self.gp.predict(X_candidates, return_std=True)
        f_best = self.gp.Y_train_.min()  # Minimize ROAS

        with np.errstate(divide='ignore'):
            z = (mu - f_best) / sigma
            ei = (mu - f_best) * norm.cdf(z) + sigma * norm.pdf(z)

        # Add exploration bonus for high uncertainty
        ei += 0.1 * sigma
        return ei
```

### 2.3 Optimization Schedule

```
WEEK 1-2: Data collection, no optimization
WEEK 3: Initial GP fit, first suggestion
WEEK 4-6: Test first suggested parameter
WEEK 7: Re-fit GP with new data, new suggestion
WEEK 8: Test second suggestion

TERMINATION CONDITIONS:
- R² > 0.3: GP is fitting well, continue
- R² < 0.1 after 30 days: Flag as not learnable, pause optimization
- Any metric violates safety bounds: Immediate pause
```

---

## Stage 3: Supervised Fine-tuning

### 3.1 Validation Criteria (ALL Required)

```
┌─────────────────────────────────────────────────────────────────┐
│                    VALIDATION CRITERIA                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. DENOISED ROAS IMPROVEMENT > 5%                           │
│     - Must be vs. control/baseline                             │
│     - Absolute improvement, not relative                        │
│                                                                 │
│  2. P-VALUE < 0.05 (AFTER BH CORRECTION)                     │
│     - T-test on denoised ROAS distributions                   │
│     - Benjamini-Hochberg for multiple comparisons             │
│                                                                 │
│  3. EFFECT SIZE (COHEN'S D) > 0.2                            │
│     - Small effect minimum                                     │
│     - 0.8 = large effect (can accept 1 segment + 1 period)  │
│                                                                 │
│  4. REPLICATES IN 2+ AUDIENCE SEGMENTS                        │
│     - Same direction in each segment                           │
│     - At least 1000 impressions per segment                    │
│                                                                 │
│  5. PERSISTS FOR 7+ DAYS                                     │
│     - Not a one-day fluke                                     │
│                                                                 │
│  6. NO CONFOUND CORRELATION > 0.2                            │
│     - Correlated with known confounders < 0.2                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Training Data Construction

```python
class SFTTrainingDataBuilder:
    """
    Builds supervised fine-tuning dataset from validated campaign outcomes.
    """

    def __init__(self, max_pairs=1000):
        self.max_pairs = max_pairs
        self.positive_pairs = []
        self.negative_pairs = []

    def add_validated_pair(self, query_context: dict, action: dict, outcome: dict):
        """
        Called only for pairs that passed ALL validation criteria.
        """
        pair = {
            'query': self._format_context(query_context),
            'action': self._format_action(action),
            'outcome': outcome['denoised_roas'],
            'confidence': outcome.get('confidence', 1.0),
            'segments': outcome.get('segments', []),
            'persistence_days': outcome.get('persistence_days', 0)
        }

        if outcome['denoised_roas'] > outcome.get('baseline', outcome['denoised_roas']):
            self.positive_pairs.append(pair)
        else:
            self.negative_pairs.append(pair)

    def build_dataset(self):
        """
        Returns training-ready dataset with 3:1 positive:negative ratio.
        """
        # Sample negative pairs to maintain ratio
        n_negatives = min(len(self.negative_pairs), len(self.positive_pairs) // 3)
        selected_negatives = random.sample(self.negative_pairs, n_negatives)

        all_pairs = self.positive_pairs + selected_negatives
        random.shuffle(all_pairs)

        # Format for LoRA training
        return [
            {
                'messages': [
                    {'role': 'user', 'content': pair['query']},
                    {'role': 'assistant', 'content': pair['action']}
                ],
                'outcome': pair['outcome']
            }
            for pair in all_pairs
        ]

    def _format_context(self, ctx):
        """Format query context for training."""
        return f"""Campaign: {ctx.get('campaign_name')}
Audience: {ctx.get('audience_segment')}
Goal: {ctx.get('objective')}
Competitor: {ctx.get('competitor')}
History: ROAS {ctx.get('recent_roas')} over {ctx.get('recent_days')} days
"""

    def _format_action(self, action):
        """Format recommended action for training."""
        return f"""Recommendation: {action.get('type')}
Channel: {action.get('channel')}
Budget: {action.get('budget_change_pct')}%

Reasoning:
{action.get('reasoning_chain', '')}

Confidence: {action.get('confidence', 0.5):.2f}
"""
```

### 3.3 LoRA Fine-tuning

```python
async def fine_tune_router_on_validated_pairs(dataset: list):
    """
    Monthly fine-tuning on validated (query → action → outcome) pairs.
    Only runs after ALL validation criteria pass + human approval.
    """
    # 1. Validate dataset quality
    assert len(dataset) >= 50, "Need minimum 50 pairs"
    assert len(dataset) <= 1000, "Cap at 1000 pairs to prevent overfitting"

    positive_rate = sum(1 for p in dataset if p['outcome'] > 0) / len(dataset)
    assert 0.4 < positive_rate < 0.9, "Sanity check on outcome distribution"

    # 2. Train/val split (90/10)
    random.shuffle(dataset)
    train = dataset[:int(len(dataset) * 0.9)]
    val = dataset[int(len(dataset) * 0.9):]

    # 3. Fine-tune with LoRA
    base_model = "claude-haiku"  # Or equivalent small model
    lora_config = {
        'lora_r': 16,
        'lora_alpha': 32,
        'lora_dropout': 0.1,
        'target_modules': ['q_proj', 'v_proj', 'k_proj', 'o_proj'],
        'bias': 'none',
        'task_type': 'CAUSAL_LM'
    }

    training_config = {
        'learning_rate': 2e-4,
        'num_train_epochs': 3,
        'per_device_train_batch_size': 4,
        'gradient_accumulation_steps': 4,
        'warmup_ratio': 0.1,
        'lr_scheduler_type': 'cosine',
        'fp16': True,
    }

    # 4. Train
    model = train_lora(base_model, train, val, lora_config, training_config)

    # 5. Evaluate on held-out
    accuracy = evaluate_on_validation(model, val)
    assert accuracy > 0.6, f"Model accuracy {accuracy} below threshold"

    # 6. Return for shadow deploy
    return model
```

---

## Integration: Full Learning Loop

```python
class LearningMechanism:
    """
    Orchestrates the three-stage learning process.
    """

    def __init__(self):
        self.denoiser = CausalImpactAnalyzer()
        self.optimizer = BayesianOptimizer()
        self.sft_builder = SFTTrainingDataBuilder()

    async def daily_inner_loop(self, campaign_id: str, date: date):
        """
        INNER LOOP: Computes denoised ROAS, updates GP.
        NO model changes. Just observation.
        """
        # Compute denoised ROAS
        result = await compute_daily_denoised_roas(campaign_id, date)

        # If learnable, add to GP training data
        if result['is_learnable']:
            await self.optimizer.add_observation(
                params=self._get_current_params(campaign_id),
                denoised_roas=result['denoised_roas']
            )

        return result

    async def weekly_optimization(self, campaign_id: str):
        """
        INNER LOOP: Suggests next parameter setting via GP.
        """
        if not self.optimizer.has_sufficient_data():
            return None  # Not enough data yet

        r_squared = self.optimizer.fit()
        if r_squared < 0.1:
            return {'status': 'not_learnable', 'r_squared': r_squared}

        suggestion = self.optimizer.suggest_next(bounds=self.param_bounds)
        return {
            'status': 'suggestion',
            'params': suggestion,
            'r_squared': r_squared,
            'requires_review': True  # Always human review
        }

    async def monthly_outer_loop(self):
        """
        OUTER LOOP: Synthesizes validated pairs for SFT.
        Human approval required before any model update.
        """
        # Collect all validated pairs from the month
        validated_pairs = await self._collect_validated_pairs_this_month()

        if len(validated_pairs) < 50:
            return {'status': 'insufficient_data', 'pairs': len(validated_pairs)}

        # Build SFT dataset
        dataset = self.sft_builder.build_from_pairs(validated_pairs)

        # Submit for human review
        submission = await self._submit_for_human_review(dataset)

        if submission['approved']:
            # Fine-tune (shadow deploy first)
            model = await fine_tune_router_on_validated_pairs(dataset)
            return await self._shadow_deploy(model)
        else:
            return {'status': 'rejected', 'reason': submission['reason']}
```

---

## Failure Modes and Mitigations

| Failure Mode | Detection | Mitigation |
|-------------|-----------|-----------|
| Causal model misspecified | Residual analysis shows structure | Ensemble multiple models (BSTS + CausalImpact + DoWhy) |
| GP overfits to noise | R² > 0.9 on training but fails on new data | Train/val split, early stopping |
| Non-stationarity | Rolling window R² drops over time | Re-fit GP every 3 months |
| Confounders leak through | Sensitivity analysis shows residual confound | Flag and exclude from learning |
| SFT overfits to small dataset | Validation accuracy drops after 2nd round | Hard cap of 1000 pairs |
| Catastrophic forgetting | Old validated pairs accuracy drops after update | Test on hold-out of old pairs before deploy |
