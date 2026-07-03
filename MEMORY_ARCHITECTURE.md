# Memory Architecture — Knowledge Graph + Vector + Episodic

**Related to:** ARCHITECTURE.md Section 4

---

## Overview

MAIS uses three complementary memory systems, each optimized for different access patterns:

```
┌─────────────────────────────────────────────────────────────────┐
│                    MEMORY ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     │
│  │Knowledge    │◄──►│Vector      │     │SQLite/     │     │
│  │Graph        │  │ │Store       │     │Episodic    │     │
│  │             │  │ │            │     │            │     │
│  │REASONING:   │  │ │RETRIEVAL:  │     │AUDIT:      │     │
│  │• Entities   │  │ │• Unstruct.  │     │• Session   │     │
│  │• Relations  │  │ │  text      │     │  logs     │     │
│  │• Causal    │  │ │• Creative  │     │• Model     │     │
│  │  chains     │  │ │  copy      │     │  updates  │     │
│  │• Audit      │  │ │• Strategy  │     │• Feedback  │     │
│  │  trail      │  │ │  docs      │     │• Raw data  │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                                 │
│  Each system:                                                     │
│  - Optimized for different query patterns                        │
│  - Hybrid fusion for cross-system queries                       │
│  - Independent scaling                                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Knowledge Graph

### 1.1 Schema

```python
# Core Node Types

class CampaignNode:
    id: str  # UUID
    name: str
    brand_id: str
    start_date: date
    end_date: date | None
    status: Literal["active", "paused", "completed", "archived"]
    budget_total: Decimal
    budget_spent: Decimal
    objective: Literal["roas", "cpa", "awareness", "traffic"]
    platform: Literal["google", "meta", "tiktok", "linkedin"]
    created_at: datetime
    updated_at: datetime

class AudienceSegmentNode:
    id: str
    name: str
    demographics: dict  # age_range, gender, location, income
    interests: list[str]
    behavioral_signals: list[str]
    estimated_size: int  # approx reach
    canonical_name: str  # for entity resolution

class CreativeAssetNode:
    id: str
    type: Literal["image", "video", "carousel", "text"]
    url: str | None
    thumbnail_url: str | None
    headline: str | None
    copy_variants: list[str]
    performance_summary: dict  # {ctr, conversions, roas}

class ChannelNode:
    id: str
    platform: str
    account_id: str
    campaign_id: str  # FK
    status: str
    daily_budget: Decimal
    current_bid: Decimal

class OutcomeMetricNode:
    id: str
    campaign_id: str  # FK
    date: date
    metric_type: Literal["roas", "cpa", "ctr", "impressions", "spend", "conversions"]
    raw_value: float
    denoised_value: float | None  # after causal cleaning
    ci_lower: float | None
    ci_upper: float | None

# Relationship Types

class RelationshipTypes:
    TARGETS = "TARGETS"  # Campaign → AudienceSegment
    USES = "USES"  # Campaign → CreativeAsset
    RUNS_ON = "RUNS_ON"  # Campaign → Channel
    PRODUCES = "PRODUCES"  # Campaign → OutcomeMetric
    SIMILAR_TO = "SIMILAR_TO"  # AudienceSegment → AudienceSegment (similarity: float)
    A_B_TESTED_WITH = "A_B_TESTED_WITH"  # CreativeAsset → CreativeAsset
    COMPETES_WITH = "COMPETES_WITH"  # Brand → Brand
    EMPLOYS_STRATEGY = "EMPLOYS_STRATEGY"  # Campaign → StrategyNode
    VALIDATED_CAUSAL = "VALIDATED_CAUSAL"  # StrategyNode → OutcomeNode
```

### 1.2 Implementation

```python
import networkx as nx
from typing import Optional
import json

class MarketingKnowledgeGraph:
    """
    Primary knowledge store for structured marketing entities and relationships.
    Optimized for traversals, causal reasoning, and audit trails.
    """

    def __init__(self, db_path: str = "data/knowledge_graph.db"):
        self.graph = nx.DiGraph()
        self.db_path = db_path
        self._load_or_create()

    # ─────────────────────────────────────────────────────────────
    # NODE OPERATIONS
    # ─────────────────────────────────────────────────────────────

    def add_campaign(self, campaign: CampaignNode) -> str:
        """Add or update a campaign node."""
        self.graph.add_node(
            campaign.id,
            **asdict(campaign),
            node_type="campaign"
        )
        self._persist()
        return campaign.id

    def get_campaign(self, campaign_id: str) -> Optional[CampaignNode]:
        """Retrieve campaign by ID."""
        node = self.graph.nodes.get(campaign_id)
        return CampaignNode(**node) if node else None

    # ─────────────────────────────────────────────────────────────
    # RELATIONSHIP OPERATIONS
    # ─────────────────────────────────────────────────────────────

    def add_relationship(self, from_id: str, to_id: str, rel_type: str, properties: dict = None):
        """Add directed relationship between nodes."""
        self.graph.add_edge(from_id, to_id, relationship=rel_type, **(properties or {}))
        self._persist()

    def get_targets(self, campaign_id: str) -> list[AudienceSegmentNode]:
        """Get all audience segments targeted by a campaign."""
        segment_ids = self.graph.successors(campaign_id)
        return [AudienceSegmentNode(**self.graph.nodes[sid]) for sid in segment_ids
                if self.graph.nodes[sid].get("node_type") == "audience_segment"]

    def get_campaign_outcomes(self, campaign_id: str, metric_type: str = None) -> list[OutcomeMetricNode]:
        """Get all outcomes for a campaign."""
        outcome_ids = self.graph.successors(campaign_id)
        outcomes = []
        for oid in outcome_ids:
            node = self.graph.nodes[oid]
            if node.get("node_type") == "outcome_metric":
                if metric_type is None or node.get("metric_type") == metric_type:
                    outcomes.append(OutcomeMetricNode(**node))
        return outcomes

    # ─────────────────────────────────────────────────────────────
    # CAUSAL TRAVERSAL
    # ─────────────────────────────────────────────────────────────

    def get_causal_chain(self, campaign_id: str) -> dict:
        """
        Traverse: Campaign → Audience → Creative → Channel → Outcomes
        Returns structured causal chain for reasoning.
        """
        chain = {
            "campaign": self.get_campaign(campaign_id),
            "audiences": self.get_targets(campaign_id),
            "creatives": self._get_creatives(campaign_id),
            "channels": self._get_channels(campaign_id),
            "outcomes": self.get_campaign_outcomes(campaign_id),
            "similar_campaigns": self._find_similar_campaigns(campaign_id)
        }
        return chain

    def get_strategy_effectiveness(self, strategy_id: str) -> dict:
        """
        For a given strategy pattern, find all campaigns that employed it
        and their aggregated outcomes.
        """
        campaigns = self._get_campaigns_using_strategy(strategy_id)
        all_outcomes = []
        for c in campaigns:
            all_outcomes.extend(self.get_campaign_outcomes(c.id))

        return {
            "strategy_id": strategy_id,
            "campaign_count": len(campaigns),
            "aggregated_roas": self._mean_roas(all_outcomes),
            "ci_95": self._bootstrap_ci(all_outcomes),
            "outcome_count": len(all_outcomes)
        }

    # ─────────────────────────────────────────────────────────────
    # ENTITY RESOLUTION
    # ─────────────────────────────────────────────────────────────

    def suggest_entity_merge(self, entity1_id: str, entity2_id: str, similarity: float) -> dict:
        """
        Suggest merging two entities. Requires human approval.
        Returns merge proposal with confidence score.
        """
        return {
            "entity1": self.graph.nodes[entity1_id],
            "entity2": self.graph.nodes[entity2_id],
            "similarity_score": similarity,
            "shared_relationships": list(nx.common_neighbors(self.graph, entity1_id, entity2_id)),
            "requires_human_review": True,  # Always requires human
            "merge_proposal_id": generate_uuid()
        }

    def apply_merge(self, proposal_id: str, approved: bool, merged_properties: dict = None):
        """
        Execute or reject entity merge proposal.
        """
        proposal = self._get_merge_proposal(proposal_id)
        if approved:
            # Create new merged node
            merged = self._merge_entities(proposal, merged_properties)
            # Redirect all edges
            # Archive original nodes (don't delete)
            self._archive_entities(proposal["entity1"], proposal["entity2"])
        else:
            # Log rejection
            self._log_merge_rejection(proposal_id)
```

### 1.3 Entity Resolution

```python
class EntityResolver:
    """
    Handles canonical name resolution and entity merging.
    'Meta' = 'Facebook' = 'FB' = 'Facebook Ads'
    """

    CANONICAL_NAMES = {
        "facebook": "meta",
        "fb": "meta",
        "facebook ads": "meta",
        "instagram": "meta",
        "google ads": "google",
        "adwords": "google",
        "gdn": "google",
        "youtube": "google",
    }

    def __init__(self, embedding_model, threshold: float = 0.85):
        self.embedding_model = embedding_model
        self.threshold = threshold
        self.vector_store = VectorStore()  # For similarity matching

    async def resolve(self, entity_text: str, entity_type: str) -> str:
        """
        Given a raw entity mention, return canonical ID.
        """
        # 1. Check exact canonical table
        canonical_key = self.CANONICAL_NAMES.get(entity_text.lower().strip())
        if canonical_key:
            return await self._get_canonical_id(canonical_key, entity_type)

        # 2. Check embedding similarity
        embedding = self.embedding_model.embed(entity_text)
        candidates = await self.vector_store.search(
            embedding,
            filter={"entity_type": entity_type},
            top_k=5
        )

        if candidates[0].similarity > self.threshold:
            return candidates[0].entity_id

        # 3. Suggest new entity (human review)
        return await self._suggest_new_entity(entity_text, entity_type, embedding)

    async def suggest_merge(self, entity1_id: str, entity2_id: str) -> dict:
        """
        Check if two entities should be merged.
        Requires human approval before merge.
        """
        emb1 = await self._get_embedding(entity1_id)
        emb2 = await self._get_embedding(entity2_id)
        similarity = cosine_similarity(emb1, emb2)

        if similarity > self.threshold:
            return {
                "should_merge": True,
                "confidence": similarity,
                "requires_review": True  # Always human review
            }
        return {"should_merge": False, "confidence": similarity}
```

---

## 2. Vector Store

### 2.1 Schema

```python
# Document Types in Vector Store

class CampaignDocument:
    entity_id: str  # Links to KG node
    entity_type: Literal["campaign", "audience", "creative", "strategy", "content"]
    content: str  # Natural language description
    embedding: list[float]
    metadata: dict

class CreativeDocument:
    entity_id: str
    copy_text: str  # Ad copy variants
    headline: str
    description: str
    call_to_action: str
    visual_tags: list[str]
    performance_context: str  # "Worked well for X audience in Y vertical"

class StrategyDocument:
    entity_id: str
    strategy_name: str
    reasoning_chain: str  # Why this strategy was chosen
    hypothesis: str
    expected_outcome: str
    actual_outcome: str | None
    lessons_learned: str | None
```

### 2.2 Implementation

```python
import chromadb
from sentence_transformers import SentenceTransformer

class MarketingVectorStore:
    """
    ChromaDB-based vector store for semantic retrieval.
    Hybrid search: vector similarity + metadata filtering.
    """

    def __init__(self, persist_dir: str = "data/vector_store"):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collections = {
            'campaigns': self.client.get_or_create_collection("campaigns"),
            'audiences': self.client.get_or_create_collection("audiences"),
            'creatives': self.client.get_or_create_collection("creatives"),
            'strategies': self.client.get_or_create_collection("strategies"),
        }

    def add_campaign_description(
        self,
        campaign_id: str,
        description: str,
        structured_data: dict
    ):
        """Add campaign with both embedding and structured metadata."""
        embedding = self.embedding_model.encode(description)

        self.collections['campaigns'].add(
            documents=[description],
            embeddings=[embedding.tolist()],
            metadatas=[{
                "campaign_id": campaign_id,
                "brand": structured_data.get("brand"),
                "vertical": structured_data.get("vertical"),
                "objective": structured_data.get("objective"),
                "platform": structured_data.get("platform"),
                "kg_node_id": structured_data.get("kg_node_id")
            }],
            ids=[campaign_id]
        )

    async def hybrid_search(
        self,
        query: str,
        collection: str,
        filters: dict = None,
        top_k: int = 10
    ) -> list[dict]:
        """
        Hybrid search: vector similarity + metadata filtering.
        Uses weighted scoring: 0.7 * semantic + 0.3 * keyword match.
        """
        # Vector search
        query_embedding = self.embedding_model.encode(query)
        vector_results = self.collections[collection].query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k * 2,
            where=filters,
            include=["documents", "metadatas", "distances"]
        )

        # Keyword search (BM25 on raw text)
        bm25_scores = self._bm25_search(
            query,
            [d for d in vector_results.get("documents", [[]])[0]],
            top_k
        )

        # Fuse results
        fused = self._fuse_scores(
            vector_results,
            bm25_scores,
            vector_weight=0.7,
            keyword_weight=0.3
        )

        return fused

    def _fuse_scores(
        self,
        vector_results: dict,
        bm25_scores: dict,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> list[dict]:
        """Combine vector and keyword scores."""
        # Build unified score map
        all_ids = set()
        for ids in vector_results.get("ids", [[]]):
            all_ids.update(ids)

        scored = []
        for doc_id in all_ids:
            idx = vector_results["ids"][0].index(doc_id)
            vec_score = 1 - vector_results["distances"][0][idx]

            bm25_score = bm25_scores.get(doc_id, 0.0)
            fused = vector_weight * vec_score + keyword_weight * bm25_score

            scored.append({
                "id": doc_id,
                "score": fused,
                "document": vector_results["documents"][0][idx],
                "metadata": vector_results["metadatas"][0][idx]
            })

        return sorted(scored, key=lambda x: x["score"], reverse=True)

    # ─────────────────────────────────────────────────────────────
    # QUERY PATTERNS
    # ─────────────────────────────────────────────────────────────

    async def find_similar_campaigns(self, campaign_id: str, top_k: int = 5) -> list[dict]:
        """Find campaigns similar to this one."""
        # Fetch from KG to get description
        kg = MarketingKnowledgeGraph()
        campaign = kg.get_campaign(campaign_id)
        description = self._campaign_to_description(campaign)

        return await self.hybrid_search(
            query=description,
            collection="campaigns",
            filters={"brand": campaign.brand_id},
            top_k=top_k
        )

    async def find_winning_creatives_for_audience(
        self,
        audience_segment: str,
        metric: str = "roas",
        top_k: int = 10
    ) -> list[dict]:
        """Find creatives that worked for similar audiences."""
        query = f"creative ad copy that performed well for {audience_segment} audience in marketing campaigns"
        return await self.hybrid_search(
            query=query,
            collection="creatives",
            filters={"metric": metric},
            top_k=top_k
        )
```

---

## 3. Episodic Store (SQLite)

### 3.1 Schema

```python
from sqlalchemy import create_engine, Column, String, Float, DateTime, Boolean, Text, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class SessionLog(Base):
    __tablename__ = "session_logs"

    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    agent_id = Column(String, nullable=False)
    query = Column(Text, nullable=False)
    response = Column(Text)
    reasoning_chain = Column(Text)  # JSON
    latency_ms = Column(Integer)
    model_used = Column(String)  # small / claude / human
    confidence = Column(Float)

class Hypothesis(Base):
    __tablename__ = "hypotheses"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    description = Column(Text, nullable=False)
    confidence = Column(Float)
    status = Column(String)  # pending / approved / rejected / validated
    evidence = Column(Text)  # JSON: p_value, effect_size, etc.
    reviewed_by = Column(String)
    reviewed_at = Column(DateTime)

class ExperimentRun(Base):
    __tablename__ = "experiment_runs"

    id = Column(String, primary_key=True)
    hypothesis_id = Column(String, nullable=False, index=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    status = Column(String)  # running / completed / aborted
    parameters = Column(Text)  # JSON
    result = Column(Text)  # JSON: denoised_roas, ci_width, etc.
    replication_segments = Column(Text)  # JSON: list of segment IDs

class ModelUpdate(Base):
    __tablename__ = "model_updates"

    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    what_changed = Column(Text, nullable=False)  # JSON: params, weights, etc.
    approved_by = Column(String, nullable=False)
    approval_reason = Column(Text)
    p_value = Column(Float)
    effect_size = Column(Float)
    status = Column(String)  # pending / approved / deployed / rolled_back
    rollback_trigger = Column(String)
    shadow_evaluation = Column(Text)  # JSON: results from shadow deploy

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String, primary_key=True)
    session_id = Column(String, index=True)
    timestamp = Column(DateTime, nullable=False)
    is_positive = Column(Boolean)
    feedback_text = Column(Text)
    campaign_id = Column(String, index=True)
    variant_id = Column(String)
```

### 3.2 Implementation

```python
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager

class EpisodicStore:
    """
    SQLite-based episodic memory for audit trails and session logs.
    Retention: 90 days for sessions, permanent for experiments/models.
    """

    def __init__(self, db_path: str = "data/episodic.db"):
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    @asynccontextmanager
    async def session(self):
        """Async session context manager."""
        s = self.Session()
        try:
            yield s
            s.commit()
        except:
            s.rollback()
            raise
        finally:
            s.close()

    # ─────────────────────────────────────────────────────────────
    # LOGGING
    # ─────────────────────────────────────────────────────────────

    async def log_session(
        self,
        agent_id: str,
        query: str,
        response: str,
        reasoning_chain: dict,
        model_used: str,
        confidence: float,
        latency_ms: int
    ):
        """Log a single agent session."""
        async with self.session() as s:
            s.add(SessionLog(
                id=generate_uuid(),
                timestamp=datetime.utcnow(),
                agent_id=agent_id,
                query=query,
                response=response,
                reasoning_chain=json.dumps(reasoning_chain),
                model_used=model_used,
                confidence=confidence,
                latency_ms=latency_ms
            ))

    async def log_model_update(self, update: ModelUpdate):
        """Log a model update with full audit trail."""
        async with self.session() as s:
            s.add(update)

    # ─────────────────────────────────────────────────────────────
    # RETRIEVAL
    # ─────────────────────────────────────────────────────────────

    async def get_recent_sessions(
        self,
        agent_id: str = None,
        limit: int = 100
    ) -> list[SessionLog]:
        """Get recent sessions, optionally filtered by agent."""
        async with self.session() as s:
            q = s.query(SessionLog)
            if agent_id:
                q = q.filter(SessionLog.agent_id == agent_id)
            return q.order_by(SessionLog.timestamp.desc()).limit(limit).all()

    async def get_hypothesis_for_review(
        self,
        min_confidence: float = 0.6
    ) -> list[Hypothesis]:
        """Get hypotheses pending outer loop review."""
        async with self.session() as s:
            return s.query(Hypothesis).filter(
                Hypothesis.status == "pending",
                Hypothesis.confidence >= min_confidence
            ).order_by(Hypothesis.confidence.desc()).all()
```

---

## 4. Cross-System Data Flow

### 4.1 New Campaign Creation

```python
async def on_new_campaign(campaign_data: dict):
    """
    Flow when a new campaign is created.
    Updates all three memory systems.
    """
    campaign_id = generate_uuid()

    # 1. Knowledge Graph: Structured entity
    kg = MarketingKnowledgeGraph()
    campaign_node = CampaignNode(
        id=campaign_id,
        name=campaign_data["name"],
        brand_id=campaign_data["brand_id"],
        start_date=campaign_data["start_date"],
        objective=campaign_data["objective"],
        budget_total=campaign_data["budget"],
        platform=campaign_data["platform"]
    )
    kg.add_campaign(campaign_node)

    # Link relationships
    for segment_id in campaign_data["audience_ids"]:
        kg.add_relationship(campaign_id, segment_id, "TARGETS")
    for creative_id in campaign_data["creative_ids"]:
        kg.add_relationship(campaign_id, creative_id, "USES")
    for channel_id in campaign_data["channel_ids"]:
        kg.add_relationship(campaign_id, channel_id, "RUNS_ON")

    # 2. Vector Store: Unstructured description
    vs = MarketingVectorStore()
    description = _campaign_to_description(campaign_node)
    await vs.add_campaign_description(
        campaign_id=campaign_id,
        description=description,
        structured_data={
            "brand": campaign_data["brand_id"],
            "vertical": campaign_data.get("vertical"),
            "objective": campaign_data["objective"],
            "kg_node_id": campaign_id
        }
    )

    # 3. Episodic Store: Audit log
    es = EpisodicStore()
    await es.log_session(
        agent_id="system",
        query=f"Created campaign: {campaign_data['name']}",
        response=f"Campaign {campaign_id} created with {len(campaign_data['audience_ids'])} audiences",
        reasoning_chain={"action": "campaign_creation"},
        model_used="system",
        confidence=1.0,
        latency_ms=0
    )
```

### 4.2 Query: "What worked for DTC brands?"

```python
async def query_what_worked_for_dtc(query: str) -> dict:
    """
    Hybrid query across all three memory systems.
    """
    # 1. Vector store: Semantic retrieval
    vs = MarketingVectorStore()
    vector_results = await vs.hybrid_search(
        query=f"{query} DTC brand campaigns",
        collection="campaigns",
        filters={"vertical": "dtc"},
        top_k=10
    )

    # 2. For each result, enrich from Knowledge Graph
    kg = MarketingKnowledgeGraph()
    enriched_results = []
    for result in vector_results:
        campaign_id = result["metadata"]["campaign_id"]
        kg_chain = kg.get_causal_chain(campaign_id)

        enriched_results.append({
            "campaign": kg_chain["campaign"],
            "audiences": kg_chain["audiences"],
            "outcomes": kg_chain["outcomes"],
            "similar_campaigns": kg_chain["similar_campaigns"],
            "vector_score": result["score"],
            "semantic_context": result["document"]
        })

    # 3. Fusion: Rank by outcome quality + semantic relevance
    ranked = sorted(
        enriched_results,
        key=lambda x: _mean_roas(x["outcomes"]) * x["vector_score"],
        reverse=True
    )

    return {
        "query": query,
        "results": ranked[:5],
        "summary": _generate_summary(ranked[:5]),
        "top_patterns": _extract_patterns(ranked[:5])
    }
```

---

## 5. Retention and Maintenance

```
┌─────────────────────────────────────────────────────────────────┐
│                    RETENTION POLICY                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  KNOWLEDGE GRAPH:                                                │
│  - Nodes: Permanent (archived after 2 years inactive)           │
│  - Relationships: Permanent                                     │
│  - Merge history: Permanent                                    │
│  - Prune: Archive nodes with no activity > 2 years            │
│                                                                 │
│  VECTOR STORE:                                                  │
│  - Documents: Re-indexed every 6 months                          │
│  - Embeddings: Recomputed when embedding model updates         │
│  - Delete: Only when source KG node is archived               │
│                                                                 │
│  EPISODIC STORE:                                               │
│  - Session logs: 90 days (for debugging)                      │
│  - Hypotheses: Until resolved or archived                      │
│  - Experiments: Permanent                                       │
│  - Model updates: Permanent (audit requirement)                 │
│  - Feedback: 2 years                                          │
│                                                                 │
│  MONTHLY MAINTENANCE JOB:                                      │
│  - Archive inactive KG nodes                                    │
│  - Re-index vector store                                       │
│  - Vacuum SQLite for storage optimization                       │
│  - Report storage metrics                                      │
└─────────────────────────────────────────────────────────────────┘
```
