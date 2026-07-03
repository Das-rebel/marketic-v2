# Test Plan — MAIS 2.0

**Related to:** VALIDATION_PIPELINE.md, SKILLS_ARCHITECTURE.md

---

## Overview

This test plan covers unit tests, integration tests, and chaos engineering for all MAIS components. **All tests must pass before Phase 1 sign-off.**

```
┌─────────────────────────────────────────────────────────────────┐
│                    TEST PYRAMID                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                         ┌───────────┐                          │
│                        │   Chaos   │                          │
│                       │  Tests    │                          │
│                      └──────┬──────┘                          │
│                             │                                  │
│                      ┌──────▼──────┐                          │
│                     │ Integration │                          │
│                     │   Tests     │                          │
│                     └──────┬──────┘                          │
│                             │                                  │
│              ┌─────────────┼─────────────┐                   │
│              │             │             │                    │
│        ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐            │
│       │  Unit     │ │  Unit     │ │  Unit     │            │
│       │  Tests    │ │  Tests    │ │  Tests    │            │
│       │  (Gate 1) │ │  (Gate 2) │ │  (Gate 3) │            │
│       └───────────┘ └───────────┘ └───────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Unit Tests by Component

### 1. DataQualityGate Tests (10 tests)

```python
# tests/unit/test_data_quality_gate.py

class TestDataQualityGate:

    @pytest.mark.asyncio
    async def test_missing_data_under_threshold(self, gate):
        """Missing data < 5% should pass."""
        data = create_dataset(missing_pct=0.03)
        result = await gate.check(data)
        assert result.passed is True

    @pytest.mark.asyncio
    async def test_missing_data_over_threshold(self, gate):
        """Missing data > 5% should fail."""
        data = create_dataset(missing_pct=0.07)
        result = await gate.check(data)
        assert result.passed is False
        assert any(i.check == "missing_data" for i in result.issues)

    @pytest.mark.asyncio
    async def test_outliers_detected(self, gate):
        """Outliers > 1% should warn."""
        data = create_dataset(outlier_pct=0.05)
        result = await gate.check(data)
        assert any(i.check == "outliers" and i.severity == "warning" for i in result.issues)

    @pytest.mark.asyncio
    async def test_insufficient_sample_size(self, gate):
        """Sample size < 100 should fail."""
        data = create_dataset(n_samples=50)
        result = await gate.check(data)
        assert result.passed is False
        assert any(i.check == "sample_size" for i in result.issues)

    @pytest.mark.asyncio
    async def test_sources_disagree(self, gate):
        """Source agreement < 90% should fail."""
        data = create_dataset(source_agreement=0.75)
        result = await gate.check(data)
        assert result.passed is False
        assert any(i.check == "source_agreement" for i in result.issues)

    @pytest.mark.asyncio
    async def test_all_checks_pass(self, gate):
        """Perfect data should pass all checks."""
        data = create_dataset(
            missing_pct=0.01,
            outlier_pct=0.0,
            n_samples=200,
            source_agreement=0.98
        )
        result = await gate.check(data)
        assert result.passed is True
        assert len(result.issues) == 0

    @pytest.mark.asyncio
    async def test_data_quality_score_calculation(self, gate):
        """Quality score should reflect data quality."""
        data = create_dataset(
            missing_pct=0.02,
            outlier_pct=0.005,
            n_samples=150,
            source_agreement=0.95
        )
        result = await gate.check(data)
        assert 0.85 <= result.data_quality_score <= 0.95

    @pytest.mark.asyncio
    async def test_empty_dataset(self, gate):
        """Empty dataset should fail gracefully."""
        data = create_dataset(n_samples=0)
        result = await gate.check(data)
        assert result.passed is False

    @pytest.mark.asyncio
    async def test_all_missing_data(self, gate):
        """100% missing should fail."""
        data = create_dataset(missing_pct=1.0)
        result = await gate.check(data)
        assert result.passed is False

    @pytest.mark.asyncio
    async def test_borderline_threshold(self, gate):
        """Exactly 5% missing should pass (on boundary)."""
        data = create_dataset(missing_pct=0.05)
        result = await gate.check(data)
        assert result.passed is True
```

### 2. ConfoundDetector Tests (15 tests)

```python
# tests/unit/test_confound_detector.py

class TestConfoundDetector:

    @pytest.mark.asyncio
    async def test_day_of_week_detected(self, detector):
        """Day-of-week effect should be detected."""
        data = create_dataset_with_day_of_week_effect()
        result = await detector.check(data)
        assert result.passed is True  # Detected but can adjust
        assert any(c.name == "day_of_week" for c in result.detected_confounds)

    @pytest.mark.asyncio
    async def test_seasonality_detected(self, detector):
        """Month-end spike should be detected."""
        data = create_dataset_with_month_end_spike()
        result = await detector.check(data)
        assert any(c.name == "seasonality" for c in result.detected_confounds)

    @pytest.mark.asyncio
    async def test_competitor_activity_detected(self, detector):
        """Competitor spend spike should be detected."""
        data = create_dataset_with_competitor_activity()
        result = await detector.check(data)
        assert any(c.name == "competitor_activity" for c in result.detected_confounds)

    @pytest.mark.asyncio
    async def test_budget_step_change_detected(self, detector):
        """Budget step change should be detected."""
        data = create_dataset_with_budget_step()
        result = await detector.check(data)
        assert any(c.name == "budget_step_change" for c in result.detected_confounds)

    @pytest.mark.asyncio
    async def test_creative_fatigue_detected(self, detector):
        """CTR decay should be detected."""
        data = create_dataset_with_fatigue()
        result = await detector.check(data)
        assert any(c.name == "creative_fatigue" for c in result.detected_confounds)

    @pytest.mark.asyncio
    async def test_multiple_confounds(self, detector):
        """Multiple confounds should all be detected."""
        data = create_dataset_with_multiple_confounds()
        result = await detector.check(data)
        assert len(result.detected_confounds) >= 2

    @pytest.mark.asyncio
    async def test_no_confounds(self, detector):
        """Clean data should have no confounds."""
        data = create_clean_dataset()
        result = await detector.check(data)
        assert len(result.detected_confounds) == 0

    @pytest.mark.asyncio
    async def test_confound_in_treatment_period_fails(self, detector):
        """Confound overlapping treatment should fail."""
        data = create_dataset_with_treatment_overlap()
        result = await detector.check(data)
        assert result.passed is False

    @pytest.mark.asyncio
    async def test_adjustable_confound_passes(self, detector):
        """Adjustable confound (day-of-week) should pass."""
        data = create_dataset_with_day_of_week_only()
        result = await detector.check(data)
        assert result.passed is True

    @pytest.mark.asyncio
    async def test_non_adjustable_confound_fails(self, detector):
        """Non-adjustable confound should fail."""
        data = create_dataset_with_competitor_activity_only()
        result = await detector.check(data)
        # Competitor is non-adjustable, should fail if in treatment
        assert result.passed is False

    @pytest.mark.asyncio
    async def test_confound_threshold_20_percent(self, detector):
        """Exactly 20% affected should pass."""
        data = create_dataset_with_confound_pct(0.20)
        result = await detector.check(data)
        # On boundary, depends on implementation
        assert isinstance(result.passed, bool)

    @pytest.mark.asyncio
    async def test_confound_19_percent_passes(self, detector):
        """< 20% affected should not be flagged."""
        data = create_dataset_with_confound_pct(0.19)
        result = await detector.check(data)
        confound_names = [c.name for c in result.detected_confounds]
        assert len(confound_names) == 0

    @pytest.mark.asyncio
    async def test_confound_21_percent_fails(self, detector):
        """20%+ affected should be flagged."""
        data = create_dataset_with_confound_pct(0.21)
        result = await detector.check(data)
        assert len(result.detected_confounds) > 0

    @pytest.mark.asyncio
    async def test_treatment_overlap_detection(self, detector):
        """Should detect when confounds overlap treatment window."""
        # This is critical - must prevent learning from confounded data
        ...

    @pytest.mark.asyncio
    async def test_no_treatment_overlap_passes(self, detector):
        """Confounds outside treatment window should pass."""
        ...
```

### 3. SignificanceChecker Tests (8 tests)

```python
# tests/unit/test_significance_checker.py

class TestSignificanceChecker:

    @pytest.mark.asyncio
    async def test_significant_result_passes(self, checker):
        """p < 0.05 should pass."""
        data = create_dataset_with_effect(p_value=0.02)
        result = await checker.check(data)
        assert result.passed is True
        assert result.statistics["adjusted_p_value"] == 0.02

    @pytest.mark.asyncio
    async def test_non_significant_result_fails(self, checker):
        """p > 0.05 should fail."""
        data = create_dataset_with_effect(p_value=0.10)
        result = await checker.check(data)
        assert result.passed is False

    @pytest.mark.asyncio
    async def test_bh_correction_applied(self, checker):
        """Benjamini-Hochberg correction should adjust p-value."""
        # Raw p=0.03 with 10 comparisons should become 0.30
        data = create_dataset_with_effect(p_value=0.03, n_comparisons=10)
        result = await checker.check(data)
        assert result.statistics["adjusted_p_value"] == 0.30
        assert result.passed is False  # 0.30 > 0.05

    @pytest.mark.asyncio
    async def test_bh_correction_identity(self, checker):
        """Single comparison should not change p-value."""
        data = create_dataset_with_effect(p_value=0.03, n_comparisons=1)
        result = await checker.check(data)
        assert result.statistics["adjusted_p_value"] == 0.03
        assert result.passed is True

    @pytest.mark.asyncio
    async def test_effect_size_too_small_fails(self, checker):
        """Cohen's d < 0.05 should fail regardless of p-value."""
        data = create_dataset_with_effect(p_value=0.01, effect_size=0.02)
        result = await checker.check(data)
        assert result.passed is False

    @pytest.mark.asyncio
    async def test_cohens_d_calculation(self, checker):
        """Cohen's d should be calculated correctly."""
        data = create_dataset_with_known_effect(effect_size=0.50)
        result = await checker.check(data)
        assert abs(result.statistics["cohens_d"] - 0.50) < 0.05

    @pytest.mark.asyncio
    async def test_welch_ttest_used(self, checker):
        """Should use Welch's t-test (unequal variances)."""
        # Welch's handles unequal variance better than standard t-test
        ...

    @pytest.mark.asyncio
    async def test_treatment_control_means(self, checker):
        """Should report treatment and control means."""
        data = create_dataset_with_effect()
        result = await checker.check(data)
        assert "treatment_mean" in result.statistics
        assert "control_mean" in result.statistics
        assert result.statistics["treatment_mean"] != result.statistics["control_mean"]
```

### 4. ReplicationChecker Tests (12 tests)

```python
# tests/unit/test_replication_checker.py

class TestReplicationChecker:

    @pytest.mark.asyncio
    async def test_single_segment_fails(self, checker):
        """Only 1 segment should fail replication."""
        data = create_dataset_with_segments(["segment_A"])
        result = await checker.check(data)
        assert result.passed is False

    @pytest.mark.asyncio
    async def test_two_segments_passes(self, checker):
        """Exactly 2 significant segments should pass."""
        data = create_dataset_with_segments(["seg_A", "seg_B"], significant=["seg_A", "seg_B"])
        result = await checker.check(data)
        assert result.passed is True

    @pytest.mark.asyncio
    async def test_two_periods_passes(self, checker):
        """Exactly 2 significant periods should pass."""
        data = create_dataset_with_periods(["week1", "week2"], significant=["week1", "week2"])
        result = await checker.check(data)
        assert result.passed is True

    @pytest.mark.asyncio
    async def test_segments_and_periods_both_required(self, checker):
        """Both segments AND periods must pass."""
        data = create_dataset_with_segments_and_periods(
            segments=["seg_A", "seg_B"],
            periods=["week1", "week2"],
            significant_segments=["seg_A"],
            significant_periods=["week1"]
        )
        result = await checker.check(data)
        assert result.passed is False

    @pytest.mark.asyncio
    async def test_three_segments_one_not_significant(self, checker):
        """3 segments, 2 significant should still pass."""
        data = create_dataset_with_segments(
            ["seg_A", "seg_B", "seg_C"],
            significant=["seg_A", "seg_B"]
        )
        result = await checker.check(data)
        assert result.passed is True

    @pytest.mark.asyncio
    @pytest.mark.parametrize("effect_size,expected_significant", [
        (0.10, False),  # Too small
        (0.15, True),   # Just under threshold
        (0.20, True),   # Above threshold
    ])
    async def test_effect_size_threshold(self, checker, effect_size, expected_significant):
        """Effect size must be > 0.05 for significance."""
        ...

    @pytest.mark.asyncio
    async def test_insufficient_data_per_segment(self, checker):
        """Segments with < 10 samples should be skipped."""
        data = create_dataset_with_segments(["seg_A", "seg_B"], sample_sizes=[5, 100])
        result = await checker.check(data)
        # Should not count seg_A due to insufficient data
        ...

    @pytest.mark.asyncio
    async def test_segment_result_details(self, checker):
        """Should return per-segment results."""
        data = create_dataset_with_segments(["seg_A", "seg_B"])
        result = await checker.check(data)
        assert len(result.segment_results) == 2
        assert all(hasattr(r, "segment_id") for r in result.segment_results)

    @pytest.mark.asyncio
    async def test_period_result_details(self, checker):
        """Should return per-period results."""
        ...

    @pytest.mark.asyncio
    async def test_zero_significant_segments_fails(self, checker):
        """No significant segments should fail."""
        data = create_dataset_with_segments(["seg_A", "seg_B"], significant=[])
        result = await checker.check(data)
        assert result.passed is False

    @pytest.mark.asyncio
    async def test_zero_significant_periods_fails(self, checker):
        """No significant periods should fail."""
        ...
```

---

## Integration Tests

### Happy Path: Dataset → All Gates Pass → Shadow Deploy

```python
# tests/integration/test_happy_path.py

@pytest.mark.asyncio
async def test_full_validation_pipeline_passes():
    """
    Test complete pipeline with clean data.
    All gates should pass → shadow deploy should start.
    """
    # 1. Create clean dataset
    data = create_clean_dataset(
        n_samples=200,
        effect_size=0.30,
        n_segments=3,
        n_periods=2
    )

    # 2. Run validation pipeline
    pipeline = ValidationPipeline()
    result = await pipeline.run(data)

    # 3. Verify
    assert result.passed is True
    assert result.failed_at is None

    # 4. Verify shadow deploy would start
    shadow_result = await ShadowDeploy().run(result.model_update)
    assert shadow_result.passed is True
```

### Confound Path: Day-of-Week Effect → Gate 2 Fails → Abort

```python
# tests/integration/test_confound_abort.py

@pytest.mark.asyncio
async def test_confound_causes_abort():
    """
    Dataset with day-of-week confound overlapping treatment
    should fail at Gate 2 (Confound Detection).
    """
    data = create_dataset_with_day_of_week_confound_overlap()

    pipeline = ValidationPipeline()
    result = await pipeline.run(data)

    assert result.passed is False
    assert result.failed_at == "ConfoundDetector"
    assert result.results["confound_detection"].passed is False
```

### Low Power Path: p=0.08 → Gate 3 Fails → Abort

```python
# tests/integration/test_low_power_abort.py

@pytest.mark.asyncio
async def test_low_power_causes_abort():
    """
    Dataset with p=0.08 should fail at Gate 3 (Significance).
    """
    data = create_dataset_with_effect(p_value=0.08)

    pipeline = ValidationPipeline()
    result = await pipeline.run(data)

    assert result.passed is False
    assert result.failed_at == "SignificanceChecker"
```

### Shadow Fail Path: Latency Spike → Auto-Rollback

```python
# tests/integration/test_shadow_rollback.py

@pytest.mark.asyncio
async def test_shadow_latency_rollback():
    """
    Model that passes validation but fails in shadow (latency 2x)
    should auto-rollback.
    """
    # 1. Create a model that passes validation
    model = create_passing_model()
    model_update = ModelUpdate(model=model)

    # 2. Simulate shadow mode with high latency
    with patch_shadow_latency(2.0):  # 2x baseline
        shadow = ShadowDeploy()
        result = await shadow.run(model_update)

    assert result.passed is False
    assert "latency" in result.recommendations[0].reason.lower()
```

### Canary Rollback: ROAS Drops 7% → Auto-Rollback

```python
# tests/integration/test_canary_rollback.py

@pytest.mark.asyncio
async def test_canary_roas_drop_rollback():
    """
    Canary with ROAS drop > 5% should auto-rollback.
    """
    model = create_passing_model()
    model_update = ModelUpdate(model=model)

    # Simulate 7% ROAS drop
    with patch_canary_roas_change(-0.07):
        canary = CanaryDeploy()
        result = await canary.run(model_update)

    assert result.status == "rolled_back"
    assert "roas" in result.reason.lower()
```

---

## Chaos Engineering Tests

### MCP Connection Drops

```python
# tests/chaos/test_mcp_failure.py

@pytest.mark.asyncio
async def test_mcp_connection_drop_mid_experiment():
    """
    If MCP connection drops during experiment:
    1. Retry 3 times with exponential backoff
    2. If all fail, skip this cycle
    3. Alert human
    4. Do NOT use stale data
    """
    with patch_mcp_connection(drop_after=2):  # Drops on 3rd attempt
        skill = GetCampaignDataSkill()

        # Should retry
        with pytest.raises(RetryExhaustedError):
            await skill.execute(valid_input)

        # Should have logged alert
        assert len(alert_handler.alerts) == 1
        assert alert_handler.alerts[0].severity == "high"

        # Data should NOT be from cache (stale)
        assert not skill.cache.get("campaign_data:test-123")
```

### Human Approval Timeout

```python
# tests/chaos/test_approval_timeout.py

@pytest.mark.asyncio
async def test_human_timeout_escalates():
    """
    If human doesn't respond within 4 hours:
    1. Escalate alert
    2. Auto-pause outer loop
    3. Do NOT proceed without human
    """
    with patch_human_response(delay=5 * 3600):  # 5 hours
        gate = HumanReviewGate()

        result = await gate.check(pending_approval)

        # Should timeout and escalate
        assert result.timed_out is True
        assert result.escalated is True
        assert result.passed is False

        # Should have sent escalation
        assert len(notification_handler.alerts) >= 1
```

### Rollback from Failed Canary

```python
# tests/chaos/test_rollback_from_canary.py

@pytest.mark.asyncio
async def test_rollback_restores_old_model():
    """
    Rollback should:
    1. Restore previous model weights
    2. Switch traffic to old model
    3. Archive new model (don't delete)
    4. Log full audit trail
    """
    # Setup
    old_model = load_model("production-v1")
    new_model = load_model("canary-failed")
    traffic_splitter = TrafficSplitter()

    # Execute rollback
    rollback_system = RollbackSystem()
    await rollback_system.rollback(
        model_update_id="canary-failed-id",
        reason="ROAS dropped 7%"
    )

    # Verify old model restored
    assert traffic_splitter.current_model == old_model
    assert traffic_splitter.current_model != new_model

    # Verify new model archived
    assert model_store.get("canary-failed-id").status == "archived"

    # Verify audit log
    audit_entry = audit_log.get_latest("rollback")
    assert audit_entry.reason == "ROAS dropped 7%"
    assert audit_entry.model_update_id == "canary-failed-id"
```

---

## Expected Results

```
┌─────────────────────────────────────────────────────────────────┐
│                    TEST RESULTS SUMMARY                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  UNIT TESTS:                                                   │
│  ───────────────────────────────────────────────────────────  │
│  DataQualityGate:      10/10 pass ✓                            │
│  ConfoundDetector:     15/15 pass ✓                            │
│  SignificanceChecker:   8/8 pass ✓                            │
│  ReplicationChecker:   12/12 pass ✓                            │
│  ───────────────────────────────────────────────────────────  │
│  Total:              45/45 pass ✓                             │
│                                                                 │
│  INTEGRATION TESTS:                                           │
│  ───────────────────────────────────────────────────────────  │
│  Happy path:          PASS ✓                                   │
│  Confound abort:      PASS ✓                                   │
│  Low power abort:     PASS ✓                                   │
│  Shadow rollback:     PASS ✓                                   │
│  Canary rollback:     PASS ✓                                   │
│  ───────────────────────────────────────────────────────────  │
│  Total:                5/5 pass ✓                             │
│                                                                 │
│  CHAOS TESTS:                                               │
│  ───────────────────────────────────────────────────────────  │
│  MCP drop:            PASS ✓                                   │
│  Human timeout:       PASS ✓                                   │
│  Rollback:            PASS ✓                                   │
│  ───────────────────────────────────────────────────────────  │
│  Total:                3/3 pass ✓                             │
│                                                                 │
│  OVERALL:           53/53 pass ✓                              │
│                                                                 │
│  Phase 1 sign-off: ALL TESTS MUST PASS                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run unit tests only
pytest tests/unit/ -v

# Run integration tests only
pytest tests/integration/ -v

# Run chaos tests only
pytest tests/chaos/ -v

# Run with coverage
pytest tests/ --cov=mais --cov-report=html

# Run specific test file
pytest tests/unit/test_data_quality_gate.py -v

# Run specific test
pytest tests/unit/test_data_quality_gate.py::TestDataQualityGate::test_missing_data_over_threshold -v

# Run with detailed output
pytest tests/ -v -s --tb=long
```
