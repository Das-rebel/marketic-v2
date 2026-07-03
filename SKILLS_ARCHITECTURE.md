# Skills Architecture

**Related to:** ARCHITECTURE.md Section 8

---

## Overview

Every skill is a production-grade software package: `SKILL.md` + `skill.py` + `skill_test.py` + `skill_config.py` + `examples/`. Skills are not documentation — they are executable code with tests and examples.

```
┌─────────────────────────────────────────────────────────────────┐
│                    SKILLS ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              SKILL PACKAGE STRUCTURE                        │  │
│  │                                                           │  │
│  │  my_skill/                                              │  │
│  │  ├── SKILL.md              ← Description + usage          │  │
│  │  ├── skill.py              ← Main implementation         │  │
│  │  ├── skill_test.py         ← Unit + integration tests   │  │
│  │  ├── skill_config.py       ← Default config + schemas     │  │
│  │  └── examples/             ← Usage examples              │  │
│  │      ├── basic_usage.py                                 │  │
│  │      └── advanced_usage.py                              │  │
│  │                                                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↑                                  │
│                              │ execute()                       │
│                              ▼                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              SKILL EXECUTOR                                │  │
│  │                                                           │  │
│  │  Validates input → Runs skill → Returns structured result │  │
│  │  Circuit breaker: 3 failures → skip + alert              │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Skill Interface Contract

```python
# skill_interface.py

from abc import ABC, abstractmethod
from typing import Any, TypedDict
from pydantic import BaseModel, Field

class SkillInput(BaseModel):
    """Base class for all skill inputs."""
    class Config:
        extra = "forbid"

class SkillOutput(BaseModel):
    """Base class for all skill outputs."""
    success: bool
    data: dict | None = None
    error: str | None = None
    metadata: dict = Field(default_factory=dict)

class SkillConfig(BaseModel):
    """Base class for skill configuration."""
    timeout_seconds: int = 30
    max_retries: int = 3
    circuit_breaker_threshold: int = 3

class Skill(ABC):
    """
    Base class for all MAIAgent skills.
    All skills MUST implement this interface.
    """

    # Class-level attributes (override in subclass)
    name: str = "base_skill"
    description: str = "Base skill"
    version: str = "1.0.0"
    input_schema: type[SkillInput] = SkillInput
    output_schema: type[SkillOutput] = SkillOutput
    config_schema: type[SkillConfig] = SkillConfig

    def __init__(self, config: SkillConfig | None = None):
        self.config = config or self.config_schema()
        self._failure_count = 0
        self._circuit_open = False

    # ─────────────────────────────────────────────────────────────
    # REQUIRED METHODS (must implement)
    # ─────────────────────────────────────────────────────────────

    @abstractmethod
    async def execute(self, input_data: SkillInput) -> SkillOutput:
        """
        Main execution method. Must be implemented by all skills.
        """
        pass

    @abstractmethod
    def validate_input(self, input_data: dict) -> SkillInput:
        """
        Validate and parse input data.
        Should raise ValidationError if invalid.
        """
        pass

    # ─────────────────────────────────────────────────────────────
    # OPTIONAL METHODS (can override)
    # ─────────────────────────────────────────────────────────────

    async def pre_execute(self, input_data: SkillInput) -> SkillInput:
        """
        Hook called before execute(). Return modified input.
        Default: return input unchanged.
        """
        return input_data

    async def post_execute(
        self,
        input_data: SkillInput,
        output: SkillOutput
    ) -> SkillOutput:
        """
        Hook called after execute(). Return modified output.
        Default: return output unchanged.
        """
        return output

    async def on_failure(
        self,
        input_data: SkillInput,
        error: Exception
    ) -> SkillOutput:
        """
        Called when execute() raises an exception.
        Return a SkillOutput (don't re-raise).
        """
        self._failure_count += 1

        if self._failure_count >= self.config.circuit_breaker_threshold:
            self._circuit_open = True
            await self._alert_circuit_breaker_open()

        return SkillOutput(
            success=False,
            error=str(error),
            metadata={"failure_count": self._failure_count}
        )

    # ─────────────────────────────────────────────────────────────
    # CIRCUIT BREAKER
    # ─────────────────────────────────────────────────────────────

    def is_available(self) -> bool:
        """Check if skill is available (circuit not open)."""
        return not self._circuit_open

    async def _alert_circuit_breaker_open(self):
        """Alert when circuit breaker opens."""
        await notification.send_alert(
            skill=self.name,
            message=f"Circuit breaker opened after {self._failure_count} failures",
            severity="high"
        )

    def reset_circuit(self):
        """Manually reset circuit breaker (after human review)."""
        self._failure_count = 0
        self._circuit_open = False
```

---

## 2. Skill Executor

```python
# skill_executor.py

class SkillExecutor:
    """
    Executes skills with validation, error handling, and circuit breaker.
    """

    def __init__(
        self,
        skill_registry: SkillRegistry,
        circuit_breaker: CircuitBreakerMonitor
    ):
        self.registry = skill_registry
        self.circuit_breaker = circuit_breaker
        self.execution_log = ExecutionLog()

    async def execute_skill(
        self,
        skill_name: str,
        input_data: dict,
        context: ExecutionContext
    ) -> SkillOutput:
        """
        Execute a skill with full lifecycle management.
        """
        # 1. Load skill
        skill = self.registry.get(skill_name)
        if not skill:
            return SkillOutput(
                success=False,
                error=f"Skill '{skill_name}' not found"
            )

        # 2. Check circuit breaker
        if not skill.is_available():
            return SkillOutput(
                success=False,
                error=f"Skill '{skill_name}' circuit breaker is open"
            )

        # 3. Validate input
        try:
            validated_input = skill.validate_input(input_data)
        except ValidationError as e:
            return SkillOutput(
                success=False,
                error=f"Invalid input: {str(e)}"
            )

        # 4. Pre-execute hook
        processed_input = await skill.pre_execute(validated_input)

        # 5. Execute with timeout
        start_time = time.time()
        try:
            output = await asyncio.wait_for(
                skill.execute(processed_input),
                timeout=skill.config.timeout_seconds
            )
        except asyncio.TimeoutError:
            return await skill.on_failure(
                processed_input,
                TimeoutError(f"Skill timed out after {skill.config.timeout_seconds}s")
            )
        except Exception as e:
            output = await skill.on_failure(processed_input, e)

        # 6. Post-execute hook
        final_output = await skill.post_execute(processed_input, output)

        # 7. Log execution
        await self.execution_log.record(
            skill_name=skill_name,
            input=input_data,
            output=final_output,
            duration_ms=(time.time() - start_time) * 1000,
            context=context
        )

        return final_output
```

---

## 3. Skill Registry

```python
# skill_registry.py

class SkillRegistry:
    """
    Registry of all available skills.
    Loads skills from filesystem and manages lifecycle.
    """

    def __init__(self, skills_dir: str = "skills"):
        self.skills_dir = skills_dir
        self._skills: dict[str, type[Skill]] = {}
        self._instances: dict[str, Skill] = {}
        self._load_all_skills()

    def _load_all_skills(self):
        """Load all skills from skills directory."""
        for skill_module in Path(self.skills_dir).iterdir():
            if skill_module.is_dir() and (skill_module / "skill.py").exists():
                self._load_skill(skill_module)

    def _load_skill(self, skill_path: Path):
        """Load a single skill."""
        # Import skill module
        module_name = f"skills.{skill_path.name}.skill"
        module = importlib.import_module(module_name)

        # Find Skill subclass
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and
                issubclass(attr, Skill) and
                attr != Skill):
                self._skills[attr.name] = attr

    def get(self, skill_name: str) -> Skill | None:
        """Get skill instance by name."""
        if skill_name not in self._instances:
            if skill_name not in self._skills:
                return None
            self._instances[skill_name] = self._skills[skill_name]()

        return self._instances[skill_name]

    def list_skills(self) -> list[dict]:
        """List all available skills."""
        return [
            {
                "name": name,
                "description": skill.description,
                "version": skill.version,
                "available": skill.is_available()
            }
            for name, skill in self._skills.items()
        ]
```

---

## 4. Base Skill Implementation

```python
# skills/base_skill.py (example template)

class BaseSkill(Skill):
    """
    Template for implementing a new skill.
    Replace this with your actual skill implementation.
    """

    name = "base_skill"
    description = "Description of what this skill does"
    version = "1.0.0"

    class Input(SkillInput):
        """Skill-specific input schema."""
        query: str = Field(..., description="The input query")
        options: list[str] | None = Field(default=None, description="Optional parameters")

    class Output(SkillOutput):
        """Skill-specific output schema."""
        result: str | None = None
        confidence: float | None = None

    class Config(SkillConfig):
        """Skill-specific configuration."""
        timeout_seconds: int = 60
        model: str = "claude-sonnet-4"

    def validate_input(self, input_data: dict) -> Input:
        """Validate input data against schema."""
        return self.Input(**input_data)

    async def execute(self, input_data: Input) -> Output:
        """
        Main execution logic.
        """
        try:
            # Your skill logic here
            result = await self._do_work(input_data)

            return Output(
                success=True,
                data={"result": result},
                metadata={"skill_version": self.version}
            )

        except Exception as e:
            return Output(
                success=False,
                error=str(e)
            )
```

---

## 5. Marketing Skills Categories

### 5.1 Category Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                    SKILL CATEGORIES                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  AUTORESEARCH (2-3 skills)                                      │
│  ├── hypothesis_generator    ← Generate testable hypotheses      │
│  └── experiment_designer     ← Design A/B tests                 │
│                                                                 │
│  COMPETITIVE (2-3 skills)                                      │
│  ├── competitor_monitor      ← Track competitor activities       │
│  └── competitive_analyzer    ← Analyze competitive gaps          │
│                                                                 │
│  CREATIVE (2-3 skills)                                         │
│  ├── copy_generator         ← Generate ad copy variants         │
│  ├── headline_tester        ← A/B test headlines               │
│  └── creative_optimizer     ← Optimize creative performance     │
│                                                                 │
│  CAMPAIGN (2-3 skills)                                         │
│  ├── budget_allocator       ← Allocate budget across channels    │
│  ├── audience_selector      ← Select audience segments          │
│  └── campaign_launcher     ← Launch campaigns on platforms      │
│                                                                 │
│  PERFORMANCE (2-3 skills)                                       │
│  ├── roas_analyzer          ← Analyze ROAS patterns             │
│  ├── anomaly_detector       ← Detect performance anomalies       │
│  └── attribution_modeler    ← Model attribution                 │
│                                                                 │
│  GROWTH (2-3 skills)                                           │
│  ├── growth_hypothesis      ← Generate growth hypotheses         │
│  └── scaling_predictor      ← Predict scaling outcomes          │
│                                                                 │
│  EVOLUTION (1-2 skills)                                        │
│  └── pattern_learner        ← Learn from outcomes               │
│                                                                 │
│  MEMORY (1-2 skills)                                           │
│  ├── knowledge_graph_writer ← Write to knowledge graph          │
│  └── memory_recaller        ← Recall relevant memories          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Skill Implementation Example: Copy Generator

```python
# skills/copy_generator/skill.py

class CopyGeneratorSkill(Skill):
    """
    Generates ad copy variants using AI.
    """

    name = "copy_generator"
    description = "Generate ad copy variants for campaigns"
    version = "1.0.0"

    class Input(SkillInput):
        campaign_id: str = Field(..., description="Campaign ID")
        product_description: str = Field(..., description="Product description")
        audience_segment: str = Field(..., description="Target audience")
        tone: str = Field(default="professional", description="Copy tone")
        num_variants: int = Field(default=3, ge=1, le=10, description="Number of variants")
        platform: str = Field(..., description="Platform (google, meta, tiktok)")

    class Output(SkillOutput):
        variants: list[dict] | None = None

    class Config(SkillConfig):
        timeout_seconds: int = 120
        model: str = "claude-sonnet-4-20250514"

    def validate_input(self, input_data: dict) -> Input:
        return self.Input(**input_data)

    async def execute(self, input_data: Input) -> Output:
        # Fetch campaign context from knowledge graph
        kg = MarketingKnowledgeGraph()
        campaign = kg.get_campaign(input_data.campaign_id)

        # Generate copy using Claude
        variants = await self._generate_variants(
            product=input_data.product_description,
            audience=input_data.audience_segment,
            tone=input_data.tone,
            num=input_data.num_variants,
            platform=input_data.platform
        )

        # Store in vector store for retrieval
        vs = MarketingVectorStore()
        for variant in variants:
            await vs.add_creative_variant(variant)

        return Output(
            success=True,
            data={"variants": variants},
            metadata={
                "skill_version": self.version,
                "campaign_id": input_data.campaign_id,
                "platform": input_data.platform
            }
        )

    async def _generate_variants(
        self,
        product: str,
        audience: str,
        tone: str,
        num: int,
        platform: str
    ) -> list[dict]:
        """Generate copy variants using Claude."""
        prompt = f"""Generate {num} ad copy variants for:
Product: {product}
Audience: {audience}
Tone: {tone}
Platform: {platform}

Return JSON array with: headline, description, call_to_action"""

        response = await claude.generate(prompt)
        return json.loads(response.content)
```

---

## 7. Skill Testing

```python
# skills/copy_generator/skill_test.py

import pytest
from skill import CopyGeneratorSkill

@pytest.fixture
def skill():
    return CopyGeneratorSkill()

@pytest.fixture
def valid_input():
    return {
        "campaign_id": "test-campaign-123",
        "product_description": "Project management software for teams",
        "audience_segment": "Engineering managers at tech companies",
        "tone": "professional",
        "num_variants": 3,
        "platform": "google"
    }

class TestCopyGenerator:

    @pytest.mark.asyncio
    async def test_execute_success(self, skill, valid_input):
        """Test successful copy generation."""
        output = await skill.execute(skill.validate_input(valid_input))

        assert output.success is True
        assert output.data is not None
        assert "variants" in output.data
        assert len(output.data["variants"]) == 3

    @pytest.mark.asyncio
    async def test_invalid_input(self, skill):
        """Test invalid input raises ValidationError."""
        with pytest.raises(ValidationError):
            skill.validate_input({"missing": "required_fields"})

    @pytest.mark.asyncio
    async def test_circuit_breaker(self, skill, valid_input):
        """Test circuit breaker opens after failures."""
        # Simulate 3 failures
        for _ in range(3):
            await skill.on_failure(
                skill.validate_input(valid_input),
                Exception("Simulated failure")
            )

        assert skill._circuit_open is True
        assert skill.is_available() is False

    @pytest.mark.asyncio
    async def test_timeout(self, skill):
        """Test skill respects timeout."""
        skill.config.timeout_seconds = 1

        slow_input = {
            **skill.validate_input({
                "campaign_id": "test",
                "product_description": "Test product",
                "audience_segment": "Test audience",
                "tone": "professional",
                "num_variants": 1,
                "platform": "google"
            })
        }

        # This would timeout if we had a slow operation
        output = await asyncio.wait_for(
            skill.execute(slow_input),
            timeout=2
        )

        # Should complete or timeout gracefully
        assert isinstance(output, CopyGeneratorSkill.Output)
```

---

## 8. Skill Configuration

```python
# skills/copy_generator/skill_config.py

from pydantic import Field
from skill_interface import SkillConfig

class CopyGeneratorConfig(SkillConfig):
    """Configuration for CopyGenerator skill."""

    # Model settings
    model: str = Field(
        default="claude-sonnet-4-20250514",
        description="Claude model to use"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature"
    )
    max_tokens: int = Field(
        default=500,
        ge=100,
        le=2000,
        description="Max tokens in response"
    )

    # Quality settings
    num_variants_default: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Default number of variants"
    )
    plagiarism_check: bool = Field(
        default=True,
        description="Check for plagiarism before returning"
    )

    # Platform-specific settings
    platform_char_limits: dict = Field(
        default={
            "google": {"headline": 30, "description": 90},
            "meta": {"headline": 40, "description": 125},
            "tiktok": {"headline": 50, "description": 150},
        },
        description="Character limits per platform"
    )

DEFAULT_CONFIG = CopyGeneratorConfig(
    timeout_seconds=120,
    max_retries=3,
    circuit_breaker_threshold=3,
    model="claude-sonnet-4-20250514",
    temperature=0.7,
    max_tokens=500,
    num_variants_default=3,
    plagiarism_check=True
)
```

---

## 9. Skill Examples

```python
# skills/copy_generator/examples/basic_usage.py

"""
Basic usage example for CopyGenerator skill.
"""

from skill import CopyGeneratorSkill

async def main():
    skill = CopyGeneratorSkill()

    input_data = {
        "campaign_id": "summer-sale-2024",
        "product_description": "Premium outdoor furniture set",
        "audience_segment": "Homeowners with backyard, income $100k+",
        "tone": "aspirational",
        "num_variants": 5,
        "platform": "meta"
    }

    output = await skill.execute(skill.validate_input(input_data))

    if output.success:
        print("Generated variants:")
        for i, variant in enumerate(output.data["variants"], 1):
            print(f"\n{i}. {variant['headline']}")
            print(f"   {variant['description']}")
            print(f"   CTA: {variant['call_to_action']}")
    else:
        print(f"Error: {output.error}")

if __name__ == "__main__":
    asyncio.run(main())
```
