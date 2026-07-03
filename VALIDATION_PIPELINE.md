# Validation Pipeline

**Related to:** ARCHITECTURE.md Section 7

---

## Overview

The validation pipeline is the gatekeeper for all model updates. No model weights change without passing through all 7 stages. This is non-negotiable.

```
┌─────────────────────────────────────────────────────────────────┐
│                    VALIDATION PIPELINE                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ STAGE 1: Data Quality Gate                               │  │
│  │ Check: Missing data < 5%, outliers flagged, sources agree │  │
│  │ FAIL → Abort                                           │  │
│  │ PASS → Stage 2                                         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ STAGE 2: Confound Detection                             │  │
│  │ Check: No day-of-week, seasonality, competitor effects │  │
│  │ FAIL → Flag confounders, adjust analysis               │  │
│  │ PASS → Stage 3                                         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ STAGE 3: Statistical Significance                       │  │
│  │ Check: p-value < 0.05 (BH-corrected)                   │  │
│  │ FAIL → Abort                                           │  │
│  │ PASS → Stage 4                                         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ STAGE 4: Replication Check                              │  │
│  │ Check: Effect in 2+ segments AND 2+ time periods       │  │
│  │ FAIL → Abort                                           │  │
│  │ PASS → Stage 5                                         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ STAGE 5: Human Review                                   │  │
│  │ Check: Human approves rationale + risk assessment        │  │
│  │ FAIL → Route back to MAIAgent for revision              │  │
│  │ PASS → Stage 6                                         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ STAGE 6: Shadow Deploy (7 days)                         │  │
│  │ Check: No errors spike, latency OK, no budget overages   │  │
│  │ FAIL → Rollback                                        │  │
│  │ PASS → Stage 7                                         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ STAGE 7: Canary Deploy (14 days, 10% traffic)          │  │
│  │ Check: ROAS maintained, errors < baseline, latency OK   │  │
│  │ FAIL → Rollback                                        │  │
│  │ PASS → Full Rollout                                    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Stage 1: Data Quality Gate

```python
class DataQualityGate:
    """
    Stage 1: Verify data is sufficient quality for analysis.
    """

    THRESHOLDS = {
        "missing_data_pct": 0.05,  # Max 5% missing
        "outlier_z_score": 4.0,     # Flag if > 4σ
        "min_sample_size": 100,      # Min observations
        "source_agreement": 0.90,   # 90% agreement across sources
    }

    async def check(self, dataset: MarketingDataset) -> GateResult:
        """
        Run data quality checks.
        """
        issues = []

        # 1. Missing data check
        missing_pct = dataset.missing_value_count / dataset.total_count
        if missing_pct > self.THRESHOLDS["missing_data_pct"]:
            issues.append(DataIssue(
                severity="fail",
                check="missing_data",
                value=missing_pct,
                threshold=self.THRESHOLDS["missing_data_pct"],
                message=f"Too much missing data: {missing_pct:.1%}"
            ))

        # 2. Outlier detection
        outliers = self._detect_outliers(dataset.values)
        if len(outliers) > len(dataset) * 0.01:  # > 1% outliers
            issues.append(DataIssue(
                severity="warning",
                check="outliers",
                value=len(outliers),
                threshold=len(dataset) * 0.01,
                message=f"Found {len(outliers)} outliers"
            ))

        # 3. Sample size check
        if len(dataset) < self.THRESHOLDS["min_sample_size"]:
            issues.append(DataIssue(
                severity="fail",
                check="sample_size",
                value=len(dataset),
                threshold=self.THRESHOLDS["min_sample_size"],
                message=f"Insufficient sample size: {len(dataset)} < {self.THRESHOLDS['min_sample_size']}"
            ))

        # 4. Source agreement
        if dataset.has_multiple_sources:
            agreement = self._check_source_agreement(dataset)
            if agreement < self.THRESHOLDS["source_agreement"]:
                issues.append(DataIssue(
                    severity="fail",
                    check="source_agreement",
                    value=agreement,
                    threshold=self.THRESHOLDS["source_agreement"],
                    message=f"Sources disagree: {agreement:.1%} agreement"
                ))

        passed = not any(i.severity == "fail" for i in issues)

        return GateResult(
            stage="data_quality",
            passed=passed,
            issues=issues,
            data_quality_score=self._compute_score(dataset, issues)
        )

    def _detect_outliers(self, values: list[float]) -> list[int]:
        """Detect outliers using z-score method."""
        mean = statistics.mean(values)
        std = statistics.stdev(values)
        threshold = self.THRESHOLDS["outlier_z_score"]

        return [
            i for i, v in enumerate(values)
            if abs((v - mean) / std) > threshold
        ]
```

---

## 2. Stage 2: Confound Detection

```python
class ConfoundDetector:
    """
    Stage 2: Detect and flag confounding variables.
    Marketing data is riddled with confounds — we must find them.
    """

    CONFOUND_PATTERNS = {
        "day_of_week": {
            "check": lambda d: d.date.weekday(),
            "adjust": True,  # Can adjust for this
        },
        "seasonality": {
            "check": lambda d: d.date.month in [11, 12],  # Holiday season
            "adjust": True,
        },
        "competitor_activity": {
            "check": lambda d: d.competitor_spend_delta > 0.2,
            "adjust": False,  # Must exclude
        },
        "budget_step_change": {
            "check": lambda d: d.budget_change_pct > 0.5,
            "adjust": False,  # Must exclude period
        },
        "creative_freshness": {
            "check": lambda d: d.days_since_creative_change < 7,
            "adjust": False,  # Must exclude
        },
    }

    async def check(self, dataset: MarketingDataset) -> GateResult:
        """
        Detect confounds and determine if effect is real.
        """
        detected_confounds = []

        for confound_name, confound_config in self.CONFOUND_PATTERNS.items():
            affected_indices = []

            for i, row in enumerate(dataset):
                if confound_config["check"](row):
                    affected_indices.append(i)

            # If > 20% of data affected, flag as confound
            if len(affected_indices) / len(dataset) > 0.2:
                detected_confounds.append(ConfoundResult(
                    name=confound_name,
                    affected_count=len(affected_indices),
                    affected_pct=len(affected_indices) / len(dataset),
                    can_adjust=confound_config["adjust"],
                    recommendation="exclude" if not confound_config["adjust"] else "adjust"
                ))

        # Check if confounds overlap with treatment period
        confounding_treatment = self._check_treatment_overlap(
            dataset, detected_confounds
        )

        if confounding_treatment:
            return GateResult(
                stage="confound_detection",
                passed=False,
                issues=[Issue(
                    severity="fail",
                    message="Treatment period confounded by external factors"
                )],
                detected_confounds=detected_confounds
            )

        return GateResult(
            stage="confound_detection",
            passed=True,
            detected_confounds=detected_confounds
        )

    def _check_treatment_overlap(
        self,
        dataset: MarketingDataset,
        confounds: list[ConfoundResult]
    ) -> bool:
        """Check if confounds overlap with treatment window."""
        for confound in confounds:
            if not confound.can_adjust:
                # Check if treatment period overlaps with confound period
                if self._period_overlaps(
                    dataset.treatment_start,
                    dataset.treatment_end,
                    confound.affected_indices
                ):
                    return True
        return False
```

---

## 3. Stage 3: Statistical Significance

```python
class SignificanceChecker:
    """
    Stage 3: T-test with Benjamini-Hochberg correction.
    """

    def __init__(self, alpha: float = 0.05):
        self.alpha = alpha

    async def check(self, experiment: Experiment) -> GateResult:
        """
        Run t-test and BH correction.
        """
        # Get treatment and control distributions
        treatment = experiment.denoised_outcomes.treatment
        control = experiment.denoised_outcomes.control

        # Welch's t-test (unequal variances)
        t_stat, raw_p = ttest_ind(treatment, control, equal_var=False)

        # Effect size (Cohen's d)
        effect_size = self._cohens_d(treatment, control)

        # Benjamini-Hochberg correction
        n_comparisons = experiment.n_hypotheses_tested
        adjusted_p = min(raw_p * n_comparisons, 1.0)

        # Minimum effect size check (practical significance)
        min_effect = 0.05  # 5% ROAS improvement minimum
        effect_passes = abs(effect_size) >= min_effect

        passed = adjusted_p < self.alpha and effect_passes

        return GateResult(
            stage="statistical_significance",
            passed=passed,
            statistics={
                "t_statistic": t_stat,
                "raw_p_value": raw_p,
                "adjusted_p_value": adjusted_p,
                "cohens_d": effect_size,
                "treatment_mean": statistics.mean(treatment),
                "control_mean": statistics.mean(control),
                "n_treatment": len(treatment),
                "n_control": len(control),
            },
            thresholds={
                "p_value": self.alpha,
                "effect_size": min_effect
            }
        )

    def _cohens_d(self, treatment: list, control: list) -> float:
        """Calculate Cohen's d effect size."""
        n1, n2 = len(treatment), len(control)
        var1 = statistics.variance(treatment)
        var2 = statistics.variance(control)

        pooled_std = sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))

        return (statistics.mean(treatment) - statistics.mean(control)) / pooled_std
```

---

## 4. Stage 4: Replication Check

```python
class ReplicationChecker:
    """
    Stage 4: Effect must replicate in 2+ segments and 2+ time periods.
    """

    def __init__(self, min_segments: int = 2, min_periods: int = 2):
        self.min_segments = min_segments
        self.min_periods = min_periods

    async def check(self, experiment: Experiment) -> GateResult:
        """
        Check replication across segments and time periods.
        """
        # Segment analysis
        segment_results = self._analyze_by_segment(experiment)
        significant_segments = [
            s for s in segment_results
            if s.effect_size > 0.05 and s.p_value < 0.05
        ]

        # Time period analysis
        period_results = self._analyze_by_period(experiment)
        significant_periods = [
            p for p in period_results
            if p.effect_size > 0.05 and p.p_value < 0.05
        ]

        replication_passes = (
            len(significant_segments) >= self.min_segments and
            len(significant_periods) >= self.min_periods
        )

        return GateResult(
            stage="replication_check",
            passed=replication_passes,
            segment_results=segment_results,
            period_results=period_results,
            summary={
                "significant_segments": len(significant_segments),
                "required_segments": self.min_segments,
                "significant_periods": len(significant_periods),
                "required_periods": self.min_periods,
            }
        )

    def _analyze_by_segment(
        self,
        experiment: Experiment
    ) -> list[SegmentResult]:
        """Analyze effect by audience segment."""
        results = []

        for segment_id, segment_data in experiment.by_segment.items():
            treatment = segment_data.treatment_outcomes
            control = segment_data.control_outcomes

            if len(treatment) < 10 or len(control) < 10:
                continue

            t_stat, p_value = ttest_ind(treatment, control)
            effect_size = self._cohens_d(treatment, control)

            results.append(SegmentResult(
                segment_id=segment_id,
                segment_name=segment_data.name,
                effect_size=effect_size,
                p_value=p_value,
                n_treatment=len(treatment),
                n_control=len(control),
                is_significant=p_value < 0.05 and abs(effect_size) > 0.05
            ))

        return results
```

---

## 5. Stage 5: Human Review

```python
class HumanReviewGate:
    """
    Stage 5: Human reviews and approves the model update.
    """

    async def check(self, validation_report: ValidationReport) -> GateResult:
        """
        Submit for human review via Slack.
        """
        # Generate review message
        message = self._build_review_message(validation_report)

        # Send to Slack
        review_request = await self.slack.send_approval_request(
            channel="#mais-reviews",
            message=message,
            blocks=self._format_blocks(validation_report)
        )

        # Wait for response (timeout: 4 hours)
        response = await self._wait_for_response(
            review_request.id,
            timeout=4 * 3600
        )

        if response.approved:
            return GateResult(
                stage="human_review",
                passed=True,
                reviewer=response.reviewer,
                approved_at=response.timestamp
            )
        else:
            return GateResult(
                stage="human_review",
                passed=False,
                rejection_reason=response.reason,
                reviewer=response.reviewer
            )

    def _build_review_message(self, report: ValidationReport) -> str:
        """Build Slack message for human review."""
        return f"""
*MAIS Model Update — Requires Your Approval*

*What changed:* {report.what_changed}
*Why:* {report.why_changed}

*Evidence Summary:*
• p-value: {report.statistics['adjusted_p_value']:.4f} (threshold: 0.05)
• Effect size (Cohen's d): {report.statistics['cohens_d']:.3f}
• Replicated in: {report.summary['significant_segments']} segments (need 2+)
• Time periods: {report.summary['significant_periods']} (need 2+)

*Confounders detected:* {len(report.confounds)}

*Risk assessment:*
• Risk if approved: {report.risk_if_approved}
• Risk if rejected: {report.risk_if_rejected}

*Next steps if approved:*
1. Shadow deploy (7 days monitoring)
2. Canary deploy (14 days at 10% traffic)
3. Full rollout

Actions:
`/mais approve {report.id}` — Approve for shadow deploy
`/mais reject {report.id}` — Reject with reason
`/mais modify {report.id}` — Request changes
        """
```

---

## 6. Stage 6: Shadow Deploy

```python
class ShadowDeploy:
    """
    Stage 6: Run new model in shadow mode for 7 days.
    All decisions logged but NOT executed.
    """

    DURATION_DAYS = 7
    SHADOW_TRAFFIC_PCT = 0  # Shadow = 0% actual traffic

    def __init__(self):
        self.monitoring_metrics = {
            "error_rate": 0.05,      # Max 5% error rate
            "p99_latency_ms": 2000,   # Max 2s p99 latency
            "budget_drift": 0.02,     # Max 2% budget overage
        }

    async def run(self, model_update: ModelUpdate) -> ShadowResult:
        """
        Run shadow deploy for 7 days.
        """
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(days=self.DURATION_DAYS)

        # Enable shadow mode
        await self.model_loader.enable_shadow_mode(model_update)

        # Collect metrics
        metrics = await self._collect_shadow_metrics(
            model_update.id,
            start_time,
            end_time
        )

        # Evaluate against thresholds
        passed = self._evaluate_shadow_metrics(metrics)

        # Log results
        shadow_result = ShadowResult(
            model_update_id=model_update.id,
            start_time=start_time,
            end_time=end_time,
            passed=passed,
            metrics=metrics,
            recommendations=self._generate_recommendations(metrics)
        )

        await self._log_shadow_result(shadow_result)

        # Disable shadow mode
        await self.model_loader.disable_shadow_mode()

        return shadow_result

    def _evaluate_shadow_metrics(self, metrics: ShadowMetrics) -> bool:
        """Check if shadow metrics are within thresholds."""
        checks = {
            "error_rate": metrics.error_rate <= self.monitoring_metrics["error_rate"],
            "latency": metrics.p99_latency_ms <= self.monitoring_metrics["p99_latency_ms"],
            "budget": metrics.budget_drift <= self.monitoring_metrics["budget_drift"],
        }

        return all(checks.values())
```

---

## 7. Stage 7: Canary Deploy

```python
class CanaryDeploy:
    """
    Stage 7: Deploy to 10% traffic for 14 days.
    Full rollback if ROAS drops > 5% or errors spike.
    """

    DURATION_DAYS = 14
    CANARY_TRAFFIC_PCT = 0.10  # 10% of traffic

    ROLLBACK_TRIGGERS = {
        "roas_drop": 0.05,        # > 5% ROAS drop → rollback
        "error_rate_increase": 0.05,  # > 5% error increase → rollback
        "p99_latency_increase": 1.5,  # 1.5x latency increase → rollback
    }

    def __init__(self):
        self.monitoring_metrics = {
            "roas_drop_threshold": self.ROLLBACK_TRIGGERS["roas_drop"],
            "error_rate_threshold": self.ROLLBACK_TRIGGERS["error_rate_increase"],
            "latency_threshold": self.ROLLBACK_TRIGGERS["p99_latency_increase"],
        }

    async def run(self, model_update: ModelUpdate) -> CanaryResult:
        """
        Run canary deploy at 10% traffic for 14 days.
        """
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(days=self.DURATION_DAYS)

        # Get baseline metrics (last 30 days before canary)
        baseline = await self._get_baseline_metrics(
            start_time - timedelta(days=30),
            start_time
        )

        # Enable canary at 10% traffic
        await self.traffic_splitter.set_canary_split(
            model_id=model_update.id,
            canary_pct=self.CANARY_TRAFFIC_PCT
        )

        # Collect canary metrics
        canary_metrics = await self._collect_canary_metrics(
            model_update.id,
            start_time,
            end_time
        )

        # Compare to baseline
        comparison = self._compare_to_baseline(canary_metrics, baseline)

        # Check rollback triggers
        should_rollback = self._check_rollback_triggers(
            comparison,
            baseline
        )

        if should_rollback:
            await self._rollback(model_update)
            return CanaryResult(
                status="rolled_back",
                reason=should_rollback.reason,
                metrics=comparison
            )

        # Canary passed
        await self._promote_to_full(model_update)

        return CanaryResult(
            status="promoted",
            metrics=comparison,
            duration_days=self.DURATION_DAYS
        )

    def _check_rollback_triggers(
        self,
        comparison: MetricsComparison,
        baseline: BaselineMetrics
    ) -> RollbackDecision | None:
        """Check if any rollback trigger is hit."""
        # ROAS check
        if comparison.roas_pct_change < -self.ROLLBACK_TRIGGERS["roas_drop"]:
            return RollbackDecision(
                triggered=True,
                reason=f"ROAS dropped {comparison.roas_pct_change:.1%} (threshold: -{self.ROLLBACK_TRIGGERS['roas_drop']:.1%})"
            )

        # Error rate check
        if comparison.error_rate_increase > self.ROLLBACK_TRIGGERS["error_rate_increase"]:
            return RollbackDecision(
                triggered=True,
                reason=f"Error rate increased {comparison.error_rate_increase:.1%} (threshold: +{self.ROLLBACK_TRIGGERS['error_rate_increase']:.1%})"
            )

        # Latency check
        if comparison.latency_increase_factor > self.ROLLBACK_TRIGGERS["p99_latency_increase"]:
            return RollbackDecision(
                triggered=True,
                reason=f"p99 latency increased {comparison.latency_increase_factor:.1f}x (threshold: {self.ROLLBACK_TRIGGERS['p99_latency_increase']}x)"
            )

        return None
```

---

## 8. Rollback System

```python
class RollbackSystem:
    """
    Handles automatic and manual rollbacks.
    """

    async def rollback(self, model_update_id: str, reason: str):
        """
        Rollback a model update to previous version.
        """
        # 1. Switch traffic to old model
        await self.traffic_splitter.set_primary_only()

        # 2. Archive new model (don't delete)
        await self.model_store.archive(model_update_id)

        # 3. Restore previous model weights
        previous_version = await self.model_store.get_previous_version(
            model_update_id
        )
        await self.model_loader.load(previous_version)

        # 4. Notify humans
        await self.notification.send_rollback_alert(
            model_update_id=model_update_id,
            reason=reason
        )

        # 5. Log to audit trail
        await self.audit_log.record(
            action="rollback",
            model_update_id=model_update_id,
            reason=reason,
            timestamp=datetime.utcnow()
        )
```

---

## 9. Full Pipeline Orchestration

```python
class ValidationPipeline:
    """
    Orchestrates all 7 validation stages.
    """

    def __init__(
        self,
        data_quality_gate: DataQualityGate,
        confound_detector: ConfoundDetector,
        significance_checker: SignificanceChecker,
        replication_checker: ReplicationChecker,
        human_review_gate: HumanReviewGate,
        shadow_deploy: ShadowDeploy,
        canary_deploy: CanaryDeploy,
        rollback_system: RollbackSystem,
    ):
        self.gates = [
            data_quality_gate,
            confound_detector,
            significance_checker,
            replication_checker,
            human_review_gate,
            shadow_deploy,
            canary_deploy,
        ]
        self.rollback_system = rollback_system

    async def run(self, experiment: Experiment) -> PipelineResult:
        """
        Run full validation pipeline.
        """
        results = []
        current_experiment = experiment

        for gate in self.gates:
            result = await gate.check(current_experiment)
            results.append(result)

            if not result.passed:
                return PipelineResult(
                    passed=False,
                    failed_at=gate.__class__.__name__,
                    results=results,
                    stage_results={g.__class__.__name__: r for g, r in results}
                )

            # Update experiment context for next gate
            current_experiment = self._update_context(current_experiment, result)

        return PipelineResult(
            passed=True,
            results=results,
            stage_results={g.__class__.__name__: r for g, r in results}
        )
```
