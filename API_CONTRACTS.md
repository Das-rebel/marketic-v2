# API Contracts — MAIS 2.0

**Related to:** TOOL_LAYER.md, IMPLEMENTATION_ROADMAP.md Phase 0

---

## Overview

This document specifies exact API contracts for all integrations: ad platforms (Google Ads, Meta Ads), MCP servers, n8n workflows, and internal services.

**All timestamps in ISO 8601 UTC. All currencies in USD.**

```
┌─────────────────────────────────────────────────────────────────┐
│                    API ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐   │
│  │ Google Ads  │      │  Meta Ads   │      │  n8n       │   │
│  │    MCP      │      │    MCP      │      │ Workflows  │   │
│  └──────┬──────┘      └──────┬──────┘      └──────┬──────┘   │
│         │                    │                    │          │
│         └────────────────────┼────────────────────┘          │
│                              │                                │
│                     ┌────────▼────────┐                      │
│                     │   MAIAgent     │                      │
│                     │   Internal API  │                      │
│                     └────────┬────────┘                      │
│                              │                                │
│         ┌────────────────────┼────────────────────┐        │
│         │                    │                    │          │
│  ┌──────▼──────┐      ┌──────▼──────┐      ┌──────▼──────┐ │
│  │  Knowledge  │      │   Vector    │      │   Episodic  │ │
│  │    Graph    │      │    Store    │      │    Store    │ │
│  └─────────────┘      └─────────────┘      └─────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Google Ads MCP Contract

### 1. get_campaign_data

**Fetch campaign performance metrics for a date range.**

```yaml
endpoint: GET /campaigns/{campaign_id}/metrics
 MCP: google-ads
```

**Request:**

```json
{
  "campaign_id": "string (required)",
  "start_date": "2024-01-01",
  "end_date": "2024-01-30",
  "metrics": [
    "roas",
    "spend",
    "conversions",
    "impressions",
    "ctr",
    "cpc",
    "frequency"
  ],
  "granularity": "DAILY"
}
```

**Response:**

```json
{
  "campaign_id": "gads_123456",
  "campaign_name": "Summer Sale 2024",
  "currency": "USD",
  "daily_metrics": [
    {
      "date": "2024-01-01",
      "roas": 2.34,
      "roas_ci_lower": 2.10,
      "roas_ci_upper": 2.58,
      "spend": 500.00,
      "conversions": 117,
      "impressions": 45000,
      "ctr": 0.0234,
      "cpc": 0.89,
      "frequency": 2.1
    }
  ],
  "data_quality_score": 0.95,
  "last_updated": "2024-01-31T08:30:00Z",
  "platform": "google_ads"
}
```

**Error Responses:**

| Code | Message | Cause |
|------|---------|-------|
| 400 | INVALID_DATE_RANGE | start_date > end_date |
| 400 | INVALID_METRICS | Unknown metric name |
| 404 | CAMPAIGN_NOT_FOUND | campaign_id doesn't exist |
| 429 | RATE_LIMITED | > 100 requests/minute |
| 500 | PLATFORM_ERROR | Google Ads API error |

---

### 2. update_bid_multiplier

**Update campaign bid multiplier. HIGH-STAKES → Human approval required.**

```yaml
endpoint: POST /campaigns/{campaign_id}/bids
 MCP: google-ads
 auth: APPROVAL_TOKEN required
```

**Request:**

```json
{
  "campaign_id": "gads_123456",
  "bid_multiplier": 1.15,
  "approval_token": "tok_abc123_signature_xyz",
  "reason": "ROAS anomaly: hypothesis hyp_001"
}
```

**Response:**

```json
{
  "success": true,
  "campaign_id": "gads_123456",
  "previous_bid": 1.00,
  "new_bid": 1.15,
  "effective_bid_amount": 1.15,
  "applied_at": "2024-01-31T09:00:00Z",
  "approval_token": "tok_abc123_signature_xyz",
  "expires_at": "2024-01-31T10:00:00Z"
}
```

**Error Responses:**

| Code | Message | Cause |
|------|---------|-------|
| 400 | INVALID_MULTIPLIER | < 0.10 or > 10.0 |
| 400 | MISSING_APPROVAL_TOKEN | approval_token required |
| 400 | INVALID_APPROVAL_TOKEN | Token invalid or expired |
| 403 | APPROVAL_REQUIRED | Budget change > $100 |
| 404 | CAMPAIGN_NOT_FOUND | Campaign doesn't exist |

---

### 3. get_audience_segments

**Get available audience segments for a campaign.**

```yaml
endpoint: GET /campaigns/{campaign_id}/audiences
```

**Response:**

```json
{
  "campaign_id": "gads_123456",
  "segments": [
    {
      "segment_id": "aud_seg_001",
      "name": "Tech Buyers",
      "type": "CUSTOM_AUDIENCE",
      "estimated_reach": 125000,
      "demographics": {
        "age_range": "25-44",
        "gender": "any",
        "income": "top_25%"
      },
      "interests": ["technology", "software", "b2b"],
      "status": "ACTIVE"
    }
  ]
}
```

---

## Meta Ads MCP Contract

### 1. get_campaign_data

**Fetch campaign performance metrics from Meta Ads.**

```yaml
endpoint: GET /campaigns/{campaign_id}/insights
 MCP: meta-ads
```

**Request:**

```json
{
  "campaign_id": "fb_987654",
  "start_date": "2024-01-01",
  "end_date": "2024-01-30",
  "metrics": [
    "roas",
    "spend",
    "purchase",
    "impressions",
    "reach",
    "ctr",
    "cpc",
    "frequency"
  ],
  "level": "campaign"
}
```

**Response:**

```json
{
  "campaign_id": "fb_987654",
  "campaign_name": "Brand Awareness Q1",
  "currency": "USD",
  "daily_metrics": [
    {
      "date": "2024-01-01",
      "roas": 1.89,
      "roas_ci_lower": 1.65,
      "roas_ci_upper": 2.13,
      "spend": 350.00,
      "purchase": 66,
      "impressions": 120000,
      "reach": 85000,
      "ctr": 0.0150,
      "cpc": 0.42,
      "frequency": 1.4
    }
  ],
  "data_quality_score": 0.92,
  "last_updated": "2024-01-31T08:00:00Z",
  "platform": "meta_ads"
}
```

---

### 2. update_campaign_budget

**Update Meta campaign budget. HIGH-STAKES → Human approval required.**

```yaml
endpoint: PUT /campaigns/{campaign_id}
 MCP: meta-ads
 auth: APPROVAL_TOKEN required
```

**Request:**

```json
{
  "campaign_id": "fb_987654",
  "daily_budget": 500.00,
  "approval_token": "tok_def456_signature_uvw",
  "reason": "Budget reallocation per budget_allocator v1"
}
```

**Response:**

```json
{
  "success": true,
  "campaign_id": "fb_987654",
  "previous_daily_budget": 400.00,
  "new_daily_budget": 500.00,
  "change_amount": 100.00,
  "change_pct": 25.0,
  "applied_at": "2024-01-31T09:15:00Z",
  "approval_token": "tok_def456_signature_uvw"
}
```

---

## Internal MAIAgent API

### 1. POST /hypotheses

**Queue a new hypothesis for validation.**

```yaml
endpoint: POST /hypotheses
 auth: INTERNAL (MAIAgent only)
```

**Request:**

```json
{
  "campaign_id": "gads_123456",
  "description": "Weekend audiences have higher intent — increase bid multiplier by 15%",
  "type": "bid_adjustment",
  "confidence": 0.72,
  "expected_effect_size": 0.15,
  "candidate_explanations": [
    {
      "explanation": "Weekend users are more likely to convert",
      "confidence": 0.72,
      "how_to_validate": "A/B test: weekend vs weekday bid multipliers"
    }
  ],
  "anomaly_flags": ["ROAS_BELOW_EXPECTED"],
  "triggered_by": "inner_loop_daily"
}
```

**Response:**

```json
{
  "hypothesis_id": "hyp_001",
  "status": "pending",
  "queue_position": 12,
  "estimated_review_date": "2024-02-05T08:00:00Z",
  "created_at": "2024-01-31T08:00:00Z"
}
```

---

### 2. GET /hypotheses/{hypothesis_id}

**Get hypothesis status and validation results.**

```yaml
endpoint: GET /hypotheses/{hypothesis_id}
```

**Response:**

```json
{
  "hypothesis_id": "hyp_001",
  "campaign_id": "gads_123456",
  "description": "Weekend audiences have higher intent",
  "status": "validated",
  "validation": {
    "passed_all_gates": true,
    "gate_results": {
      "data_quality": {"passed": true, "score": 0.95},
      "confounds": {"passed": true, "confounds": []},
      "significance": {"passed": true, "p_value": 0.023, "cohens_d": 0.31},
      "replication": {"passed": true, "segments": 3, "periods": 2}
    }
  },
  "recommended_action": "queue_for_outer_loop",
  "created_at": "2024-01-31T08:00:00Z",
  "validated_at": "2024-02-01T10:30:00Z"
}
```

---

### 3. POST /model-updates

**Submit a model update proposal for human review.**

```yaml
endpoint: POST /model-updates
 auth: INTERNAL (Outer loop only)
```

**Request:**

```json
{
  "type": "lora_weights",
  "target_skill": "budget_allocator",
  "changes": {
    "weights": "base64_encoded_weights...",
    "version": "v1.2.0"
  },
  "evidence": {
    "p_value": 0.023,
    "cohens_d": 0.31,
    "effect_size": 0.15,
    "replicated_segments": 3,
    "persistence_days": 21
  },
  "risk_assessment": {
    "risk_if_approved": "Low — small parameter change",
    "risk_if_rejected": "Medium — missing ROAS improvement"
  },
  "rollback_procedure": "Revert to previous LoRA weights",
  "affected_campaigns": ["gads_123456", "fb_987654"]
}
```

**Response:**

```json
{
  "model_update_id": "mu_001",
  "status": "pending_approval",
  "submitted_at": "2024-02-01T10:30:00Z",
  "approval_deadline": "2024-02-01T14:30:00Z",
  "approval_url": "https://slack.com/.../mu_001"
}
```

---

## n8n Webhook Contracts

### 1. /mais/execute

**Webhook for MAIAgent → n8n execution.**

```yaml
endpoint: POST /mais/execute
 auth: APPROVAL_TOKEN (HMAC signature)
```

**Request:**

```json
{
  "token": "tok_abc123_signature_xyz",
  "action": "update_bid_multiplier",
  "parameters": {
    "campaign_id": "gads_123456",
    "bid_multiplier": 1.15
  },
  "timestamp": "2024-01-31T09:00:00Z",
  "callback_url": "https://mais.internal/webhooks/execution-complete"
}
```

**Response:**

```json
{
  "execution_id": "exec_001",
  "status": "queued",
  "estimated_completion": "2024-01-31T09:00:05Z"
}
```

---

### 2. /mais/execution-complete

**Callback from n8n after execution completes.**

```yaml
endpoint: POST /mais/webhooks/execution-complete
 auth: INTERNAL (n8n only)
```

**Request:**

```json
{
  "execution_id": "exec_001",
  "status": "success",
  "result": {
    "campaign_id": "gads_123456",
    "new_bid": 1.15,
    "applied_at": "2024-01-31T09:00:03Z"
  },
  "duration_ms": 3000,
  "timestamp": "2024-01-31T09:00:03Z"
}
```

**Error Response:**

```json
{
  "execution_id": "exec_001",
  "status": "failed",
  "error": {
    "code": "PLATFORM_ERROR",
    "message": "Campaign budget exhausted"
  },
  "duration_ms": 1500,
  "timestamp": "2024-01-31T09:00:01Z"
}
```

---

## Knowledge Graph API

### 1. POST /nodes/campaign

**Create or update a campaign node.**

```yaml
endpoint: POST /nodes/campaign
 auth: INTERNAL
```

**Request:**

```json
{
  "id": "gads_123456",
  "name": "Summer Sale 2024",
  "brand_id": "brand_acme",
  "platform": "google_ads",
  "start_date": "2024-06-01",
  "end_date": "2024-08-31",
  "budget_total": 50000.00,
  "objective": "roas",
  "status": "active"
}
```

---

### 2. POST /relationships

**Create a relationship between nodes.**

```yaml
endpoint: POST /relationships
 auth: INTERNAL
```

**Request:**

```json
{
  "from_id": "gads_123456",
  "from_type": "campaign",
  "to_id": "aud_seg_001",
  "to_type": "audience_segment",
  "relationship_type": "TARGETS",
  "properties": {
    "since": "2024-06-01",
    "bid_modifier": 1.0
  }
}
```

---

### 3. GET /causal-chain/{campaign_id}

**Get complete causal chain for a campaign.**

```yaml
endpoint: GET /causal-chain/{campaign_id}
```

**Response:**

```json
{
  "campaign": {
    "id": "gads_123456",
    "name": "Summer Sale 2024",
    "status": "active"
  },
  "audiences": [
    {"id": "aud_seg_001", "name": "Tech Buyers"}
  ],
  "creatives": [
    {"id": "cre_001", "name": "Hero Image v1", "type": "image"}
  ],
  "channels": [
    {"id": "ch_001", "platform": "google_ads", "status": "active"}
  ],
  "outcomes": [
    {
      "id": "out_001",
      "date": "2024-01-15",
      "metric_type": "roas",
      "raw_value": 2.34,
      "denoised_value": 2.28
    }
  ],
  "similar_campaigns": [
    {"id": "gads_111111", "similarity": 0.87}
  ]
}
```

---

## Vector Store API

### 1. POST /documents/campaign

**Add campaign document to vector store.**

```yaml
endpoint: POST /documents/campaign
 auth: INTERNAL
```

**Request:**

```json
{
  "campaign_id": "gads_123456",
  "content": "Summer sale campaign targeting tech buyers with product focus messaging. Ran in Q2 2024. ROAS 2.34.",
  "metadata": {
    "brand": "acme",
    "vertical": "saas",
    "objective": "roas",
    "platform": "google_ads",
    "kg_node_id": "gads_123456"
  }
}
```

---

### 2. POST /search/hybrid

**Hybrid search across vector and keyword matching.**

```yaml
endpoint: POST /search/hybrid
```

**Request:**

```json
{
  "query": "tech buyers SaaS ROAS campaigns",
  "collection": "campaigns",
  "filters": {
    "brand": "acme",
    "platform": "google_ads"
  },
  "top_k": 10
}
```

**Response:**

```json
{
  "results": [
    {
      "id": "gads_123456",
      "score": 0.92,
      "content": "Summer sale campaign targeting tech buyers...",
      "metadata": {
        "brand": "acme",
        "vertical": "saas"
      }
    }
  ],
  "query_time_ms": 23
}
```

---

## Approval Token Contract

### Token Structure

```json
{
  "token_id": "tok_abc123",
  "action": "update_bid_multiplier",
  "parameters": {
    "campaign_id": "gads_123456",
    "bid_multiplier": 1.15
  },
  "issued_at": "2024-01-31T09:00:00Z",
  "expires_at": "2024-01-31T10:00:00Z",
  "auto_approved": false,
  "confidence": 0.72,
  "signature": "hmac_sha256_signature"
}
```

### Validation Request

```yaml
endpoint: POST /tokens/validate
```

**Request:**

```json
{
  "token_id": "tok_abc123",
  "signature": "hmac_sha256_signature"
}
```

**Response:**

```json
{
  "valid": true,
  "action": "update_bid_multiplier",
  "parameters": {
    "campaign_id": "gads_123456",
    "bid_multiplier": 1.15
  },
  "auto_approved": false
}
```

---

## Error Codes Reference

```
┌─────────────────────────────────────────────────────────────────┐
│                    ERROR CODES                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  400 BAD_REQUEST           — Malformed request                │
│  401 UNAUTHORIZED          — Missing or invalid auth           │
│  403 FORBIDDEN             — Action requires approval          │
│  404 NOT_FOUND             — Resource doesn't exist            │
│  409 CONFLICT              — State conflict (e.g., duplicate)  │
│  422 UNPROCESSABLE         — Validation failed                 │
│  429 RATE_LIMITED          — Too many requests                 │
│  500 INTERNAL_ERROR        — Server error                      │
│  503 SERVICE_UNAVAILABLE   — Dependency unavailable            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
