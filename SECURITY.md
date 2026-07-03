# Security & Data Governance

**Related to:** TOOL_LAYER.md, API_CONTRACTS.md

---

## Overview

MAIS handles sensitive marketing data and requires strict security controls, data governance, and audit trails.

```
┌─────────────────────────────────────────────────────────────────┐
│                    SECURITY REQUIREMENTS                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  DATA TYPES:                                                   │
│  ───────────────────────────────────────────────────────────  │
│  • Campaign budgets and spend (financial)                      │
│  • Audience segments (potentially PII)                        │
│  • Ad performance data (business intelligence)                │
│  • API credentials for ad platforms                           │
│  • User interactions with approval workflows                  │
│                                                                 │
│  COMPLIANCE:                                                  │
│  ───────────────────────────────────────────────────────────  │
│  • GDPR: No PII in logs, data retention limits                │
│  • SOC2: Encrypt at rest, TLS in flight, access controls      │
│  • Audit trail: 7-year retention for regulatory               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Secrets Management

### Secrets Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                    SECRETS MANAGEMENT                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  TIER 1: PLATFORM API KEYS (Highest Sensitivity)              │
│  ───────────────────────────────────────────────────────────  │
│  • Google Ads API key                                          │
│  • Meta Marketing API access token                            │
│  • Stored in: HashiCorp Vault (AES-256 encrypted)            │
│  • Access: Requires 2-person approval                        │
│  • Rotation: Every 90 days                                    │
│                                                                 │
│  TIER 2: APPLICATION SECRETS                                  │
│  ───────────────────────────────────────────────────────────  │
│  • Claude API key                                             │
│  • Slack webhook tokens                                       │
│  • HMAC signing keys                                          │
│  • Stored in: Vault                                          │
│  • Rotation: Every 90 days                                    │
│                                                                 │
│  TIER 3: INFRASTRUCTURE SECRETS                               │
│  ───────────────────────────────────────────────────────────  │
│  • Database passwords                                         │
│  • Redis passwords                                           │
│  • Stored in: Vault or K8s secrets                           │
│  • Rotation: Every 180 days                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Vault Configuration

```yaml
# vault/config.hcl

storage "raft" {
  path = "/var/lib/vault/data"

  retry {
    num_retries = 5
  }
}

listener "tcp" {
  address     = "[::]:8200"
  cluster_address = "[::]:8201"
  tls_disable = "false"
  tls_cert_file = "/etc/vault/tls/server.crt"
  tls_key_file = "/etc/vault/tls/server.key"
}

# Enable audit logging
audit "file" {
  path = "/var/log/vault/audit.log"
  format = "json"
}

# Enable Kubernetes auth
auth "kubernetes" {
  token_reviewer_service_account = "vault-auth"
  kubernetes_host = "https://kubernetes.default.svc"
}
```

### Secret Access Policy

```yaml
# vault/policies/mais.hcl

# MAIAgent can read ad platform credentials
path "secret/data/mais/ad-platforms/*" {
  capabilities = ["read"]
}

# MAIAgent can read (not write) approval tokens
path "secret/data/mais/tokens/*" {
  capabilities = ["read"]
}

# Only human operators can write secrets
path "secret/data/mais/ad-platforms/*" {
  capabilities = ["write"]
  denied = ["MAIAgent"]
}

# Audit log access for compliance
path "audit/*" {
  capabilities = ["read"]
}
```

---

## Data Retention

### Retention Schedule

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA RETENTION SCHEDULE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  RAW CAMPAIGN METRICS                                           │
│  ───────────────────────────────────────────────────────────  │
│  Retention: 2 years                                            │
│  Storage: Encrypted S3 (AES-256)                              │
│  PII: No PII stored                                           │
│  Deletion: Automated after 2 years                            │
│                                                                 │
│  DENOISED ROAS (AUDIT TRAIL)                                   │
│  ───────────────────────────────────────────────────────────  │
│  Retention: 2 years                                           │
│  Storage: Encrypted S3 + SQL                                  │
│  Purpose: Audit trail for model updates                       │
│                                                                 │
│  MODEL UPDATES (PERMANENT)                                     │
│  ───────────────────────────────────────────────────────────  │
│  Retention: Permanent                                         │
│  Storage: Encrypted S3 + Git                                  │
│  Purpose: Regulatory compliance, rollback capability          │
│                                                                 │
│  SESSION LOGS                                                  │
│  ───────────────────────────────────────────────────────────  │
│  Retention: 90 days                                            │
│  Storage: SQL (hot)                                           │
│  PII: No PII in session logs                                  │
│  Deletion: Automated after 90 days                           │
│                                                                 │
│  HYPOTHESES (UNTIL RESOLVED)                                  │
│  ───────────────────────────────────────────────────────────  │
│  Active: Until resolved (approved/rejected/expired)           │
│  Archive: 2 years after resolution                            │
│                                                                 │
│  FEEDBACK                                                     │
│  ───────────────────────────────────────────────────────────  │
│  Retention: 2 years                                           │
│  Storage: Encrypted SQL                                       │
│  PII: No direct PII                                          │
│                                                                 │
│  AUDIT LOGS                                                   │
│  ───────────────────────────────────────────────────────────  │
│  Retention: 7 years (regulatory requirement)                  │
│  Storage: Immutable log storage                               │
│  Access: Restricted to compliance team                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Data Classification

```python
# data_classifier.py

class DataClassification:
    """
    Classify data by sensitivity level.
    """

    # No PII - can be logged
    PUBLIC = "public"
    # Internal - can be in encrypted logs
    INTERNAL = "internal"
    # Confidential - restricted access, encrypted
    CONFIDENTIAL = "confidential"
    # Restricted - most sensitive, 2-person approval
    RESTRICTED = "restricted"

CLASSIFICATION_RULES = {
    # Campaign data - internal
    "campaign_id": INTERNAL,
    "campaign_name": INTERNAL,
    "roas": INTERNAL,
    "spend": INTERNAL,
    "conversions": INTERNAL,

    # Platform credentials - restricted
    "api_key": RESTRICTED,
    "access_token": RESTRICTED,
    "client_secret": RESTRICTED,

    # Audience data - confidential (may contain demographics)
    "audience_segment": CONFIDENTIAL,
    "demographics": CONFIDENTIAL,

    # Decision logs - internal
    "hypothesis_id": INTERNAL,
    "model_update_id": INTERNAL,
    "approval_token": INTERNAL,
}

def classify_data(data: dict) -> str:
    """
    Classify a data record by its most sensitive field.
    """
    max_classification = PUBLIC

    for key, value in data.items():
        field_classification = CLASSIFICATION_RULES.get(key, PUBLIC)

        if field_classification == RESTRICTED:
            return RESTRICTED
        elif field_classification == CONFIDENTIAL:
            max_classification = CONFIDENTIAL
        elif field_classification == INTERNAL and max_classification == PUBLIC:
            max_classification = INTERNAL

    return max_classification
```

---

## Audit Logging

### Audit Log Schema

```python
# audit/models.py

class AuditLogEntry(Base):
    __tablename__ = "audit_log"

    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, nullable=False, index=True)

    # Who
    actor_type = Column(String)  # human | agent | system
    actor_id = Column(String)   # user_id or agent_id
    actor_name = Column(String)

    # What
    action = Column(String, nullable=False)  # e.g., model_update_approved
    resource_type = Column(String)  # e.g., model_update
    resource_id = Column(String)

    # Details (JSON, no PII)
    action_details = Column(JSON)

    # Context
    ip_address = Column(String)  # Truncated to /16 for privacy
    user_agent = Column(String)
    session_id = Column(String)

    # Compliance
    compliance_tags = Column(JSON)  # e.g., ["GDPR", "SOX"]
    retention_until = Column(DateTime)

    # Integrity
    checksum = Column(String)  # SHA-256 of entry
    previous_checksum = Column(String)  # Chain integrity
```

### Audit Event Types

```
┌─────────────────────────────────────────────────────────────────┐
│                    REQUIRED AUDIT EVENTS                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  MODEL CHANGES                                                 │
│  ───────────────────────────────────────────────────────────  │
│  • model_update.submitted       — Who submitted, what changed   │
│  • model_update.approved        — Who approved, conditions      │
│  • model_update.rejected       — Who rejected, reason           │
│  • model_update.deployed       — When deployed, to which env    │
│  • model_update.rollbacked     — Why rolled back                │
│                                                                 │
│  DATA ACCESS                                                   │
│  ───────────────────────────────────────────────────────────  │
│  • data.campaign.read          — Who accessed campaign data      │
│  • data.export               — Any bulk data export              │
│                                                                 │
│  APPROVAL WORKFLOWS                                           │
│  ───────────────────────────────────────────────────────────  │
│  • approval.requested         — What required approval          │
│  • approval.escalated         — When escalated, to whom         │
│  • approval.timeout           — When human didn't respond        │
│                                                                 │
│  SECURITY EVENTS                                               │
│  ───────────────────────────────────────────────────────────  │
│  • auth.login               — Human login to system             │
│  • auth.logout              — Human logout                      │
│  • auth.apikey_created      — New API key generated             │
│  • auth.apikey_revoked      — API key revoked                   │
│  • security.token_invalid   — Invalid token presented           │
│  • security.breach_attempt  — Suspected breach attempt          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Audit Log Example

```json
{
  "id": "audit_001234",
  "timestamp": "2024-01-31T09:15:32Z",
  "actor_type": "human",
  "actor_id": "user_jane_doe",
  "actor_name": "Jane Doe",
  "action": "model_update.approved",
  "resource_type": "model_update",
  "resource_id": "mu_001",
  "action_details": {
    "what_changed": "LoRA weights v1.2.0 for budget_allocator",
    "why": "ROAS improvement hypothesis validated",
    "p_value": 0.023,
    "cohens_d": 0.31,
    "conditions": ["shadow_deploy_7d", "canary_deploy_14d"]
  },
  "ip_address": "192.168.1.0",
  "session_id": "sess_abc123",
  "compliance_tags": ["GDPR", "SOX"],
  "retention_until": "2031-01-31T00:00:00Z",
  "checksum": "sha256:a1b2c3..."
}
```

---

## Access Control

### RBAC Model

```
┌─────────────────────────────────────────────────────────────────┐
│                    ROLE-BASED ACCESS CONTROL                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ROLES                                                         │
│  ───────────────────────────────────────────────────────────  │
│                                                                 │
│  ADMIN                                                         │
│  • Full access to all resources                                │
│  • Can approve any model update                                │
│  • Can manage users and roles                                  │
│  • Can access audit logs                                       │
│                                                                 │
│  MARKETING_MANAGER                                            │
│  • Read/write campaigns and budgets                            │
│  • Approve model updates (except strategic)                    │
│  • View dashboards and reports                                 │
│  • Cannot manage users                                        │
│                                                                 │
│  DATA_SCIENTIST                                               │
│  • Read-only access to campaign data                          │
│  • Can submit hypotheses for validation                       │
│  • Can view validation pipeline status                        │
│  • Cannot approve model updates                               │
│                                                                 │
│  ENGINEER                                                      │
│  • Read/write access to skills and infrastructure              │
│  • Can deploy new skills                                      │
│  • Cannot approve model updates                               │
│  • Cannot access audit logs                                   │
│                                                                 │
│  VIEWER                                                        │
│  • Read-only access to dashboards                             │
│  • Cannot access raw data or audit logs                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Permission Matrix

```
┌─────────────────────────────────────────────────────────────────┐
│                    PERMISSION MATRIX                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ACTION                    ADMIN  MGR  DATA  ENG  VIEWER       │
│  ────────────────────────────────────────────────────────────  │
│  model_update.approve       ✓      ✓*   ✗    ✗    ✗          │
│  model_update.reject       ✓      ✓    ✗    ✗    ✗          │
│  campaign.read             ✓      ✓    ✓    ✓    ✓          │
│  campaign.write            ✓      ✓    ✗    ✗    ✗          │
│  hypothesis.submit         ✓      ✓    ✓    ✓    ✗          │
│  hypothesis.review         ✓      ✓    ✗    ✗    ✗          │
│  skills.deploy            ✓      ✗    ✗    ✓    ✗          │
│  audit_log.read           ✓      ✗    ✗    ✗    ✗          │
│  secrets.read             ✓      ✗    ✗    ✗    ✗          │
│  users.manage            ✓      ✗    ✗    ✗    ✗          │
│                                                                 │
│  * MGR can approve except strategic model updates               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Encryption

### Encryption at Rest

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENCRYPTION AT REST                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  DATABASE                                                       │
│  ───────────────────────────────────────────────────────────  │
│  Engine: PostgreSQL with AWS RDS encryption                     │
│  Key: AWS KMS (AES-256)                                       │
│  Tables: All tables encrypted                                  │
│  Backups: Encrypted with same KMS key                           │
│                                                                 │
│  OBJECT STORAGE (S3)                                           │
│  ───────────────────────────────────────────────────────────  │
│  Buckets: All with SSE-S3 encryption                            │
│  Key: AWS S3 managed (AES-256)                                │
│  Versioning: Enabled for audit trail                           │
│  Lifecycle: Move to Glacier after 90 days                      │
│                                                                 │
│  KNOWLEDGE GRAPH (Neo4j)                                      │
│  ───────────────────────────────────────────────────────────  │
│  At-rest encryption: Enabled                                   │
│  Key: Neo4j managed                                           │
│                                                                 │
│  VECTOR STORE (ChromaDB)                                      │
│  ───────────────────────────────────────────────────────────  │
│  Storage: Encrypted filesystem                                 │
│  Backup: Encrypted tarball to S3                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Encryption in Transit

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENCRYPTION IN TRANSIT                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  EXTERNAL COMMUNICATIONS                                        │
│  ───────────────────────────────────────────────────────────  │
│  TLS 1.3 required for all external APIs                       │
│  TLS 1.2 minimum for internal services                        │
│  Certificate: Let's Encrypt (auto-renew)                       │
│  HSTS: Enabled with 1-year max-age                            │
│                                                                 │
│  INTERNAL SERVICES (K8s)                                      │
│  ───────────────────────────────────────────────────────────  │
│  mTLS between all pods (Istio service mesh)                   │
│  SPIFFE/SPIRE for workload identity                            │
│  Certificates rotated every 24 hours                           │
│                                                                 │
│  DATABASE CONNECTIONS                                           │
│  ───────────────────────────────────────────────────────────  │
│  SSL/TLS required for all database connections                │
│  Certificate verification enabled                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Compliance Checklist

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMPLIANCE CHECKLIST                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  GDPR                                                          │
│  ───────────────────────────────────────────────────────────  │
│  □ No PII in session logs                                      │
│  □ No PII in audit logs                                       │
│  □ Data retention policies enforced                            │
│  □ Right to deletion implemented                              │
│  □ Data processing agreement in place                         │
│  □ Consent mechanism for audience data                       │
│                                                                 │
│  SOC2                                                          │
│  ───────────────────────────────────────────────────────────  │
│  □ Encryption at rest (AES-256)                               │
│  □ Encryption in transit (TLS 1.3)                            │
│  □ Access controls (RBAC) implemented                         │
│  □ Audit logging enabled                                       │
│  □ Incident response plan documented                          │
│  □ Change management process                                  │
│  □ Vulnerability scanning                                     │
│                                                                 │
│  REGULATORY                                                   │
│  ───────────────────────────────────────────────────────────  │
│  □ 7-year audit log retention                                 │
│  □ Audit trail immutable                                      │
│  □ Financial data accuracy controls                           │
│  □ Approval workflows for financial changes                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
