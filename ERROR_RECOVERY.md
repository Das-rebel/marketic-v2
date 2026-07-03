# Error Recovery & Circuit Breaker Patterns

**Related to:** SKILLS_ARCHITECTURE.md Section 6, VALIDATION_PIPELINE.md

---

## Overview

MAIS must handle failures gracefully. This document specifies failure modes, recovery procedures, and circuit breaker patterns for all components.

```
┌─────────────────────────────────────────────────────────────────┐
│                    ERROR RECOVERY PRINCIPLES                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. FAIL FAST — Detect failures quickly, don't cascade          │
│  2. GRACEFUL DEGRADATION — Partial functionality > total down │
│  3. NO SILENT ERRORS — Every failure is logged and alerted      │
│  4. SELF-HEALING — Retry with backoff where appropriate        │
│  5. HUMAN ESCALATION — Critical failures go to humans           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Failure Mode Matrix

```
┌─────────────────────────────────────────────────────────────────┐
│                    FAILURE MODE MATRIX                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ FAILURE          │ SYMPOM        │ RECOVERY           │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │ MCP connection   │ No metrics    │ Retry 3x backoff   │    │
│  │ drop            │              │ Skip cycle + alert  │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │ Skill timeout   │ Latency spike │ Kill + circuit open │    │
│  │ (>30s)         │              │ Alert human         │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │ Data quality   │ Missing >5%   │ Wait 24h           │    │
│  │ gate fail      │              │ Flag unlearnable    │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │ Validation     │ Gate fails    │ Queue for next      │    │
│  │ gate fail      │              │ outer loop          │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │ Shadow deploy  │ Latency 2x   │ Auto-rollback      │    │
│  │ latency spike  │              │ Alert human         │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │ Canary ROAS    │ ROAS -7%     │ Auto-rollback      │    │
│  │ drop           │              │ Full investigation  │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │ Human approval │ 4h timeout   │ Escalate to manager │    │
│  │ timeout       │              │ Stop outer loop     │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │ Token invalid │ n8n rejects  │ Re-request approval │    │
│  │              │ execution    │ Alert if repeated   │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │ Budget drift  │ >2% overage  │ Auto-pause          │    │
│  │              │              │ Alert human         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Circuit Breaker Pattern

### State Machine

```
┌─────────────────────────────────────────────────────────────────┐
│                    CIRCUIT BREAKER STATES                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  CLOSED (Normal) ────────────────────────────────────────────  │
│  │                                                             │
│  │  Success → Stay CLOSED                                      │
│  │  Failure → failure_count++                                  │
│  │           if failure_count >= threshold:                     │
│  │             state = OPEN                                     │
│  │             schedule reopen check in 5min                   │
│  │                                                             │
│  ▼                                                             │
│  OPEN (Failing) ──────────────────────────────────────────────  │
│  │                                                             │
│  │  Requests blocked → Return error immediately                │
│  │  After 5min → state = HALF_OPEN                           │
│  │                                                             │
│  ▼                                                             │
│  HALF_OPEN (Testing) ─────────────────────────────────────────  │
│  │                                                             │
│  │  Success → state = CLOSED, reset failure_count              │
│  │  Failure → state = OPEN, reset failure_count               │
│  │                                                             │
└─────────────────────────────────────────────────────────────────┘
```

### Implementation

```python
# circuit_breaker.py

from enum import Enum
from typing import Callable, TypeVar, Generic
import asyncio
import time

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

T = TypeVar('T')

class CircuitBreaker(Generic[T]):
    """
    Circuit breaker for protecting against cascading failures.
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: float = 60.0,  # 1 minute
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: float | None = None
        self.success_count = 0

    async def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Execute function through circuit breaker.
        """
        # Check if we should transition from OPEN to HALF_OPEN
        if self.state == CircuitState.OPEN:
            if self._should_attempt_recovery():
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker is OPEN. Retry after {self.recovery_timeout}s"
                )

        # Execute function
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result

        except self.expected_exception as e:
            self._on_failure()
            raise

    def _should_attempt_recovery(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if self.last_failure_time is None:
            return True
        return (time.time() - self.last_failure_time) >= self.recovery_timeout

    def _on_success(self):
        """Handle successful call."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= 2:  # Need 2 successes to close
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
        else:
            self.failure_count = 0

    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            # Failed during recovery attempt → go back to OPEN
            self.state = CircuitState.OPEN
            self.success_count = 0
        elif self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is OPEN."""
    pass
```

### Skill Circuit Breaker

```python
# skills/circuit_breaker.py

class SkillCircuitBreaker:
    """
    Circuit breaker for skill execution.
    Tracks failures per skill.
    """

    def __init__(self):
        self.breakers: dict[str, CircuitBreaker] = {}
        self.alert_handler = AlertHandler()

    def get_breaker(self, skill_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for skill."""
        if skill_name not in self.breakers:
            self.breakers[skill_name] = CircuitBreaker(
                failure_threshold=3,
                recovery_timeout=300,  # 5 minutes
                expected_exception=SkillExecutionError
            )
        return self.breakers[skill_name]

    async def execute(
        self,
        skill: Skill,
        input_data: SkillInput
    ) -> SkillOutput:
        """
        Execute skill through circuit breaker.
        """
        breaker = self.get_breaker(skill.name)

        try:
            return await breaker.call(skill.execute, input_data)

        except CircuitBreakerOpenError as e:
            # Log and alert
            await self.alert_handler.send(
                level="high",
                message=f"Circuit breaker OPEN for skill {skill.name}",
                context={"skill": skill.name}
            )

            # Return error output (don't propagate)
            return SkillOutput(
                success=False,
                error=f"Skill temporarily unavailable: {skill.name}",
                metadata={
                    "circuit_breaker": "open",
                    "retry_after": breaker.recovery_timeout
                }
            )
```

---

## Recovery Procedures

### 1. MCP Connection Drop

```python
# recovery/mcp_connection.py

class MCPConnectionRecovery:
    """
    Recovery procedure for MCP connection failures.
    """

    def __init__(
        self,
        mcp_client: MCPClient,
        alert_handler: AlertHandler,
        cache: Cache
    ):
        self.mcp = mcp_client
        self.alert = alert_handler
        self.cache = cache
        self.max_retries = 3
        self.backoff_base = 2  # Exponential backoff: 2, 4, 8 seconds

    async def execute_with_recovery(
        self,
        func: Callable,
        *args,
        **kwargs
    ):
        """
        Execute MCP call with retry and recovery.
        """
        last_error = None

        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)

            except MCPConnectionError as e:
                last_error = e
                backoff = self.backoff_base ** attempt

                await self.alert.send(
                    level="warning",
                    message=f"MCP connection failed (attempt {attempt + 1}/{self.max_retries})",
                    context={"error": str(e), "backoff": backoff}
                )

                if attempt < self.max_retries - 1:
                    await asyncio.sleep(backoff)
                    await self._attempt_reconnect()

        # All retries exhausted
        await self._handle_exhausted_retries(last_error)
        raise RetryExhaustedError(
            f"MCP connection failed after {self.max_retries} attempts"
        )

    async def _attempt_reconnect(self):
        """Attempt to reconnect MCP."""
        try:
            await self.mcp.reconnect()
        except Exception as e:
            # Log but don't fail — next retry will check
            pass

    async def _handle_exhausted_retries(self, error: Exception):
        """
        After all retries exhausted:
        1. Alert human
        2. Use stale data if available (with flag)
        3. Log incident
        """
        await self.alert.send(
            level="critical",
            message="MCP connection failed after all retries",
            context={"error": str(error)}
        )

        # Check if we have stale cached data
        cached = await self.cache.get("campaign_data:stale")
        if cached:
            # Mark as stale and continue
            cached["is_stale"] = True
            cached["stale_reason"] = "MCP connection failed"
            return cached

        raise NoDataAvailableError("No stale data available, MCP unavailable")
```

### 2. Skill Timeout

```python
# recovery/skill_timeout.py

class SkillTimeoutRecovery:
    """
    Recovery procedure for skill timeouts.
    """

    def __init__(
        self,
        skill: Skill,
        circuit_breaker: SkillCircuitBreaker,
        alert_handler: AlertHandler
    ):
        self.skill = skill
        self.cb = circuit_breaker
        self.alert = alert_handler

    async def execute_with_timeout(
        self,
        input_data: SkillInput,
        timeout_seconds: int = 30
    ):
        """
        Execute skill with timeout and recovery.
        """
        try:
            result = await asyncio.wait_for(
                self.cb.execute(self.skill, input_data),
                timeout=timeout_seconds
            )
            return result

        except asyncio.TimeoutError:
            # Kill the task
            await self._handle_timeout(input_data)

        except CircuitBreakerOpenError:
            # Already handled by circuit breaker
            raise

    async def _handle_timeout(self, input_data: SkillInput):
        """
        On timeout:
        1. Increment failure count
        2. If 3+ failures, open circuit breaker
        3. Alert human
        4. Return error output
        """
        await self.alert.send(
            level="high",
            message=f"Skill {self.skill.name} timed out",
            context={
                "skill": self.skill.name,
                "input": input_data.dict()
            }
        )

        # Check circuit breaker
        breaker = self.cb.get_breaker(self.skill.name)
        breaker.failure_count += 1
        breaker.last_failure_time = time.time()

        if breaker.failure_count >= breaker.failure_threshold:
            breaker.state = CircuitState.OPEN
            await self.alert.send(
                level="critical",
                message=f"Circuit breaker OPEN for {self.skill.name}",
                context={"failures": breaker.failure_count}
            )
```

### 3. Validation Gate Failure

```python
# recovery/validation_gate_failure.py

class ValidationGateRecovery:
    """
    Recovery procedure for validation gate failures.
    """

    async def handle_gate_failure(
        self,
        gate_name: str,
        result: GateResult,
        hypothesis: Hypothesis
    ) -> RecoveryAction:
        """
        Determine recovery action for failed gate.
        """
        # Gate 1: Data Quality → Wait for more data
        if gate_name == "data_quality":
            if result.issues[0].check == "missing_data":
                return RecoveryAction(
                    action="wait",
                    reason="Waiting for missing data to arrive",
                    wait_hours=24,
                    escalation="none"
                )

        # Gate 2: Confounds → Exclude confounded period
        if gate_name == "confounds":
            confound = result.detected_confounds[0]
            if confound.recommendation == "exclude":
                return RecoveryAction(
                    action="exclude_period",
                    reason=f"Exclude {confound.name} from analysis",
                    parameters={"exclude_confounds": True}
                )

        # Gate 3-4: Significance/Replication → Need more data
        if gate_name in ["significance", "replication"]:
            return RecoveryAction(
                action="queue_next_month",
                reason="Insufficient statistical power",
                escalation="human_review"
            )

        # Gate 5: Human → Escalate
        if gate_name == "human_review":
            return RecoveryAction(
                action="escalate",
                reason="Human did not respond",
                escalation="manager"
            )

        # Default: Queue for next outer loop
        return RecoveryAction(
            action="queue_next_loop",
            reason="Generic gate failure",
            escalation="none"
        )
```

---

## Rollback Procedures

### Automatic Rollback Triggers

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUTOMATIC ROLLBACK TRIGGERS                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  SHADOW DEPLOY:                                               │
│  ───────────────────────────────────────────────────────────  │
│  • Error rate > 5%                                          │
│  • p99 latency > 2x baseline                                │
│  • Budget drift > 2%                                         │
│                                                                 │
│  CANARY DEPLOY:                                               │
│  ───────────────────────────────────────────────────────────  │
│  • ROAS drop > 5%                                            │
│  • Error rate increase > 5%                                   │
│  • p99 latency > 1.5x baseline                               │
│                                                                 │
│  IMMEDIATE (Stop Everything):                                  │
│  ───────────────────────────────────────────────────────────  │
│  • Data breach                                               │
│  • Unauthorized budget change                                │
│  • PII exposure                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Rollback Implementation

```python
# recovery/rollback.py

class RollbackSystem:
    """
    Handles model rollback procedures.
    """

    def __init__(
        self,
        model_store: ModelStore,
        traffic_splitter: TrafficSplitter,
        audit_logger: AuditLogger,
        alert_handler: AlertHandler
    ):
        self.store = model_store
        self.traffic = traffic_splitter
        self.audit = audit_logger
        self.alert = alert_handler

    async def rollback(
        self,
        model_update_id: str,
        reason: str,
        triggered_by: str = "automated"
    ):
        """
        Execute rollback procedure.
        """
        # 1. Get current and previous models
        current = self.store.get(model_update_id)
        previous = self.store.get_previous_version(model_update_id)

        if not previous:
            raise NoPreviousVersionError(
                f"No previous version to rollback to for {model_update_id}"
            )

        # 2. Log rollback intent
        await self.audit.log(
            action="rollback_initiated",
            model_update_id=model_update_id,
            reason=reason,
            triggered_by=triggered_by
        )

        # 3. Switch traffic to previous model
        await self.traffic.switch_to(previous.id)

        # 4. Archive current model (don't delete)
        await self.store.archive(
            model_id=current.id,
            reason=f"Rolled back: {reason}"
        )

        # 5. Notify humans
        await self.alert.send(
            level="critical",
            message=f"Model rolled back: {model_update_id}",
            context={
                "reason": reason,
                "triggered_by": triggered_by,
                "previous_model": previous.id
            }
        )

        # 6. Log completion
        await self.audit.log(
            action="rollback_completed",
            model_update_id=model_update_id,
            previous_model_id=previous.id,
            reason=reason
        )
```

---

## Health Checks

### Component Health Checks

```python
# health/checks.py

class HealthCheck:
    """
    Health check for a component.
    """

    def __init__(self, name: str):
        self.name = name
        self.status = "healthy"
        self.last_check = None
        self.issues = []

    async def check(self) -> HealthStatus:
        """Run health check."""
        raise NotImplementedError


class MCPHealthCheck(HealthCheck):
    """Health check for MCP connections."""

    async def check(self) -> HealthStatus:
        self.last_check = datetime.utcnow()
        self.issues = []

        for platform in ["google_ads", "meta_ads"]:
            try:
                result = await self.mcp.health(platform)
                if not result.healthy:
                    self.issues.append(f"{platform}: {result.error}")
            except Exception as e:
                self.issues.append(f"{platform}: {str(e)}")

        self.status = "unhealthy" if self.issues else "healthy"
        return HealthStatus(
            name=self.name,
            status=self.status,
            issues=self.issues,
            last_check=self.last_check
        )


class DatabaseHealthCheck(HealthCheck):
    """Health check for database connections."""

    async def check(self) -> HealthStatus:
        self.last_check = datetime.utcnow()
        self.issues = []

        # Check KG
        try:
            await self.kg.query("MATCH (n) RETURN count(n) LIMIT 1")
        except Exception as e:
            self.issues.append(f"Neo4j: {str(e)}")

        # Check vector store
        try:
            await self.vectorstore.health()
        except Exception as e:
            self.issues.append(f"Vector store: {str(e)}")

        # Check episodic
        try:
            await self.db.execute("SELECT 1")
        except Exception as e:
            self.issues.append(f"SQLite: {str(e)}")

        self.status = "unhealthy" if self.issues else "healthy"
        return HealthStatus(
            name=self.name,
            status=self.status,
            issues=self.issues,
            last_check=self.last_check
        )
```

### Health Check Endpoint

```yaml
# GET /health

{
  "status": "degraded",
  "timestamp": "2024-01-31T09:15:00Z",
  "components": {
    "mcp_connections": {
      "status": "healthy",
      "google_ads": "healthy",
      "meta_ads": "healthy"
    },
    "databases": {
      "status": "degraded",
      "neo4j": "healthy",
      "vector_store": "healthy",
      "episodic": "unhealthy",
      "issue": "Connection timeout"
    },
    "skills": {
      "status": "healthy",
      "circuit_breakers": {
        "get_campaign_data": "closed",
        "calculate_denoised_roas": "closed",
        "hypothesis_generator": "closed"
      }
    },
    "queue_depth": {
      "hypothesis_queue": 12,
      "pending_approvals": 3
    }
  },
  "alerts": [
    {
      "severity": "warning",
      "message": "Episodic database connection timeout"
    }
  ]
}
```
