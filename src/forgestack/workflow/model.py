"""Phase model. Config is the source of truth; AGTX stays the runtime authority."""

from __future__ import annotations

from dataclasses import dataclass, field

ALLOWED_PHASE_KEYS = {"research", "planning", "running", "review", "preresearch"}
AGENT_PHASE_KEYS = ("research", "planning", "running", "review")


@dataclass
class PhaseDef:
    key: str
    label: str = ""
    purpose: str = ""
    agent: str = ""
    skills: list[str] = field(default_factory=list)
    team: list[str] = field(default_factory=list)
    artifact: str | None = None
    prompt: str = ""


@dataclass
class PhaseModel:
    research: bool = True
    cyclic: bool = False
    phases: list[PhaseDef] = field(default_factory=list)

    @classmethod
    def default(cls) -> PhaseModel:
        return cls(
            research=True,
            cyclic=False,
            phases=[
                PhaseDef(key="research", label="Research", prompt=DEFAULT_PROMPTS["research"]),
                PhaseDef(key="planning", label="Planning", prompt=DEFAULT_PROMPTS["planning"]),
                PhaseDef(key="running", label="Running", prompt=DEFAULT_PROMPTS["running"]),
                PhaseDef(key="review", label="Review", prompt=DEFAULT_PROMPTS["review"]),
            ],
        )


DEFAULT_PROMPTS: dict[str, str] = {
    "research": """Task:
{task}

You are in the RESEARCH / DISCOVERY phase.
Understand the problem before planning a solution.

Do:
1. Read the grooming brief, ticket, or kickoff notes.
2. Inspect relevant documentation and existing code.
3. Identify unclear requirements, assumptions, dependencies, and risks.
4. Investigate existing architecture and conventions.
5. Identify questions that genuinely require human/product input.
6. Resolve technical questions from the repository where possible.
7. Produce a concise research/discovery summary for Planning.

Do NOT implement production code, prematurely design the full solution, or invent product requirements.""",
    "planning": """Task:
{task}

You are in the PLANNING phase.
Turn the requirement into an implementation-ready contract.

Do:
1. Validate the intended user/business outcome.
2. Resolve remaining ambiguity.
3. Determine the architecture and technical approach.
4. Define domain rules, interfaces, constraints, and edge cases.
5. Define acceptance criteria and expected tests.
6. Produce an implementation-ready specification.
7. Produce a concrete implementation plan / work decomposition.
8. Reuse existing project conventions and architecture.

Do NOT implement production code.""",
    "running": """Task:
{task}

You are in the IMPLEMENTATION phase. The planning/specification phase is authoritative.

Implement the approved specification and plan.

Do:
1. Read the approved spec and plan completely.
2. Implement incrementally.
3. Follow existing architecture and project conventions.
4. Add or update tests.
5. Run relevant verification.
6. Perform a self-review before declaring completion.
7. Keep changes scoped to the approved task.

If ponytail discipline is available, apply its YAGNI/reuse/stdlib ladder and minimal-diff
guidance to avoid over-engineering. Otherwise follow the equivalent principles:
smallest change that works, no speculative abstraction, no scaffolding for later.

Do NOT silently modify or reinterpret approved requirements.""",
    "review": """Task:
{task}

You are in the independent REVIEW / QA phase. You did not author the implementation.
Treat the approved specification and acceptance criteria as authoritative.

Review separately for:
1. Specification and acceptance-criteria compliance
2. Correctness
3. Engineering/code quality
4. Test quality and missing regression coverage
5. Edge cases
6. Security concerns
7. Architectural consistency
8. Unnecessary scope or requirement drift

Classify findings as BLOCKING / IMPORTANT / OPTIONAL.
Do NOT implement new functionality during review.""",
}
