<!--
Sync Impact Report
==================
Version change: TEMPLATE → 1.0.0 (initial ratification)
Modified principles: N/A (first concrete version)
Added sections:
  - Core Principles I–V (Zero-Dependency Footprint, Universal Portability,
    Standard CLI I/O & Simple Distribution, Test-First Discipline,
    Performance & Responsiveness)
  - Technology Constraints
  - Development Workflow & Quality Gates
  - Governance
Removed sections: none (all placeholders resolved)
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ no changes required (Constitution
    Check gate already reads from this file dynamically)
  - .specify/templates/spec-template.md ✅ no changes required (generic,
    compatible with principles)
  - .specify/templates/tasks-template.md ✅ no changes required (generic,
    compatible with principles)
  - .specify/templates/checklist-template.md ✅ no changes required
Follow-up TODOs: none
-->

# Snake CLI Game Constitution

## Core Principles

### I. Zero-Dependency Footprint (NON-NEGOTIABLE)

The game MUST run using only the chosen language's standard library. No
third-party packages, frameworks, or external binaries may be added to the
runtime path. If a capability appears to need an external package (e.g.
advanced terminal UI, color libraries, input handling), the standard
library's built-in facilities MUST be used or the feature MUST be scoped
down until it fits within this constraint. Development-only tooling (test
runner, linter, formatter) is exempt but MUST NOT be required to run the
game itself.

**Rationale**: The project's core promise is "install nothing, run
anywhere." Every added dependency is a future install failure, a version
conflict, or a platform incompatibility. A dependency-free game can be
cloned and run with nothing but the language runtime already on the
machine.

### II. Universal Portability

The game MUST run unmodified on Linux, macOS, and Windows terminals,
including minimal/headless shells (SSH sessions, basic terminal emulators,
no GPU). It MUST NOT assume a specific terminal size beyond a documented
minimum, true-color support, mouse input, or any OS-specific API. Any
platform-specific code path (e.g. differing keyboard-input handling between
POSIX and Windows) MUST be isolated behind a single abstraction and covered
by tests on each supported platform before merge.

**Rationale**: "Run pretty much everywhere" is a hard requirement, not an
aspiration. Portability failures are cheapest to catch at design time, not
after a user reports the game crashes on their platform.

### III. Standard CLI I/O & Simple Distribution

The game MUST be a single entry-point program invoked from a terminal,
using only text/character-cell rendering. Output goes to stdout, errors and
diagnostics go to stderr, and the program MUST exit with a non-zero code on
failure. Distribution MUST require at most one command to obtain and run
(e.g. `git clone` + run, or a single-file script) — no build pipelines,
package managers, or installers beyond what the language runtime itself
provides.

**Rationale**: Lightweight means a new user can go from "got the code" to
"playing the game" in under a minute, on any machine, without an internet
connection for installation.

### IV. Test-First Discipline (NON-NEGOTIABLE)

Game logic (movement, collision detection, scoring, growth, game-over
conditions) MUST be implemented as pure, terminal-independent functions
with automated tests written before the implementation. Tests MUST fail
first (red), then the minimal implementation MUST make them pass (green).
Rendering and input-handling code, which are harder to unit test, MUST at
minimum be exercised by integration or smoke tests that verify the program
starts, accepts input, and exits cleanly.

**Rationale**: A small, dependency-free codebase is only valuable if it
stays correct as it evolves. Separating pure game logic from I/O keeps the
zero-dependency constraint compatible with rigorous, fast automated tests.

### V. Performance & Responsiveness

The game loop MUST maintain a consistent, configurable tick rate (default
suitable for classic Snake, e.g. 5–12 moves/second) with input latency low
enough that a keypress is reflected within one tick. The game MUST use
negligible CPU when idle between ticks (no busy-waiting) and MUST start up
in under one second on commodity hardware.

**Rationale**: A CLI game's entire user experience is responsiveness; any
perceptible input lag or CPU-spinning defeats the "lightweight" promise
even if the dependency and portability rules are followed.

## Technology Constraints

- **Language/runtime**: A single language and its standard library only,
  chosen during the planning phase specifically for strong cross-platform
  terminal I/O support without third-party packages. The choice MUST be
  documented and justified in the implementation plan's Technical Context.
- **No network access**: The game MUST NOT require or initiate any network
  connection to run or play.
- **No persistent system state**: Any optional persistence (e.g. high
  score) MUST be a single local file the user can delete freely, and the
  game MUST function fully (high scores simply reset) if that file is
  absent or unwritable.
- **Minimum terminal size**: A documented minimum terminal size (columns x
  rows) MUST be declared, and the game MUST fail with a clear error message
  rather than rendering incorrectly if the terminal is smaller.

## Development Workflow & Quality Gates

- Every change to game logic MUST include or update automated tests per
  Principle IV before being considered complete.
- Every change MUST be manually or automatically verified on at least two
  of the three supported platform families (Linux/macOS/Windows) before
  merge, per Principle II; cross-platform CI is preferred once available.
- Any proposal to add a dependency, network call, or persistent system
  integration MUST be rejected unless it first amends this constitution.
- Code reviews MUST explicitly check the diff against each Core Principle;
  a violation MUST be either fixed or justified and recorded before merge.

## Governance

This constitution supersedes all other project practices, templates, and
ad-hoc conventions. Where a plan, spec, or task conflicts with a principle
here, the principle wins and the artifact MUST be revised.

**Amendment procedure**: Amendments are proposed via a documented change
(PR or equivalent) that edits this file directly, states the rationale, and
updates the version per the policy below. Amendments affecting Core
Principles MUST also note any downstream templates or docs that need
updates, propagated in the same change where practical.

**Versioning policy**: This constitution follows semantic versioning:
- **MAJOR**: Backward-incompatible removal or redefinition of a principle
  (e.g. relaxing the zero-dependency rule).
- **MINOR**: A new principle or section is added, or guidance is materially
  expanded.
- **PATCH**: Clarifications, wording, or typo fixes with no semantic change.

**Compliance review**: Every implementation plan MUST pass the
Constitution Check gate before and after the design phase. Reviewers MUST
treat unresolved Core Principle violations as blocking, not advisory.

**Version**: 1.0.0 | **Ratified**: 2026-06-30 | **Last Amended**: 2026-06-30
