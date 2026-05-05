# Codex Machinae

**Version:** 2.0.0 — Draft
**Last updated:** 2026-04-15
**Scope:** Framework for developing, testing, deploying, maintaining, and monitoring software projects.

This playbook defines the entire lifecycle of a software project: from requirements gathering through to deployment and continuous dependency monitoring. It is designed for independent developers and small teams operating with autonomous agents (Claude Code, Ruflo, or equivalents).

---

## Table of Contents

### Part I — Core (universal)

1. [Requirements and planning](#1-requirements-and-planning)
2. [Project structure](#2-project-structure)
3. [Code quality](#3-code-quality)
4. [Security requirements](#4-security-requirements)
5. [Testing strategy](#5-testing-strategy)
6. [Documentation](#6-documentation)
7. [CI/CD and deployment](#7-cicd-and-deployment)
8. [Boundary Contracts](#8-boundary-contracts)
9. [Change classification](#9-change-classification)
10. [Remediation workflow](#10-remediation-workflow)
11. [Project lifecycle](#11-project-lifecycle)
12. [Conventions for AI agents](#12-conventions-for-ai-agents)

### Part II — Domain Appendices (activate per project type)

- [D1 Web Service](#d1-web-service)
- [D2 Library / SDK](#d2-library--sdk)
- [D3 CLI Tool](#d3-cli-tool)
- [D4 Embedded / Firmware](#d4-embedded--firmware)
- [D5 ML / Data Pipeline](#d5-ml--data-pipeline)
- [D6 Mobile App](#d6-mobile-app)
- [D7 Static Site / Frontend-only](#d7-static-site--frontend-only)

### Part III — Cross-cutting Modules (activate by trigger)

- [M1 Surveillance](#m1-surveillance)
- [M2 Security-sensitive](#m2-security-sensitive)
- [M3 Release & Distribution](#m3-release--distribution)
- [M4 Classification & Taxonomy](#m4-classification--taxonomy)

### Meta

- [Known limitations and roadmap](#known-limitations-and-roadmap)

### Appendices

- [A — Per-phase checklists](#appendix-a--phase-checklists)
- [B — Templates](#appendix-b--templates)
- [C — Glossary](#appendix-c--glossary)
- [D — Tooling Specifications](#appendix-d--tooling-specifications)

---

# PART I — CORE (universal)

The Core applies to every project regardless of type. Domain Appendices (Part II) and
Cross-cutting Modules (Part III) add content on top of the Core when their activation trigger
fires. When the Core and a module disagree, the Core wins unless the module explicitly marks
the override.

---

## 1. Requirements and planning

Every feature, bugfix, or project begins with written requirements. Code without documented requirements is technical debt from the first commit.

### 1.1 Requirements document hierarchy

```
PRD (Product Requirements Document)
 └── Epic
      └── User Story
           └── Acceptance Criteria
                └── Technical task
```

Every level is traceable to the one above it. A technical task without a referenced User Story is a warning signal — it could be unnecessary work or scope creep.

### 1.2 PRD (Product Requirements Document)

The PRD is the highest-level document. It defines the **what** and the **why**, never the **how** (that is architecture). Minimum content:

| Section | Content | Required |
|---------|---------|----------|
| **Status and ownership** | Draft version, author, date of last update | Yes |
| **Purpose and scope** | What the system guarantees and what it does NOT cover | Yes |
| **Stakeholders and users** | Who uses the system and in what context | Yes |
| **Functional requirements** | What the system must do, organised by area | Yes |
| **Non-functional requirements** | Performance, security, accessibility, scalability | Yes |
| **Architectural constraints** | Mandatory technologies, integrations, limitations | Yes |
| **Boundaries with other systems** | What is the responsibility of other repos/services/teams | Yes |
| **Open questions** | Known unknowns, with owner and resolution strategy | Yes |
| **Architectural decisions** | Referenced ADR (Architecture Decision Records) | Recommended |
| **Later-phase work** | Work explicitly deferred, with justification | Recommended |
| **Appendices** | Source documents, external references | Recommended |

**Pre-implementation checklist.** Every PRD MUST include a checklist at the beginning of the document listing decisions already made and confirmed. The implementer verifies it before writing any code. If an item on the checklist does not match the code in the repository, implementation halts until the discrepancy is resolved.

### 1.3 User story

Standard format:

```
As a [user role]
I want [action]
So that [benefit]
```

Every User Story MUST have:

- **Unique ID** — format `US-<area>-<number>` (e.g. `US-AUTH-001`)
- **Priority** — P0 (blocker), P1 (must-have for release), P2 (should-have), P3 (nice-to-have)
- **Estimate** — in hours or story points, updated after the first working session
- **Acceptance criteria** — list of verifiable conditions that define "done"
- **Dependencies** — reference to other User Stories that must be completed first
- **Link to PRD** — the PRD section that this story implements

### 1.4 Acceptance criteria

Each criterion is a binary condition (pass or fail). Format:

```
GIVEN [initial context]
WHEN [user or system action]
THEN [expected result]
```

Acceptance criteria become tests. If a criterion cannot be translated into an automated test, it must be rewritten until it can.

### 1.5 Architecture Decision Records (ADR)

Every significant architectural decision is documented in an ADR. Minimum format:

```markdown
# ADR-<number>: <title>

**Status:** proposed | accepted | deprecated | superseded by ADR-<n>
**Date:** YYYY-MM-DD
**Context:** Why this decision is necessary.
**Decision:** What was decided.
**Consequences:** Positive and negative impact of the decision.
**Alternatives rejected:** What was considered and discarded, with justification.
```

ADRs are **append-only** — they are never deleted; they are superseded by new ADRs that reference them.

### 1.6 Backlog management

The backlog is an ordered list by priority. Rules:

- Every item has a status: `todo`, `in-progress`, `blocked`, `review`, `done`
- No item remains `in-progress` for more than one week without an update
- `blocked` items must have a reason and an owner responsible for unblocking
- `done` items must have all Acceptance Criteria satisfied and tests written
- The backlog is reviewed weekly; P3-priority items older than 90 days are archived or deleted

### 1.7 State-of-the-art research

Before implementing a feature, a module, or an integration, the system must prompt the user to conduct state-of-the-art research. This applies both to the project as a whole and to individual parts.

#### 1.7.1 When research is mandatory

| Trigger | What to research | Expected output |
|---------|-----------------|-----------------|
| **New project** (Phase 0) | Existing similar projects, established frameworks, dominant architectural patterns in the domain | Report covering: existing solutions, pros/cons, justified decision on build vs adopt vs fork |
| **Significant new feature** (P0 or P1) | Reference implementations, specialised libraries, documented patterns | "State of the art" section in the User Story with links and evaluation |
| **New dependency** | Available alternatives, maturity/community/maintenance comparison, licence | Comparative table in `DEPENDENCIES.md` with justification for the choice |
| **Technology choice** (language, framework, database) | Recent benchmarks, adoption trends, case studies in the domain | ADR with "Alternatives rejected" section populated from real research |
| **Architectural refactoring** | Current patterns in the industry, documented migrations from other projects | ADR with references to similar experiences |

#### 1.7.2 What to research for each component

For every significant part of the project, research should cover:

**Existing solutions.** Does a library, service, or open-source project already exist that does what I am about to write? If so, is it more mature, tested, and maintained than what I could produce? Rule: do not reinvent the wheel unless the existing wheels are not suited to the road ahead — and document why they are not in the ADR.

**Patterns and best practices.** How do mature projects in the same domain solve this problem? Which architectural patterns have emerged as dominant? Which anti-patterns have been documented? Search: engineering blog posts from relevant companies, recent conferences, RFCs and proposals in reference repositories.

**Technology evolution.** Is the technology I am using still the best choice? Are there newer alternatives that resolve known issues with the current technology? Is the community active or in decline? Search: GitHub star trends, release frequency, number of active contributors, open vs closed issues.

**Experience from others.** Who else has done something similar and what did they learn? What mistakes can I avoid? Search: public post-mortems, case studies, technical forum threads, conference talks.

#### 1.7.3 How the AI agent supports research

The AI agent MUST proactively suggest research at the following moments:

**At the start of a new project:** "Before implementing, shall I research the state of the art for [project domain]? I can look for similar projects, established frameworks, and architectural patterns used in the industry."

**When a new dependency is added:** "You are about to add [library]. Would you like me to check whether there are more recent or mature alternatives? I can compare: maturity, update frequency, community size, licence, and any known issues."

**When an architectural choice is proposed:** "This decision has a long-term impact. Would you like me to look at how other projects in the [X] domain have approached the same problem? I can find public ADRs, engineering blog posts, and case studies."

**When the project enters a new phase:** "The project is about to tackle [new area]. Would you like me to carry out a state-of-the-art check on the technologies and patterns used in this area?"

**During periodic review:** "It has been [N] months since the last state-of-the-art research for [component]. Some of the technologies in use may have better alternatives or significant updates. Would you like me to carry out a check?"

#### 1.7.4 Research register

Document each research exercise in `docs/research/`:

```
docs/research/
├── YYYY-MM-DD-<topic>.md          # Research report
├── YYYY-MM-DD-<topic>.md
└── index.md                        # Index with date, topic, outcome
```

Report format:

```markdown
# Research: [Topic]

**Date:** YYYY-MM-DD
**Trigger:** new project | new feature | new dependency | periodic review
**Author:** human | AI agent | both

## Research question
[What we wanted to know]

## Solutions found
[List with pros/cons/maturity/licence]

## Recommendation
[What to do and why]

## Sources
[Links to documentation, blogs, repositories, papers]

## Decision taken
[What was decided and reference to the ADR if present]
```

#### 1.7.5 State-of-the-art research agent (State-of-the-Art Scout)

In addition to the dependency surveillance agents (M1.1), the playbook includes an agent dedicated to state-of-the-art research. This agent operates differently from the others: it does not monitor a single dependency, but scans the technological landscape surrounding the project.

**Frequency:** quarterly for stable components, monthly for components under active development.

**What it does:**

1. **Technology health check.** For every significant technology in the project (language, framework, database, key libraries), verifies: latest release, release frequency over the past year, trend of open issues, state of documentation, any deprecation or end-of-life announcements.

2. **Alternative scanning.** Searches for new libraries or services that solve the same problem as an existing dependency, but with a different or improved approach. It does not suggest switching — it flags that the alternative exists and leaves the decision to the human.

3. **Pattern evolution.** Verifies whether the architectural patterns used in the project are still considered best practice or whether the community has moved towards different approaches. Searches: updates to official style guides, new RFCs in reference repositories, recent talks from key conferences.

4. **Security landscape.** Verifies whether the project's security practices are aligned with current recommendations (OWASP, NIST, CIS benchmarks). Searches: new vulnerability classes, new scanning tools, updates to recommendations.

5. **Ecosystem health.** Evaluates the overall health of the ecosystem: is the community growing or in decline? Are there significant forks? Are there controversies (licence, governance, ownership) that could impact the project?

**Output:** a report in `docs/research/` with classified findings:

| Finding | Meaning | Action |
|---------|---------|--------|
| `healthy` | The technology is active, maintained, with no superior alternatives | None |
| `watch` | An emerging alternative or trend to monitor exists | Add to the next research cycle |
| `evaluate` | An alternative is mature enough to warrant serious evaluation | Create an ADR with comparison |
| `migrate` | The technology is in decline, deprecated, or has significant issues | Plan migration in the backlog |
| `urgent` | End-of-life, critical vulnerability without a patch, hostile fork | Immediate action |

### 1.8 Definition of Done

The Definition of Done is split into two layers. **Core DoD** applies to every item in every project, regardless of domain, phase, or tooling. **Contextual DoD** applies only when its precondition holds — the item need not satisfy a contextual check when the trigger has not fired.

An item is "done" when all applicable checks below pass.

#### 1.8.1 Core DoD (process integrity — always applies)

- [ ] The planned change is actually complete — no half-finished edits, no placeholder stubs left behind
- [ ] Commit messages follow Conventional Commits (§3.3)
- [ ] `PROJECT_STATUS.md` is updated
- [ ] Protected paths have not been modified without prior approval (agent-config protected-paths list)
- [ ] Cross-references (§…) still resolve; broken links fixed or removed

#### 1.8.2 Contextual DoD (applies when the precondition holds)

| Check | Precondition |
|-------|--------------|
| Code complies with style conventions (§3) | Code was written or modified |
| All Acceptance Criteria are satisfied | The item is backed by a User Story (§1.3) |
| Tests are written and pass (§5) | The project has adopted a testing strategy |
| Coverage has not dropped below the threshold (§5.3) | A coverage threshold is declared |
| CI is green | CI is configured for the project |
| Documentation is up to date (§6) | External-facing behaviour changed |
| Code has been reviewed (self- or peer-) | The project's practice requires review |
| Boundary Contract Map updated (§8) | A contract was added, removed, or changed |
| State-of-the-art research has been conducted (§1.7) | A §1.7 trigger fired for this item |
| ADR written (§1.5) | A significant architectural decision was taken |

An agent MUST declare, for each contextual check, whether the precondition held; checks whose precondition did not hold are recorded as `n/a` rather than silently skipped. This keeps the audit trail explicit.

---

## 2. Project structure

The playbook follows an **emergent architecture** principle: a project starts with the smallest possible footprint and grows only when justified by its PRD and phase. Scaffolding folders up front — "just in case" — is waste and locks the project into structure it may never need.

### 2.1 Minimum Core of Existence

Every project MUST contain, at initialisation, only these files:

```
project-root/
├── README.md                    # One-paragraph orientation
├── PROJECT_STATUS.md            # Current session state (§2.3)
└── <agent-config>               # Rules for the AI agent(s) working on the project (§2.4)
```

Nothing else is mandatory at Phase 0. Every further folder or file is introduced through the Emergent Expansion Protocol (§2.2) when a trigger fires.

### 2.2 Emergent Expansion Protocol

Rather than creating folders defensively, the AI agent proposes expansions as the PRD and the project evolve. When a trigger fires, the agent MUST surface a proposal in this form:

> "I suggest adding `<path>` to cover <concern> because <trigger>. Cost of omission: <what breaks if we don't>."

The human accepts, rejects, or defers. No folder is created without an accepted proposal.

**Expansion catalogue (non-exhaustive).** Folders are added only when their trigger fires:

| Path | Trigger | Covers |
|------|---------|--------|
| `docs/prd/00-prd.md` | A PRD is being written (always, Phase 0 of any non-trivial project) | Requirements |
| `docs/adr/` | First architectural decision needs recording | Decision history |
| `docs/api/` | Project exposes or consumes a programmatic API | API surface |
| `docs/runbooks/` | Project is deployed to any environment | Operational procedures |
| `docs/research/` | State-of-the-art research is triggered (§1.7) | Research register |
| `src/`, `tests/` | Code is about to be written | Implementation |
| `scripts/` | First automation script is needed | Local tooling |
| `ci/` | Automated checks are enabled | CI/CD configuration |
| `ci/adapters/<forge>/` | A specific forge is adopted (GitHub, GitLab, …) | Forge-specific glue |
| `DEPENDENCIES.md` | First external runtime dependency is added | Dependency contracts |
| `CHANGELOG.md` | Project reaches its first release (v0.1.0+) | Release history |
| `COMPATIBILITY.md` | Boundary Contract Map is populated (§8) | Generated compatibility status |
| `compat-data/`, `compatibility/`, `surveillance/` | Surveillance agents are activated (M1.1) | External dependency monitoring |
| `.config/` | Linting/formatting rules diverge from tool defaults | Tooling configuration |

**Rule:** no folder without a fired trigger. Empty scaffolds and `.gitkeep` files are forbidden.

**Rule:** the agent also proposes **removal** when a folder loses its trigger (e.g. last surveillance agent removed → `surveillance/` can be archived).

### 2.3 PROJECT_STATUS.md

Updated at every working session. Four fixed sections:

```markdown
## Objective
What the project must achieve in this phase.

## Modified Files
List of files modified in the last session, with reason.

## Logical State
Current status: what works, what does not, what is blocked.

## Next Action
The next concrete action to perform.
```

### 2.4 Agent configuration

Operational rules for the AI agent(s) live in one of two layouts, depending on how many agents collaborate on the project:

**Single-agent project.** A single file (e.g. `CLAUDE.md`, `GEMINI.md`) contains all rules.

**Multi-agent project.** Rules are split into two layers:

- `AI-AGENTS.md` — shared source of truth for all agents. When a rule here conflicts with an agent-specific file, this file wins.
- `CLAUDE.md`, `GEMINI.md`, … — per-agent files covering only agent-specific syntax, tool use, and permissions. They must not contradict `AI-AGENTS.md`.

Whichever layout is used, the configuration MUST cover:

- Language and writing style (e.g. British English, active voice, short sentences)
- List of forbidden words, if any
- Scope of permitted modifications per autonomy level (L0/L1/L2 — see §10)
- Naming conventions for branches, commits, files
- Protected paths (files the agent cannot modify without human confirmation)
- Editorial rules (max line length, punctuation constraints, etc.)

### 2.5 Project-size profile

The project declares a **size profile** that modulates which checklist items (Appendix A)
are mandatory, recommended, or optional. The profile is declared once in the agent
configuration file (§2.4) and applies for the project's lifetime unless explicitly changed.

| Profile | Typical team | Typical codebase | When to choose |
|---------|-------------|------------------|----------------|
| **Solo** | 1 person | < 5 000 lines | Side projects, prototypes, personal tools, early-stage exploration |
| **Small** | 2–5 people | 5 000–50 000 lines | Startup MVPs, internal tools, focused microservices |
| **Large** | 6+ people | > 50 000 lines | Production systems, multi-team projects, regulated environments |

**How profiles interact with checklists:**

Each checklist item in Appendix A carries an implicit default of **mandatory for all
profiles**. Items that are downgraded for smaller profiles are tagged inline:

- ⬇ `[Small: recommended]` — mandatory for Large, recommended for Small and Solo.
- ⬇ `[Solo: optional]` — mandatory for Large and Small, optional for Solo.
- ⬇ `[Small: optional]` — mandatory for Large, optional for Small and Solo.

Items without a tag are mandatory regardless of profile. The tagging is deliberately
conservative: most items remain mandatory because the playbook's value comes from
discipline, not from cutting corners. The profile exists to acknowledge that a solo
developer maintaining a personal tool does not need the same ceremony as a regulated
production system.

**Rules:**

1. The profile does not affect Core sections (§§1–12) — those rules apply universally.
   Only checklist *items* in Appendix A are modulated.
2. "Recommended" means the item should be done unless there is a concrete reason not to.
   "Optional" means the item adds value but can be skipped without risk.
3. A project may upgrade its profile at any time (Solo → Small, Small → Large). Downgrading
   requires a conscious review: items that were mandatory under the old profile and are now
   optional must be explicitly evaluated, not silently dropped.
4. When in doubt, choose the higher profile. Over-engineering process is cheaper than
   under-engineering quality.

---

## 3. Code quality

### 3.1 Architectural principles

Every project MUST adhere to these principles regardless of language:

**Separation of concerns.** Every module has a single, well-defined responsibility. Code that communicates with external APIs lives in a separate adapter/client layer, apart from business logic and the UI.

**Dependency inversion.** High-level modules do not depend on low-level modules — both depend on abstractions (interfaces, types, contracts). This makes the code testable and the client layer replaceable.

**Fail fast.** Errors are detected and reported as early as possible. Invalid input is rejected at the boundary, not propagated silently.

**Immutability by default.** Prefer immutable data structures and pure functions. Mutable state is confined to explicit store/state managers.

**Explicit over implicit.** No hidden magic: no undeclared global state, no side effects in getters, no circular imports.

### 3.2 Naming conventions

| Element | Convention | Example |
|----------|------------|---------|
| File | kebab-case | `user-profile.ts`, `auth-client.py` |
| Class/Component | PascalCase | `UserProfile`, `AuthClient` |
| Function/method | camelCase (JS/TS), snake_case (Python) | `getUserById()`, `get_user_by_id()` |
| Constant | SCREAMING_SNAKE_CASE | `MAX_RETRY_COUNT`, `API_BASE_URL` |
| Environment variable | SCREAMING_SNAKE_CASE with project prefix | `ARC_CORTEX_URL`, `APP_SECRET_KEY` |
| Branch | `<type>/<id>-<short-description>` | `feat/US-AUTH-001-login-flow` |
| Commit | Conventional Commits | `feat(auth): add login endpoint` |
| Test file | Same name as the tested file + `.test` or `.spec` | `auth-client.test.ts` |

### 3.3 Conventional Commits

Every commit message follows the format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Permitted types:

| Type | When to use it |
|------|--------------|
| `feat` | New feature |
| `fix` | Bugfix |
| `docs` | Documentation only |
| `style` | Formatting, semicolons, etc. (no logic change) |
| `refactor` | Code change that neither adds a feature nor fixes a bug |
| `test` | Adding or modifying tests |
| `chore` | Build, CI, dependencies, tooling |
| `perf` | Performance improvement |
| `ci` | Changes to the CI/CD pipeline |
| `revert` | Revert of a previous commit |
| `compat` | Change related to compatibility with external dependencies |

The `BREAKING CHANGE:` footer is mandatory for any change that breaks backward compatibility.

### 3.4 Linting and formatting

Every project MUST have:

- **Linter** configured and integrated into CI. CI fails if there are lint errors.
- **Formatter** configured with rules identical to the linter. No debate on style: the formatter decides.
- **Pre-commit hook** (optional but recommended) that runs lint + format before every commit.

Recommended configuration by language:

| Language | Linter | Formatter | Config file |
|-----------|--------|-----------|-------------|
| TypeScript/JavaScript | ESLint (flat config) | Prettier | `eslint.config.js`, `.prettierrc` |
| Python | Ruff (lint + format) | Ruff | `ruff.toml` or `pyproject.toml` |
| Rust | Clippy | rustfmt | `clippy.toml`, `rustfmt.toml` |
| Go | golangci-lint | gofmt | `.golangci.yml` |
| Bash | ShellCheck | shfmt | `.shellcheckrc` |

**Rule zero:** no commit enters the repo with lint warnings. A warning is an error.

### 3.5 Complexity and metrics

Thresholds that CI MUST enforce:

| Metric | Threshold | Action if exceeded |
|---------|--------|-------------------|
| Cyclomatic complexity per function | ≤ 15 | CI fail |
| Lines per function | ≤ 50 (indicative) | Warning |
| Lines per file | ≤ 400 (indicative) | Warning |
| Nesting depth | ≤ 4 levels | CI fail |
| Parameters per function | ≤ 5 | Warning, suggest options object |
| Circular imports | 0 | CI fail |
| `any` type (TypeScript) | 0 in production | CI fail (permitted in tests with justification) |
| `// @ts-ignore` or `# type: ignore` | 0 in production | CI fail (permitted with an explanatory comment) |

### 3.6 Error handling

Universal rules:

- **Never swallow errors silently.** Every `catch` must log, rethrow, or handle explicitly. An empty `catch` is a bug.
- **Typed errors.** Define error classes/types for every domain of the application. Do not use strings as errors.
- **Error boundary.** Every layer of the architecture (UI, business logic, adapter, infra) has its own error boundary that translates errors from the lower layer into errors meaningful to the upper layer.
- **Retry with backoff.** Calls to external services must have retry with exponential backoff and a maximum number of attempts. Never infinite retry.
- **Explicit timeouts.** Every external call has a configured timeout. No call waits indefinitely.

### 3.7 Dependency management

- **Lock file** always committed (`package-lock.json`, `Pipfile.lock`, `Cargo.lock`, `go.sum`).
- **Exact versions** for direct production dependencies. Ranges (`^`, `~`) permitted only for development dependencies.
- **Regular audit.** `npm audit`, `pip-audit`, `cargo audit` run in CI on every PR.
- **Intentional updates.** Dependencies are not updated "because a new version is available" — they are updated when there is a reason (bugfix, security patch, required feature). An update is a tracked task, not a side effect.
- **Phantom dependencies.** CI verifies that there are no imports of packages not declared in the dependencies. Tools: `depcheck` (npm), `deptry` (Python).

### 3.8 Branching strategy

**Trunk-based development** for individual developers and small teams:

- `main` is always deployable
- Short-lived feature branches (max 3–5 days)
- No `develop` branch — it is unnecessary overhead for small teams
- Branch naming: `<type>/<id>-<description>` (e.g. `feat/US-AUTH-001-login`)
- Merge via squash (one commit per feature branch)
- Tags for releases: `v<major>.<minor>.<patch>`

---

## 4. Security requirements

### 4.1 Fundamental principles

**Defence in depth.** No single control is sufficient. Every layer validates its own inputs independently.

**Least privilege.** Every component has only the minimum permissions necessary. API tokens, database users, file system access — everything is reduced to the minimum.

**Zero trust on input.** All input is hostile until proven otherwise: query parameters, request bodies, headers, file uploads, environment variables, data from external APIs.

### 4.2 Input validation

Every entry point of the application MUST validate input:

| Layer | What to validate | How |
|-------|--------------|------|
| **API endpoint** | Type, format, range, length of every parameter | Schema validation (Zod, Pydantic, JSON Schema) |
| **UI form** | Format, length, permitted characters | Client-side + server-side validation (never client-only) |
| **File upload** | Real MIME type (not just extension), size, content | Magic bytes check, antivirus if available |
| **Database query** | Query parameters, injection | Prepared statement / parameterised query (never string concatenation) |
| **Data from external APIs** | Response schema, mandatory fields, types | Same validation as user input — an external API can be compromised |

**Rule:** validation is declarative (schema), not imperative (chain of `if` statements). A schema is testable, documentable, and reusable.

### 4.3 Secrets management

| Rule | Detail |
|--------|----------|
| **Never in code** | No secrets in source files, commits, or logs. `.gitignore` includes `.env`, `*.key`, `*.pem` |
| **Environment variables** | Primary method for secrets in local and CI environments |
| **Secret manager** | For production: GitHub Secrets, Vault, AWS SSM, or equivalent |
| **Rotation** | Every secret has an expiry date. Rotation is automated or scheduled |
| **Audit** | Every access to a secret is logged. If a secret is compromised, it must be rotated immediately |
| **`.env.example`** | The repo contains a `.env.example` with variable names (without values) and explanatory comments |

Authentication, authorisation, per-PR security checklist, and OWASP Top 10 coverage are handled by M2 Security-sensitive, which activates whenever the project handles authentication, authorisation, or PII; serves untrusted clients over a network; or processes attacker-controlled input.

---

## 5. Testing strategy

### 5.1 Testing pyramid

```
          ┌─────────┐
          │   E2E   │  Few, slow, costly. Validate complete user flows.
         ┌┴─────────┴┐
         │Integration │  Medium. Verify that modules work together.
        ┌┴───────────┴┐
        │  Scenarios   │  Contract tests against real or emulated services.
       ┌┴─────────────┴┐
       │     Unit       │  Many, fast, cheap. One function, one behaviour.
       └────────────────┘
```

| Tier | What it tests | Environment | Speed | Quantity |
|------|-----------|----------|----------|----------|
| **Unit** | Single function, pure logic | In-memory, full mock | < 1s per test | Hundreds |
| **Scenario** | Contract with external service | Emulator or real container | < 5s per test | Dozens |
| **Integration** | Interacting modules | Real container, real database | < 30s per test | Dozens |
| **E2E** | Complete user flow | Full stack, real browser | < 2min per test | A handful |

### 5.2 Rules for each tier

**Unit tests:**
- Every public function has at least one test
- Test the behaviour, not the implementation — if a refactor breaks the test but not the behaviour, the test is wrong
- No external dependencies (network, file system, database) — everything mocked
- Naming: `describe('functionName', () => { it('should <behaviour> when <condition>') })`

**Scenario/Contract tests:**
- Every contract in the Boundary Contract Map has at least one contract test
- Validation uses JSON Schema with `additionalProperties: true` (new fields do not break it)
- Fixtures are generated from real interactions, not written by hand
- Assertion discipline follows §5.6 (set-based when order is not part of the contract)

**Integration tests:**
- Every critical flow (login, main CRUD, payment) has at least one integration test
- Tests create their own data and clean it up — no dependency on pre-existing state
- Dynamic port binding for parallel containers — no hard-coded ports

**E2E tests:**
- Coverage of critical user flows (happy path + main error paths)
- Tools: Playwright (web), Detox (mobile), or equivalent
- Automatic retry for flaky tests (max 2 retries), but flaky tests must be fixed, not ignored
- Screenshot/video on failure for debugging

### 5.3 Coverage

**Ratchet model:** coverage can only increase, never decrease.

| Metric | Minimum threshold | Enforcement |
|---------|--------------|-------------|
| Line coverage | Defined in the baseline file, ratchet up-only | CI fail if it drops |
| Branch coverage | Defined in the baseline file, ratchet up-only | CI fail if it drops |
| Per-file coverage | No new file below 70% | CI fail |
| Coverage delta on PR | ≥ 0% (the PR cannot lower coverage) | CI fail |

**Baseline file:** `coverage-baseline.json` in the project root. Contains per-file coverage for the current state. CI compares and fails if any key decreases.

**Escape valve:** a PR may lower coverage only with a footer in the commit message explaining the reason:

```
Low-Coverage-Reason: Refactor of auth-client.ts — tests in follow-up PR #123
```

The escape valve is tracked and reviewed weekly. No escape valve may remain open for more than 2 weeks.

### 5.4 Test data strategy

- **Inline creation.** Tests create the data they need inline, not from shared fixture files. This makes every test self-documenting and independent.
- **Factory pattern.** For complex data, use factory functions that produce valid objects with sensible defaults and targeted overrides.
- **Golden files.** Only for true snapshot testing (UI rendering, rendered documents). For API and data contracts prefer schema-primary validation (§5.7); golden files there couple tests to incidental output ordering and drift silently. Updated explicitly with a flag (`--update-snapshots`), never silently.
- **Seed script.** For development databases, a deterministic script that populates realistic data. Separate from the tests.

### 5.5 Tests in CI

| Trigger | Tiers executed | Timeout | Parallelism |
|---------|-------------|---------|-------------|
| Push to feature branch | Unit + lint | 5 min | Maximum |
| PR towards main | Unit + scenario + integration | 15 min | Per-tier |
| Merge to main | Unit + scenario + integration + E2E | 30 min | Per-tier |
| Scheduled (nightly) | All + full compat matrix | 60 min | Per-slot |
| Release tag | All + smoke tests on staging | 45 min | Sequential |

### 5.6 Assertion discipline: set-based vs sequence-based

Before writing an assertion, decide which of the two shapes the contract actually guarantees; the wrong choice turns every unrelated reorder into a red build.

| Shape | Use when | Assertion form |
|-------|----------|----------------|
| **Set-based** | Order is not part of the contract (listings without `ORDER BY`, parallel fan-in, unordered collections) | Compare as sets or multisets; assert membership and cardinality, not position |
| **Sequence-based** | Order is part of the contract (sorted endpoints, pagination, event streams, log replays) | Compare as ordered lists; any position change is a real failure |

Flakiness from "wrong shape" assertions must be fixed by changing the assertion, not by pinning the implementation to a coincidental order.

### 5.7 Schema-primary validation for contracts

Every outbound or inbound contract on the Boundary Contract Map (§8) is validated primarily against its schema — shape, types, required fields, value ranges, enum membership — and only secondarily against concrete example payloads.

Rules:

- The schema is the source of truth; fixture payloads exist to exercise the schema, not to pin exact bytes
- `additionalProperties: true` on inbound contracts (tolerant reader), `additionalProperties: false` on outbound contracts owned by the project (strict producer)
- Enum values are never duplicated across schema and code — both point to a single declaration
- A schema change on a shared contract is a contract-breaking change (§10.7) regardless of whether any current consumer happens to tolerate it

Golden-file equality is reserved for artefacts where the whole byte sequence *is* the contract (rendered UI snapshots, generated documents, wire-format fixtures). Using golden files for structured API responses couples the test to ordering and serialisation choices that the contract does not actually guarantee.

### 5.8 Two-layer regression snapshots

When the project consumes data or behaviour produced by an upstream system (external API, library output, generated schema, LLM-scored output), snapshots are split into two layers that are reviewed differently:

| Layer | What it captures | Review posture |
|-------|------------------|----------------|
| **Upstream layer** | Output of the upstream system as seen by the project | A diff here is expected whenever upstream changes; review confirms the change is benign and the project still satisfies its contracts |
| **Project layer** | Output of the project's own code given a fixed input | A diff here is a regression of the project itself and must be explained before merge |

Conflating the two layers makes every upstream update look like a project regression and trains reviewers to rubber-stamp snapshot updates. Keep the files separate (e.g. `snapshots/upstream/` vs `snapshots/project/`) and require different reviewers or different labels for updates to each.

Data-migration-specific testing patterns (golden queries that compare pre- and post-migration read results) live in D5 ML / Data Pipeline, which activates whenever the project persists structured data subject to schema evolution.

---

## 6. Documentation

### 6.1 Required documents

| Document | Content | Update |
|-----------|----------|---------------|
| **README.md** | Project purpose, quick start, high-level architecture, links to docs | On every significant change |
| **CHANGELOG.md** | History of changes per release, Keep a Changelog format | On every release |
| **DEPENDENCIES.md** | Critical dependencies, versions, contracts, links to official docs | When a dependency changes |
| **COMPATIBILITY.md** | Compatibility status with external dependencies (generated) | Automatic |
| **PROJECT_STATUS.md** | Current project status | Every session |
| **docs/prd/** | PRD and requirements documents | When requirements change |
| **docs/adr/** | Architecture Decision Records | On every architectural decision |
| **docs/runbooks/** | Operational procedures (deploy, rollback, incident response) | On every process change |

### 6.2 Code documentation

**Code comments — when and how:**

| Comment | Do not comment |
|----------|---------------|
| The **why** behind a non-obvious decision | The **what** (the code already says it) |
| Workarounds with a link to the bug/issue | Obvious code (`i++; // increment i`) |
| Assumptions that may not hold in future | Code that should be rewritten rather than commented |
| Contracts and invariants | TODOs without a reference issue |

**TODO/FIXME/HACK:** permitted ONLY with a reference to an issue:

```typescript
// TODO(US-AUTH-042): Replace with OAuth2 PKCE flow when Stripe supports it
// HACK(#issue-789): Workaround for upstream bug in synapse-client v2.237
```

TODOs without an issue = CI emits a warning. TODOs older than 30 days without an issue = CI fail.

API-surface documentation (REST endpoints, SDK exports, CLI contracts) is domain-specific and lives in the relevant appendix: D1.1 for web services, D2.1 for libraries/SDKs, D3.1 for command-line tools.

### 6.3 CHANGELOG.md

Keep a Changelog format (`keepachangelog.com`):

```markdown
## [Unreleased]

### Added
- New endpoint POST /api/v1/users (#123)

### Changed
- Migrated auth from session to JWT (#456)

### Deprecated
- Endpoint GET /api/v1/legacy-users — use /api/v1/users

### Removed
- Support for Node.js 16

### Fixed
- Fix race condition in WebSocket reconnect (#789)

### Security
- Updated stripe-sdk for CVE-2026-1234
```

The CHANGELOG is written by humans (or the AI agent), not generated from commits. Commits are too granular; the CHANGELOG is for the software's users.

---

## 7. CI/CD and deployment

### 7.1 Pipeline overview

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│  COMMIT  │──▶│  BUILD   │──▶│  TEST    │──▶│  STAGE   │──▶│  DEPLOY  │
└──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
     │              │              │              │              │
     ▼              ▼              ▼              ▼              ▼
  lint +         compile +      unit +         smoke +        release +
  format +       package        integration    scenario       health
  secret         artefact       + contract     tests in       check +
  scan                                         pre-prod       rollback
                                                              ready
```

The five-stage skeleton is universal. What "package artefact", "pre-prod environment", and "release" mean concretely depends on the project type — see the relevant domain appendix (D1 for web services, D4 for firmware, D5 for data pipelines, …).

### 7.2 Pipeline stages

#### 7.2.1 Build

- **Compile** the source into runnable form (binary, bytecode, transpiled JS, firmware image, bundled assets, …)
- **Package** the output as the distribution artefact (container image, wheel, executable, firmware blob, mobile bundle, …)
- **Artefacts are immutable:** the artefact tested in the Stage environment is the same artefact released at Deploy. Never rebuild per environment.

#### 7.2.2 Test

Execution of the test tiers according to the table in §5.5.

#### 7.2.3 Stage

- **Install the artefact** in a pre-production environment (staging, sandbox, simulator, hardware-in-the-loop bench, …)
- **Run smoke and scenario tests** against that environment before promotion
- **Promotion to Deploy requires green smoke tests**

The concrete shape of the pre-production environment depends on the project type (see the relevant appendix).

#### 7.2.4 Deploy

- **Release the tested artefact** to its consumers (production servers, package registry, firmware fleet, app store, …)
- **Validate the release** with a health check or acceptance verification appropriate to the artefact
- **Keep the prior version's artefact available** so rollback stays cheap
- **Strategy specifics** (blue-green, rolling, canary, OTA, staged rollout, store review) are domain-specific — see the relevant appendix

### 7.3 Rollback

Every deploy MUST be reversible. Rollback is a first-class operation, not an emergency.

| Scenario | Action | Target time |
|----------|--------|-------------|
| Health check fails post-deploy | Automatic rollback to the previous version | < 2 minutes |
| Critical bug discovered after release | Manual rollback (one button/command) | < 5 minutes |
| Rollback not possible (irreversible change) | Hotfix forward, immediate release | Depends on the fix |

When a specific class of change is inherently hard to reverse (a data migration, a breaking contract publication, a firmware flash), the domain appendix that owns that class defines the rollback protocol for it.

### 7.4 Configuration as code

- All CI/CD configuration is in the repository (`.github/workflows/`, `.gitlab-ci.yml`, etc.)
- No "click-ops" configuration in the forge — if it is not in the repository, it does not exist
- Forge-specific configuration in `ci/adapters/<forge>/`
- CI business logic (scripts, classifier, aggregator) lives outside the forge directory — it is portable

### 7.5 Adapter pattern for CI

All CI logic that is specific to GitHub Actions (or GitLab, or Forgejo) lives under `ci/adapters/<forge>/`. The rest (scripts, classifier, aggregator, compatibility database) is portable. Migrating to a new forge is a single-directory swap plus a new adapter.

---

## 8. Boundary Contracts

A **boundary contract** is any promise the system makes to something outside its own implementation: a device, a human, a data store, another piece of code. The **Boundary Contract Map** is the structured inventory of these promises. It answers the question: **where exactly in the code does each contract live, and who is its counterparty?**

The map is the substrate on which classification (§9) and remediation (§10) operate. When M1 Surveillance is active, it is also the target of compatibility testing (M1.2).

**Applicability.** Boundary Contracts are universal: they apply whenever a project has at least one external boundary worth tracking. A purely internal script with no inbound or outbound contracts does not need a map; a service that exposes APIs, consumes dependencies, drives hardware, or renders a UI does.

### 8.1 Contract axes

Every contract sits on one of four axes. A single contract may touch multiple axes when its shape spans them (for example, a REST endpoint that takes a JSON Schema body is both `api` and `data`).

| Axis | What it covers | Examples |
|------|----------------|----------|
| **Hardware** | Physical or virtual device interfaces | Sensor I/O, GPIO, serial/USB, device drivers, hardware event streams |
| **UI** | Interfaces exposed to humans | Web pages, mobile screens, CLI commands, voice prompts, desktop widgets |
| **Data** | Schemas and serialisation agreements | JSON Schema, protobuf, ORM models, database tables, file formats (CSV, Parquet), on-wire message shapes, environment variables and feature flags |
| **API** | Programmatic interfaces consumed by other code | REST/GraphQL/gRPC endpoints, SDK methods, RPC, webhooks, CLIs invoked by other programs |

Direction matters. Each contract is either:

- **Inbound** — the project exposes it; the counterparty is downstream.
- **Outbound** — the project consumes it; the counterparty is upstream.

Both directions are tracked. Inbound contracts are watched against the promise the project makes to its consumers (regression). Outbound contracts are watched against the promise the upstream makes to the project (drift).

### 8.2 Contract map format

```json
{
  "contracts": [
    {
      "id": "stripe.charges.create",
      "axis": "api",
      "direction": "outbound",
      "counterparty": "stripe-api",
      "shape": "POST /v1/charges",
      "file": "src/payments/stripe-client.ts",
      "line": 42,
      "context": "createCharge()",
      "risk_weight": "high",
      "test_coverage": true,
      "last_verified": "2026-04-15"
    }
  ],
  "generated_at": "2026-04-15T10:00:00Z",
  "generator": "manual|ast-walker|grep",
  "contract_count": 47
}
```

The `shape` field is axis-specific: method + path for `api`, a schema identifier for `data`, a device path or event name for `hardware`, a screen or command identifier for `ui`.

### 8.3 Generation

Three strategies, in order of reliability:

1. **AST walker** (best) — static analysis of the source code. Resolves template literals, dynamic imports, type inference. Tools: `ts-morph` for TypeScript, `ast` for Python, `go/ast` for Go. Applies primarily to `api` and `data` contracts.
2. **Structured grep** — pattern search with `ripgrep`. Fast but misses dynamic paths. Useful for `hardware` device paths, CLI contracts, and well-patterned API calls.
3. **Manual** — curated by hand. Acceptable as an initial stub, to be replaced as soon as an automated generator is viable. Often the only option for `ui` contracts.

Different axes can use different generators; the resulting entries are merged into a single map.

### 8.4 Cardinality guard

If the total contract count drops by more than 10% between one generation and the next, CI MUST fail. The guard applies per-axis as well as globally — a 20% drop in `api` contracts with no corresponding PRD change is a red flag even if the total remains stable. Catches: refactors that move calls outside the recognised pattern, configuration changes that exclude files, walker updates.

---

## 9. Change classification

### 9.1 Buckets

| Bucket | Description |
|--------|-------------|
| `data-model` | Changes to schemas, models, types |
| `api-endpoint` | Endpoints added, removed, modified |
| `sdk-method` | Library methods changed |
| `auth` | Authentication, permissions, policies |
| `config` | Environment variables, feature flags |
| `docs-only` | Documentation only |
| `internal` | Internal refactoring, no contract impact |
| `security` | Security patches |
| `deprecation` | Deprecation of existing contracts |
| `migration` | Migrations that modify existing data |

### 9.2 Severity

| Severity | Definition | Action |
|----------|------------|--------|
| `safe` | `internal` or `docs-only` only | Auto-merge after green CI |
| `additive` | New endpoints, new fields, new libraries | PR with report |
| `breaking` | Contracts removed, renamed, signature changed | Draft PR + human review |
| `p0` | Security advisory, protocol change | Draft PR + immediate notification |

### 9.3 Never-auto-merge list

Conditions that always force human review: endpoint removal/rename, response format change, auth protocol change, rate limit reduction, SDK method removal, migration that rewrites data, critical/high security advisory, required field change, WebSocket handshake change, functional test regression.

---

## 10. Remediation workflow

Remediation is a **risk-modulated response pattern**. It applies to any change that passes through classification (§9) — a dependency bump, an inbound contract update, an internal refactor, a config edit — not only to dependency upgrades.

**When to adopt.** The pattern scales down to "everything is L2" (all changes require a human) and scales up to "L0 is enabled for well-tested safe changes". A small project with no CI and no automated classifier operates entirely at L2 by default; that is a valid adoption of the pattern, not an absence of it. L0 and L1 activate only when the project has the machinery to support them (CI, correctness gate, regression tests, classifier). Projects adopt levels as their risk tolerance and tooling maturity allow.

### 10.1 Autonomy levels

| Level | Applies when | Action | Approval |
|-------|--------------|--------|----------|
| **L0** | Change classified `safe` (§9) and all tests green | Auto-merge | None |
| **L1** | Change classified `additive` and the agent's fix passes the correctness gate (§10.2) | PR with fix-claim | Human review |
| **L2** | Change classified `breaking` or `p0`, or matches any never-auto-merge rule, or the project does not yet have L0/L1 machinery | Draft PR + notification | Human intervention |

The levels are a ladder. A project unable to meet L0's preconditions simply stays at L2 for that class of change; no step is mandatory.

### 10.2 Correctness gate (L1)

Green CI is not sufficient to clear L1. The agent MUST: validate against the specific schema that triggered the failure, include a structured fix-claim, add a regression test, and limit changes to the client/adapter layer.

### 10.3 Circuit breaker

3 open L1 PRs OR 5 attempts in 14 days → L1 automation paused, everything degrades to L2, human acknowledgement required before re-enabling.

### 10.4 Human-agent handover

When the circuit breaker trips (§10.3), the agent MUST produce a **handover dossier** before degrading to L2. The dossier is attached to the tracking issue and contains:

| Section | Content |
|---------|---------|
| **Trigger summary** | Which contract, what classification, what change triggered the sequence |
| **Attempt log** | For each failed L1 attempt: PR link, fix-claim, test result, reason for failure |
| **Root-cause hypothesis** | The agent's best assessment of why the fix did not hold (schema mismatch, upstream regression, environmental) |
| **Blast radius** | Files, endpoints, and downstream consumers affected |
| **Suggested next steps** | Concrete actions the human can take, ranked by likelihood of success |
| **Reproduction steps** | Minimal steps or commands to reproduce the failure locally |

The dossier reduces the human's ramp-up time from "read three PRs and guess" to "read one summary and act". The agent does not attempt further automation on the affected contract until the human explicitly re-enables L1.

### 10.5 Adoption workflow

When a change is classified as introducing new capabilities in an existing contract: cross-reference with the Boundary Contract Map, add a wrapper in the client, write a contract test, open an adoption PR + tracking issue for UI changes.

### 10.6 Deprecation tracking

Record the deprecation, cross-reference with the Boundary Contract Map, open a `deprecation-watch` issue. Migration is always human-led.

### 10.7 Contract-breaking change protocol

Triggered whenever a tracked contract breaks (major version bump of an outbound dependency, incompatible schema change, endpoint removal, hardware protocol revision, UI-flow breaking change). Actions: L1 disabled for the affected contract, coverage baseline resettable, Boundary Contract Map mandatorily regenerated, test harness verified end-to-end, issue opened as a tracking epic.

### 10.8 Human report

For each change, the agent produces a report with: what changed, classification, where it impacts (files and lines), what must be modified to maintain operability, what can be adopted, test results, recommended action, and the autonomy level selected with justification.

---

## 11. Project lifecycle

Each phase lists the **Core steps** that apply to every project, followed by activation blocks that only apply when the named module or domain is active. This structure mirrors the Emergent Expansion Protocol (§2.2): nothing module-specific is mandatory until the module's trigger fires.

### 11.1 Phase 0 — Ideation and requirements

**Core (always):**

1. Write the PRD (§1.2)
2. Define user stories with acceptance criteria (§1.3, §1.4)
3. Document architectural decisions in ADRs (§1.5)
4. Create the backlog ordered by priority (§1.6)
5. Define the Definition of Done (§1.8)
6. Identify critical dependencies and document them in `DEPENDENCIES.md`

### 11.2 Phase 1 — Technical bootstrap

**Core (always):**

1. Create the directory structure (§2.1)
2. Configure linting, formatting, pre-commit hooks (§3.4)
3. Configure the base CI pipeline (build + lint + unit test) (§7)
4. Write `CLAUDE.md` (or the equivalent agent-configuration file) with operating rules (§2.4)
5. Generate the initial contract map (§8)
6. Write `.env.example` with all variables documented — where the project handles secrets (§4.3)

**If M1 Surveillance is active, also:**

- Configure surveillance agents (M1.1)
- Create the first compatibility record (`untested`) (M1.3)

**If the project persists structured data (relational or otherwise), also:**

- Write the seed script for the development data store (§5.4)

### 11.3 Phase 2 — Active development

**Core (always):**

1. Work by User Story, respecting the Definition of Done (§1.8)
2. Update `PROJECT_STATUS.md` at every session (§2.3)
3. Write tests for every appropriate tier (§5)
4. Maintain the coverage ratchet (§5.3)
5. Update the CHANGELOG on every user-visible change (§6.3)
6. Keep the contract map up to date after significant refactors (§8)

**If M1 Surveillance is active, also:**

- Agents run in the background and produce compatibility records (M1.3)
- Fix and adoption PRs generated by the agents are reviewed and merged (M1.1)

**If D1 Web Service, D2 Library/SDK, or D3 CLI Tool is active, also:**

- Update API documentation when the contract surface changes (D1.1 / D2.1 / D3.1)

### 11.4 Phase 3 — Maturity and maintenance

**Core (always):**

1. Fixes are primarily L0/L1 (§9, §10)
2. Quarterly review of baseline and thresholds
3. Update the never-auto-merge list (§9.3)

**If M1 Surveillance is active, also:**

- Agents continue surveillance (M1.1)
- Monthly classifier retrospective (M1.4.2)

**If M2 Security-sensitive is active, also:**

- Annual review of OWASP Top 10 coverage and security practices (M2.3)

### 11.5 Phase 4 — Major dependency upgrade

1. The major-version protocol activates (§10.7)
2. L1 disabled, everything is L2
3. Contract map regenerated (§8)
4. Coverage baseline reset (§5.3)
5. Test harness verified
6. Return to Phase 3 after migration

### 11.6 Phase R — Retrofit (existing projects)

Phase R applies when the Codex Machinae is adopted on a project that already has code,
history, and technical debt. Unlike Phases 0–4, Phase R is not sequential — it is a
one-time convergence protocol that brings the project into a state from which it can
enter the normal lifecycle at Phase 2 or Phase 3 depending on its maturity.

**Trigger:** the project has existing source code, a repository with history, and at
least one deployed or distributable artefact. If the project is greenfield, start at
Phase 0 instead.

#### 11.6.1 Debt-scoping audit

Before any change, produce a structured assessment of the gap between the project's
current state and the playbook's expectations. The audit covers:

| Area | What to check | Output |
|------|---------------|--------|
| Requirements artefacts | PRD, user stories, ADRs, backlog | List of missing or incomplete artefacts |
| Project structure | Directory layout (§2.1), configuration files, agent config (§2.4) | Conformance delta |
| Code quality | Linting, formatting, commit conventions (§3) | Gap list with estimated effort |
| Security posture | Secrets management (§4.3), input validation (§4.2) | Risk register |
| Test coverage | Current coverage vs playbook baseline (§5.3), tier distribution | Coverage report + ratchet starting point |
| Documentation | README, CHANGELOG, code comments (§6) | Missing-doc list |
| CI/CD | Pipeline maturity vs §7 expectations | Pipeline gap analysis |
| Boundary contracts | Existing integration points vs contract map (§8) | Draft contract map |

The audit result is a document (`RETROFIT_AUDIT.md`) committed to the repository root.
It is the single source of truth for retrofit planning.

#### 11.6.2 Retroactive contract mapping

Generate the Boundary Contract Map (§8) from the existing codebase. For each integration
point discovered:

1. Classify by axis (api, data, ui, hardware) and direction (inbound, outbound, bidirectional)
2. Record the current compatibility status (`untested`, `compatible`, `incompatible`)
3. Note any undocumented or implicit contracts — these are the highest-risk items

The contract map is the foundation for activating M1 Surveillance and for understanding
the project's blast radius on dependency changes.

#### 11.6.3 Prioritised adoption plan

Using the audit and the contract map, produce an ordered adoption plan. The plan groups
work into three tiers:

| Tier | Criteria | Examples |
|------|----------|----------|
| **T1 — Safety net** | Items that prevent silent regression or data loss | Coverage ratchet (§5.3), secrets audit (§4.3), CI pipeline baseline (§7) |
| **T2 — Structure** | Items that bring the project into conformance with Core conventions | Directory layout (§2.1), agent config (§2.4), CHANGELOG (§6.3), contract map (§8) |
| **T3 — Process** | Items that enable ongoing lifecycle operations | Surveillance activation (M1), checklist adoption (Appendix A), Definition of Done (§1.8) |

Each tier is a commit boundary. T1 is non-negotiable and must be completed before T2
begins. T2 and T3 may be interleaved if the project's context demands it, but T1 always
comes first.

#### 11.6.4 Module activation

During retrofit, modules and domain appendices are activated exactly as in a greenfield
project: when the trigger fires (§2.2). The difference is that triggers may already be
satisfied by the existing codebase. The agent or analyst walks the trigger list and
activates every module whose condition is met.

Modules activated during retrofit follow the same rules as in the normal lifecycle, but
the initial state of their artefacts (compatibility records, security reviews, taxonomy
registries) is populated retroactively rather than incrementally.

#### 11.6.5 Entry into the normal lifecycle

Once T1 and T2 are complete, the project enters the normal lifecycle:

- If the project is actively developed and receives regular feature work → enter at
  **Phase 2** (§11.3).
- If the project is stable and receives only maintenance and dependency updates → enter
  at **Phase 3** (§11.4).

The `RETROFIT_AUDIT.md` remains in the repository as a historical record. It is not
updated after entry into the normal lifecycle — `PROJECT_STATUS.md` takes over.

---

## 12. Conventions for AI agents

### 12.1 General rules

- The agent reads `CLAUDE.md` before any action
- The agent updates `PROJECT_STATUS.md` after every session
- The agent never modifies files on the never-auto-merge list without human confirmation
- The agent never modifies business logic — only the client/adapter layer and tests
- The agent always includes a regression test for every fix
- The agent does not pretend to execute operations — if it cannot do something, it says so

### 12.2 Grounding on live data

The first step of any fix loop MUST be: retrieve live data from the dependency and pin it in context. Prevents hallucination of non-existent signatures, endpoints, or behaviours.

### 12.3 Mandatory fix-claim

Every PR produced by the agent MUST include a structured fix-claim (§10.2).

### 12.4 Limited scope

The L1 agent may ONLY add new files, new exports, modify files in the client/adapter layer, and add tests.

The L1 agent may NOT modify existing methods, change existing call sites, alter UI behaviour, modify deploy configuration, or delete files or code.

### 12.5 Proposal before code

For complex features, the agent MUST propose the approach in written form (document or comment) and await human approval before writing code. No "surprise" code.

### 12.6 Structured logging

Every agent action is logged as an event in the compatibility database. Everything is traceable, reproducible, and auditable.

### 12.7 Multi-agent coordination (optional)

This subsection activates only when the analyst chooses to employ more than one agent on
the same project. It is not a requirement — single-agent operation remains the default.
The protocol is LLM-agnostic: an "agent" may be any model (Claude, Gemini, Copilot, or
any other provider). Multi-agent covers both multiple instances of the same LLM and
mixed-LLM teams. Every participating agent must individually comply with §§12.1–12.6
regardless of the coordination protocol.

#### 12.7.1 Lead agent designation

The analyst nominates one agent as the **lead**. The lead is the single writer for
coordination artefacts (`PROJECT_STATUS.md`, the Boundary Contract Map, `CHANGELOG.md`).
All other agents read those files but do not modify them. If an agent needs a
coordination artefact updated, it requests the change from the lead or from the analyst.

The lead designation is recorded in the project's agent-configuration file (§2.4) so
that every agent can identify it at session start.

#### 12.7.2 Scope partitioning

Each agent receives an explicit perimeter before starting work. Partitioning may be by:

| Strategy | When to use | Example |
|----------|-------------|---------|
| **By module/domain** | Large projects with independent subsystems | Agent A owns D1, Agent B owns D5 |
| **By directory** | When module boundaries map cleanly to folders | Agent A owns `src/api/`, Agent B owns `src/ml/` |
| **By user story** | Sprint-based work with non-overlapping stories | Agent A works on US-007, Agent B on US-012 |

The analyst documents the partition in the agent-configuration file or in
`PROJECT_STATUS.md`. An agent must not operate outside its assigned perimeter without
explicit analyst approval.

#### 12.7.3 Conflict prevention

1. **File-level exclusivity** — a file being modified by one agent is off-limits to
   others until the change is committed. Agents declare intent before editing by noting
   the target file in their session log.
2. **Lead coordination** — when two agents must touch the same file, the lead (or the
   analyst) determines the sequence. The second agent waits until the first agent's
   commit is merged.
3. **Merge conflicts** — if a conflict arises despite the protocol, resolution always
   requires human intervention. No agent auto-resolves merge conflicts in a multi-agent
   context.

#### 12.7.4 Shared artefacts protocol

Files are classified by write access:

| Category | Write access | Examples |
|----------|-------------|----------|
| **Single-writer** | Lead agent only | `PROJECT_STATUS.md`, contract map (§8), `CHANGELOG.md` |
| **Partitioned** | Owning agent per scope partition | Source code, tests, domain-specific docs |
| **Human-only** | No agent writes without explicit approval | Never-auto-merge list (§9.3), agent-configuration file (§2.4) |

An agent encountering a file outside its write-access category must request the change
through the lead or the analyst rather than editing directly.

#### 12.7.5 Inter-agent handover

When work passes from one agent to another (shift change, scope transfer, or escalation),
the outgoing agent produces a structured handover note:

| Field | Content |
|-------|---------|
| **Scope completed** | List of files changed, stories closed, tests added |
| **Decisions taken** | Architectural or design choices made during the session |
| **Open blockers** | Issues that prevented completion, with root-cause hypotheses |
| **Context for the next agent** | Key findings, relevant file locations, state of any in-progress work |

The handover note is appended to the session log or committed as a standalone file in
the project's documentation directory. The receiving agent reads it before starting work.

#### 12.7.6 Mixed-LLM considerations

When agents from different LLM providers collaborate:

- Each agent's configuration file (§2.4) is provider-specific (`CLAUDE.md`, `GEMINI.md`,
  etc.) but all share the common rules in `AI-AGENTS.md`.
- Agents must not assume shared context or memory between providers. All coordination
  happens through committed artefacts, not through implicit state.
- The analyst is responsible for ensuring that provider-specific instructions do not
  contradict the shared rules or the scope partition.

---

# PART II — DOMAIN APPENDICES

---

Domain Appendices add project-type-specific content on top of the Core. Activate an appendix
when its trigger fires; otherwise ignore it. Multiple appendices may be active for a single
project (a web service that ships a client SDK activates D1 and D2).

Each appendix adds content to the Core; it never replaces Core rules. If an appendix and the
Core disagree, the Core wins unless the appendix explicitly marks the override.

## D1 Web Service

**Activation trigger.** The project exposes HTTP, REST, GraphQL, WebSocket, or gRPC endpoints
to clients outside its own process.

**In addition to Core.** Core §6 required documents, code docs, and CHANGELOG apply. This
appendix adds the API-surface conventions and runtime/deploy patterns specific to networked
services.

### D1.1 API documentation

Every public HTTP/REST, GraphQL, gRPC, or WebSocket endpoint MUST have documentation generated from the code:

| Type | Recommended tool | Output |
|------|------------------|--------|
| REST API | OpenAPI/Swagger (from annotations) | `docs/api/openapi.yaml` |

API documentation is generated in CI and published automatically. Manually written API documentation that diverges from the code is an announced bug.

### D1.2 Deploy strategy

- **Production release** triggered by a release tag (`v*.*.*`)
- **Rolling update** or **blue-green** — never a "big bang" deploy without automatic rollback
- **Canary** for high-risk changes: route a small percentage of traffic to the new version first, promote only after stability metrics hold
- **Health check** post-deploy: the application responds on `/healthz` within 60 seconds
- **Automatic rollback** if the health check fails after 3 attempts
- **Feature flags** for risky features: deploy the disabled code, enable gradually

### D1.3 Environments

| Environment | Purpose | Data | Deploy |
|----------|-------|------|--------|
| **Local** | Development | Seed script | Manual |
| **CI** | Automated tests | Generated by tests | Automatic on push |
| **Staging** | Pre-production validation | Anonymised copy of production | Automatic on merge to main |
| **Production** | Real users | Real | Manual/automatic on tag |

Staging is a replica of production: same infrastructure topology, same secrets (rotated), same database schema. A divergence between staging and production is a bug in the environment definition, not a feature.

### D1.4 Request-path testing

In addition to Core §5 (testing pyramid, coverage ratchet, schema-primary validation), web
services require tests that exercise the request path end-to-end through the network stack.

**Contract tests.** Every inbound API contract (§8, axis `api`, direction `inbound`) has at
least one contract test that sends a real HTTP request to a running instance of the service
and asserts on status code, response schema, and key semantic invariants. Contract tests run
in CI against a throwaway environment (Docker Compose, Testcontainers, or equivalent).

**Negative-path coverage.** For every endpoint, test at least:

| Scenario | Expected behaviour |
|----------|--------------------|
| Missing required field | 400 with a machine-readable error body |
| Invalid type / out-of-range value | 400 |
| Unauthenticated request (when auth required) | 401 |
| Insufficient permissions | 403 |
| Non-existent resource | 404 |
| Malformed `Content-Type` | 415 |
| Rate-limit exceeded | 429 with `Retry-After` header |

**Latency assertions.** Critical endpoints (login, health check, primary read path) carry a
latency ceiling in the test suite. The ceiling is a p95 measured over at least 50 sequential
requests against a local instance. Exceeding it does not break CI by default — it emits a
warning — but the team may promote any ceiling to a hard gate via §5.3 ratchet.

**Idempotency.** Every `PUT` and `DELETE` endpoint is tested for idempotency: sending the
same request twice produces the same observable state as sending it once.

### D1.5 Rate-limiting and back-pressure

**Rate-limiting.** Every public-facing endpoint MUST enforce a rate limit. The limit is
declared per-endpoint (or per-group) and is surfaced to the caller via standard headers:

| Header | Meaning |
|--------|---------|
| `X-RateLimit-Limit` | Maximum requests allowed in the window |
| `X-RateLimit-Remaining` | Requests remaining in the current window |
| `X-RateLimit-Reset` | UTC epoch seconds when the window resets |
| `Retry-After` | Seconds to wait (returned with 429) |

Internal endpoints behind a trusted network boundary may omit rate-limiting if and only if
the Boundary Contract Map (§8) records the trust assumption explicitly.

**Back-pressure.** When a downstream dependency is slow or unavailable, the service MUST shed
load rather than queue unboundedly:

- Circuit breaker on every outbound contract marked `risk_weight: high` in the contract map.
  States: closed → open (after N consecutive failures or error-rate threshold) → half-open
  (probe with a single request) → closed.
- Timeout on every outbound call. The timeout is explicit in the code, never implicit from a
  library default. Suggested starting point: 2× the p99 latency observed in production.
- Bulkhead isolation: failure in one outbound dependency does not exhaust the thread/connection
  pool used by other dependencies. Implementation: per-dependency connection pools, or
  async concurrency limiters.

### D1.6 Observability

**Structured logging.** Every log entry is a structured object (JSON or key-value), never a
free-form string. Mandatory fields:

| Field | Content |
|-------|---------|
| `timestamp` | ISO 8601 with timezone |
| `level` | `debug`, `info`, `warn`, `error` |
| `service` | Service name (from configuration) |
| `trace_id` | Distributed trace identifier (propagated from inbound request) |
| `message` | Human-readable summary |

Log entries MUST NOT contain secrets, tokens, passwords, or PII. When M2 is active, this
rule is enforced by the M2.2 PR checklist.

**Metrics.** At a minimum, every web service exposes:

| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | Total requests, labelled by method, path, status |
| `http_request_duration_seconds` | Histogram | Latency distribution, labelled by method, path |
| `http_active_connections` | Gauge | Current open connections |
| Dependency health | Gauge | One gauge per outbound contract (0 = down, 1 = up) |

Metrics are exposed via a `/metrics` endpoint (Prometheus-compatible) or pushed to the
telemetry backend. The choice is recorded in the contract map (axis `api`, direction
`inbound`, counterparty `telemetry-backend`).

**Distributed tracing.** Every inbound request receives (or propagates) a trace ID using
W3C Trace Context (`traceparent` header). The trace ID is attached to all log entries and
outbound calls for the duration of the request. Tracing is sampled in production (suggested
starting point: 1% of traffic, 100% of errors).

**Health and readiness.** Two endpoints, always present:

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `GET /healthz` | Liveness — is the process alive? | 200 if the process can serve; no dependency checks |
| `GET /readyz` | Readiness — can the process accept traffic? | 200 only when all critical dependencies are reachable |

Both endpoints are excluded from rate-limiting and authentication.

## D2 Library / SDK

**Activation trigger.** The project is published as a reusable package to a registry
(npm, PyPI, Maven Central, crates.io, NuGet, RubyGems, Packagist, Go modules, …) or consumed
directly via VCS reference as a library.

**In addition to Core.** Core §6 required documents, code docs, and CHANGELOG apply. This
appendix adds the patterns specific to published packages.

### D2.1 API documentation

Every public SDK surface (exported modules, classes, functions, types) MUST have
documentation generated from the code:

| Type | Recommended tool | Output |
|------|------------------|--------|
| TypeScript SDK | TypeDoc | `docs/api/` |
| Python SDK | Sphinx + autodoc | `docs/api/` |

API documentation is generated in CI and published alongside the package. Manually
written API documentation that diverges from the code is an announced bug.

### D2.2 Semantic versioning

Published libraries follow [Semantic Versioning 2.0.0](https://semver.org/) strictly:

| Bump | When | Example |
|------|------|---------|
| **Major** | Breaking change to the public API | Removing an exported function, changing a return type, renaming a parameter |
| **Minor** | Additive change — new functionality, no existing contract broken | New exported function, new optional parameter with a default |
| **Patch** | Bug fix or internal change — no public API change | Fix incorrect return value, performance improvement, dependency update |

**What counts as public API.** Every symbol that is exported from the package's entry
point(s) and reachable by a consumer without bypassing access controls. Internal modules
(prefixed with `_` in Python, not re-exported in TypeScript `index.ts`) are not public
API — but if a consumer can import them, they are de facto public until the package
enforces module boundaries.

**Pre-release versions.** Use SemVer pre-release identifiers for unstable releases:
`1.0.0-alpha.1`, `1.0.0-beta.3`, `1.0.0-rc.1`. Pre-release versions carry no
backwards-compatibility guarantee. The CHANGELOG (§6.3) must note when a pre-release
is promoted to stable.

### D2.3 Deprecation policy

Removing or changing a public API symbol requires a deprecation cycle:

1. **Annotate.** Mark the symbol as deprecated in the code using the language's standard
   mechanism (`@deprecated` JSDoc tag, `warnings.warn(DeprecationWarning)` in Python,
   `@Deprecated` annotation in Java/Kotlin). The annotation includes the replacement
   and the version in which the symbol will be removed.
2. **Document.** Record the deprecation in the CHANGELOG under a `Deprecated` section.
3. **Minimum window.** The deprecated symbol remains functional for at least **one minor
   release** after the deprecation is published. For widely-used libraries (> 1 000
   weekly downloads or equivalent), extend to **two minor releases**.
4. **Remove.** The symbol is removed in the next major release after the window expires.
   The removal is recorded in the CHANGELOG under `Removed`.

Deprecation warnings MUST be visible at runtime (log or stderr) so consumers discover
them during testing, not after a version bump breaks their code.

### D2.4 Breaking-change detection

CI includes an automated step that compares the current public API surface against the
last published version and fails the build if:

- A public symbol was removed or renamed on a minor or patch bump.
- A function signature changed in an incompatible way (parameter removed, type narrowed,
  return type changed) on a minor or patch bump.
- A type was widened in a way that could break consumer type-checks on a patch bump.

| Language | Recommended tool | Mechanism |
|----------|------------------|-----------|
| TypeScript | `api-extractor` (Microsoft) | Generates `.d.ts` rollup; diff against baseline |
| Python | `griffe` | Extracts API from source; reports breaking changes |
| Java/Kotlin | `japicmp` | Compares JAR bytecode against previous version |
| Rust | `cargo-semver-checks` | Lint against SemVer violations |

The baseline is the API snapshot of the last published version, committed as a CI
artefact (e.g. `api-report.md` for `api-extractor`). The snapshot is updated on every
release, not on every commit.

### D2.5 Package publishing

**Pre-publish checklist (automated in CI where possible):**

1. All tests pass across all tiers (§5.5).
2. Coverage has not dropped below baseline (§5.3).
3. CHANGELOG updated with a release entry (§6.3).
4. Version bumped in the package manifest (`package.json`, `pyproject.toml`, `Cargo.toml`,
   `pom.xml`).
5. API documentation regenerated (D2.1).
6. Breaking-change detection passed (D2.4).
7. Git tag created matching the version (`v1.2.3`).

**CI publish pipeline.** Publishing is triggered by a version tag, never by a manual
`npm publish` or `twine upload`. The pipeline:

1. Checks out the tagged commit.
2. Runs the full test suite.
3. Builds the distributable artefact (tarball, wheel, JAR, crate).
4. Publishes to the registry using credentials stored in CI secrets.
5. Creates a GitHub Release (or equivalent) with the CHANGELOG entry as the body.

**Registry-specific notes:**

| Registry | Key concern |
|----------|------------|
| npm | Use `prepublishOnly` script to enforce build + test before pack. Publish with `--provenance` for supply-chain attestation where supported |
| PyPI | Build with `build`, publish with `twine`. Use Trusted Publishers (OIDC) over long-lived API tokens |
| Maven Central | Sign artefacts with GPG. Use staging repositories for validation before promotion |
| crates.io | Run `cargo publish --dry-run` in CI before the real publish |

### D2.6 Multi-language coordination

When the same SDK ships in more than one language (e.g. TypeScript + Python client for
the same API):

1. **Version parity.** All language variants share the same major.minor version. Patch
   versions may diverge for language-specific fixes but must be documented in a shared
   CHANGELOG or a per-language CHANGELOG with cross-references.
2. **Feature matrix.** Maintain a table listing every public capability and its
   implementation status per language (`implemented`, `planned`, `not applicable`).
   The matrix lives in `docs/sdk-feature-matrix.md` or equivalent.
3. **Release coordination.** All language variants are released within the same sprint
   or release cycle. A feature available in one language but not another for more than
   one release cycle is a backlog item, not an accepted divergence.
4. **Contract sharing.** Where possible, generate client SDKs from a shared contract
   definition (OpenAPI spec, gRPC `.proto` files, GraphQL schema). Manual implementations
   across languages are a maintenance liability — prefer code generation with thin
   hand-written wrappers for ergonomics.

## D3 CLI Tool

**Activation trigger.** The project's primary interface is a command-line executable invoked
by humans or by scripts.

**In addition to Core.** Core §6 required documents, code docs, and CHANGELOG apply. This
appendix adds the patterns specific to command-line interfaces.

### D3.1 CLI documentation

The CLI's contract surface (flags, subcommands, exit codes, output modes) MUST be
documented and kept in sync with the code:

| Type | Recommended tool | Output |
|------|------------------|--------|
| CLI | `--help` + generated man page | `docs/cli/` |

Documentation is generated from the code (help strings, argument metadata) in CI.
Manually written documentation that diverges from `--help` is an announced bug.

### D3.2 Argument and subcommand design

CLI interfaces follow POSIX and GNU conventions unless the target platform has a
dominant alternative (e.g. PowerShell verb-noun on Windows):

| Rule | Example |
|------|---------|
| Short flags are single dash + single letter | `-v`, `-f` |
| Long flags are double dash + kebab-case word | `--verbose`, `--output-format` |
| Boolean flags do not take a value | `--dry-run` (not `--dry-run=true`) |
| Value flags use `=` or space | `--output=json` or `--output json` |
| `--` terminates flag parsing | `mytool -- -not-a-flag` |
| Subcommands precede flags | `mytool deploy --env staging` |
| No ambiguity between positional args and flags | Positional args come after all flags, or are unambiguous by position |

**Help hierarchy.** Every level of the command tree has a `--help` output:

- `mytool --help` — lists subcommands and global flags.
- `mytool <subcommand> --help` — lists subcommand-specific flags and arguments.

Help text includes at least: one-line description, usage synopsis, flag table with
defaults, and one example invocation.

**Global flags.** The following flags are reserved across all subcommands:

| Flag | Short | Meaning |
|------|-------|---------|
| `--help` | `-h` | Show help and exit |
| `--version` | `-V` | Show version and exit |
| `--verbose` | `-v` | Increase output verbosity (stackable: `-vvv`) |
| `--quiet` | `-q` | Suppress non-error output |

### D3.3 Exit-code contracts

Every CLI tool defines and documents a set of exit codes. The minimum set:

| Code | Meaning | When |
|------|---------|------|
| `0` | Success | The command completed its intended operation |
| `1` | User error | Invalid input, missing required argument, file not found |
| `2` | Internal error | Unexpected failure, unhandled exception, bug |

Domain-specific codes (`3`–`125`) are permitted but must be documented in the help text
and in `docs/cli/exit-codes.md`. Codes `126`–`255` are reserved by the shell and must
not be used.

**Testing.** Every documented exit code has at least one test that triggers it and
asserts on the exact code. Exit-code tests are part of the integration tier (§5).

### D3.4 Machine-readable output

Every command that produces structured output supports at least one machine-readable
format alongside the human-readable default:

| Flag | Format | When to use |
|------|--------|-------------|
| `--json` | JSON (one object or array per invocation) | Scripting, piping to `jq`, programmatic consumption |
| `--csv` | CSV with header row | Tabular data, spreadsheet import |

**Rules:**

1. Human-readable output is the default. Machine-readable is opt-in via flag.
2. The JSON schema is stable within a major version. Breaking changes follow D2.2
   SemVer rules (machine-readable output is public API).
3. JSON output goes to stdout. Errors and warnings go to stderr regardless of output
   mode, so piping works correctly: `mytool list --json | jq '.[] | .name'`.
4. When `--json` is active, the exit code still reflects success/failure — the caller
   should not need to parse JSON to detect errors.

### D3.5 Shell completion

The CLI ships or generates completion scripts for at least two shells:

| Shell | Generation mechanism | Installation |
|-------|---------------------|-------------|
| Bash | `mytool completion bash` | Source in `.bashrc` or install to `/etc/bash_completion.d/` |
| Zsh | `mytool completion zsh` | Install to `$fpath` or source in `.zshrc` |
| Fish | `mytool completion fish` (optional) | Install to `~/.config/fish/completions/` |

Completion covers subcommands, flags (including value suggestions where feasible), and
file-path arguments. Completion scripts are regenerated in CI when the command tree
changes and included in the release artefact.

Most CLI frameworks generate completions automatically (Cobra for Go, Clap for Rust,
Click for Python, Commander/Yargs for Node.js). Prefer framework-native generation
over hand-written scripts.

### D3.6 Installation and distribution

The CLI is distributed through multiple channels appropriate to the target audience:

| Channel | When to support | Artefact |
|---------|----------------|----------|
| **Standalone binary** | Always (if compiled language) | Pre-built binaries per OS/arch in GitHub Releases |
| **Homebrew** | macOS/Linux audience | Tap formula or core formula |
| **apt / deb** | Debian/Ubuntu server audience | `.deb` package |
| **Scoop / Chocolatey** | Windows audience | Manifest in a bucket/repo |
| **npm / pip / cargo install** | Developer audience using the language's ecosystem | Published to the language registry |
| **Container image** | CI/CD and ephemeral usage | Minimal image with the binary as entrypoint |

**Rules:**

1. Every supported channel has a CI step that builds and publishes the artefact on
   release tag.
2. The installation matrix (channels × OS × architecture) is documented in the README
   and tested in CI for at least the primary channel.
3. Standalone binaries are checksummed (SHA-256) and the checksums file is published
   alongside the binaries. Signed binaries are preferred where feasible (GPG or
   Sigstore/cosign).
4. Reproducible builds are a goal: given the same source and toolchain version, the
   output binary should be byte-identical. Record the toolchain version in CI and in
   the release notes.

## D4 Embedded / Firmware

**Activation trigger.** The project runs on fixed hardware with bounded memory, storage,
or energy; or requires toolchains cross-compiling to a target architecture; or depends on
peripherals (sensors, radios, actuators) whose contracts are captured in the Boundary Contract
Map under the Hardware axis.

**In addition to Core.** Core applies fully — requirements, code quality, testing pyramid,
documentation, CI/CD concepts, boundary contracts, change classification, remediation. This
appendix adds the patterns that only arise when the artefact runs on constrained hardware.

### D4.1 Hardware boundary contracts

Every peripheral (sensor, actuator, radio, display, storage) is an outbound contract in the
Boundary Contract Map (§8, axis `hardware`). The contract entry records:

| Field | Content |
|-------|---------|
| `device` | Part number or family (e.g. `BME280`, `SX1276`) |
| `bus` | Communication bus (I2C, SPI, UART, GPIO, USB, CAN, …) |
| `address` | Bus address or pin assignment |
| `driver` | Source file that owns the abstraction |
| `datasheet` | Path or URL to the canonical datasheet |
| `voltage_level` | Logic-level voltage (e.g. 3.3 V, 5 V) |
| `power_budget_mW` | Typical and peak draw (from datasheet) |

**Hardware Abstraction Layer (HAL).** All peripheral access passes through a thin HAL whose
interface is defined independently of the hardware. Application code never reads a register
or toggles a pin directly. The HAL is the contract boundary: changes to the board layout or
to a peripheral revision affect only the HAL implementation, never the application.

### D4.2 Cross-compilation and toolchain

- The project declares the exact toolchain version (compiler, linker, SDK) in a version-locked
  file (`toolchain.toml`, `platformio.ini`, `west.yml`, or equivalent). The same file is used
  by CI and by every developer.
- The build produces a deterministic binary: same source + same toolchain + same flags = same
  output, byte-for-byte. When full determinism is not achievable, the delta is documented in
  an ADR.
- Binary size is tracked as a ratchet (§5.3 pattern): a CI step compares the artefact size
  against a committed baseline. A regression beyond a declared threshold (e.g. +2%) fails
  the build unless the increase is justified in the commit message.

### D4.3 Hardware-in-the-loop (HIL) testing

Core §5 testing pyramid applies. This section adds the tier that can only run on real hardware
or a cycle-accurate simulator.

**HIL tier placement.** HIL tests sit above integration tests in the pyramid. They are slower
and more expensive; they run on merge to `main` or on a nightly schedule, not on every push.

**What HIL tests cover:**

| Category | Example |
|----------|---------|
| Peripheral I/O | Sensor reads return plausible values; actuator commands reach the device |
| Timing | ISR latency stays within the declared deadline |
| Power state transitions | Sleep → wake → resume produces the correct peripheral state |
| Communication protocols | Full frame exchange on bus (CAN, I2C, SPI) with a real or loopback peer |
| Firmware update | OTA or flash-based update completes and the device boots the new image |

**HIL infrastructure.** The CI runner has access to a physical board (or a farm of boards)
via a debug probe (J-Link, ST-Link, OpenOCD, or equivalent). The runner flashes the artefact,
executes the test suite over the debug channel, and collects results. If no physical board is
available, a cycle-accurate simulator (QEMU with the correct machine model, Renode, or vendor
simulator) is an acceptable substitute — but the substitution is recorded in the contract map
so the team knows which contracts are verified on real hardware and which on simulation.

### D4.4 Flash and OTA update strategy

- **Image signing.** Every firmware image is signed before distribution. The bootloader
  verifies the signature before applying the update. Unsigned images are rejected.
- **A/B partitioning.** The device maintains two firmware slots (A and B). The new image is
  written to the inactive slot. If the boot self-test fails, the bootloader reverts to the
  previous slot automatically.
- **Rollback trigger.** The application reports "healthy" to the bootloader within a
  configurable window after first boot (watchdog or explicit confirmation). If the window
  expires without confirmation, the bootloader treats the update as failed and reverts.
- **OTA transport.** When the device has network connectivity, updates are delivered over an
  encrypted channel (TLS 1.2+). The update payload includes a manifest with version, size,
  SHA-256 hash, and signature. The device verifies the manifest before downloading the image.
- **Offline update.** When no network is available, updates are delivered via removable media
  (SD card, USB). The same signing and verification rules apply.
- **Version contract.** The running firmware version is always queryable (via a debug command,
  a status register, or an API endpoint). The version string follows the project's tagging
  convention (§3.8).

### D4.5 Power and thermal budgets

**Power budget.** The project maintains a power budget document (`docs/power-budget.md` or
equivalent) that lists every component's draw in each operating mode:

| Component | Sleep (mW) | Idle (mW) | Active (mW) | Peak (mW) | Source |
|-----------|-----------|-----------|-------------|-----------|--------|
| MCU | — | — | — | — | Datasheet §X.Y |
| Radio | — | — | — | — | Datasheet §X.Y |
| Sensor A | — | — | — | — | Measured |
| … | | | | | |
| **Total** | — | — | — | — | |

The budget is validated against the power source (battery capacity, solar harvest rate, USB
supply) to derive a minimum operating life. Any change that adds a component or increases
duty cycle updates the budget document and verifies that the operating-life target still holds.

**Thermal budget.** When the system operates in an enclosure or in an environment with
constrained dissipation, the same table includes a thermal column (junction temperature at
steady state). The thermal budget is validated by measurement during HIL testing (D4.3) or
by thermal simulation.

### D4.6 Bring-up checklist

When a new board revision arrives, the following checklist is executed before any application
code runs. Each step is recorded in `docs/bring-up/<board-rev>.md`.

- [ ] Visual inspection: correct components populated, no solder bridges
- [ ] Power rail verification: each rail within ±5% of nominal at no-load
- [ ] Programmer connection: debug probe communicates with the MCU
- [ ] Bootloader flash: bootloader boots, serial/debug console active
- [ ] Peripheral smoke test: each peripheral responds to a basic read/write
- [ ] Clock verification: system clock within ±50 ppm of expected frequency
- [ ] Power measurement: idle and active draw match the power budget (D4.5) within ±15%
- [ ] Firmware flash: full application boots on the new board
- [ ] HIL suite pass: all D4.3 tests pass on the new revision

## D5 ML / Data Pipeline

**Activation trigger.** The project trains or fine-tunes models, transforms datasets at scale,
or persists structured data subject to schema evolution (relational or otherwise).

**In addition to Core.** Core §5 testing fundamentals apply. This appendix adds the testing
patterns that only arise when data is being reshaped, and will grow to cover pipeline-
reproducibility, dataset versioning, drift monitoring, and evaluation contracts.

### D5.1 Golden queries for data migrations

For any migration that alters schema or rewrites data, maintain a small curated set of **golden queries** — canonical read queries whose results must match before and after the migration (modulo an explicit, documented allow-list of intentional differences).

Rules:

- Golden queries live alongside the migration script, version-controlled with it
- They are executed automatically against a pre-migration snapshot and the post-migration state; any unexplained divergence blocks promotion of the migration
- Each query has a short rationale explaining which invariant it protects (row counts per tenant, aggregate totals, referential integrity across renamed tables, …)
- "Intentional difference" entries are not free-form prose: they are a structured list referenced from the migration's remediation record (§10)

Golden queries are complementary to schema migrations' own tests; they catch semantic drift that schema-level checks miss (e.g. a column renamed correctly but backfilled with the wrong default).

### D5.2 Database migration

- **Forward-only migration.** Every migration has an `up` file and a `down` file. The `down` is tested — it is not an empty placeholder.
- **Migration separate from the application deploy.** The migration runs before the deploy. If the migration fails, the deploy does not start.
- **Backward compatibility.** The new version of the code MUST work with both the old and the new version of the database for at least one deploy cycle. This allows rollback without rolling back the database.
- **Data migration vs schema migration.** The two are separate. Schema first, data after. Never in the same migration.

**Irreversible-migration rule.** If a deploy includes an irreversible database migration, it must be tagged as `BREAKING` in the CHANGELOG and requires explicit approval before deploying. Because rolling back the application does not undo the migration, the rollback scenario for this class of change is "hotfix forward" — see Core §7.3.

### D5.3 Training-pipeline reproducibility

Every training run MUST be reproducible from its recorded inputs. The minimum record per run:

| Artefact | Content | Storage |
|----------|---------|---------|
| **Run manifest** | Dataset version, code commit, dependency lock, hyperparameters, random seeds, hardware spec (GPU model, driver version) | Version-controlled or experiment tracker |
| **Trained model** | Serialised weights + architecture definition | Model registry (MLflow, W&B, DVC, or equivalent) |
| **Evaluation report** | Metrics on the held-out evaluation set (D5.6) | Stored alongside the model in the registry |
| **Training log** | Loss curves, resource utilisation, wall-clock time | Experiment tracker |

**Determinism.** When the framework supports it, pin every source of non-determinism
(random seeds, CUDA deterministic mode, data-loader shuffle seed). Document any remaining
non-deterministic operations (e.g. certain GPU kernels) in the run manifest so that "same
inputs → same outputs" failures are explained, not mysterious.

**Pipeline-as-code.** The training pipeline is defined in version-controlled code, not in
notebook cells or manual shell commands. A single entry-point command (e.g. `make train`,
`dvc repro`, `python -m train`) reproduces the entire pipeline from raw data to evaluated
model. Interactive notebooks are permitted for exploration but are never the canonical
training path.

### D5.4 Dataset versioning

Datasets are versioned artefacts with the same rigour as code:

- Every dataset has a unique version identifier (content hash, tag, or monotonic version
  number). The identifier is recorded in the run manifest (D5.3).
- Dataset transformations (filtering, labelling, augmentation, splitting) are defined in
  code, not applied manually. The transformation pipeline is version-controlled alongside
  the data schema.
- Large datasets that cannot live in the Git repository are tracked via DVC, Git-LFS, or a
  dedicated registry. The pointer file (`.dvc`, `.gitattributes`, manifest) is committed;
  the data itself is stored externally.
- Schema changes to the dataset (new columns, changed types, dropped features) follow the
  same classification (§9) and remediation (§10) workflow as any other data-model change.

### D5.5 Drift monitoring

Once a model is serving predictions, the project monitors two kinds of drift:

**Data drift.** The distribution of incoming features diverges from the distribution the
model was trained on. Detection methods (choose at least one):

| Method | What it measures | Suggested threshold |
|--------|-----------------|---------------------|
| Population Stability Index (PSI) | Distribution shift per feature | PSI > 0.2 → alert |
| Kolmogorov–Smirnov test | Maximum CDF distance | p < 0.01 → alert |
| Jensen–Shannon divergence | Symmetric distribution divergence | JSD > 0.1 → alert |

**Concept drift.** The relationship between features and the target changes — the model's
predictions degrade even though the input distribution looks stable. Detected by monitoring
live performance metrics (accuracy, precision, recall, or the domain-specific metric defined
in D5.6) against the evaluation baseline. A sustained drop beyond a declared threshold
triggers a retraining investigation.

**Alert flow.** Drift alerts flow through Core classification (§9, bucket `data-model`) and
remediation (§10). Severity mapping:

| Signal | Severity | Action |
|--------|----------|--------|
| Data drift above threshold, no performance drop | L1 — `safe` | Log, monitor next window |
| Data drift + performance drop within tolerance | L2 — `review` | Schedule retraining evaluation |
| Performance drop beyond tolerance | L3 — `breaking` | Retrain or roll back to previous model |

### D5.6 Evaluation contracts

Every model has an **evaluation contract** — a versioned specification of how the model's
quality is measured before promotion to production.

| Element | Content |
|---------|---------|
| **Evaluation dataset** | A held-out set, versioned alongside training data (D5.4), never used during training |
| **Primary metric** | The single metric that gates promotion (e.g. F1, AUROC, RMSE) |
| **Threshold** | The minimum acceptable value of the primary metric; updated via ratchet (§5.3) |
| **Secondary metrics** | Additional metrics reported for context but not gating |
| **Slice analysis** | Performance broken down by critical subgroups (demographic, geographic, temporal) to surface hidden regressions |
| **Comparison baseline** | The currently deployed model's evaluation report; the new model must meet or exceed the primary metric |

The evaluation contract is executed automatically in CI. A model that fails the contract is
not promoted — it is sent back for investigation, not manually overridden.

## D6 Mobile App

**Activation trigger.** The project ships to iOS App Store, Google Play, or any
vendor-gated mobile distribution channel. This includes native apps (Swift/Kotlin),
cross-platform frameworks (Flutter, React Native, .NET MAUI), and hybrid apps
(Capacitor, Cordova).

**In addition to Core.** Core applies fully — requirements, code quality, testing pyramid,
documentation, CI/CD concepts, boundary contracts, change classification, remediation.
This appendix adds the patterns specific to mobile distribution, device fragmentation,
and platform-mandated constraints.

### D6.1 App-store submission and review

Every release destined for a store follows a structured submission workflow:

| Step | Action |
|------|--------|
| **1. Pre-submission checklist** | All tests pass, CHANGELOG updated, version and build number bumped, store metadata updated (screenshots, description, what's new) |
| **2. Build** | CI produces a signed artefact: `.ipa` (iOS) or `.aab` (Android). Signing credentials are stored in CI secrets, never on developer machines |
| **3. Upload** | Artefact uploaded to App Store Connect / Google Play Console via CI (Fastlane, Gradle Play Publisher, or equivalent) |
| **4. Internal testing** | Distribute to internal testers (TestFlight internal group, Google Play internal track) for smoke testing |
| **5. External testing** | Distribute to external beta testers (TestFlight external group, Google Play open/closed track) for broader validation |
| **6. Submit for review** | Submit to Apple App Review / Google Play review. Include review notes explaining any non-obvious functionality |
| **7. Staged rollout** | After approval, release to a percentage of users (see D6.2) |

**Review rejection protocol.** If the store rejects the build:

1. Record the rejection reason in the project's issue tracker.
2. Fix the issue in a patch release (do not resubmit the same build with metadata-only changes unless the rejection was metadata-related).
3. Re-submit with review notes explaining the fix.
4. If the rejection is disputed, file an appeal through the store's dispute channel and document the outcome.

### D6.2 Staged rollouts

Never release to 100% of users immediately. Use the store's staged-rollout mechanism:

| Phase | Percentage | Duration | Gate |
|-------|-----------|----------|------|
| **Canary** | 1–5% | 24–48 hours | No crash-rate spike (D6.4), no critical bug reports |
| **Early adopters** | 10–25% | 48–72 hours | Crash rate stable, no P0/P1 issues |
| **Wide** | 50% | 24–48 hours | Metrics stable, user feedback reviewed |
| **Full** | 100% | — | All gates passed |

**Halt criteria.** Roll back (or pause the rollout) immediately if:

- Crash-free rate drops below the project's threshold (suggested: < 99.5%).
- A P0 or P1 bug is confirmed by more than one user.
- A store-policy violation is discovered post-release.

Rolling back on mobile means halting the staged rollout and, if necessary, publishing a
hotfix. Unlike server-side rollback, a published mobile binary cannot be removed from
devices that already installed it — the fix must go forward.

### D6.3 Device and OS compatibility

Mobile projects maintain an explicit support matrix:

| Dimension | Policy |
|-----------|--------|
| **Minimum OS version** | Support at least the two most recent major OS versions (e.g. iOS 17+ / Android 14+). Document the policy in the README and in the store listing |
| **Target SDK** | Always target the latest stable SDK to access new APIs and satisfy store requirements |
| **Screen sizes** | Test on at least three form factors: small phone, large phone, tablet (if supported) |
| **Hardware variation** | Test on at least one low-end and one high-end device per platform |

**Deprecating an OS version.** When dropping support for an OS version:

1. Announce in the CHANGELOG at least one minor release before the drop.
2. Show an in-app notice to users on the deprecated OS version.
3. Remove the OS from the CI test matrix only after the deprecation release ships.

### D6.4 Crash reporting and on-device telemetry

Every mobile app integrates a crash-reporting and analytics service:

| Capability | Recommended tools | Requirements |
|------------|-------------------|--------------|
| **Crash reporting** | Firebase Crashlytics, Sentry, Bugsnag | Automatic symbolication (dSYM for iOS, mapping file for Android), uploaded in CI on every release build |
| **Analytics** | Firebase Analytics, Amplitude, Mixpanel | Consent-gated (GDPR/CCPA). No tracking fires before the user grants consent |
| **Performance monitoring** | Firebase Performance, Sentry Performance | App start time, screen rendering time, network latency |

**Rules:**

1. **Symbolication files** (dSYM, ProGuard/R8 mapping) are uploaded to the crash-reporting service as a CI step on every release build. Without them, crash reports are unreadable.
2. **Consent.** Analytics and non-essential telemetry require explicit user consent. Crash reporting may run without consent if it collects no PII (stack traces only, no user identifiers). When M2 Security-sensitive is active, the consent implementation is reviewed against M2.2.
3. **Crash-free rate.** The project defines a target crash-free rate (suggested: ≥ 99.5% of sessions). The rate is monitored daily; a drop below threshold triggers investigation.
4. **No PII in crash reports.** User identifiers, email addresses, and authentication tokens must never appear in crash logs. Breadcrumbs (user actions leading to a crash) are anonymised.

### D6.5 Offline-first and data synchronisation

Mobile apps must handle network absence gracefully:

1. **Offline-capable by default.** Core functionality works without a network connection. Features that require network connectivity degrade gracefully with a clear user message — not a crash or a blank screen.
2. **Local storage.** Data that the user creates or modifies offline is persisted locally (SQLite, Core Data, Room, or equivalent). The local store is the source of truth until sync completes.
3. **Conflict resolution.** When the user modifies data offline and the server state has changed, the app applies a documented conflict-resolution strategy:
   - **Last-write-wins** for low-risk fields (preferences, display settings).
   - **Manual merge** for high-risk fields (financial data, shared documents). The app presents both versions and lets the user choose.
4. **Sync indicator.** The UI shows the sync state: synced, pending, syncing, conflict. The user always knows whether they are looking at local or server data.

### D6.6 Over-the-air (OTA) vs store updates

Some frameworks (React Native, Flutter via Shorebird, Expo) support OTA code updates
that bypass the store review cycle. OTA is powerful but carries risk:

| Aspect | Store update | OTA update |
|--------|-------------|------------|
| **Review** | Store-reviewed | Not reviewed by the store |
| **Rollback** | Halt staged rollout | Instant rollback to previous bundle |
| **Scope** | Any change (native + JS) | JS/Dart-only changes (no native code) |
| **Compliance** | Always compliant | Must comply with store policies (Apple §3.3.2, Google Play Developer Policy §8.6) |
| **Latency** | Hours to days (review queue) | Minutes |

**Rules:**

1. OTA is permitted only for bug fixes and minor UI adjustments — never for new features that would require store review.
2. Every OTA update is versioned and logged in the project's release history (M3.2).
3. The app includes a mechanism to force a store update when a native-code change is required (minimum-version check against a server-side flag).
4. OTA rollback is tested as part of the release process. If the rollback mechanism fails, OTA is disabled until it is fixed.

## D7 Static Site / Frontend-only

**Activation trigger.** The project renders entirely client-side or as a statically-generated
site, with no backend owned by the project itself. This includes single-page applications
(SPA), statically-generated sites (SSG), and hybrid frameworks (Next.js static export,
Astro, Nuxt generate) where no server runtime is deployed by the project.

**In addition to Core.** Core applies fully — requirements, code quality, testing pyramid,
documentation, CI/CD concepts, boundary contracts, change classification, remediation.
This appendix adds the patterns specific to client-side rendering, asset delivery, and
browser-environment constraints.

### D7.1 Build and bundle budgets

Every frontend project maintains explicit size budgets for production artefacts. Budgets
are committed as a baseline file (e.g. `.bundle-budget.json`) and enforced in CI via a
ratchet mechanism analogous to §5.3 coverage ratchet.

| Artefact | Budget metric | Suggested starting point |
|----------|--------------|--------------------------|
| **JS (compressed)** | Total gzip/brotli size of all JS bundles | ≤ 200 KB initial load |
| **CSS (compressed)** | Total gzip/brotli size of all CSS | ≤ 50 KB |
| **Images** | Largest single image (post-optimisation) | ≤ 200 KB; prefer modern formats (WebP, AVIF) |
| **Total page weight** | Sum of all assets for the critical path | ≤ 500 KB initial load |

**Rules:**

1. The budget ratchet only moves downward — if a build produces a smaller bundle, the
   baseline is updated automatically on merge to main.
2. A build that exceeds any budget fails CI. The developer must either optimise or
   request an escape valve (§5.3) with an expiry date and justification.
3. Tree-shaking verification: CI reports which dependencies contribute the most to
   bundle size. Dependencies that are imported but unused (or partially used with no
   tree-shaking) are flagged.
4. Code-splitting is mandatory for any route or feature that is not needed on initial
   load. Lazy-loaded chunks have their own individual budget.

### D7.2 Hosting and CDN contracts

The project's Boundary Contract Map (§8) includes the CDN and hosting provider as
outbound contracts on the `api` axis:

| Contract | Direction | What to document |
|----------|-----------|-----------------|
| CDN (e.g. Cloudflare, Vercel Edge, AWS CloudFront) | outbound | Cache TTLs per asset type, invalidation mechanism, edge-function limits (execution time, memory, request size) |
| Hosting (e.g. Vercel, Netlify, GitHub Pages, S3) | outbound | Build command, output directory, redirect/rewrite rules, environment variables |
| Analytics / third-party scripts | outbound | Each third-party script loaded on the page (tag managers, analytics, chat widgets) |

**Cache-invalidation strategy.** Static assets (JS, CSS, images) use content-hashed
filenames (`main.a1b2c3.js`) and are served with long-lived cache headers
(`Cache-Control: public, max-age=31536000, immutable`). HTML files are served with
short TTLs (`max-age=0, must-revalidate` or `s-maxage=60`) so deployments take effect
immediately.

**Edge functions.** If the project uses edge functions (middleware, A/B testing,
geolocation routing), they are treated as boundary contracts with their own tests.
Edge-function cold-start latency is monitored and budgeted.

### D7.3 Client-side error reporting

Errors that occur in the browser must be captured, reported, and triaged:

1. **Error-reporting service.** Integrate a service (Sentry, Bugsnag, Datadog RUM, or
   equivalent) that captures unhandled exceptions and unhandled promise rejections.
2. **Source maps.** Upload source maps to the error-reporting service on every
   deployment. Source maps are never served publicly — they are uploaded as a build
   step and associated with the release version.
3. **Session context.** Each error report includes: browser/OS, page URL, release
   version, user consent status. No PII is attached without explicit user consent.
   When M2 Security-sensitive is active, the PII exclusion is enforced by M2.2.
4. **Error budget.** Define an error-rate threshold (e.g. < 0.1% of sessions with an
   unhandled JS error). Exceeding the threshold triggers investigation, analogous to
   the coverage ratchet.
5. **Session replay** (optional). If enabled, replay is consent-gated and masks all
   form inputs by default. Replay recordings are retained for a maximum of 30 days
   unless a longer retention is justified and approved.

### D7.4 Accessibility

Accessibility is a non-negotiable quality dimension, not an optional enhancement.

**Baseline standard:** WCAG 2.2 Level AA. The project may target Level AAA for specific
criteria but Level AA is the minimum.

**Testing layers:**

| Layer | Tool examples | When |
|-------|--------------|------|
| **Automated lint** | eslint-plugin-jsx-a11y, axe-core, Lighthouse CI | Every PR (CI) |
| **Automated audit** | axe-core in integration tests, Pa11y | Every PR (CI) |
| **Manual audit** | Screen reader (VoiceOver, NVDA), keyboard-only navigation | Every release and after significant UI changes |

**Rules:**

1. Every interactive element is keyboard-accessible (focusable, operable, visible
   focus indicator).
2. Every image has an `alt` attribute. Decorative images use `alt=""` and
   `role="presentation"`.
3. Colour contrast meets WCAG AA ratios (4.5:1 for normal text, 3:1 for large text).
4. Form inputs have associated `<label>` elements. Error messages are programmatically
   associated with the input.
5. Dynamic content changes are announced to screen readers via ARIA live regions.
6. The page is usable at 200% zoom without horizontal scrolling.

Accessibility violations found by automated tools fail CI. Violations found by manual
audit are filed as bugs with severity proportional to impact.

### D7.5 Core Web Vitals

The project monitors [Core Web Vitals](https://web.dev/vitals/) and maintains
thresholds that trigger investigation when breached:

| Metric | What it measures | Threshold (good) | Threshold (needs improvement) |
|--------|-----------------|-------------------|-------------------------------|
| **LCP** (Largest Contentful Paint) | Loading performance | ≤ 2.5 s | ≤ 4.0 s |
| **INP** (Interaction to Next Paint) | Responsiveness | ≤ 200 ms | ≤ 500 ms |
| **CLS** (Cumulative Layout Shift) | Visual stability | ≤ 0.1 | ≤ 0.25 |

**Monitoring:**

1. **Lab data.** Lighthouse CI runs on every PR against a representative set of pages.
   Results are compared against the thresholds above. Regression beyond "needs
   improvement" fails CI.
2. **Field data.** Real-user monitoring (RUM) via the web-vitals library or the
   error-reporting service (D7.3). Field data is reviewed weekly; a sustained
   regression triggers investigation.
3. **Budget alerts.** When a metric crosses from "good" to "needs improvement" in
   field data, an alert is raised (issue, Slack notification, or equivalent).

CLS is particularly sensitive to layout shifts caused by late-loading images, fonts, or
third-party scripts. Every image has explicit `width` and `height` attributes (or CSS
`aspect-ratio`). Font loading uses `font-display: swap` or `optional` to prevent
invisible text.

---

# PART III — CROSS-CUTTING MODULES

---

Cross-cutting Modules add capabilities that compose with any domain. Activate a module when
its trigger fires. A module may be active alongside any set of Domain Appendices.

Each module adds content to the Core; it never replaces Core rules.

## M1 Surveillance

**Activation trigger.** The Boundary Contract Map (§8) contains at least one outbound contract
(dependency, upstream API, device driver, external data source) whose evolution must be
tracked over time. A project with no outbound contracts — a pure offline utility, a one-shot
script — does not need this module. When in doubt: if the project has a lock file
(`package-lock.json`, `poetry.lock`, `Cargo.lock`, …) or calls any external API, the trigger
has fired.

**In addition to Core.** Surveillance runs autonomous agents against outbound contracts at
regular intervals; detected changes flow through Core classification (§9) and remediation
(§10), and the detection path itself is self-tested so the loop stays honest. Every action
produced by the module is an event in the compatibility database (M1.3), which is the audit
trail.

**Relationship to other modules and appendices.** M1 composes with any domain:

| Domain active | M1 watches |
|---------------|------------|
| D1 Web Service | Upstream APIs, cloud-provider SDKs, container base images |
| D4 Embedded | Device-driver versions, toolchain releases, RTOS updates |
| D5 ML / Data | Framework versions (PyTorch, TensorFlow), dataset registry changes, model-serving API drift |
| Any | Language runtime, linter/formatter, CI runner images |

### M1.1 Surveillance agents

Agents are autonomous processes that monitor external dependencies at regular intervals.

#### M1.1.1 Architecture

```
┌─────────────────────────────────────────────────┐
│                  SCHEDULER                       │
│  (cron / CI schedule / workflow_dispatch)         │
└──────┬──────┬──────┬──────┬──────┬───────────────┘
       │      │      │      │      │
       ▼      ▼      ▼      ▼      ▼
   ┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐
   │Agent ││Agent ││Agent ││Agent ││Agent │
   │Pkg   ││Docker││GitHub││API   ││Docs  │
   │Watch ││Watch ││Watch ││Probe ││Watch │
   └──┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘
      │       │       │       │       │
      ▼       ▼       ▼       ▼       ▼
   ┌─────────────────────────────────────┐
   │         CHANGE CLASSIFIER           │
   └──────────────┬──────────────────────┘
                  │
                  ▼
   ┌─────────────────────────────────────┐
   │         IMPACT ANALYSER             │
   │    (cross-ref with contract map)     │
   └──────────────┬──────────────────────┘
                  │
          ┌───────┴────────┐
          ▼                ▼
   ┌────────────┐   ┌────────────┐
   │ REMEDIATION│   │  ADOPTION  │
   │   (fix)    │   │  (improve) │
   └────────────┘   └────────────┘
```

#### M1.1.2 Agent types

**M1.1.2.1 Package Watch** — detects new versions of dependencies. Frequency: 5 min (RSS) or 1h (JSON API). Filter: stable releases only.

**M1.1.2.2 API Probe** — runs contract tests against every endpoint in the contract map. Frequency: 6h for critical endpoints, 24h for others. Verifies: reachability, schema, semantics, new/missing fields, deprecation headers, rate limits, versioning.

**M1.1.2.3 Docs Watch** — monitors changelogs and official documentation. Frequency: 24h. Method: fetch + textual diff.

**M1.1.2.4 Security Watch** — detects security advisories. Frequency: 15 min. Sources: GHSA, NVD, native audit tools. Any advisory forces L2.

**M1.1.2.5 Container/Image Watch** — detects new Docker images. Frequency: 15 min. Timeout: 90 min with backoff.

**M1.1.2.6 State-of-the-Art Scout** — an agent dedicated to state-of-the-art research. Unlike the other agents: it does not monitor a single dependency, but scans the technological landscape around the project. Frequency: quarterly for stable components, monthly for components under active development.

What it does each cycle:

1. **Technology health check.** For every significant technology in the project, verifies: latest release, release frequency over the past year, open issue trends, documentation status, deprecation or end-of-life announcements.

2. **Alternative scanning.** Searches for new libraries or services that solve the same problem as an existing dependency with a different or better approach. Does not suggest switching — it flags that the alternative exists and leaves the decision to the human.

3. **Pattern evolution.** Verifies whether the architectural patterns used in the project are still best practice or whether the community has moved towards different approaches. Looks for: updates to official style guides, new RFCs, talks from key conferences.

4. **Security landscape.** Verifies whether security practices are aligned with current recommendations (OWASP, NIST, CIS).

5. **Ecosystem health.** Assesses the health of the ecosystem: growing or declining community, significant forks, controversies (licence, governance, ownership).

Output: report in `docs/research/` with findings classified into 5 levels: `healthy` (no action), `watch` (monitor in the next cycle), `evaluate` (create ADR with comparison), `migrate` (plan migration in the backlog), `urgent` (immediate action — end-of-life, critical vulnerability, hostile fork).

The agent proactively suggests research when: a new project is started, a dependency is added, an architectural choice is proposed, the project enters a new phase, or N months have passed since the last research on a component. Full details in §1.7.

#### M1.1.3 Heartbeat

Every agent, every cycle — even when nothing is detected — emits a heartbeat. Alert if the most recent is older than 6 hours.

#### M1.1.4 Multi-source configuration

For every critical dependency, at least two sources with different roles: primary (fast trigger) and backstop (recovery). The backstop reconciles missed versions when the primary comes back online.

### M1.2 Compatibility test matrix

#### M1.2.1 Slots

| Slot | Definition | Purpose |
|------|------------|---------|
| `latest` | Version that triggered the cycle | Compatibility with the new change |
| `recent` | Most recent stable version (21-day window) | Masked regressions |
| `baseline` | Pinned version, reviewed quarterly | Declared contract |

#### M1.2.2 Run manifest

At the start of each cycle, before any test, the system freezes versions in a JSON manifest. Eliminates ambiguity if the matrix resolves differently between steps.

#### M1.2.3 Test data

1. **Seed workload** — creates data that exercises every outbound contract
2. **Golden queries** — queries with expected results to verify post-migration integrity
3. **Snapshot regression** — loads snapshots from previous versions and verifies data accessibility

### M1.3 Compatibility database

#### M1.3.1 Format

Flat JSON in the repo, one file per version per dependency. No external database.

```
compat-db/
├── stripe-api/
│   ├── 2026-04-01_v2024-12-18.json
│   └── 2026-04-15_v2025-01-15.json
├── express/
│   ├── 2026-04-10_4.21.0.json
│   └── 2026-04-18_4.21.1.json
└── _aggregated/
    └── 2026-04-18.json
```

#### M1.3.2 Events (append-only)

The `events` array is the complete audit trail. Never modify or remove events.

#### M1.3.3 Aggregation

Each slot produces its own payload; an aggregation job merges them. `pass` only if all slots are `pass`. If any slot is `fail`, the rollup is `fail`. If a slot is `error`, the rollup is `partial`.

#### M1.3.4 Portability

Plain JSON in the repo. Migrating to another forge = copy directory + new CI adapter.

### M1.4 Self-testing and observability

#### M1.4.1 Detection heartbeat

Every polling cycle emits a heartbeat. Alert if the most recent is older than 6 hours.

#### M1.4.2 Classifier retrospective

Monthly job: reviews all `safe` auto-merged records from the past 30 days. False negative rate > 10% → alert to recalibrate.

#### M1.4.3 End-to-end canary

Weekly job: injects a synthetic record to verify the entire detection → classification → issue → contract-map cross-ref → event emission path. Cleans up after verification.

#### M1.4.4 Boundary Contract Map cardinality guard

Delegates to Core §8.4. If the total contract count — or any single-axis count — drops by
more than 10% between generations, CI fails. M1 adds a scheduled re-generation (weekly or on
dependency change) so the guard runs even when no human remembers to regenerate the map.

## M2 Security-sensitive

**Activation trigger.** The project handles authentication, authorisation, or personally
identifiable information; OR serves untrusted clients over a network; OR processes
attacker-controlled input. When in doubt: if the project has a login flow, stores user data,
accepts file uploads, or exposes an API without a trusted-network assumption in the contract
map (§8), the trigger has fired.

**In addition to Core.** Core §4 (Fundamental principles, Input validation, Secrets management)
applies to every project. This module adds the patterns that make sense only when the trigger
above fires: identity handling, a per-PR security checklist, OWASP coverage, and
dependency-vulnerability management.

**Relationship to domain appendices.** M2 composes with any domain. When D1 (Web Service) is
active, M2 is almost always active as well. When D4 (Embedded) is active, M2 fires if the
device handles credentials, communicates over an untrusted channel, or processes
attacker-influenced input (OTA payloads, sensor data from an adversarial environment).

### M2.1 Authentication and authorisation

- **Passwords.** Never in plain text, never in logs, never in URLs. Hashed with bcrypt/argon2, unique salt per user.
- **Tokens.** JWT with short expiry (15 min access, 7 days refresh). Refresh token rotated on every use.
- **Session.** `HttpOnly`, `Secure`, `SameSite=Strict` cookies. Session ID regenerated after login.
- **API keys.** Never in source code. Never in the frontend. Always in an environment variable or secret manager.
- **Authorisation.** Checked on every request, not only at login. Explicit RBAC or ABAC, never hard-coded.

### M2.2 Security checklist for every PR

- [ ] No secrets committed (verified by tools: `trufflehog`, `gitleaks`)
- [ ] Input validated with schema at every boundary
- [ ] Parameterised queries (no SQL concatenation)
- [ ] Errors do not expose stack traces or internal details to the user
- [ ] Security headers present (CSP, X-Frame-Options, X-Content-Type-Options)
- [ ] Dependencies free of known vulnerabilities (`npm audit` / `pip-audit` clean)
- [ ] Rate limiting configured for public endpoints
- [ ] Logs do not contain PII or secrets

### M2.3 OWASP Top 10 as baseline

Every networked application MUST be protected against the current OWASP Top 10 (Web) or the
relevant OWASP vertical (API Security, Mobile, LLM, …) when one exists for the project's
domain.

**Annual review.** Once per year the team walks through each OWASP item and records, for each:

| Item | Covered by | Verified how | Last reviewed |
|------|-----------|-------------|---------------|
| A01 Broken Access Control | RBAC middleware + integration tests | CI + manual pentest | YYYY-MM-DD |
| A02 Cryptographic Failures | TLS termination + hashing policy (M2.1) | Config audit | YYYY-MM-DD |
| … | | | |

The table lives in `docs/security/owasp-review.md` (or equivalent). An empty or stale table
(last reviewed > 12 months ago) is flagged by the M2.2 checklist.

### M2.4 Dependency-vulnerability management

When M1 Surveillance is also active, its Security Watch agent (M1.1.2.4) detects advisories
automatically. This section defines the response policy regardless of how the advisory is
discovered.

| Advisory severity | Response SLA | Action |
|-------------------|-------------|--------|
| Critical (CVSS ≥ 9.0) | 24 hours | Patch, upgrade, or mitigate. If no fix exists, disable the affected feature and document the workaround |
| High (CVSS 7.0–8.9) | 72 hours | Patch or upgrade. Workaround acceptable only if the patch introduces a breaking change requiring D5.2-style migration |
| Medium (CVSS 4.0–6.9) | Next sprint | Schedule the upgrade; track in the backlog |
| Low (CVSS < 4.0) | Best effort | Upgrade when convenient; do not block releases |

**Transitive dependencies.** The policy applies to transitive (indirect) dependencies as well.
When a transitive dependency has a critical advisory and the direct dependency has not released
a fix, the project pins a patched fork or applies a lockfile override — and opens an upstream
issue. The override is recorded in the contract map (§8) so it is not forgotten.

## M3 Release & Distribution

**Activation trigger.** The project ships versioned artefacts to external consumers
(applies whenever D2, D3, D4, or D6 is active; may also apply to D1 when artefacts are
published to an internal registry).

**In addition to Core.** This module defines the universal release process that applies
across all domains. Domain appendices (D2.5 Package publishing, D3.6 Installation and
distribution, D4.4 Flash and OTA) add domain-specific details; M3 owns the cross-cutting
patterns that bind them together.

### M3.1 Release cadence

The project declares its release model in the agent configuration file (§2.4):

| Model | Description | When to use |
|-------|-------------|-------------|
| **Release-when-ready** | A release is cut whenever a meaningful set of changes is merged | Small teams, libraries, CLI tools with rapid iteration |
| **Release train** | Releases happen on a fixed schedule (e.g. every two weeks) regardless of content | Larger teams, products with external stakeholders expecting predictable delivery |
| **Event-driven** | Releases are tied to external events (hardware rev, conference, regulatory deadline) | Embedded/firmware, regulated industries |

**Freeze windows.** When the project adopts a release train, the last 20% of the cycle
is a freeze window: only bug fixes and documentation enter the release branch. New
features merge to the development branch and ride the next train.

**Multi-artefact coordination.** When a single project produces more than one artefact
(e.g. a backend service + a client SDK + a CLI), all artefacts follow the same release
cadence. Version numbers may differ (each artefact has its own SemVer), but releases are
cut in the same cycle. The release-coordination checklist lives in `docs/release-matrix.md`
or equivalent.

### M3.2 Changelog automation

The CHANGELOG (§6.3) is generated from Conventional Commits (§3.3) and refined by a
human editor before publication:

**Step 1 — Generate.** A CI step produces a draft CHANGELOG entry from commit messages
since the last release tag. Commits are grouped by type (`feat`, `fix`, `refactor`,
`docs`, `chore`) and filtered: `chore` commits are excluded from the public CHANGELOG
unless they affect consumer-visible behaviour.

**Step 2 — Edit.** A human (or lead agent with human approval) edits the draft to:

- Rewrite terse commit messages into consumer-facing language.
- Merge related entries (e.g. three `fix` commits for the same bug become one entry).
- Add a summary paragraph at the top for major releases.
- Flag breaking changes prominently at the start of the entry.

**Step 3 — Publish.** The final CHANGELOG entry is committed alongside the version bump.
The same text is used as the body of the GitHub Release (or equivalent platform release).

**Format.** Follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) with sections:
`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`.

### M3.3 Artefact signing and provenance

Every release artefact is accompanied by a verification mechanism appropriate to the
project's risk profile:

| Level | Mechanism | When required |
|-------|-----------|---------------|
| **Minimum** | SHA-256 checksum file published alongside artefacts | Always |
| **Standard** | GPG signature or Sigstore/cosign signature on each artefact | When M2 Security-sensitive is active, or when the artefact is distributed to untrusted channels |
| **Provenance** | SLSA Level 2+ provenance attestation (build platform, source commit, builder identity) | Regulated environments, supply-chain-critical libraries |

**Supply-chain attestation.** Where the registry supports it, use platform-native
provenance mechanisms:

- npm: `--provenance` flag (OIDC-based, ties the package to a specific CI build).
- PyPI: Trusted Publishers (OIDC from GitHub Actions, GitLab CI).
- Container images: `cosign` attestation attached to the image manifest.
- Go modules: `go.sum` provides content-based integrity; SLSA provenance adds builder
  attestation.

Signing keys or OIDC trust policies are documented in the project's `SECURITY.md` or
equivalent. Key rotation follows the schedule defined when M2 is active.

### M3.4 Release-notes protocol

Every release includes a release note structured for two audiences:

**Developer-facing** (in the CHANGELOG and GitHub Release body):

```
## [version] — YYYY-MM-DD

### Breaking changes
- [description + migration guide]

### Added
- [new feature]

### Fixed
- [bug fix]

### Deprecated
- [symbol, with replacement and removal version]
```

**End-user-facing** (when the project has non-developer consumers — e.g. a desktop app,
a CLI with a broad audience, a firmware update):

- One paragraph summarising what changed in plain language.
- A "What you need to do" section if the update requires action (migration, config
  change, hardware reset).
- Known issues, if any.

The developer-facing note is always produced. The end-user-facing note is produced when
the domain appendix requires it (D3 CLI, D4 Embedded, D6 Mobile) or when the analyst
judges it necessary.

### M3.5 Rollback of a published release

When a published release contains a critical defect:

| Step | Action |
|------|--------|
| **1. Assess** | Determine severity: data loss, security vulnerability, or functional regression. If security, follow M2 response SLA (M2.4) |
| **2. Decide** | Yank/unpublish the broken version, or publish a patch release. Prefer patch release when possible — yanking breaks consumers who pinned the version |
| **3. Yank (if necessary)** | Use the registry's yank mechanism (`npm deprecate`, `cargo yank`, PyPI yank). Do not delete — yank marks the version as unsuitable while preserving it for pinned consumers |
| **4. Patch** | Publish a new patch version with the fix. The CHANGELOG entry for the patch references the broken version explicitly |
| **5. Communicate** | Post a GitHub Advisory (if security), update the CHANGELOG, and notify consumers through the project's communication channel (GitHub Discussions, mailing list, Discord) |
| **6. Retrospective** | Record what allowed the defect to ship (missing test, insufficient review, CI gap) and add a mitigation to the release checklist |

A rollback is never silent. Every yanked or patched version is documented in the
CHANGELOG and in the GitHub Releases page.

## M4 Classification & Taxonomy

**Activation trigger.** The project owns, extends, or depends on a domain-specific ontological
framework (threat intelligence, biomedical coding, geospatial metadata, fraud signalling,
vulnerability cataloguing, …). If the project invents its own terminology, this module
activates on the first naming decision.

**In addition to Core.** This module is framework-agnostic: it ships no curated catalogue of
taxonomies. Instead, it defines the principles, governance, and scouting protocol the project
follows to discover, adopt, and maintain whatever domain-specific frameworks its problem space
requires. Illustrative examples (MITRE ATT&CK, STIX, FT3, CAPEC, TLP, F3EAD, SNOMED, ICD,
ISO 19115) appear only to show the *shape* of adoption, never as defaults.

### M4.1 Design principles

**MECE (Mutually Exclusive, Collectively Exhaustive).** Every taxonomy the project owns or
adopts must partition its domain without overlap and without gaps. When a real-world entity
could belong to two categories, the taxonomy has an overlap bug; when an entity belongs to
none, the taxonomy has a coverage bug. Both are tracked as defects (§9, bucket `data-model`).

**Parsimony.** Introduce the fewest categories that explain the observed data. A taxonomy that
is too fine-grained creates classification paralysis; one that is too coarse loses
discriminating power. Start small, split only when a category demonstrably contains entities
that require different treatment.

**Stable identifiers.** Every term in the taxonomy has a machine-readable identifier that
never changes once assigned, even if the human-readable label is renamed. Format:
`<namespace>-<monotonic-number>` (e.g. `THREAT-042`). Deleted terms are tombstoned, never
recycled.

**Semantic versioning of the taxonomy.** The taxonomy itself has a version (semver):

| Change | Version bump | Migration required |
|--------|--------------|--------------------|
| Add a new term | Minor | No |
| Rename a label (ID unchanged) | Patch | No |
| Split or merge terms | Major | Yes — all classified records must be re-mapped |
| Remove (tombstone) a term | Major | Yes |

### M4.2 Governance

**Ownership.** Every taxonomy has a single owner (person or team). The owner approves
additions, merges, splits, and deprecations. In a solo-developer project, the developer is
the owner; the governance protocol still applies to maintain audit trail.

**Proposal protocol.** Any change to the taxonomy follows this flow:

1. **RFC.** A short document (issue, PR description, or `docs/taxonomy/rfc-NNN.md`) stating:
   what changes, why, which classified records are affected, migration plan if major.
2. **Review.** The owner reviews; the AI agent may review for MECE and parsimony violations.
3. **Decision.** Approve, reject, or request revision. Decision recorded in the RFC.
4. **Execution.** Merge the change, bump the taxonomy version, run the migration if major.

**Deprecation.** A term is deprecated before removal. Deprecated terms carry a `deprecated`
flag, a `successor` pointer (the term that replaces them), and a sunset date. During the
deprecation window, both the old and new term are accepted; after sunset, only the new term
is valid. Classification attempts using a deprecated term after sunset emit a warning (or
error, if the project configures it so).

### M4.3 Scouting protocol

**Binding to §1.7 SOTA Scout.** When M4 is active, the State-of-the-Art Scout (§1.7.5,
M1.1.2.6) gains an additional responsibility: for every domain the project touches, the
scout researches whether an established, community-maintained taxonomy or ontology already
exists.

**Scouting steps (executed per domain, on first encounter and then at the §1.7.5 cadence):**

1. **Survey.** Search for published standards, open-source frameworks, and academic ontologies
   that classify entities in the project's domain. Sources: ISO/IEC standards bodies, OASIS,
   W3C, IETF, domain-specific registries, peer-reviewed literature, GitHub/GitLab topic
   searches.
2. **Evaluate.** For each candidate, assess:
   - Coverage: does it cover the project's problem space?
   - Adoption: is it used by other projects in the same domain?
   - Maintenance: is it actively maintained? Last update date? Governance model?
   - Licence: compatible with the project's licence?
   - Machine-readability: available in a structured format (M4.6)?
3. **Recommend.** Produce a short report in `docs/research/` (§1.7.4 format) classifying each
   candidate as `adopt` (use as-is), `adapt` (use with local extensions), `watch` (promising
   but immature), or `ignore` (irrelevant or abandoned). The recommendation is non-binding —
   the human decides.
4. **Record.** The chosen framework (if any) is recorded in the project's taxonomy registry
   (`docs/taxonomy/registry.md` or equivalent) with: framework name, version adopted, scope
   of adoption (full or partial), local extensions, and the scouting report that justified
   the choice.

### M4.4 Adoption patterns

When the scouting protocol (M4.3) identifies a framework worth adopting, the project follows
one of three patterns:

**Full adoption.** The project uses the framework's taxonomy verbatim, without local
extensions. The framework's identifiers become the project's identifiers. Updates to the
framework are tracked by M1 Surveillance (if active) as an outbound contract.

**Partial adoption with local extensions.** The project adopts a subset of the framework and
adds local terms for concepts the framework does not cover. Local extensions use a distinct
namespace prefix (e.g. `LOCAL-`) so they are visually and programmatically distinguishable
from upstream terms. Local extensions follow the same governance (M4.2) as the rest of the
taxonomy.

**Inspiration only.** The project designs its own taxonomy, informed by the framework's
structure but not bound by its identifiers. The scouting report (M4.3) documents what was
borrowed and why the project diverged.

### M4.5 Audits

The taxonomy is audited periodically (suggested: quarterly, aligned with the §1.7.5 SOTA
Scout cadence). The audit checks:

| Check | Method | Failure threshold |
|-------|--------|-------------------|
| **Coverage** | Sample N records from the past quarter; classify each. Unclassifiable records = coverage gap | > 5% unclassifiable |
| **Ambiguity** | Two independent classifiers (human or AI) classify the same N records; measure inter-rater agreement (Cohen's κ or equivalent) | κ < 0.8 |
| **False positives** | Review records classified in the past quarter; count misclassifications | > 5% misclassified |
| **Drift** | Compare the distribution of classifications this quarter vs. last. A new cluster of records in a single category may signal a missing split | PSI > 0.2 on any category |
| **Staleness** | Check for terms with zero classifications in the past 6 months | Any stale term triggers a deprecation review |

Audit results are recorded in `docs/taxonomy/audit-YYYY-QN.md`. Failures trigger an RFC
(M4.2) for corrective action.

### M4.6 Machine-readable formats

Every taxonomy the project owns MUST have a machine-readable serialisation alongside the
human-readable documentation. Supported formats (choose at least one):

| Format | When to use |
|--------|-------------|
| JSON Schema | When the taxonomy is used for input validation or API contracts |
| JSON-LD / RDF | When the taxonomy participates in a linked-data ecosystem |
| OWL | When formal reasoning over the taxonomy is required |
| CSV / TSV | When the taxonomy is consumed by data pipelines or spreadsheets |
| Custom YAML | Acceptable for internal tooling; must be convertible to at least one of the above |

The machine-readable file is version-controlled alongside the taxonomy documentation. A CI
step validates that the human-readable and machine-readable representations are in sync (e.g.
every term in the Markdown table has a corresponding entry in the JSON Schema, and vice
versa).

### M4.7 Upstream contribution protocol

When a project's local extension (M4.4) proves broadly useful, the owner considers
contributing it back to the upstream framework. The protocol:

1. **Maturity gate.** The local term has been in use for at least two audit cycles (M4.5)
   with no MECE violations.
2. **Proposal.** Open an issue or RFC in the upstream framework's repository, following its
   contribution guidelines. Reference the project's usage data (classification count,
   coverage improvement).
3. **Tracking.** Record the proposal in `docs/taxonomy/upstream-contributions.md` with
   status (`proposed`, `accepted`, `rejected`, `withdrawn`).
4. **Adoption of upstream version.** If accepted, the project migrates from its local term
   to the upstream term (major version bump per M4.1). If rejected, the local term remains
   with a note explaining the divergence.

### M4.8 Illustrative examples

The following examples show the *shape* of taxonomy adoption across diverse domains. They are
not defaults — a project activates M4 because of its own domain, not because these examples
exist.

| Domain | Framework | What it classifies | Adoption shape |
|--------|-----------|-------------------|----------------|
| Threat intelligence | MITRE ATT&CK | Adversary tactics, techniques, procedures | Full or partial adoption; local techniques for niche attack surfaces |
| Threat intelligence | STIX / TAXII | Structured threat information exchange | Full adoption as a transport format |
| Fraud signalling | FT3 (Stripe) | Fraud tactics and techniques | Partial adoption; local extensions for domain-specific fraud vectors |
| Vulnerability | CVE / CWE / CAPEC | Vulnerabilities, weaknesses, attack patterns | Full adoption as identifiers; local severity overlay |
| Sharing policy | TLP (Traffic Light Protocol) | Information-sharing boundaries | Full adoption; no local extensions expected |
| Intelligence cycle | F3EAD | Find, Fix, Finish, Exploit, Analyse, Disseminate | Inspiration; adapted to the project's operational rhythm |
| Biomedicine | SNOMED CT / ICD | Clinical terms, diagnoses | Full or partial adoption; local extensions for research-specific phenotypes |
| Geospatial | ISO 19115 | Geographic metadata | Full adoption for metadata; local extensions for domain-specific layers |

---

## Known limitations and roadmap

This section records structural limitations identified during the post-modularisation review
(April 2026) and the planned mitigations. It is a living section: entries are removed when
the limitation is resolved, not when work begins.

### Mechanical barrier to adoption

Many Core processes (coverage ratchet, contract-map generation, surveillance agents) assume
CI/CD tooling and automation infrastructure that a new adopter does not have on day one.
Without reference implementations, the compliance cost is high.

**Mitigation — Tooling specifications (Appendix D).** The playbook now defines the
contracts that reference implementations must satisfy for three tools:
- **D.1 AST Walker** — contract-map generator (§8 automation).
- **D.2 Coverage Ratchet** — CI step enforcing §5.3.
- **D.3 Surveillance Agent Scaffold** — M1.1 implementation.

Implementations are built in dedicated repositories and validated against Appendix D.

### ~~Incomplete domain coverage~~ — Resolved

All seven domain appendices (D1–D7) and all four cross-cutting modules (M1–M4) are
fully populated. No stubs remain.

### Checklist density

Appendix A is comprehensive but dense. For small projects, unfiltered application of the full
checklist can slow velocity disproportionately.

**Mitigation — Project-size profiles (§2.5).** The project declares a size profile (Solo,
Small, Large) that modulates checklist items as mandatory, recommended, or optional.
Checklist items in Appendix A are tagged inline where the profile changes their obligation
level. Untagged items remain mandatory for all profiles.

---

## Appendix A — Phase checklists

Each checklist is split into **Core** items (always apply) and **conditional** blocks that
activate only when the named module or domain appendix is active. Skip a conditional block
entirely when its trigger has not fired.

Items tagged with a profile downgrade (e.g. `[Solo: optional]`) follow the rules in §2.5.
Untagged items are mandatory for all profiles.

### A.1 Phase 0 checklist (Requirements)

**Core**

- [ ] PRD written with all mandatory sections (§1.2) `[Solo: recommended]`
- [ ] State-of-the-art research conducted for the project domain (§1.7)
- [ ] Pre-implementation checklist in the PRD completed and verified `[Solo: recommended]`
- [ ] User stories with acceptance criteria for the first sprint `[Solo: optional]`
- [ ] ADRs for fundamental architectural decisions (with "Alternatives rejected" from real research) `[Solo: recommended]`
- [ ] Backlog created and ordered by priority `[Solo: optional]`
- [ ] Definition of Done defined and shared
- [ ] Critical dependencies identified in `DEPENDENCIES.md` (with alternatives comparison §1.7.1)

**When M4 Classification & Taxonomy is active**

- [ ] Scouting protocol (M4.3) executed for every domain the project touches
- [ ] Taxonomy decisions recorded in `docs/taxonomy/registry.md`

### A.2 Phase 1 checklist (Bootstrap)

**Core**

- [ ] Directory structure created (§2.1)
- [ ] Linter + formatter configured and integrated into CI (§3.4)
- [ ] Base CI pipeline working (build + lint + unit) (§7) `[Solo: recommended]`
- [ ] Agent configuration written (§2.4)
- [ ] Contract map generated (even manually) (§8) `[Solo: recommended]`
- [ ] `.env.example` with all variables documented (§4.3)
- [ ] Initial coverage baseline committed (§5.3) `[Solo: recommended]`

**When M1 Surveillance is active**

- [ ] Surveillance agents configured (M1.1)
- [ ] First compatibility record created (`untested`)
- [ ] Heartbeat alert configured (threshold: 6 hours) (M1.4.1) `[Small: recommended]`

**When M2 Security-sensitive is active**

- [ ] Secret scan configured in CI (M2.2)

**When the project has persistent structured data**

- [ ] Seed script for development database (§5.4)

**When D4 Embedded / Firmware is active**

- [ ] Toolchain version locked (D4.2)
- [ ] Binary-size baseline committed (D4.2)
- [ ] Power budget document created (D4.5)

### A.3 Checklist for every PR

**Core**

- [ ] Code follows naming conventions (§3.2)
- [ ] Commit message in Conventional Commits format (§3.3)
- [ ] No lint warnings (§3.4)
- [ ] Input validated with schema at every boundary (§4.2)
- [ ] Tests written for new/modified code (§5)
- [ ] Coverage has not dropped below baseline (§5.3) `[Solo: recommended]`
- [ ] Documentation updated where necessary (§6)
- [ ] Contract map updated if dependencies added/removed (§8) `[Solo: recommended]`
- [ ] Errors handled explicitly, no empty catch blocks (§3.6)

**When M2 Security-sensitive is active**

- [ ] No secrets committed (verified by tools: `trufflehog`, `gitleaks`) (M2.2)
- [ ] Parameterised queries — no SQL concatenation (M2.2)
- [ ] Errors do not expose stack traces or internal details to the user (M2.2)
- [ ] Security headers present (CSP, X-Frame-Options, X-Content-Type-Options) (M2.2)
- [ ] Dependencies free of known vulnerabilities (M2.4)
- [ ] Logs do not contain PII or secrets (M2.2)

**When D1 Web Service is active**

- [ ] Rate limiting configured for public endpoints (D1.5)
- [ ] Negative-path tests cover the endpoint (D1.4)

**When D2 Library / SDK is active**

- [ ] Public API surface unchanged on minor/patch bump (D2.4)
- [ ] Deprecated symbols annotated with replacement and removal version (D2.3)

**When D3 CLI Tool is active**

- [ ] Exit codes match documented contract (D3.3)
- [ ] `--json` output schema unchanged on minor/patch bump (D3.4)

**When D4 Embedded / Firmware is active**

- [ ] Binary size has not regressed beyond threshold (D4.2)
- [ ] Power budget updated if a component or duty cycle changed (D4.5)

**When D6 Mobile App is active**

- [ ] Minimum OS version policy respected (D6.3)
- [ ] Crash-reporting symbolication files included in build (D6.4)
- [ ] Offline behaviour tested for modified code paths (D6.5)

**When D7 Static Site / Frontend-only is active**

- [ ] Bundle size has not regressed beyond budget (D7.1)
- [ ] Automated accessibility audit passed (D7.4)
- [ ] No new accessibility violations from axe-core or equivalent (D7.4)

**When M4 Classification & Taxonomy is active**

- [ ] Taxonomy terms follow MECE and parsimony principles (M4.1)
- [ ] Machine-readable serialisation updated if taxonomy changed (M4.6)

### A.4 Checklist for release

**Core**

- [ ] All tests pass across all tiers (§5.5)
- [ ] CHANGELOG.md updated (§6.3)
- [ ] Version tag created (§3.8)
- [ ] Pre-production smoke tests green on promotion (§7.2) `[Solo: optional]`
- [ ] Rollback tested (§7.3) `[Solo: recommended]`

**When D1 Web Service is active**

- [ ] API documentation regenerated (D1.1)
- [ ] Health and readiness endpoints verified (D1.6)

**When D2 Library / SDK is active**

- [ ] API documentation regenerated (D2.1)
- [ ] Breaking-change detection passed (D2.4)
- [ ] Version bump matches SemVer rules (D2.2)
- [ ] Deprecation window respected for removed symbols (D2.3)
- [ ] Package published via CI pipeline, not manually (D2.5)

**When D3 CLI Tool is active**

- [ ] CLI documentation regenerated (D3.1)
- [ ] All exit codes tested (D3.3)
- [ ] Shell completions regenerated (D3.5)
- [ ] Installation channels built and checksummed (D3.6)

**When D4 Embedded / Firmware is active**

- [ ] Firmware image signed (D4.4)
- [ ] A/B partition rollback verified (D4.4)
- [ ] Bring-up checklist completed for new board revisions (D4.6)

**When D5 ML / Data Pipeline is active**

- [ ] Database migration tested (up AND down) (D5.2)
- [ ] Evaluation contract passed for any updated model (D5.6)

**When D6 Mobile App is active**

- [ ] Signed build artefact produced by CI (D6.1)
- [ ] Internal and external testing completed (D6.1)
- [ ] Staged rollout configured — not releasing to 100% immediately (D6.2)
- [ ] Symbolication files uploaded to crash-reporting service (D6.4)
- [ ] Store metadata updated (screenshots, description, what's new) (D6.1)

**When D7 Static Site / Frontend-only is active**

- [ ] Bundle budgets met (D7.1)
- [ ] Source maps uploaded to error-reporting service (D7.3)
- [ ] Manual accessibility audit completed for significant UI changes (D7.4)
- [ ] Core Web Vitals within "good" thresholds in Lighthouse CI (D7.5)
- [ ] Cache-invalidation strategy verified (content-hashed assets, short HTML TTL) (D7.2)

**When M1 Surveillance is active**

- [ ] Compat database updated with current state (M1.3)

**When M3 Release & Distribution is active**

- [ ] CHANGELOG entry generated and human-edited (M3.2)
- [ ] Artefact checksum file published (M3.3)
- [ ] Artefact signed or provenance attested where required (M3.3)
- [ ] Release notes published (developer-facing; end-user-facing where applicable) (M3.4)
- [ ] Release cadence respected — no freeze-window violations (M3.1)

### A.5 Surveillance checklist (M1 — periodic)

This checklist applies only when M1 Surveillance is active.

- [ ] Agents active with recent heartbeat (< 6 hours) (M1.4.1) `[Small: recommended]`
- [ ] Weekly canary passed (M1.4.3) `[Small: recommended]`
- [ ] Monthly retrospective executed (M1.4.2) `[Small: recommended]`
- [ ] Never-auto-merge list reviewed (§9.3)
- [ ] Coverage baseline updated (§5.3)
- [ ] Contract map regenerated after refactor (§8)
- [ ] Thresholds reviewed quarterly (M1.4) `[Small: recommended]`
- [ ] State-of-the-Art Scout run in the current quarter (§1.7.5, M1.1.2.6)
- [ ] SOTA reports reviewed and actions planned for `evaluate` or `migrate` signals

### A.6 Security review checklist (M2 — periodic)

This checklist applies only when M2 Security-sensitive is active.

- [ ] OWASP Top 10 review table updated within the past 12 months (M2.3)
- [ ] Dependency-vulnerability backlog triaged — no critical/high advisories past SLA (M2.4)
- [ ] Secret-scanning tool coverage verified (no new file patterns excluded) (M2.2)

### A.7 Taxonomy audit checklist (M4 — quarterly)

This checklist applies only when M4 Classification & Taxonomy is active.

- [ ] Coverage audit completed (M4.5)
- [ ] Ambiguity audit completed (M4.5)
- [ ] False-positive audit completed (M4.5)
- [ ] Drift audit completed (M4.5)
- [ ] Staleness audit completed — stale terms sent to deprecation review (M4.5)
- [ ] Machine-readable serialisation in sync with human-readable docs (M4.6)
- [ ] Upstream contributions tracked and statuses updated (M4.7)

### A.8 Phase R checklist (Retrofit)

This checklist applies when adopting Codex Machinae on an existing project (§11.6).

**Debt-scoping audit (§11.6.1)**

- [ ] `RETROFIT_AUDIT.md` produced and committed
- [ ] Requirements artefacts gap assessed (PRD, stories, ADRs)
- [ ] Code quality gap assessed (linting, formatting, commits)
- [ ] Security posture reviewed (secrets, input validation)
- [ ] Test coverage measured and ratchet starting point set (§5.3)
- [ ] Documentation gaps identified (README, CHANGELOG, code comments)
- [ ] CI/CD pipeline gap analysed against §7

**Contract mapping (§11.6.2)**

- [ ] Boundary Contract Map generated from existing codebase (§8)
- [ ] All integration points classified by axis and direction
- [ ] Undocumented or implicit contracts flagged as high-risk

**Adoption tiers (§11.6.3)**

- [ ] T1 (Safety net) completed — coverage ratchet, secrets audit, CI baseline
- [ ] T2 (Structure) completed — directory layout, agent config, CHANGELOG, contract map
- [ ] T3 (Process) completed — module activation, checklist adoption, Definition of Done

**Module activation (§11.6.4)**

- [ ] All module triggers evaluated against existing codebase
- [ ] Active modules' artefacts populated retroactively

**Lifecycle entry (§11.6.5)**

- [ ] Target phase determined (Phase 2 or Phase 3)
- [ ] `PROJECT_STATUS.md` created or updated to reflect current phase

### A.9 Multi-agent setup checklist (§12.7 — when activated)

This checklist applies only when the analyst has chosen to employ multiple agents.

**Designation and partitioning**

- [ ] Lead agent nominated and recorded in agent-configuration file (§12.7.1)
- [ ] Scope partition defined and documented (§12.7.2)
- [ ] Each agent's perimeter confirmed as non-overlapping
- [ ] Write-access categories assigned to shared artefacts (§12.7.4)

**Mixed-LLM (if applicable)**

- [ ] Provider-specific config files consistent with shared `AI-AGENTS.md` (§12.7.6)
- [ ] No contradictions between provider-specific instructions and scope partition

**Operational**

- [ ] Handover note format agreed (§12.7.5)
- [ ] Conflict-prevention protocol understood by all participating agents (§12.7.3)

---

## Appendix B — Templates

### B.1 PRD template

```markdown
# [Project Name] — Product Requirements Document

**Status:** Draft v1
**Owner:** [name]
**Last updated:** [date]

### Pre-implementation checklist

- [ ] [Decision 1 already confirmed]
- [ ] [Decision 2 already confirmed]

---

## 1. Purpose and scope

### 1.1 What this system guarantees
### 1.2 What this system does not cover

## 2. Users and stakeholders
## 3. Functional requirements
## 4. Non-functional requirements

### 4.1 Performance
### 4.2 Security
### 4.3 Accessibility
### 4.4 Scalability

## 5. Architectural constraints
## 6. Open questions

| # | Topic | Owner | Status |
|---|-------|-------|--------|

## 7. Later-phase work

| Item | Phase | Notes |
|------|-------|-------|

## Appendices
```

### B.2 User Story template

```markdown
# US-[AREA]-[NUMBER]: [Short title]

**Priority:** P0 | P1 | P2 | P3
**Estimate:** [hours/points]
**PRD ref:** §[section]
**Dependencies:** US-[xxx], US-[yyy]

## Story
As a [role]
I want [action]
So that [benefit]

## Acceptance Criteria

1. GIVEN [context]
   WHEN [action]
   THEN [result]

2. GIVEN [context]
   WHEN [action]
   THEN [result]

## Technical notes
[notes for the implementer]
```

### B.3 ADR template

```markdown
# ADR-[NUMBER]: [Title]

**Status:** proposed | accepted | deprecated | superseded by ADR-[n]
**Date:** YYYY-MM-DD

## Context
[Why this decision is necessary]

## Decision
[What was decided]

## Consequences
[Positive and negative impact]

## Alternatives rejected
[What was considered and discarded, with rationale]
```

### B.4 DEPENDENCIES.md template

```markdown
# Dependencies

## Critical dependencies

### [Dependency name]
- **Type:** REST API | SDK | Database | Service
- **Version:** [current version]
- **Contract:** [link to contract documentation]
- **Contract count:** [number of contracts in Boundary Contract Map, by axis]
- **Surveillance agent:** [agent id]
- **Last verified:** [date]
- **Notes:** [particular notes, known quirks, workarounds]

## Development dependencies

### [Name]
- **Purpose:** [what it is used for]
- **Version:** [version]
- **Pinned:** yes | no (range)
```

### B.5 Compatibility record template (M1)

```json
{
  "dependency": "[name]",
  "version": "[version that triggered the cycle]",
  "detected_at": "YYYY-MM-DDTHH:MM:SSZ",
  "source": "[agent id: pkg-watch | api-probe | docs-watch | security-watch | container-watch]",
  "slots": {
    "latest": { "version": "[resolved]", "result": "pass | fail | error" },
    "recent": { "version": "[resolved]", "result": "pass | fail | error" },
    "baseline": { "version": "[resolved]", "result": "pass | fail | error" }
  },
  "rollup": "pass | fail | partial",
  "severity": "L0 | L1 | L2",
  "events": [
    { "type": "detected", "at": "...", "by": "..." },
    { "type": "classified", "at": "...", "severity": "..." },
    { "type": "remediated | adopted", "at": "...", "pr": "..." }
  ]
}
```

### B.6 OWASP review template (M2)

```markdown
# OWASP Top 10 Review — [Year]

**Reviewed by:** [name]
**Date:** YYYY-MM-DD
**OWASP version:** [e.g. 2021]

| # | Item | Covered by | Verified how | Status |
|---|------|-----------|-------------|--------|
| A01 | Broken Access Control | | | ✅ / ⚠️ / ❌ |
| A02 | Cryptographic Failures | | | |
| A03 | Injection | | | |
| A04 | Insecure Design | | | |
| A05 | Security Misconfiguration | | | |
| A06 | Vulnerable and Outdated Components | | | |
| A07 | Identification and Authentication Failures | | | |
| A08 | Software and Data Integrity Failures | | | |
| A09 | Security Logging and Monitoring Failures | | | |
| A10 | Server-Side Request Forgery (SSRF) | | | |

## Actions
[List any items that are not fully covered, with remediation plan]
```

### B.8 Boundary Contract Map example (§8)

> Complete `COMPATIBILITY.md` for a hypothetical web service that exposes a REST API,
> consumes Stripe and a PostgreSQL database, and renders a React SPA.

```json
{
  "contracts": [
    {
      "id": "rest.orders.create",
      "axis": "api",
      "direction": "inbound",
      "counterparty": "mobile-app",
      "shape": "POST /v1/orders",
      "file": "src/routes/orders.ts",
      "line": 28,
      "context": "createOrder()",
      "risk_weight": "high",
      "test_coverage": true,
      "last_verified": "2026-04-18"
    },
    {
      "id": "rest.orders.list",
      "axis": "api",
      "direction": "inbound",
      "counterparty": "mobile-app",
      "shape": "GET /v1/orders?status={status}",
      "file": "src/routes/orders.ts",
      "line": 55,
      "context": "listOrders()",
      "risk_weight": "medium",
      "test_coverage": true,
      "last_verified": "2026-04-18"
    },
    {
      "id": "stripe.charges.create",
      "axis": "api",
      "direction": "outbound",
      "counterparty": "stripe-api",
      "shape": "POST /v1/charges",
      "file": "src/payments/stripe-client.ts",
      "line": 42,
      "context": "createCharge()",
      "risk_weight": "high",
      "test_coverage": true,
      "last_verified": "2026-04-15"
    },
    {
      "id": "stripe.webhooks.charge.succeeded",
      "axis": "api",
      "direction": "inbound",
      "counterparty": "stripe-api",
      "shape": "POST /webhooks/stripe (event: charge.succeeded)",
      "file": "src/webhooks/stripe-handler.ts",
      "line": 17,
      "context": "handleChargeSucceeded()",
      "risk_weight": "high",
      "test_coverage": true,
      "last_verified": "2026-04-15"
    },
    {
      "id": "db.orders",
      "axis": "data",
      "direction": "outbound",
      "counterparty": "postgresql",
      "shape": "public.orders (id, user_id, status, total, created_at)",
      "file": "src/db/schema/orders.ts",
      "line": 8,
      "context": "OrderModel",
      "risk_weight": "high",
      "test_coverage": true,
      "last_verified": "2026-04-18"
    },
    {
      "id": "db.users",
      "axis": "data",
      "direction": "outbound",
      "counterparty": "postgresql",
      "shape": "public.users (id, email, hashed_password, role, created_at)",
      "file": "src/db/schema/users.ts",
      "line": 5,
      "context": "UserModel",
      "risk_weight": "high",
      "test_coverage": true,
      "last_verified": "2026-04-18"
    },
    {
      "id": "ui.orders.dashboard",
      "axis": "ui",
      "direction": "inbound",
      "counterparty": "end-user",
      "shape": "screen:orders-dashboard",
      "file": "src/ui/pages/OrdersDashboard.tsx",
      "line": 1,
      "context": "OrdersDashboard",
      "risk_weight": "medium",
      "test_coverage": false,
      "last_verified": "2026-04-10"
    },
    {
      "id": "env.stripe_secret_key",
      "axis": "data",
      "direction": "outbound",
      "counterparty": "runtime-environment",
      "shape": "env:STRIPE_SECRET_KEY",
      "file": "src/config/env.ts",
      "line": 12,
      "context": "loadEnv()",
      "risk_weight": "high",
      "test_coverage": true,
      "last_verified": "2026-04-18"
    }
  ],
  "generated_at": "2026-04-18T14:30:00Z",
  "generator": "ast-walker",
  "contract_count": 8,
  "axis_counts": {
    "api": 4,
    "data": 3,
    "ui": 1,
    "hardware": 0
  }
}
```

> **Reading guide.** The map covers all four axes. Two `api` contracts are inbound
> (the REST endpoints the mobile app calls), two are outbound (Stripe). The `data`
> axis includes both database schemas and an environment variable — the latter is a
> contract because changing the variable name breaks the deployment. The single `ui`
> entry has `test_coverage: false`, which the Surveillance module (M1) would flag as
> a gap. The `axis_counts` block feeds the cardinality guard (§8.4).

---

### B.7 Taxonomy term template (M4)

```yaml
id: "[NAMESPACE]-[NUMBER]"
label: "[Human-readable name]"
description: "[One-sentence definition]"
parent: "[parent term ID, or null if top-level]"
status: "active | deprecated"
deprecated_successor: "[successor term ID, if deprecated]"
deprecated_sunset: "YYYY-MM-DD"
introduced_in: "[taxonomy version, e.g. 1.2.0]"
source: "upstream:[framework-name] | local"
```

### B.9 Retrofit Audit template (§11.6)

```markdown
# Retrofit Audit — [Project Name]

**Date:** [YYYY-MM-DD]
**Analyst:** [name or agent ID]
**Repository:** [URL or path]
**Current state:** [brief description — e.g. "active development, no CI, partial tests"]

## Gap assessment

| Area | Playbook expectation | Current state | Gap severity | Effort estimate |
|------|---------------------|---------------|--------------|-----------------|
| Requirements artefacts (§1) | PRD, stories, ADRs, backlog | | | |
| Project structure (§2) | Standard layout, agent config | | | |
| Code quality (§3) | Linting, formatting, commits | | | |
| Security (§4) | Secrets management, input validation | | | |
| Testing (§5) | Coverage ratchet, tier distribution | | | |
| Documentation (§6) | README, CHANGELOG, code comments | | | |
| CI/CD (§7) | Pipeline with build/lint/test/deploy | | | |
| Boundary contracts (§8) | Contract map generated | | | |

## Contract map summary

| Axis | Direction | Count | Documented | Undocumented |
|------|-----------|-------|------------|--------------|
| api | inbound | | | |
| api | outbound | | | |
| data | inbound | | | |
| data | outbound | | | |
| ui | outbound | | | |
| hardware | inbound | | | |

## Activated modules and domains

| Module/Domain | Trigger met? | Rationale |
|---------------|-------------|-----------|
| D1 Web Service | | |
| D4 Embedded | | |
| D5 ML / Data | | |
| M1 Surveillance | | |
| M2 Security-sensitive | | |
| M4 Classification | | |

## Adoption plan

### T1 — Safety net (mandatory first)
1. [item]

### T2 — Structure
1. [item]

### T3 — Process
1. [item]

## Target lifecycle phase

**Recommended entry point:** Phase [2|3]
**Rationale:** [why this phase]
```

---

## Appendix C — Glossary

| Term | Definition |
|------|------------|
| **PRD** | Product Requirements Document — specification of the what and the why |
| **ADR** | Architecture Decision Record — documented architectural decision |
| **User Story** | Functional requirement from the user's perspective |
| **Acceptance Criteria** | Binary conditions that define "done" |
| **Definition of Done** | Universal checklist applied to every work item |
| **Domain appendix** | A section of the playbook (D1–D7) that adds project-type-specific content on top of Core when its activation trigger fires |
| **Cross-cutting module** | A section of the playbook (M1–M4) that adds capability-specific content composable with any domain when its activation trigger fires |
| **Boundary contract** | A promise the system makes to something outside its own implementation (hardware, UI, data, API); can be inbound (exposed) or outbound (consumed) |
| **Boundary Contract Map** | Structured inventory of all boundary contracts, tagged by axis and direction (§8) |
| **Bucket** | Change category (api-endpoint, data-model, etc.) |
| **Severity** | Level of impact of the change (safe, additive, breaking, p0) |
| **Slot** | A version in the test matrix (latest, recent, baseline) |
| **L0/L1/L2** | Autonomy levels in remediation |
| **Heartbeat** | Periodic signal confirming that an agent is active |
| **Canary** | Synthetic end-to-end test of the surveillance system |
| **Golden query** | Query with expected result to verify data integrity |
| **Fix-claim** | Structured declaration accompanying every agentic fix |
| **Circuit breaker** | Mechanism that disables automation after too many failures |
| **Never-auto-merge** | Conditions that always force human review |
| **Ratchet** | Mechanism that prevents coverage from dropping |
| **Escape valve** | Tracked temporary exception to a ratchet rule |
| **Conventional Commits** | Standard for structured commit messages |
| **Blue-green deploy** | Deployment strategy using two alternating environments |
| **Rolling update** | Gradual deployment that replaces instances one at a time |
| **Feature flag** | Toggle that enables/disables a feature without deployment |
| **HAL** | Hardware Abstraction Layer — thin interface isolating application code from peripheral access (D4.1) |
| **HIL** | Hardware-in-the-loop — test tier that exercises code on real hardware or a cycle-accurate simulator (D4.3) |
| **Data drift** | Divergence of incoming feature distributions from the training distribution (D5.5) |
| **Concept drift** | Change in the relationship between features and the target, degrading model quality (D5.5) |
| **Evaluation contract** | Versioned specification of how a model's quality is measured before promotion (D5.6) |
| **Taxonomy** | A structured classification of terms in a domain, following MECE and parsimony principles (M4.1) |
| **Scouting protocol** | The process by which the AI discovers domain-specific frameworks for adoption (M4.3) |
| **MECE** | Mutually Exclusive, Collectively Exhaustive — design constraint for taxonomies (M4.1) |
| **SOTA Scout** | Agent that researches the state of the art for project technologies and patterns |
| **Technology health check** | Periodic health verification of a technology (releases, community, trends) |
| **Alternative scanning** | Search for libraries or services alternative to those in use |
| **Pattern evolution** | Monitoring of the evolution of architectural best practices in the industry |
| **Back-pressure** | Load-shedding mechanism (circuit breaker, timeout, bulkhead) preventing cascading failure (D1.5) |
| **Semantic versioning (SemVer)** | Versioning scheme (major.minor.patch) encoding backwards-compatibility promises for published packages (D2.2) |
| **Deprecation window** | Minimum period during which a deprecated symbol remains functional before removal (D2.3) |
| **Breaking-change detection** | Automated CI step comparing current public API surface against the last published version (D2.4) |
| **Exit-code contract** | Documented mapping between CLI exit codes and their meaning, tested in CI (D3.3) |
| **Shell completion** | Auto-generated scripts enabling tab-completion of CLI subcommands and flags (D3.5) |
| **Release cadence** | The model governing when releases are cut: release-when-ready, release train, or event-driven (M3.1) |
| **Freeze window** | The final portion of a release-train cycle during which only fixes enter the release branch (M3.1) |
| **Artefact provenance** | Attestation tying a published artefact to its source commit, build platform, and builder identity (M3.3) |
| **Release yank** | Registry mechanism that marks a published version as unsuitable without deleting it (M3.5) |
| **Bundle budget** | Size threshold for production JS/CSS/image artefacts, enforced as a ratchet in CI (D7.1) |
| **Core Web Vitals** | Google's metrics for loading (LCP), responsiveness (INP), and visual stability (CLS) (D7.5) |
| **Cache-invalidation strategy** | The rules governing how CDN/browser caches are cleared on deployment (D7.2) |
| **Staged rollout** | Percentage-based release to mobile users, gated by crash-rate and quality metrics (D6.2) |
| **Crash-free rate** | Percentage of user sessions without an unhandled crash, monitored as a quality threshold (D6.4) |
| **OTA update (mobile)** | Code update delivered directly to the app, bypassing the store review cycle (D6.6) |
| **OTA** | Over-the-air — firmware update delivered via network (D4.4) |
| **A/B partitioning** | Firmware update strategy maintaining two slots for automatic rollback (D4.4) |
| **Phase R (Retrofit)** | One-time convergence protocol for adopting the playbook on an existing project (§11.6) |
| **Retrofit audit** | Structured gap assessment between a project's current state and the playbook's expectations (§11.6.1) |
| **Debt-scoping** | The process of measuring the distance between an existing project and playbook conformance (§11.6.1) |
| **Adoption tier** | Priority grouping (T1 safety net, T2 structure, T3 process) for ordering retrofit work (§11.6.3) |
| **Lead agent** | The agent designated as single writer for coordination artefacts in a multi-agent setup (§12.7.1) |
| **Scope partition** | Explicit assignment of non-overlapping work perimeters to agents in a multi-agent setup (§12.7.2) |
| **Inter-agent handover** | Structured note transferring context from one agent to another during shift change or scope transfer (§12.7.5) |
| **Project-size profile** | Declaration (Solo, Small, Large) that modulates checklist obligation levels in Appendix A (§2.5) |
| **AST Walker** | Static-analysis tool that generates the Boundary Contract Map by scanning source code (Appendix D.1) |
| **Coverage ratchet (tool)** | CI step that enforces the coverage-ratchet mechanism by comparing coverage reports against a committed baseline (Appendix D.2) |
| **Surveillance agent scaffold** | Minimal agent that runs contract tests on a schedule and produces compatibility records (Appendix D.3) |

---

## Appendix D — Tooling Specifications

This appendix defines the **contracts** that reference implementations must satisfy. It
specifies input, output, behaviour, and integration points for each tool. The playbook
does not ship implementations — those live in dedicated repositories and are validated
against these specifications.

Each specification follows a common structure: purpose, activation trigger (when the tool
becomes relevant), interface (input/output), behavioural rules, integration with the
playbook, and acceptance criteria.

### D.1 AST Walker — Contract Map Generator

**Purpose:** Automatically generate or update the Boundary Contract Map (§8) by
statically analysing the project's source code.

**Activation trigger:** the project has a codebase with at least one boundary contract
(API endpoint, database schema, external service call, hardware interface, UI data
binding). Relevant whenever §8 applies.

#### D.1.1 Interface

| Parameter | Description |
|-----------|-------------|
| **Input** | Project root path; language/framework hint (optional — auto-detected when possible); existing `COMPATIBILITY.md` (optional — for delta mode) |
| **Output** | `COMPATIBILITY.md` in the format defined by B.8, written to the project root |
| **Mode: full** | Scans the entire codebase and produces a complete contract map from scratch |
| **Mode: delta** | Compares the current codebase against an existing `COMPATIBILITY.md` and reports additions, removals, and changes |
| **Exit codes** | `0` success; `1` new contracts found (delta mode — CI can gate on this); `2` error |

#### D.1.2 Detection rules

The walker must identify boundary contracts by analysing:

| Axis | What to detect | Typical source patterns |
|------|---------------|------------------------|
| **api — inbound** | Exposed endpoints, RPC handlers, GraphQL resolvers, CLI commands | Route decorators, handler registrations, schema definitions |
| **api — outbound** | HTTP clients, SDK calls, gRPC stubs, message-queue producers | Import of client libraries, fetch/request calls, queue publish |
| **data — inbound** | Database reads, file reads, cache gets, event consumers | ORM queries, file-open for read, cache-get calls, subscriber registrations |
| **data — outbound** | Database writes, file writes, cache sets, event producers | ORM save/insert, file-open for write, cache-set calls, publisher calls |
| **ui — outbound** | Data bindings, props passed to UI components, template variables | Framework-specific patterns (React props, template context, view models) |
| **hardware — inbound** | Sensor reads, GPIO inputs, ADC reads, peripheral status | HAL read calls, register reads, device-file reads |
| **hardware — outbound** | Actuator writes, GPIO outputs, DAC writes, display commands | HAL write calls, register writes, device-file writes |

The walker is not required to detect every contract with zero false negatives. The
specification defines a **minimum recall target of 80%** for the supported languages —
the remaining contracts are added manually. False positives are acceptable as long as
the output clearly marks confidence level (`high`, `medium`, `low`) so the analyst can
triage.

#### D.1.3 Language support

The MVP must support at least two languages from different paradigms:

- **TypeScript** (via `ts-morph` or equivalent AST library)
- **Python** (via the `ast` standard-library module)

Additional languages are added as separate parser plugins. The walker architecture must
allow a new language parser to be added without modifying the core detection logic.

#### D.1.4 Behavioural rules

1. The walker never modifies source code — it is read-only.
2. In delta mode, contracts present in the existing map but no longer detected in the
   code are marked `removed?` (with a question mark) rather than silently deleted.
   Only the analyst confirms actual removal.
3. The output format matches B.8 exactly — the walker's output must be valid input for
   the surveillance agent (D.3).
4. The walker logs every detection decision at debug level so false positives can be
   investigated.

#### D.1.5 Integration points

| Playbook reference | Integration |
|--------------------|-------------|
| §8 Boundary Contracts | The walker automates §8.3 (contract-map generation) |
| §11.2 Phase 1 | "Generate the initial contract map" can be executed by the walker |
| §11.6.2 Phase R | Retroactive contract mapping uses the walker in full mode |
| M1 Surveillance | The walker's output feeds M1.3 compatibility records |
| B.8 Contract Map example | The walker's output format matches this template |

#### D.1.6 Acceptance criteria

- [ ] Full mode produces a valid `COMPATIBILITY.md` for a TypeScript project with REST endpoints and a database
- [ ] Full mode produces a valid `COMPATIBILITY.md` for a Python project with HTTP clients and file I/O
- [ ] Delta mode correctly identifies added and removed contracts against a known baseline
- [ ] Confidence tagging (`high`/`medium`/`low`) is present on every detected contract
- [ ] Exit code 1 in delta mode when new contracts are found
- [ ] Output passes structural validation against B.8 format

---

### D.2 Coverage Ratchet — CI Step

**Purpose:** Enforce the coverage-ratchet mechanism (§5.3) as an automated CI step that
fails the pipeline when test coverage drops below the committed baseline.

**Activation trigger:** the project has a test suite that produces a coverage report.
Relevant whenever §5.3 applies.

#### D.2.1 Interface

| Parameter | Description |
|-----------|-------------|
| **Input** | Path to the coverage report (auto-detected or explicit); path to the baseline file (default: `.coverage-baseline.json`) |
| **Output** | Pass/fail verdict; human-readable summary (lines covered, delta, threshold); updated baseline file (on pass, if `--update` flag is set) |
| **Formats supported** | Cobertura XML, lcov, Istanbul JSON, coverage.py JSON — at minimum two of these |
| **Exit codes** | `0` coverage at or above baseline; `1` coverage below baseline; `2` configuration or parse error |

#### D.2.2 Baseline file format

```json
{
  "version": 1,
  "updated": "YYYY-MM-DDTHH:MM:SSZ",
  "line_coverage_pct": 78.4,
  "branch_coverage_pct": 62.1,
  "escape_valves": [
    {
      "path": "src/legacy/parser.ts",
      "reason": "Legacy code pending rewrite — US-042",
      "expires": "2026-06-30",
      "approved_by": "analyst-name"
    }
  ]
}
```

#### D.2.3 Behavioural rules

1. The ratchet only moves upward. If the current coverage exceeds the baseline, the
   baseline is updated automatically when `--update` is passed (typically on merge to
   the main branch).
2. **Escape valves** (§5.3) are respected: files listed in `escape_valves` are excluded
   from the ratchet comparison. Expired escape valves (past their `expires` date) are
   treated as if they do not exist — the file's coverage counts again.
3. The tool never modifies test files or source code — it is a read-only comparator
   with optional baseline-file write.
4. When coverage drops, the output names the specific files or modules responsible for
   the regression, ordered by impact (largest drop first).

#### D.2.4 Integration points

| Playbook reference | Integration |
|--------------------|-------------|
| §5.3 Coverage ratchet | Direct implementation of the ratchet mechanism |
| §7.2 Pipeline stages | Runs in the Build or Stage phase of the pipeline |
| §11.2 Phase 1 | "Initial coverage baseline committed" is produced by `--update` on first run |
| A.2 Phase 1 checklist | Satisfies "Initial coverage baseline committed (§5.3)" |

#### D.2.5 Acceptance criteria

- [ ] Correctly parses at least two coverage-report formats (e.g. Cobertura XML + Istanbul JSON)
- [ ] Exit code 0 when coverage is at or above baseline
- [ ] Exit code 1 when coverage drops, with file-level regression report
- [ ] Escape valves correctly exclude listed files from comparison
- [ ] Expired escape valves are ignored (file counts toward coverage again)
- [ ] `--update` flag writes the new baseline only when coverage has increased

---

### D.3 Surveillance Agent Scaffold

**Purpose:** Provide a minimal but functional surveillance agent (M1.1) that
periodically runs contract tests, produces compatibility records (M1.3), and opens
issues when a contract breaks.

**Activation trigger:** M1 Surveillance is active and the project has at least one
outbound boundary contract worth monitoring.

#### D.3.1 Interface

| Parameter | Description |
|-----------|-------------|
| **Input** | `COMPATIBILITY.md` (contract map); test commands per contract (configured in a manifest file); issue-tracker integration config (GitHub Issues, GitLab Issues, or Linear) |
| **Output** | Compatibility records (M1.3 format, written to `docs/compatibility/`); issues opened for broken contracts; heartbeat signal (M1.4.1) |
| **Execution model** | Cron-scheduled (recommended: every 6 hours, configurable). Stateless between runs — all state is in committed artefacts |

#### D.3.2 Manifest file format

```yaml
version: 1
schedule: "0 */6 * * *"
contracts:
  - id: "api-out-stripe"
    test_command: "npm test -- --grep 'stripe contract'"
    timeout_seconds: 120
    severity_on_failure: "breaking"
  - id: "data-out-postgres"
    test_command: "pytest tests/contracts/test_postgres.py"
    timeout_seconds: 60
    severity_on_failure: "additive"
issue_tracker:
  provider: "github"
  repository: "org/repo"
  labels: ["surveillance", "contract-break"]
```

#### D.3.3 Behavioural rules

1. Each run tests every contract listed in the manifest. A contract that was `compatible`
   and now fails transitions to `incompatible` — a new compatibility record is written
   and an issue is opened.
2. A contract that was `incompatible` and now passes transitions to `compatible` — the
   record is updated and the corresponding issue is closed (or commented on, if manual
   close is preferred).
3. The agent never modifies source code or tests — it only runs existing test commands
   and writes records.
4. The heartbeat (M1.4.1) is a timestamp file (`docs/compatibility/.heartbeat`) updated
   at the end of every run. If the heartbeat is older than the configured threshold
   (default: 6 hours), external monitoring should alert.
5. If a test command times out, the contract status is recorded as `timeout` and the
   issue is opened with a timeout label.
6. The agent produces a structured log of every run (contracts tested, results, issues
   opened/closed) for auditability (§12.6).

#### D.3.4 Compatibility record format

Each record follows the B.5 template. The agent writes one file per run per contract
that changed status:

```
docs/compatibility/YYYY-MM-DD-<contract-id>.md
```

Records for unchanged contracts are not duplicated — only transitions generate new files.

#### D.3.5 Integration points

| Playbook reference | Integration |
|--------------------|-------------|
| M1.1 Surveillance agents | The scaffold implements the agent described in M1.1 |
| M1.3 Compatibility records | Output format matches B.5 |
| M1.4.1 Heartbeat | The `.heartbeat` file implements the heartbeat mechanism |
| M1.4.2 Classifier retrospective | Run logs provide input for monthly retrospectives |
| §8 Boundary Contracts | The manifest references contract IDs from the contract map |
| D.1 AST Walker | The walker's output (`COMPATIBILITY.md`) is the agent's input |

#### D.3.6 Acceptance criteria

- [ ] Runs all contracts listed in the manifest and produces correct compatibility records
- [ ] Transitions (`compatible` → `incompatible` and vice versa) trigger issue creation/closure
- [ ] Heartbeat file is updated at the end of every run
- [ ] Timeout handling produces a `timeout` status and opens an issue
- [ ] Structured run log is produced for every execution
- [ ] Stateless between runs — deleting all local state except committed artefacts and re-running produces identical results
