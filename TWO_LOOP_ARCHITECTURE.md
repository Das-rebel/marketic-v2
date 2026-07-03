# Two-Loop Architecture — Inner + Outer

**Related to:** ARCHITECTURE.md Section 3

---

## Overview

The two-loop architecture separates **fast observation** (what happened?) from **slow deliberation** (what does it mean?).

```
┌─────────────────────────────────────────────────────────────────┐
│                    TWO-LOOP ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                 OUTER LOOP (Monthly)                       │  │
│  │  ─── What does it all mean?                             │  │
│  │  ─── Which patterns are real?                           │  │
│  │  ─── What should we change?                            │  │
│  │  ─── Who approved the last model update?                │  │
│  │                                                           │  │
│  │  Frequency: First Monday of each month                 │  │
│  │  OR when inner loop queue > 20 high-confidence items    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↑                                  │
│                              │ Hypotheses queue                  │
│                              │                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                 INNER LOOP (Daily + Weekly)             │  │
│  │                                                           │  │
│  │  DAILY (06:00 UTC) — Fast SPC monitoring                 │  │
│  │  ─── What's happening today?                            │  │
│  │  ─── Any immediate anomalies?                          │  │
│  │  ─── Queue quick hypotheses                            │  │
│  │                                                           │  │
│  │  WEEKLY (Monday 06:00 UTC) — Deep analysis              │  │
│  │  ─── Week-over-week trends                            │  │
│  │  ─── Segment-level patterns                           │  │
│  │  ─── Creative fatigue detection                      │  │
│  │  ─── Competitor movement analysis                     │  │
│  │                                                           │  │
│  │  CANNOT: Change models, change budget, post content    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↑                                  │
│                              │ Data ingestion                  │
│                              │                                 │
│                         DATA SOURCES                            │
│              (Ad platforms, analytics, market intel)           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Inner Loop (Daily + Weekly)

The inner loop operates at TWO timescales:

- **Daily** (06:00 UTC): Fast SPC monitoring, quick anomaly detection
- **Weekly** (Monday 06:00 UTC): Deep analysis, week-over-week trends, segment patterns

### 1.1 Daily Loop

```python
class InnerLoop:
    """
    Daily: Observe, flag, hypothesize. NO model changes.
    """

    DAILY_CRON = "0 6 * * *"  # 06:00 UTC daily

    async def run(self, date: date) -> DailyBrief:
        """
        Main inner loop entry point.
        """
        # 1. Collect yesterday's performance data
        metrics = await self._collect_daily_metrics(date)

        # 2. Statistical process control
        anomalies = self._run_spc(metrics)

        # 3. Generate hypothesis candidates
        hypotheses = await self._generate_hypotheses(anomalies, metrics)

        # 4. Score and queue promising ones
        queued = self._score_and_queue(hypotheses)

        # 5. Update daily brief
        brief = DailyBrief(
            date=date,
            metrics=metrics,
            anomalies=anomalies,
            new_hypotheses=len(queued),
            queue_depth=self._get_queue_depth(),
            status="healthy" if not anomalies.flags else "attention_needed"
        )

        await self._publish_daily_brief(brief)
        return brief
```

### 1.2 Statistical Process Control (SPC)

```python
class SPCMonitor:
    """
    Exponentially Weighted Moving Average (EWMA) chart.
    Flags when ROAS deviates > 2σ from rolling mean.
    """

    def __init__(self, lambda_weight: float = 0.3, sigma_limit: float = 2.0):
        self.lambda_weight = lambda_weight  # Smoothing factor
        self.sigma_limit = sigma_limit    # Trigger threshold

    def update(self, new_value: float) -> SPCResult:
        """
        Update EWMA chart with new daily ROAS.
        Returns anomaly flags if triggered.
        """
        # Update EWMA
        if self.ewma is None:
            self.ewma = new_value
            self.variance = 0
        else:
            self.ewma = (self.lambda_weight * new_value +
                        (1 - self.lambda_weight) * self.ewma)

            # Update variance (Exponentially Weighted)
            self.variance = (self.lambda_weight *
                           (new_value - self.ewma)**2 +
                           (1 - self.lambda_weight) * self.variance)

        std_dev = sqrt(self.variance)
        z_score = (new_value - self.ewma) / std_dev if std_dev > 0 else 0

        is_anomaly = abs(z_score) > self.sigma_limit

        return SPCResult(
            date=self.current_date,
            raw_value=new_value,
            ewma=self.ewma,
            z_score=z_score,
            is_anomaly=is_anomaly,
            flags=self._interpret_flags(z_score)
        )

    def _interpret_flags(self, z_score: float) -> list[str]:
        """Interpret what the SPC signal means."""
        flags = []
        if z_score > self.sigma_limit:
            flags.append("ROAS_ABOVE_EXPECTED")
        elif z_score < -self.sigma_limit:
            flags.append("ROAS_BELOW_EXPECTED")
        if abs(z_score) > 3:
            flags.append("EXTREME_DEVIATION")

        # Consecutive violations (Western Electric rules)
        self.violation_history.append(z_score)
        if len(self.violation_history) >= 4:
            if all(abs(z) > 1 for z in self.violation_history[-4:]):
                flags.append("CONSECUTIVE_DEVIATION")
        return flags
```

### 1.3 Hypothesis Generation

```python
class HypothesisGenerator:
    """
    Generates hypothesis candidates from anomalies and patterns.
    Does NOT update models. Just queues for outer loop review.
    """

    async def generate(
        self,
        spc_results: list[SPCResult],
        metrics: DailyMetrics
    ) -> list[Hypothesis]:
        """
        Generate hypothesis candidates from daily observations.
        """
        hypotheses = []

        # 1. SPC-triggered hypotheses
        for spc in spc_results:
            if spc.is_anomaly:
                hypotheses.append(
                    await self._hypothesis_from_spc_anomaly(spc, metrics)
                )

        # 2. Trend hypotheses
        trend = self._detect_trend(metrics.time_series)
        if trend:
            hypotheses.append(await self._hypothesis_from_trend(trend, metrics))

        # 3. Audience performance hypotheses
        audience_results = self._analyze_audience_performance(metrics)
        for audience in audience_results.underperformers:
            hypotheses.append(
                await self._hypothesis_audience_gap(audience, metrics)
            )

        # 4. Creative fatigue hypotheses
        fatigue = self._detect_fatigue(metrics.creative_performance)
        if fatigue.detected:
            hypotheses.append(
                await self._hypothesis_fatigue(fatigue, metrics)
            )

        return hypotheses

    async def _hypothesis_from_spc_anomaly(
        self,
        spc: SPCResult,
        metrics: DailyMetrics
    ) -> Hypothesis:
        """
        Hypothesis: "ROAS dropped X% for [campaign] on [platform]"
        """
        # Root cause analysis
        causal_chain = await self._traverse_causal_chain(
            metrics.campaign_id,
            start_date=metrics.date - timedelta(days=7),
            end_date=metrics.date
        )

        # Generate candidate explanations
        explanations = await self._llm_reason(
            prompt=f"""Given this ROAS anomaly for campaign {metrics.campaign_id}:
            - ROAS dropped from {spc.ewma:.2f} to {spc.raw_value:.2f}
            - Z-score: {spc.z_score:.2f}
            - Platform: {metrics.platform}
            - Audience: {metrics.audience}

            What are the 3 most likely causes?
            Format: [cause] | [confidence 0-1] | [how to validate]
            """
        )

        # Score confidence
        confidence = self._score_confidence(
            z_score=abs(spc.z_score),
            data_quality=metrics.data_quality_score,
            replication_count=causal_chain.replication_count
        )

        return Hypothesis(
            id=generate_uuid(),
            type="spc_anomaly",
            description=f"ROAS anomaly: {spc.flags}",
            confidence=confidence,
            causal_chain=causal_chain,
            candidate_explanations=explanations,
            created_at=datetime.utcnow(),
            status="pending",
            priority=self._priority_from_confidence(confidence)
        )
```

### 1.4 Queue Management

```python
class HypothesisQueue:
    """
    Priority queue for hypothesis candidates.
    Triggers outer loop when threshold reached.
    """

    def __init__(self, max_queue: int = 20, min_confidence: float = 0.6):
        self.queue = []
        self.max_queue = max_queue
        self.min_confidence = min_confidence

    def add(self, hypothesis: Hypothesis):
        """Add hypothesis to queue if confidence sufficient."""
        if hypothesis.confidence >= self.min_confidence:
            heapq.heappush(self.queue, (-hypothesis.confidence, hypothesis))
            self._check_trigger()

    def _check_trigger(self):
        """
        Trigger outer loop if queue is full or high-confidence threshold.
        """
        high_confidence_count = sum(
            1 for _, h in self.queue if h.confidence > 0.75
        )

        if len(self.queue) >= self.max_queue:
            self._trigger_outer_loop("queue_full")

        elif high_confidence_count >= 5:
            self._trigger_outer_loop("high_confidence_threshold")

    async def _trigger_outer_loop(self, reason: str):
        """
        Notify outer loop to run synthesis.
        """
        await send_to_outer_loop(
            reason=reason,
            queue_depth=len(self.queue),
            avg_confidence=self._avg_confidence(),
            top_hypotheses=self.queue[:5]
        )

### 1.5 Weekly Loop

```python
class WeeklyInnerLoop:
    """
    Weekly: Deep analysis, week-over-week trends, segment patterns.
    Runs every Monday at 06:00 UTC.
    """

    WEEKLY_CRON = "0 6 * * 1"  # Monday 06:00 UTC

    async def run(self, week_start: date, week_end: date) -> WeeklyBrief:
        """
        Main weekly inner loop entry point.
        """
        # 1. Collect week's data
        metrics = await self._collect_weekly_metrics(week_start, week_end)

        # 2. Week-over-week analysis
        wow_analysis = self._analyze_week_over_week(metrics)

        # 3. Segment-level deep dive
        segment_analysis = await self._analyze_segments(metrics)

        # 4. Creative fatigue detection
        fatigue_report = self._detect_creative_fatigue(metrics)

        # 5. Competitor movement (weekly cadence)
        competitor_moves = await self._analyze_competitor_movement(week_start, week_end)

        # 6. Generate strategic hypotheses
        hypotheses = await self._generate_strategic_hypotheses(
            wow_analysis, segment_analysis, fatigue_report, competitor_moves
        )

        # 7. Queue high-confidence hypotheses
        queued = self._queue_hypotheses(hypotheses)

        # 8. Publish weekly brief
        brief = WeeklyBrief(
            week_start=week_start,
            week_end=week_end,
            wow_roas_change=wow_analysis.roas_change_pct,
            segment_winners=segment_analysis.top_segments,
            segment_losers=segment_analysis.bottom_segments,
            fatigue_alerts=fatigue_report.alerts,
            competitor_moves=competitor_moves,
            new_hypotheses=len(queued),
            queue_depth=self._get_queue_depth(),
            status=self._assess_status(wow_analysis, segment_analysis, fatigue_report)
        )

        await self._publish_weekly_brief(brief)
        return brief

    def _analyze_week_over_week(self, metrics: WeeklyMetrics) -> WOWAnalysis:
        """
        Compare this week to last week across key metrics.
        """
        return WOWAnalysis(
            roas_change_pct=metrics.this_week_avg_roas / metrics.last_week_avg_roas - 1,
            spend_change_pct=metrics.this_week_spend / metrics.last_week_spend - 1,
            conversion_change_pct=metrics.this_week_conversions / metrics.last_week_conversions - 1,
            impressions_change_pct=metrics.this_week_impressions / metrics.last_week_impressions - 1,
            ctr_change_pct=metrics.this_week_ctr / metrics.last_week_ctr - 1,
            significant_changes=self._flag_significant_changes(metrics),
            trend_direction=self._determine_trend(metrics)
        )

    async def _analyze_segments(self, metrics: WeeklyMetrics) -> SegmentAnalysis:
        """
        Deep dive into audience segment performance.
        """
        segment_results = {}

        for segment_id, segment_data in metrics.by_segment.items():
            # Week-over-week for this segment
            wow_roas = segment_data.this_week_roas / segment_data.last_week_roas - 1
            wow_spend = segment_data.this_week_spend / segment_data.last_week_spend - 1

            # Efficiency: ROAS per dollar spent
            efficiency = segment_data.this_week_roas / segment_data.this_week_spend

            segment_results[segment_id] = SegmentResult(
                segment_id=segment_id,
                segment_name=segment_data.name,
                this_week_roas=segment_data.this_week_roas,
                last_week_roas=segment_data.last_week_roas,
                wow_roas_change=wow_roas,
                wow_spend_change=wow_spend,
                efficiency_score=efficiency,
                conversions=segment_data.this_week_conversions,
                avg_cpa=segment_data.this_week_spend / segment_data.this_week_conversions
            )

        # Rank segments
        sorted_segments = sorted(
            segment_results.values(),
            key=lambda s: s.wow_roas_change
        )

        return SegmentAnalysis(
            top_segments=sorted_segments[-3:],      # Top 3 by ROAS improvement
            bottom_segments=sorted_segments[:3],     # Bottom 3 by ROAS improvement
            all_segments=segment_results,
            recommendation=self._generate_segment_recommendations(sorted_segments)
        )

    def _detect_creative_fatigue(self, metrics: WeeklyMetrics) -> FatigueReport:
        """
        Detect creative fatigue using CTR decay and engagement metrics.
        """
        alerts = []

        for creative_id, creative_data in metrics.by_creative.items():
            # Check CTR trend over 4+ weeks
            if len(creative_data.ctr_history) >= 4:
                ctr_trend = self._calculate_trend(creative_data.ctr_history)

                # If CTR is declining > 15% over 4 weeks
                if ctr_trend.slope < -0.15:
                    alerts.append(FatigueAlert(
                        creative_id=creative_id,
                        creative_name=creative_data.name,
                        ctr_decline_pct=abs(ctr_trend.slope) * 100,
                        weeks_underperforming=ctr_trend.weeks_declining,
                        recommendation="Refresh creative or pause",
                        urgency="high" if ctr_trend.slope < -0.25 else "medium"
                    ))

            # Check frequency saturation
            if creative_data.avg_frequency > 5:
                alerts.append(FatigueAlert(
                    creative_id=creative_id,
                    creative_name=creative_data.name,
                    avg_frequency=creative_data.avg_frequency,
                    recommendation="Reduce frequency cap",
                    urgency="medium"
                ))

        return FatigueReport(
            detected=len(alerts) > 0,
            alerts=alerts,
            overall_fatigue_score=self._calculate_fatigue_score(alerts)
        )

    async def _analyze_competitor_movement(
        self,
        week_start: date,
        week_end: date
    ) -> CompetitorMoves:
        """
        Analyze competitor activity over the week.
        """
        # Fetch competitor ad intelligence
        competitor_ads = await self.competitor_intel.get_ads(
            start_date=week_start,
            end_date=week_end
        )

        moves = []
        for competitor_id, ads in competitor_ads.items():
            new_ads = [a for a in ads if a.first_seen >= week_start]
            if new_ads:
                moves.append(CompetitorMove(
                    competitor_id=competitor_id,
                    competitor_name=competitor_ads[competitor_id].name,
                    new_ad_count=len(new_ads),
                    themes=self._extract_themes(new_ads),
                    sentiment=self._analyze_sentiment(new_ads),
                    positioning_change=self._detect_positioning_change(competitor_id),
                    spend_estimate=self._estimate_spend(ads)
                ))

        return CompetitorMoves(
            week_start=week_start,
            week_end=week_end,
            active_movers=moves,
            market_sentiment=self._aggregate_market_sentiment(moves)
        )

---

## 2. Outer Loop (Monthly)

### 2.1 What It Does

```python
class OuterLoop:
    """
    Monthly: Synthesize, validate, authorize updates.
    Human approval required for any model change.
    """

    OUTER_CRON = "0 8 1-7 * 1"  # First Monday of month, 08:00 UTC

    async def run(self) -> OuterLoopResult:
        """
        Main outer loop entry point.
        """
        # 1. Collect hypotheses from inner loop queue
        hypotheses = await self._drain_hypothesis_queue()

        # 2. Group into strategic themes
        themes = self._group_into_themes(hypotheses)

        # 3. Validate each theme statistically
        validated = []
        for theme in themes:
            validation = await self._validate_theme(theme)
            if validation.passed:
                validated.append(validation)

        # 4. Generate model update proposals
        proposals = []
        for validation in validated:
            if validation.requires_model_update:
                proposal = await self._generate_proposal(validation)
                proposals.append(proposal)

        # 5. Submit for human review
        for proposal in proposals:
            await self._submit_for_human_review(proposal)

        return OuterLoopResult(
            themes_reviewed=len(themes),
            validated=len(validated),
            proposals_submitted=len(proposals),
            requires_human_action=True
        )
```

### 2.2 Theme Synthesis

```python
class ThemeSynthesizer:
    """
    Groups related hypotheses into strategic themes.
    E.g., "Engineering persona underpriced" ← 7 individual hypotheses.
    """

    def _group_into_themes(self, hypotheses: list[Hypothesis]) -> list[Theme]:
        """
        Cluster hypotheses into themes using vector similarity.
        """
        # Embed hypothesis descriptions
        embeddings = self._embed_hypotheses([h.description for h in hypotheses])

        # Cluster using DBSCAN
        clusters = self._dbscan(embeddings, eps=0.3, min_samples=2)

        themes = []
        for cluster_id, hypothesis_ids in clusters.items():
            cluster_hypotheses = [h for h in hypotheses if h.id in hypothesis_ids]

            theme = Theme(
                id=generate_uuid(),
                name=self._name_theme(cluster_hypotheses),
                hypotheses=cluster_hypotheses,
                aggregate_confidence=self._mean_confidence(cluster_hypotheses),
                span=self._date_range(cluster_hypotheses),
                evidence_strength=self._evidence_strength(cluster_hypotheses)
            )
            themes.append(theme)

        return sorted(themes, key=lambda t: t.evidence_strength, reverse=True)

    def _evidence_strength(self, theme: Theme) -> float:
        """
        Composite score of theme robustness.
        """
        confidence_score = theme.aggregate_confidence
        replication_score = min(len(theme.hypotheses) / 10, 1.0)  # Cap at 10 hyps
        consistency_score = self._temporal_consistency(theme)
        effect_size_score = self._mean_effect_size(theme.hypotheses)

        return (
            0.4 * confidence_score +
            0.2 * replication_score +
            0.2 * consistency_score +
            0.2 * effect_size_score
        )
```

### 2.3 Validation

```python
class ThemeValidator:
    """
    Validates a strategic theme against statistical significance gate.
    ALL criteria must pass for model update authorization.
    """

    async def validate(self, theme: Theme) -> ValidationResult:
        """
        Run full statistical significance pipeline on a theme.
        """
        results = {}

        # 1. Effect size
        results["effect_size"] = self._check_effect_size(theme)
        if not results["effect_size"].passed:
            return ValidationResult(passed=False, results=results, reason="Effect size too small")

        # 2. Statistical significance
        results["significance"] = self._check_significance(theme)
        if not results["significance"].passed:
            return ValidationResult(passed=False, results=results, reason="Not statistically significant")

        # 3. Replication across segments
        results["replication"] = self._check_replication(theme)
        if not results["replication"].passed:
            return ValidationResult(passed=False, results=results, reason="Failed to replicate across segments")

        # 4. Persistence
        results["persistence"] = self._check_persistence(theme)
        if not results["persistence"].passed:
            return ValidationResult(passed=False, results=results, reason="Effect did not persist")

        # 5. No confounds
        results["confounds"] = self._check_confounds(theme)
        if not results["confounds"].passed:
            return ValidationResult(passed=False, results=results, reason="Confounding variables present")

        return ValidationResult(passed=True, results=results, reason="All gates passed")

    def _check_significance(self, theme: Theme) -> CheckResult:
        """
        T-test on denoised ROAS distributions with BH correction.
        """
        # Collect all paired observations
        treatment = []  # Denoised ROAS for theme-active periods
        control = []   # Denoised ROAS for non-active periods

        for hypothesis in theme.hypotheses:
            treatment.extend(hypothesis.outcomes.treatment)
            control.extend(hypothesis.outcomes.control)

        # T-test
        t_stat, p_value = ttest_ind(treatment, control)

        # Benjamini-Hochberg correction
        n_comparisons = len(theme.hypotheses)
        adjusted_p = min(p_value * n_comparisons, 1.0)

        return CheckResult(
            passed=adjusted_p < 0.05,
            metric="p_value",
            value=adjusted_p,
            threshold=0.05,
            details={
                "raw_p": p_value,
                "n_comparisons": n_comparisons,
                "treatment_n": len(treatment),
                "control_n": len(control),
                "treatment_mean": mean(treatment),
                "control_mean": mean(control)
            }
        )

    def _check_replication(self, theme: Theme) -> CheckResult:
        """
        Effect must replicate in 2+ distinct audience segments.
        """
        segment_results = {}
        for hypothesis in theme.hypotheses:
            for segment_id, segment_result in hypothesis.by_segment.items():
                if segment_id not in segment_results:
                    segment_results[segment_id] = []
                segment_results[segment_id].append(segment_result)

        # Check each segment
        significant_segments = 0
        for segment_id, results in segment_results.items():
            avg_effect = mean(results)
            if avg_effect > 0.05:  # Positive effect in this segment
                significant_segments += 1

        return CheckResult(
            passed=significant_segments >= 2,
            metric="replicating_segments",
            value=significant_segments,
            threshold=2,
            details={"segment_breakdown": segment_results}
        )
```

---

## 3. Human Approval Flow

### 3.1 When Human Is Required

```
┌─────────────────────────────────────────────────────────────────┐
│                    DECISION AUTHORITY MATRIX                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  OUTER LOOP ACTIONS REQUIRING HUMAN:                            │
│  ───────────────────────────────────────────────────────────  │
│  Model weight update                                        │ ✓ Human
│  Budget reallocation > $1000/month cumulative               │ ✓ Human
│  New audience segment targeting                             │ ✓ Human
│  Creative strategy pivot (e.g., switch from features to pain │ ✓ Human
│  Pause active campaign (brand risk)                          │ ✓ Human
│                                                                 │
│  OUTER LOOP ACTIONS NOT REQUIRING HUMAN:                     │
│  ───────────────────────────────────────────────────────────  │
│  Hypothesis synthesis (informational only)                   │ ✗
│  Strategy document update (no model change)                   │ ✗
│  Reporting and dashboards                                    │ ✗
│                                                                 │
│  INNER LOOP ACTIONS REQUIRING HUMAN:                        │
│  ───────────────────────────────────────────────────────────  │
│  Nothing automatically triggers human                          │
│  (Inner loop only observes and queues)                      │
│                                                                 │
│  ROUTING DECISIONS:                                         │
│  ───────────────────────────────────────────────────────────  │
│  Confidence > 0.75, low-stakes                              │ Auto
│  Confidence < 0.75, any stakes                            │ ✓ Human
│  High-stakes (brand, content, legal)                       │ ✓ Human
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Approval UX

```python
class HumanApprovalFlow:
    """
    Slack/Email notification for human review.
    """

    async def submit_proposal(self, proposal: ModelUpdateProposal):
        """
        Submit model update proposal for human review.
        """
        message = f"""
        *MAIS Model Update Proposal* — Requires Your Approval

        *What changed:* {proposal.what_changed}
        *Why:* {proposal.why_changed}
        *Evidence:*
        - p-value: {proposal.p_value:.4f} (threshold: 0.05)
        - Effect size (Cohen's d): {proposal.effect_size:.2f}
        - Replicated in: {proposal.replicated_segments} segments
        - Persistence: {proposal.persistence_days} days

        *Risk assessment:*
        - Risk if approved: {proposal.risk_if_approved}
        - Risk if rejected: {proposal.risk_if_rejected}

        *Rollback procedure:*
        {proposal.rollback_procedure}

        *Affects:* {proposal.affected_campaigns}

        Actions:
        /mais approve {proposal.id} — Deploy after shadow period
        /mais reject {proposal.id} — Cancel, log reason
        /mais modify {proposal.id} — Request changes
        """

        await self.slack.send(
            channel="#mais-approvals",
            message=message,
            blocks=self._format_blocks(proposal),
            callback_id=proposal.id
        )

        # Log submission
        await self._log_submission(proposal)

        # Set escalation timer
        if not await self._wait_for_approval(proposal.id, timeout=4*3600):
            await self._escalate(proposal)
```

---

## 4. Timescales Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                    TIMESCALE REFERENCE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  INNER LOOP (Daily):                                           │
│  ───────────────────────────────────────────────────────────  │
│  06:00 UTC    Collect yesterday's metrics                       │
│  06:30 UTC    Run SPC monitoring                              │
│  07:00 UTC    Generate hypotheses (quick)                     │
│  07:30 UTC    Score and queue                                 │
│  08:00 UTC    Publish daily brief (Slack)                     │
│                                                                 │
│  INNER LOOP (Weekly — Monday):                               │
│  ───────────────────────────────────────────────────────────  │
│  06:00 UTC    Collect week's data                             │
│  06:30 UTC    Week-over-week analysis                         │
│  07:00 UTC    Segment-level deep dive                        │
│  07:30 UTC    Creative fatigue detection                      │
│  08:00 UTC    Competitor movement analysis                    │
│  08:30 UTC    Strategic hypothesis generation                 │
│  09:00 UTC    Queue high-confidence hypotheses                 │
│  09:30 UTC    Publish weekly brief (Slack)                    │
│                                                                 │
│  OUTER LOOP (Monthly):                                        │
│  ───────────────────────────────────────────────────────────  │
│  First Monday   Collect pending hypotheses                      │
│  08:00 UTC    Group into themes                              │
│  09:00 UTC    Run validation pipeline                         │
│  10:00 UTC    Generate model update proposals                 │
│  10:30 UTC    Submit for human review (Slack)                  │
│  D+1 to D+7   Human reviews pending                          │
│  D+7          Shadow deploy begins (7 days)                   │
│  D+14         Canary deploy begins (10% traffic, 14 days)     │
│  D+28         Full rollout OR rollback                         │
│                                                                 │
│  PARAMETERS:                                                  │
│  ───────────────────────────────────────────────────────────  │
│  EWMA λ (smoothing): 0.3                                     │
│  SPC σ limit: 2.0                                             │
│  Min hypothesis confidence: 0.6                                 │
│  Queue trigger (depth): 20                                     │
│  Queue trigger (high-confidence): 5 above 0.75                │
│  Shadow deploy duration: 7 days                                │
│  Canary duration: 14 days (10% traffic)                      │
│  Approval timeout: 4 hours (then escalate)                   │
└─────────────────────────────────────────────────────────────────┘
```
