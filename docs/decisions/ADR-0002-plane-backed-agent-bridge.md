# ADR-0002: Provider-neutral project-to-agent bridge

## Status

Accepted

## Context

ForgeStack currently provides a local-first CLI and integration layer around
external development tools. Its existing workflow is centered on AGTX, while
the project also needs a human-visible collaboration surface that can be
shared with product owners, project managers, and other developers.

The project will use Plane first, with future support for Linear and Huly. The
tracker should remain the project-management system of record; ForgeStack
should connect human planning to coding-agent execution rather than rebuild a
Kanban or documentation product.

The first workflow must preserve human approval, support multiple specialist
workers, and keep project context durable outside an individual agent session.

## Decision

ForgeStack is a provider-neutral bridge between human project management and
AI coding-agent execution.

```text
Human
  ↕
Manager Agent ── tracker MCP ── Tracker
                              ↕
                    ForgeStack Orchestrator
                              ↕
                         tracker API
                              ↕
                    Worker Agents / worktrees
                              ↕
                         Repository
                              ↘
                         Tracker updates
```

### Responsibilities

- **Tracker:** Human-visible projects, milestones, modules, work items,
  priorities, decisions, plans, comments, and review status.
- **Manager Agent:** Shapes human intent, reads repository context, proposes
  specifications and plans, creates meaningful planning structure, and asks for
  approval before execution.
- **Orchestrator:** Reads approved work, creates or activates meaningful child
  work items, selects workers by capability, manages execution dependencies and
  worktrees, collects verification, and posts progress and handoffs.
- **Worker Agents:** Perform bounded repository or artifact work and return a
  structured handoff. Workers do not update the tracker directly.
- **Human:** Approves the transition to Ready and makes the final Done
  decision.

### Tracker communication

The first implementation intentionally uses both supported tracker interfaces
for different roles:

- The Manager Agent uses the tracker's MCP integration for conversational,
  context-rich planning.
- The Orchestrator uses the tracker's API for deterministic manual execution,
  task lookup, child-task updates, progress, and handoffs.

These are two transports for one tracker, not two sources of truth. ForgeStack
must define ownership for fields and operations so Manager, Orchestrator, and
human edits do not compete silently.

The `doctor` command will eventually check the selected agent's MCP readiness
and the tracker's API configuration. It may offer to install or configure
missing external components only after explicit user approval. Credentials are
kept outside the repository.

### Domain model

ForgeStack uses provider-neutral concepts and maps them to provider-specific
features:

- Project: product or shared work context.
- Initiative or Objective: optional strategic goal.
- Milestone or Release: outcome or release checkpoint.
- Module or Area: feature domain.
- Work Item: generic record whose kind may be epic, story, task, bug, or
  subtask.
- Cycle or Sprint: optional execution timebox.

Parent/child work items are used for independently meaningful decomposition.
Internal subagent activity does not require a tracker work item unless it has a
human-relevant outcome.

### Human and execution state

The tracker owns the human lifecycle:

```text
Backlog → Planning → Ready → In Progress → Human Review → Done
```

`Blocked` is a separate state for work that needs a decision, dependency,
access, clarification, or correction. It is not equivalent to Human Review:
Human Review means the agent considers the work complete; Blocked means work
cannot continue.

ForgeStack keeps separate execution state, such as:

```text
queued → running → succeeded / failed / blocked / cancelled
```

Detailed worker runtime state is not mirrored into the tracker's Kanban.

### Execution and coordination

The first Orchestrator is manually invoked with an explicit work-item target,
or by a Manager Agent request for a target item. It does not scan the entire
tracker or run as a background daemon initially.

The Manager may use planning subagents to produce a specification, acceptance
criteria, risks, and implementation plan. After human approval, the
Orchestrator may dispatch multiple workers when their scopes are independent.
Workers use separate worktrees when they may write code. The Orchestrator only
merges compatible work automatically; otherwise it returns the worktrees and
handoffs for review.

Each worker handoff includes, at minimum:

- status;
- changed files or artifacts;
- commands and verification results;
- review findings;
- unresolved risks;
- recommended next action.

### Repository ownership

The repository remains the source of code and durable technical documentation.
The `.forgestack/` directory is reserved for ForgeStack-owned project
configuration, agent capability templates, provider/project references,
execution manifests, and concise handoff artifacts. It must not become a dump
of raw agent transcripts or a competing copy of the full tracker plan.

Global agent templates are configured through ForgeStack's CLI wizard and may
be overridden per project. Secrets and credentials are never stored in Git.

### Provider boundary

Tracker integrations use a provider-neutral contract separate from the existing
tool installation/detection adapter protocol. The first provider is Plane;
Linear and Huly are future implementations. Provider-specific capabilities are
exposed explicitly rather than pretending every tracker has identical
hierarchy, workflow, or automation features.

AGTX remains the current local execution runtime during migration. This ADR
does not authorize replacing AGTX immediately or adding broad tracker
synchronization. The first validation target is one complete Plane-backed
workflow.

## Consequences

- Human collaborators can use a familiar shared tracker without learning
  ForgeStack internals.
- ForgeStack can add Linear and Huly later without making the core model
  tracker-specific.
- The Manager and Orchestrator have clear write boundaries.
- Multiple specialist agents can work in parallel without sharing a writable
  worktree.
- The first implementation has two tracker transports and must handle
  authentication, capability discovery, and conflict ownership.
- Existing AGTX-centered code and documentation require incremental migration;
  this ADR describes the target boundary, not an immediate rewrite.
- The initial success criterion is a manually triggered Plane workflow from
  approved work through agent execution and Human Review.

## Alternatives rejected

- Starting a new repository and discarding the existing ForgeStack foundation.
- Making ForgeStack another project-management UI.
- Binding the core domain directly to Plane concepts.
- Requiring every internal subagent run to become a visible tracker item.
- Running an autonomous background orchestrator before the manual workflow is
  proven.
- Making workers update the tracker directly.
