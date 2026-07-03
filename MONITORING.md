# Monitoring & Observability Framework

**Related to:** ARCHITECTURE.md Section 6, VALIDATION_PIPELINE.md

---

## Overview

MAIS requires comprehensive monitoring across three dimensions: health (is the system running?), performance (is it running well?), and business (is it achieving goals?).

```
┌─────────────────────────────────────────────────────────────────┐
│                    MONITORING PILLARS                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  HEALTH                  PERFORMANCE              BUSINESS         │
│  ───────────────────────────────────────────────────────────  │
│  System uptime           Latency                 ROAS            │
│  Error rates            Throughput              ROAS improvement  │
│  MCP connections        Queue depth             Cost per decision │
│  Data freshness         CPU/Memory              Hypotheses/loop   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Metrics Catalog

### Inner Loop Health

```
┌─────────────────────────────────────────────────────────────────┐
│                    INNER LOOP METRICS                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  SPC ANOMALY DETECTION                                          │
│  ───────────────────────────────────────────────────────────  │
│  spc.anomaly_rate           gauge      # anomalies / total checks │
│                               target: < 5% false positive rate  │
│                                                                 │
│  spc.anomaly_flags         counter    labels: flag_type          │
│                               (ROAS_ABOVE, ROAS_BELOW, EXTREME)  │
│                                                                 │
│  HYPOTHESIS GENERATION                                         │
│  ───────────────────────────────────────────────────────────  │
│  hypothesis.generated      counter    labels: type              │
│  hypothesis.queued         counter    labels: confidence_bucket   │
│                               (low: <0.6, med: 0.6-0.75, high: >0.75) │
│  hypothesis.queue_depth    gauge                                  │
│                               alert: > 15 pending                 │
│                                                                 │
│  hypothesis.latency       histogram   buckets: 1s, 5s, 10s, 30s  │
│                               target: p95 < 30s                  │
│                                                                 │
│  DATA FRESHNESS                                               │
│  ───────────────────────────────────────────────────────────  │
│  data.last_updated        gauge      Unix timestamp             │
│                               alert: > 4 hours ago               │
│  data.quality_score      gauge      0-1                        │
│                               alert: < 0.80                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Outer Loop Health

```
┌─────────────────────────────────────────────────────────────────┐
│                    OUTER LOOP METRICS                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  VALIDATION PIPELINE                                           │
│  ───────────────────────────────────────────────────────────  │
│  validation.gate_passed     counter    labels: gate_name        │
│  validation.gate_failed     counter    labels: gate_name, reason │
│  validation.duration        histogram   buckets: 1m, 5m, 10m, 30m  │
│  validation.queue_depth    gauge                                  │
│                                                                 │
│  GATE-SPECIFIC                                                │
│  ───────────────────────────────────────────────────────────  │
│  gate.data_quality.score   gauge      0-1                      │
│  gate.confounds.detected   counter    labels: confound_type     │
│  gate.significance.p_value gauge      0-1                       │
│  gate.replication.segments gauge                               │
│                                                                 │
│  HUMAN APPROVAL                                                │
│  ───────────────────────────────────────────────────────────  │
│  approval.requested       counter                                │
│  approval.approved        counter                                │
│  approval.rejected        counter                                │
│  approval.timeout         counter                                │
│  approval.latency         histogram   buckets: 1h, 2h, 4h, 24h  │
│                               alert: > 10% timeout rate          │
│                                                                 │
│  MODEL UPDATES                                                │
│  ───────────────────────────────────────────────────────────  │
│  model_update.submitted    counter                                │
│  model_update.approved     counter                                │
│  model_update.rejected     counter                                │
│  model_update.deployed     counter                                │
│  model_update.rollbacked  counter                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Production Health

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRODUCTION METRICS                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  SHADOW DEPLOY                                                │
│  ───────────────────────────────────────────────────────────  │
│  shadow.error_rate         gauge      0-1                      │
│                               alert: > 5%                       │
│  shadow.latency_p99        gauge      milliseconds              │
│                               alert: > 2000ms                   │
│  shadow.budget_drift       gauge      0-1 (drift from plan)    │
│                               alert: > 2%                      │
│                                                                 │
│  CANARY DEPLOY                                                │
│  ───────────────────────────────────────────────────────────  │
│  canary.roas_change        gauge      relative change           │
│                               alert: < -5%                     │
│  canary.error_rate         gauge      0-1                      │
│  canary.latency_increase   gauge      multiplier vs baseline    │
│                               alert: > 1.5x                     │
│  canary.traffic_split      gauge      % to canary               │
│  canary.duration           gauge      days remaining            │
│                                                                 │
│  SKILL EXECUTION                                              │
│  ───────────────────────────────────────────────────────────  │
│  skill.execution          counter    labels: skill_name          │
│  skill.success            counter    labels: skill_name          │
│  skill.failure            counter    labels: skill_name, reason │
│  skill.latency            histogram   labels: skill_name        │
│                               buckets: 1s, 5s, 10s, 30s, 60s    │
│  skill.circuit_breaker    gauge      labels: skill_name        │
│                               (0=closed, 1=open)               │
│                                                                 │
│  COST TRACKING                                                │
│  ───────────────────────────────────────────────────────────  │
│  cost.total               counter    labels: provider           │
│  cost.per_decision        gauge      labels: tier               │
│                               (routing, reasoning, creative)     │
│  cost.daily_budget        gauge      vs allocated               │
│                               alert: > 100%                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Alerting Rules

### Critical Alerts (PagerDuty)

```yaml
# alerting/critical.yml

groups:
  - name: mais.critical
    rules:
      - alert: MCPConnectionDown
        expr: mcp_connection_status == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "MCP connection to {{ $labels.platform }} is down"
          description: "Failed to connect to {{ $labels.platform }} for 5 minutes"

      - alert: DataStale
        expr: time() - data.last_updated > 4 * 3600
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Data is stale (last update {{ $value | humanizeDuration }} ago)"
          description: "Marketing data has not been updated in over 4 hours"

      - alert: CanaryROASDrop
        expr: canary.roas_change < -0.05
        for: 1h
        labels:
          severity: critical
        annotations:
          summary: "Canary ROAS dropped {{ $value | printf \"%.1f\" }}%"
          description: "Automated rollback will trigger if drop continues"

      - alert: HumanApprovalTimeout
        expr: rate(approval_timeout[1h]) > 0.1
        for: 1h
        labels:
          severity: critical
        annotations:
          summary: "Human approval timeout rate > 10%"
          description: "Multiple pending approvals have timed out"

      - alert: RollbackTriggered
        expr: increase(model_update.rollbacked[1h]) > 0
        for: 0m
        labels:
          severity: critical
        annotations:
          summary: "Model rollback triggered"
          description: "Automated rollback was triggered for model update {{ $labels.model_update_id }}"
```

### Warning Alerts (Slack)

```yaml
# alerting/warning.yml

groups:
  - name: mais.warning
    rules:
      - alert: HypothesisQueueGrowing
        expr: hypothesis.queue_depth > 15
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "Hypothesis queue has {{ $value }} items"
          description: "Queue has been growing, consider running outer loop early"

      - alert: ValidationGateFailing
        expr: rate(validation.gate_failed[1h]) / rate(validation.gate_passed[1h]) > 0.8
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Validation failing > 80% of the time"
          description: "Most hypotheses are failing validation gates"

      - alert: SkillLatencyHigh
        expr: histogram_quantile(0.95, skill.latency) > 30
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "{{ $labels.skill_name }} p95 latency is {{ $value }}s"
          description: "Skill is taking longer than expected"

      - alert: CircuitBreakerOpen
        expr: sum(skill.circuit_breaker) by (skill_name) > 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Circuit breaker open for {{ $labels.skill_name }}"
          description: "Skill has been skipped due to repeated failures"

      - alert: CostOverrun
        expr: cost.daily_budget > 1.0
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Daily cost is {{ $value | printf \"%.0f\" }}% of budget"
          description: "Cost tracking shows we're over daily budget"
```

---

## Dashboards

### Executive Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXECUTIVE DASHBOARD                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   ROAS       │  │   ROAS       │  │  Model       │        │
│  │   Current    │  │   Change     │  │  Updates     │        │
│  │              │  │   vs Last    │  │  This Month  │        │
│  │    2.87     │  │    +12%     │  │     2       │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  ROAS TREND (30 DAYS)                    │   │
│  │  3.0 ┤                                                     │   │
│  │      │                         ╭─╮                       │   │
│  │  2.5 ┤              ╭─╮  ╭─╮  │ ╭─                     │   │
│  │      │         ╭─╮  │ │  │ │  ╭╯                       │   │
│  │  2.0 ┤  ╭─╮  ╭─╮  ╭╯ ╰──╯ ╰──╯                        │   │
│  │      │  │ │  │ │  ╰─╮                                   │   │
│  │  1.5 ┼──╯ ╰──╯ ╰──╯ ╰────────────────────────────────────│   │
│  │      └────────────────────────────────────────────────────│   │
│  │       Day 1    Day 7    Day 14   Day 21   Day 30        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ Hypotheses   │  │  Approval   │  │  Cost/      │        │
│  │  Generated   │  │  SLA Hit   │  │  Decision   │        │
│  │  This Week  │  │  Rate      │  │             │        │
│  │     47      │  │    94%    │  │   $0.85    │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Inner Loop Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│                    INNER LOOP DASHBOARD                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           SPC CHART (24-HOUR ROLLING)                     │   │
│  │  Upper │  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─    │   │
│  │ Control│                                               │   │
│  │  Limit │          ●  ●                                 │   │
│  │        │      ●         ●  ●                   ●      │   │
│  │  EWMA  │    ●    ●          ●  ●  ●  ●        ●      │   │
│  │        │  ●                          ●  ●               │   │
│  │  Lower │  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─    │   │
│  │ Control│                                               │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌────────────────────┐  ┌────────────────────┐                 │
│  │  Queue Depth      │  │  Anomaly Rate     │                 │
│  │                   │  │                   │                 │
│  │      12           │  │      3.2%        │                 │
│  │    (target <15)   │  │   (target <5%)   │                 │
│  └────────────────────┘  └────────────────────┘                 │
│                                                                 │
│  RECENT HYPOTHESES                                             │
│  ───────────────────────────────────────────────────────────  │
│  hyp_042  │ ROAS anomaly │ confidence 0.78 │ queued │ 2m ago  │
│  hyp_041  │ Trend change │ confidence 0.65 │ queued │ 15m ago │
│  hyp_040  │ Segment gap  │ confidence 0.55 │ ignore │ 1h ago  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Validation Pipeline Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│                    VALIDATION PIPELINE DASHBOARD                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  GATE STATUS                                                   │
│  ───────────────────────────────────────────────────────────  │
│  Gate 1: Data Quality    ● PASSING    avg score: 0.94       │
│  Gate 2: Confounds       ● PASSING    0 flagged              │
│  Gate 3: Significance   ● PASSING    avg p-value: 0.02      │
│  Gate 4: Replication     ● PASSING    3 segments, 2 periods   │
│  Gate 5: Human Review    ◐ PENDING   waiting 2h 34m          │
│  Gate 6: Shadow Deploy   ○ WAITING   starts in 1d 2h          │
│  Gate 7: Canary Deploy   ○ WAITING   starts in 8d 2h          │
│                                                                 │
│  PASS RATES (LAST 30 DAYS)                                    │
│  ───────────────────────────────────────────────────────────  │
│  Gate 1: 98%  ████████████████████████████████████▒          │
│  Gate 2: 85%  ███████████████████████████████▒               │
│  Gate 3: 72%  ██████████████████████████▒                    │
│  Gate 4: 65%  ██████████████████████▒                       │
│  Gate 5: 94%  █████████████████████████████████████████▒    │
│  (of those reaching gate 5)                                   │
│                                                                 │
│  RECENT VALIDATION RESULTS                                     │
│  ───────────────────────────────────────────────────────────  │
│  hyp_042 │ G2 FAIL │ competitor_activity overlap │ 1h ago    │
│  hyp_041 │ G4 FAIL │ only 1 segment significant  │ 3h ago   │
│  hyp_040 │ G3 FAIL │ p-value = 0.12              │ 5h ago    │
│  hyp_039 │ ALL PASS│ queued for human review     │ 8h ago   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Observability Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                    OBSERVABILITY STACK                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  METRICS                    LOGGING                 TRACING       │
│  ────────────────────────────────────────────────────────────  │
│  Prometheus                 Loki                   Jaeger       │
│  (Time-series DB)           (Aggregated logs)       (Distributed │
│                             (80GB/day)              tracing)    │
│        ↓                       ↓                        ↓       │
│  Grafana                    Grafana                  Grafana     │
│  (Dashboards)               (Log search)             (Traces)   │
│                                                                 │
│  ALERTING                                                         │
│  ────────────────────────────────────────────────────────────  │
│  Alertmanager → PagerDuty (critical) / Slack (warning)        │
│                                                                 │
│  INFRASTRUCTURE                                                  │
│  ────────────────────────────────────────────────────────────  │
│  Node Exporter → Prometheus (system metrics)                    │
│  cAdvisor → Prometheus (container metrics)                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Runbook Templates

### Runbook: MCP Connection Down

```markdown
# Runbook: MCP Connection Down

## Symptoms
- Alert: MCPConnectionDown
- MCP connection status = 0 for > 5 minutes

## Impact
- Cannot fetch campaign data
- Inner loop will use stale data
- Decisions may be based on outdated information

## Resolution Steps

1. **Check MCP server status**
   ```bash
   kubectl get pods -n mais | grep mcp
   curl -s http://mcp-server:8080/health
   ```

2. **Check credentials**
   ```bash
   kubectl get secret mcp-creds -n mais -o yaml
   # Verify Google Ads and Meta credentials are valid
   ```

3. **Restart MCP server**
   ```bash
   kubectl rollout restart deployment/mcp-server -n mais
   ```

4. **Check rate limits**
   ```bash
   curl -s http://mcp-server:8080/metrics | grep rate_limit
   # If rate limited, wait and retry
   ```

5. **Verify data recovery**
   ```bash
   # After reconnect, verify data is flowing
   watch -n 5 'curl -s http://mais-api/internal/data/last_updated'
   ```

## Escalation
- If not resolved in 15 minutes → Escalate to backend lead
- If data loss > 4 hours → Notify stakeholders
```

### Runbook: Canary ROAS Drop

```markdown
# Runbook: Canary ROAS Drop

## Symptoms
- Alert: CanaryROASDrop
- canary.roas_change < -0.05 for > 1 hour

## Impact
- Automated rollback will trigger if drop continues
- ~10% of traffic is seeing degraded experience

## Resolution Steps

1. **Check which model changed**
   ```bash
   # Get model update ID
   kubectl get modelupdates -n mais --sort-by=.metadata.creationTimestamp | tail -5

   # Check what changed
   mais-cli model diff <model_update_id>
   ```

2. **Check for external factors**
   ```bash
   # Was there a competitor action?
   mais-cli competitor activity --since 24h

   # Was there a budget change?
   mais-cli campaign budget-changes --since 24h
   ```

3. **Manual rollback (if needed)**
   ```bash
   mais-cli model rollback <model_update_id> --reason "ROAS drop investigation"
   ```

4. **Investigate root cause**
   ```bash
   # Compare canary vs baseline metrics
   mais-cli analyze canary --compare baseline --since 7d

   # Check if specific segments are affected
   mais-cli segment performance --model canary --breakdown
   ```

5. **Document findings**
   ```bash
   # Create incident report
   mais-cli incident report --model <model_update_id> --impact -5.2%
   ```

## Post-Incident
- Schedule review of model update process
- Update validation gates if needed
```
