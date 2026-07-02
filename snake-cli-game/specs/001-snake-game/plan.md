# Implementation Plan: Classic Terminal Snake Game

**Branch**: `001-snake-game` | **Date**: 2026-07-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-snake-game/spec.md`

---

## Summary

Build a zero-dependency, cross-platform CLI Snake game in Python 3.8+ using
only the standard library. The game renders via ANSI escape codes to any
modern terminal, reads input through a platform-abstracted daemon thread
(`termios`/`select` on POSIX, `msvcrt` on Windows), and separates pure game
logic from I/O so that all gameplay rules are fully unit-testable without a
terminal. The implementation covers the full game loop, two end conditions
(collision → game over, board full → win), absolute four-directional controls
(all arrow keys map to screen directions), live scoring, and in-session restart.

---

## Technical Context

**Language/Version**: Python 3.8+ (standard library only)

**Primary Dependencies**: None — stdlib modules only:
`collections`, `enum`, `random`, `select`, `sys`, `threading`, `time`,
`tty`, `termios` (POSIX), `msvcrt` (Windows), `shutil`, `unittest`

**Storage**: N/A — no persistence required (spec Assumption 4)

**Testing**: `unittest` (stdlib); `python -m unittest discover`

**Target Platform**: Linux, macOS, Windows 10+ (build 14931+); any terminal
with ANSI escape code support

**Project Type**: Single-package CLI application; entry via `python -m snake`

**Performance Goals**:
- 5 ticks/second default (configurable 1–30 via `--speed`)
- Input latency ≤ 1 tick (≤ 100 ms at default speed)
- Startup time < 1 second on commodity hardware

**Constraints**:
- Zero external packages at runtime (Constitution Principle I)
- Minimum terminal: 24 columns × 24 rows for default 20×20 board
- No network access; no persistent state across launches

**Scale/Scope**: Single player, single process, single terminal session

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Design Check

| Principle | Status | Evidence |
|-----------|--------|---------|
| I. Zero-Dependency Footprint | ✅ PASS | Python stdlib only: `collections`, `tty`, `termios`, `msvcrt`, `select`, `threading`, `random`, `time`, `shutil`, `unittest`. No pip installs required to run. |
| II. Universal Portability | ✅ PASS | ANSI escapes work on Linux/macOS/Windows 10+. Input abstracted: `termios`+`select` on POSIX, `msvcrt` on Windows. Platform branch isolated in `input_handler.py`. Terminal size checked via `shutil.get_terminal_size()`. |
| III. Standard CLI I/O & Simple Distribution | ✅ PASS | Single entry point `python -m snake`. Errors → stderr. Exit codes documented. No installer, build step, or package manager needed. |
| IV. Test-First Discipline | ✅ PASS | Pure game logic (`game.py`) has no I/O dependencies → fully unit-testable. Tests written before implementation. Red-Green-Refactor enforced per task order in `tasks.md`. |
| V. Performance & Responsiveness | ✅ PASS | Default 5 Hz tick with `time.sleep` remainder (no busy-waiting). Daemon input thread polls with `select`/`kbhit` timeout < tick interval. Sub-1s startup (no import overhead). |

No violations. Complexity Tracking table not required.

### Post-Design Check (Phase 1 complete)

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Zero-Dependency Footprint | ✅ PASS | Data model uses `collections.deque`, `enum.Enum`, `typing.NamedTuple` — all stdlib. |
| II. Universal Portability | ✅ PASS | Platform-specific path isolated to `input_handler.py`; all other modules are platform-agnostic. |
| III. Standard CLI I/O | ✅ PASS | CLI contract uses only positional/optional args via `argparse` (stdlib); rendering is pure ANSI. |
| IV. Test-First | ✅ PASS | 9 test cases identified (see quickstart.md); all target pure `game.py` functions. |
| V. Performance | ✅ PASS | No synchronization bottlenecks; `threading.Lock` held for < 1 µs per tick. |

---

## Project Structure

### Documentation (this feature)

```text
specs/001-snake-game/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: technical decisions
├── data-model.md        # Phase 1: entities and state transitions
├── quickstart.md        # Phase 1: validation guide
├── contracts/
│   ├── cli-contract.md  # CLI invocation, exit codes, screen layout
│   └── input-contract.md # Key bindings, turning logic, platform encoding
└── tasks.md             # Phase 2: implementation tasks (via /speckit-tasks)
```

### Source Code (repository root)

```text
snake/
├── __main__.py       # Entry point: argparse, terminal size check, starts game loop
├── game.py           # Pure game logic: GameSession, Snake, GameState, Direction, turning, collision, scoring
├── renderer.py       # ANSI rendering: score bar, board, game-over/win overlays
├── input_handler.py  # Platform-specific input: POSIX (tty/termios/select) vs Windows (msvcrt)
└── terminal.py       # Terminal lifecycle: raw mode setup/teardown, cursor hide/show, resize check

tests/
├── test_game.py      # Unit tests for all game.py logic (no terminal, no I/O)
└── test_integration.py  # Smoke test: drive GameSession through state transitions programmatically
```

**Structure Decision**: Single-package flat layout. No `src/` wrapper needed
for a project this small. `python -m snake` works from the repo root when the
`snake/` directory is present. Tests are co-located at root level for
`python -m unittest discover` to find them.

---

## Implementation Areas

### Area 1: Game Logic (`game.py`)

All pure, side-effect-free functions and classes. This area is the most
critical to get right first — all other areas depend on it.

Key components:
- `Direction` enum + relative turn table + 180° reversal check
- `Position` NamedTuple + out-of-bounds check
- `Snake` class — `deque`-based body, `move()` / `grow()` operations
- `GameState` enum (`ACTIVE`, `GAME_OVER`, `WIN`)
- `GameBoard` dataclass — width, height, free cell computation
- `GameSession` — tick loop logic, `handle_input()`, `reset()`
- Fruit respawn: `random.choice(list(free_cells))`
- Win detection: `len(free_cells) == 0` after fruit eaten

### Area 2: Terminal Lifecycle (`terminal.py`)

Handles setup and teardown around gameplay:
- `enter_raw_mode()` / `exit_raw_mode()` — saves/restores `termios` attrs on
  POSIX; no-op on Windows (msvcrt handles raw input natively)
- `hide_cursor()` / `show_cursor()` — ANSI `\x1b[?25l` / `\x1b[?25h`
- `check_terminal_size(min_cols, min_rows)` — uses `shutil.get_terminal_size()`;
  exits with code 1 if too small
- Context manager pattern for safe teardown on exception / SIGINT

### Area 3: Input Handling (`input_handler.py`)

Platform-abstracted keyboard reading. Exposes one function:
`get_key() → str | None`

Internal implementation:
- Detect platform at import time (`sys.platform`)
- **POSIX path**: `select.select([sys.stdin], [], [], POLL_TIMEOUT)` → read
  1–3 bytes → decode ESC sequence
- **Windows path**: `msvcrt.kbhit()` loop with `time.sleep(0.01)` → `getch()`
  → handle `\xe0` prefix for arrows
- Returns canonical key name: `"UP"`, `"DOWN"`, `"LEFT"`, `"RIGHT"`, `"QUIT"`,
  `"RESTART"`, or `None`; all four arrow directions are now returned (previously
  UP/DOWN were unused)

### Area 4: Rendering (`renderer.py`)

Stateless render functions — always draw from game state:
- `render(session: GameSession, board_top_row: int)` — full frame redraw
- `draw_score_bar(score: int)`
- `draw_board(board, snake, fruit)` — builds string buffer, writes once to
  `sys.stdout` to minimise flicker
- `draw_overlay(state: GameState, score: int, board)` — GAME OVER or YOU WIN
- ANSI: `\x1b[H` to home, then write entire frame as one `sys.stdout.write()`

### Area 5: Entry Point (`__main__.py`)

- `argparse` for `--width`, `--height`, `--speed`
- Terminal size validation before entering raw mode
- `try/finally` to guarantee terminal restoration
- `KeyboardInterrupt` → treat as quit, exit 0

---

## Testing Plan

All tests in `test_game.py` must be written and failing before `game.py` is
implemented (Constitution Principle IV — NON-NEGOTIABLE).

### Unit Tests (`test_game.py`)

| Test | What it verifies | FR |
|------|-----------------|-----|
| `test_turn_left_from_each_heading` | Relative left turn table — all 4 headings | FR-004 |
| `test_turn_right_from_each_heading` | Relative right turn table — all 4 headings | FR-004 |
| `test_reversal_discarded` | 180° reversal suppressed; heading unchanged | FR-005 |
| `test_last_key_wins` | Two inputs in same tick → only last applied | FR-005b |
| `test_snake_moves_without_growth` | Body length unchanged after non-fruit tick | FR-003 |
| `test_fruit_eat_grow_score` | Eat fruit → length +1, score +1, fruit moves | FR-007 |
| `test_score_is_exactly_one_per_fruit` | Score increments by exactly 1 | FR-007 |
| `test_self_collision_ends_game` | Head enters body cell → GAME_OVER | FR-010 |
| `test_wall_collision_ends_game` | Head exits board → GAME_OVER | FR-011 |
| `test_win_when_board_full` | Last free cell eaten → WIN state | FR-016 |
| `test_score_resets_on_restart` | `reset()` sets score to 0, new snake | FR-014 |
| `test_fruit_not_on_snake` | Spawned fruit never overlaps snake body | FR-006 |
| `test_initial_snake_length` | Snake starts with exactly 3 segments | data-model |

### Smoke Tests (`test_integration.py`)

| Test | What it verifies |
|------|-----------------|
| `test_session_ticks_without_terminal` | `GameSession.tick()` N times → no exceptions |
| `test_state_transition_to_game_over` | Drive snake into wall programmatically → GAME_OVER |
| `test_restart_from_game_over` | GAME_OVER → reset → ACTIVE with score 0 |

---

## Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Windows ANSI codes disabled on older builds | Low (Win10 14931+ required per contract) | Document minimum Windows version; detect and error if ANSI not supported |
| Terminal left in raw mode on crash | Medium | `try/finally` in `terminal.py` context manager; register `atexit` handler as second safety net |
| ESC sequence fragmentation (POSIX) | Low | Read with very short second timeout; treat lone ESC as ignored |
| Fruit spawn in last free cell followed immediately by win not detected | Low | Win check occurs after growth, before rendering |
| `select.select` not available on Windows | Certain | `select` is POSIX-only for file descriptors; Windows path uses `msvcrt` exclusively |
