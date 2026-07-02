---
description: "Task list for Classic Terminal Snake Game implementation"
---

# Tasks: Classic Terminal Snake Game

**Input**: Design documents from `specs/001-snake-game/`

**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/ ✅ | quickstart.md ✅

**Tests**: Included — Constitution Principle IV (NON-NEGOTIABLE) mandates test-first.
All game-logic tests MUST be written and confirmed failing before their
corresponding implementation tasks are begun.

**Organization**: Tasks are grouped by user story. Each phase delivers an
independently testable increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no cross-task dependency)
- **[US#]**: Maps to user story in spec.md
- All file paths are relative to the repository root

---

## Phase 1: Setup

**Purpose**: Create the package skeleton so all other tasks have a valid import
target. No logic — stubs and `pass` bodies only.

- [x] T001 Create `snake/` package directory and `snake/__init__.py` (empty); create `tests/` directory and `tests/__init__.py` (empty)
- [x] T002 [P] Create `snake/game.py` with stub definitions: `class Position`, `class Direction`, `class Snake`, `class GameBoard`, `class GameState`, `class GameSession` — all with `pass` bodies and the imports they will need (`collections`, `enum`, `random`, `typing`)
- [x] T003 [P] Create `snake/terminal.py` with stub functions: `check_terminal_size()`, `enter_raw_mode()`, `exit_raw_mode()`, `hide_cursor()`, `show_cursor()` — all with `pass` bodies
- [x] T004 [P] Create `snake/renderer.py` with stub functions: `render()`, `draw_score_bar()`, `draw_board()`, `draw_overlay()` — all with `pass` bodies
- [x] T005 [P] Create `snake/input_handler.py` with stub: `get_key() -> str | None` returning `None`, plus a `start_input_thread()` stub
- [x] T006 [P] Create `snake/__main__.py` with minimal `argparse` skeleton accepting `--width`, `--height`, `--speed` with documented defaults (20, 20, 10); `if __name__ == "__main__": pass`
- [x] T007 [P] Create `tests/test_game.py` with `import unittest`, `from snake.game import *`, and an empty `TestGameLogic(unittest.TestCase)` class
- [x] T008 [P] Create `tests/test_integration.py` with `import unittest`, `from snake.game import GameSession, GameBoard, GameState`, and an empty `TestIntegration(unittest.TestCase)` class

**Checkpoint**: `python -m unittest discover -s tests` runs (0 tests collected, no import errors)

---

## Phase 2: Foundational Game Primitives (Blocking Prerequisite)

**Purpose**: Implement the core data types and game primitives that every user
story depends on. TDD mandatory per Constitution Principle IV.

**⚠️ CRITICAL**: No user story work begins until this phase is complete.
Write each test group, confirm they FAIL, then implement.

### Tests — Primitives (write first, confirm failure)

- [x] T009 Write failing tests for `Direction` in `tests/test_game.py`: `test_turn_left_from_each_heading` (4 cases), `test_turn_right_from_each_heading` (4 cases), `test_reversal_is_opposite` (UP↔DOWN, LEFT↔RIGHT) — run and confirm ALL FAIL before T010

- [x] T010 Write failing tests for `Position` in `tests/test_game.py`: `test_position_equality`, `test_position_out_of_bounds_detection` — confirm ALL FAIL before T011

- [x] T011 Write failing tests for `Snake` in `tests/test_game.py`: `test_snake_initial_length_is_3`, `test_snake_move_does_not_change_length`, `test_snake_grow_increases_length_by_one`, `test_snake_head_is_first_body_element`, `test_snake_body_cells_excludes_head` — confirm ALL FAIL before T012

### Implementation — Primitives

- [x] T012 Implement `Direction` enum in `snake/game.py`: values `UP/DOWN/LEFT/RIGHT` each with `(row_delta, col_delta)`; `turn_left()` and `turn_right()` methods using the relative turn table from `data-model.md`; `is_opposite(other)` method — T009 tests go green

- [x] T013 Implement `Position` as a `NamedTuple(row: int, col: int)` in `snake/game.py`; add `is_out_of_bounds(width, height) -> bool` — T010 tests go green

- [x] T014 Implement `Snake` class in `snake/game.py`: `body: collections.deque[Position]` (head = `body[0]`); `direction: Direction`; `head` property; `body_cells` property returning `set(list(body)[1:])`; `move(new_head)` (prepend + pop tail); `grow(new_head)` (prepend, no pop) — T011 tests go green

### Tests — GameBoard and GameSession skeleton (write first, confirm failure)

- [x] T015 Write failing tests for `GameBoard` and `GameSession` init in `tests/test_game.py`: `test_gameboard_free_cells_excludes_snake_and_fruit`, `test_gamesession_initial_state_is_active`, `test_gamesession_initial_score_is_zero` — confirm ALL FAIL before T016

### Implementation — GameBoard and GameSession skeleton

- [x] T016 Implement `GameBoard` dataclass in `snake/game.py`: `width: int`, `height: int`; `all_cells()` returning set of all Positions; no mutable state — T015 partial green

- [x] T017 Implement `GameState` enum in `snake/game.py`: `ACTIVE`, `GAME_OVER`, `WIN`

- [x] T018 Implement `GameSession.__init__` in `snake/game.py`: accepts `GameBoard`; initialises `snake` (3-segment body centered, heading RIGHT), `fruit` (random free cell), `state = GameState.ACTIVE`, `score = 0`, `pending_dir = None`, `_lock = threading.Lock()` — T015 tests go green

**Checkpoint**: `python -m unittest tests/test_game.py` — all Phase 2 tests pass (≥ 17 assertions). `python -m snake` runs and exits immediately (no crash).

---

## Phase 3: User Story 1 — Play a Round of Snake (Priority: P1) 🎯 MVP

**Goal**: A player launches the game, the snake moves continuously, the player
steers with left/right arrows (relative to heading), eats fruit to grow, and
the score updates immediately at the top of the screen.

**Independent Test**: `python -m snake` → snake moves on its own → steer into
fruit → snake grows by 1 segment → score bar reads `Score: 1` → play continues.
See quickstart.md Scenarios 1, 7, 8.

### Tests — Core Tick Logic (write first, confirm failure)

- [x] T019 Write failing tests for `GameSession.tick()` movement in `tests/test_game.py`: `test_tick_moves_snake_forward`, `test_tick_applies_pending_dir_and_clears_it`, `test_tick_discards_reversal_input`, `test_last_key_wins_two_inputs_same_tick` — confirm ALL FAIL before T020

- [x] T020 Write failing tests for fruit collection in `tests/test_game.py`: `test_fruit_eat_grows_snake`, `test_fruit_eat_increments_score_by_one`, `test_new_fruit_not_on_snake_after_eat`, `test_fruit_spawns_in_random_free_cell` — confirm ALL FAIL before T021

### Implementation — Tick and Fruit Logic

- [x] T021 Implement `GameSession.handle_input(key: str)` in `snake/game.py`: acquire lock → compute new direction from current heading + relative turn → discard if 180° reversal (FR-005) → else store in `pending_dir` (last-key-wins, FR-005b) → release lock

- [x] T022 Implement `GameSession.tick()` core movement path in `snake/game.py`: acquire lock → consume `pending_dir` → release lock; compute `new_head = head + direction.delta`; if no collision and no fruit: `snake.move(new_head)` — T019 tests go green

- [x] T023 Implement fruit-collection branch in `GameSession.tick()` in `snake/game.py`: if `new_head == fruit`: `snake.grow(new_head)`, `score += 1`, attempt respawn (`random.choice` of free cells) — T020 tests go green

### Implementation — Input Thread

- [x] T024 [P] Implement `snake/input_handler.py` fully: detect `sys.platform`; POSIX path uses `tty.setraw` + `select.select([sys.stdin], [], [], 0.05)` + multi-byte ESC sequence decode per `contracts/input-contract.md`; Windows path uses `msvcrt.kbhit()` poll + `msvcrt.getch()` + `\xe0` prefix handling; returns canonical `"LEFT"`, `"RIGHT"`, `"QUIT"`, `"RESTART"`, or `None`

- [x] T025 [P] Implement `snake/terminal.py` fully: `check_terminal_size(min_cols, min_rows)` using `shutil.get_terminal_size()`; `enter_raw_mode()` / `exit_raw_mode()` (saves/restores `termios` attrs on POSIX, no-op on Windows); `hide_cursor()` writes `\x1b[?25l` to stdout; `show_cursor()` writes `\x1b[?25h`; `TerminalContext` context manager combining enter/exit/hide/show with `atexit` safety net

### Implementation — Rendering (Score Bar and Board)

- [x] T026 Implement `draw_score_bar(score: int)` in `snake/renderer.py`: writes `\x1b[1;1HScore: {score}   ` (trailing spaces clear old digits) using ANSI cursor positioning; monochrome only (no color codes) per FR-001

- [x] T027 Implement `draw_board(board: GameBoard, snake: Snake, fruit: Position)` in `snake/renderer.py`: builds the full board string in memory (`+--+` top/bottom, `|  |` sides, cells rendered as `O`/`o`/`*`/` `); writes entire frame in one `sys.stdout.write()` call to minimise flicker; uses `\x1b[2;1H` to position at row 2 before writing

### Implementation — Game Loop Entry Point

- [x] T028 Implement the active-state game loop in `snake/__main__.py`: parse args → `check_terminal_size` (exit 1 if too small) → create `GameBoard` + `GameSession` → start input daemon thread (calls `input_handler.get_key()` in a loop, calls `session.handle_input()`, runs as `daemon=True`) → main loop: record `tick_start`, call `session.tick()`, call `renderer.render(session)`, `time.sleep(max(0, TICK_INTERVAL - elapsed))`; handle `KeyboardInterrupt` as clean quit inside `TerminalContext`

**Checkpoint**: `python -m unittest tests/test_game.py` — all Phase 2 + Phase 3 logic tests pass. `python -m snake` — play a complete round: snake moves, turns, eats fruit, score updates. Quickstart Scenarios 1, 7, 8 pass.

---

## Phase 4: User Story 2 — Round End: Collision or Victory (Priority: P2)

**Goal**: Self-collision and wall collision end the game immediately showing
"GAME OVER" + final score; filling the board ends the game showing "YOU WIN!"
+ final score. The correct end screen is displayed 100% of the time.

**Independent Test**: Steer snake into its own body → "GAME OVER" shown with
correct score. Drive snake into wall → "GAME OVER". Fill board in test fixture
→ `state == WIN`. See quickstart.md Scenarios 2, 3, 6.

### Tests — Collision and Win Detection (write first, confirm failure)

- [x] T029 Write failing tests for collision detection in `tests/test_game.py`: `test_self_collision_sets_game_over`, `test_wall_collision_top`, `test_wall_collision_bottom`, `test_wall_collision_left`, `test_wall_collision_right` — confirm ALL FAIL before T030

- [x] T030 Write failing test for win detection in `tests/test_game.py`: `test_win_when_no_free_cells_after_eat` (construct a near-full board fixture, eat last fruit, assert `state == WIN` and fruit is `None`) — confirm FAILS before T031

### Implementation — Collision and Win Detection

- [x] T031 Implement self-collision detection in `GameSession.tick()` in `snake/game.py`: after computing `new_head`, check `new_head in snake.body_cells`; if true: `state = GameState.GAME_OVER`, return early — T029 self-collision tests go green

- [x] T032 Implement wall-collision detection in `GameSession.tick()` in `snake/game.py`: check `new_head.is_out_of_bounds(board.width, board.height)`; if true: `state = GameState.GAME_OVER`, return early — T029 wall-collision tests go green

- [x] T033 Implement win detection in `GameSession.tick()` in `snake/game.py`: inside fruit-collection branch, after `grow` and `score += 1`, compute `free_cells = board.all_cells() - set(snake.body)`; if `len(free_cells) == 0`: `state = GameState.WIN`, `fruit = None`; else: spawn fruit at `random.choice(list(free_cells))` — T030 test goes green

### Implementation — End-Screen Rendering

- [x] T034 Implement `draw_overlay(state: GameState, score: int, board: GameBoard)` in `snake/renderer.py`: if `state == GAME_OVER`: render centered `GAME OVER` + `Final Score: N` + `R = Restart  Q = Quit` lines inside the board border; if `state == WIN`: render centered `YOU WIN!` + same score/prompt lines — visually distinct from each other per FR-012/FR-016

- [x] T035 Wire end-screen rendering into the game loop in `snake/__main__.py`: when `session.state != ACTIVE`, call `renderer.draw_overlay()` instead of `renderer.draw_board()`; pause tick loop and wait for `RESTART` or `QUIT` input only

**Checkpoint**: `python -m unittest tests/test_game.py` — all Phase 2–4 logic tests pass. Play manually: all four collision/win paths produce correct end screens. Quickstart Scenarios 2, 3, 6 pass.

---

## Phase 5: User Story 3 — Start a New Game After Game Over (Priority: P3)

**Goal**: From any end screen (GAME OVER or WIN), pressing R starts a fresh
round with score 0 and a new snake, without relaunching the program. Pressing
Q exits cleanly with terminal restored.

**Independent Test**: Trigger GAME OVER → press R → new game starts (score 0,
fresh snake) → play another round → game over again. Press Q from game-over
screen → shell prompt returns with cursor visible. See quickstart.md Scenarios 4, 5.

### Tests — Reset Logic (write first, confirm failure)

- [x] T036 Write failing tests for `GameSession.reset()` in `tests/test_game.py`: `test_reset_sets_score_to_zero`, `test_reset_sets_state_to_active`, `test_reset_creates_new_snake_at_start_length`, `test_reset_places_new_fruit` — confirm ALL FAIL before T037

### Implementation — Reset and In-Session Restart

- [x] T037 Implement `GameSession.reset()` in `snake/game.py`: re-initialise `snake` to 3-segment starting state, `score = 0`, `state = GameState.ACTIVE`, `pending_dir = None`, place `fruit` at random free cell — T036 tests go green

- [x] T038 Wire `RESTART` key into the end-screen wait loop in `snake/__main__.py`: on `RESTART` key received → call `session.reset()` → resume main tick loop (no process restart, no re-import)

- [x] T039 Ensure `QUIT` key handling exits cleanly from any point in `snake/__main__.py`: `QUIT` during ACTIVE play → break main loop; `QUIT` during end-screen wait → break wait loop; both paths reach the `TerminalContext.__exit__` which restores terminal and shows cursor; process exits with code 0

### Smoke / Integration Tests

- [x] T040 [P] Write and run integration tests in `tests/test_integration.py`: `test_session_ticks_50_times_without_exception` (programmatic tick loop, no terminal); `test_state_transition_active_to_game_over` (drive snake into wall via ticks); `test_reset_after_game_over_returns_to_active` (game over → reset → tick 5 more times, no exception) — all must pass

**Checkpoint**: `python -m unittest discover -s tests -v` — all tests pass (unit + integration). Quickstart Scenarios 4 and 5 pass. Complete session: play → game over → restart → play → quit works without relaunching.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Harden edge cases, validate all quickstart scenarios, and confirm
constitution compliance.

- [x] T041 [P] Verify terminal restoration on abnormal exit in `snake/terminal.py` and `snake/__main__.py`: add `atexit.register(show_cursor)` and `atexit.register(exit_raw_mode)` as a secondary safety net; manually test Ctrl+C mid-game and confirm shell prompt is clean with cursor visible

- [x] T042 [P] Implement minimum terminal size error path in `snake/__main__.py`: if `check_terminal_size()` fails, write `Error: terminal too small. Minimum {min_cols}x{min_rows} required; current terminal is {w}x{h}.` to `stderr` and `sys.exit(1)` before entering raw mode — verify exit code 1 and no raw-mode side effects (Quickstart Scenario 6)

- [x] T043 [P] Add `--help` usage text and controls reminder to `argparse` in `snake/__main__.py`: include controls (Left/Right arrow, Q, R) in the description or epilog so `python -m snake --help` shows them

- [x] T044 Add `try/except Exception` around the main loop body in `snake/__main__.py`: on unexpected error write traceback to `stderr` and exit with code 2; terminal MUST still be restored via `TerminalContext.__exit__`

- [x] T045 Run full quickstart.md validation: execute all 8 scenarios manually; confirm every acceptance criterion in spec.md US1, US2, US3 is satisfied; record any discrepancies and fix before marking complete

**Checkpoint**: All 8 quickstart scenarios pass. `python -m unittest discover -s tests -v` shows OK. Constitution Principles I–V verified: zero third-party imports, runs on at least 2 platforms, single `python -m snake` launch, all logic tests exist and pass, tick rate is consistent.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Requires Phase 1 — **BLOCKS all user story phases**
- **Phase 3 (US1)**: Requires Phase 2 complete
- **Phase 4 (US2)**: Requires Phase 3 complete (collision detection extends `tick()`)
- **Phase 5 (US3)**: Requires Phase 4 complete (reset path wires into end-screen loop)
- **Phase 6 (Polish)**: Requires Phase 5 complete

### Within-Phase Dependencies

**Phase 2**:
`T009 → T012` (Direction impl) → `T013` (Position impl) → `T014` (Snake impl)
→ `T015 → T016` (tests) → `T017` (GameBoard) → `T018` (GameSession init)

**Phase 3**:
`T019 → T020` (tests) → `T021` (handle_input) → `T022` (tick movement)
→ `T023` (fruit branch)
`T024 [P]` and `T025 [P]` can start once Phase 2 is done (different files)
`T026 → T027` (renderer, same file) can start once Phase 2 is done
`T028` (game loop) requires T021–T027

**Phase 4**:
`T029 → T030` (tests) → `T031 → T032 → T033` (collision + win in game.py)
→ `T034 → T035` (overlay rendering + game loop wiring)

**Phase 5**:
`T036` (tests) → `T037` (reset impl) → `T038` (restart wiring) → `T039` (quit wiring)
`T040 [P]` (integration tests) can be written alongside T037–T039

### Parallel Opportunities per Phase

**Phase 1** — once T001 creates the directories, T002–T008 can all run in parallel (7 separate files).

**Phase 3** — once T023 completes:
- `T024` (`input_handler.py`) and `T025` (`terminal.py`) can run in parallel with each other
- `T026`+`T027` (`renderer.py`) can run in parallel with T024/T025
- T028 waits for all of T024, T025, T026, T027

**Phase 5** — `T040` (integration tests in `test_integration.py`) can be written and run in parallel with T037–T039 (different files).

**Phase 6** — T041, T042, T043 all touch different concerns; T041 (`terminal.py`) and T042/T043 (`__main__.py`) can be parallelised; T044 follows T042.

---

## Parallel Example: Phase 3 (US1)

```
After T023 completes:

  Parallel track A:  T024 — implement snake/input_handler.py
  Parallel track B:  T025 — implement snake/terminal.py
  Parallel track C:  T026 → T027 — implement snake/renderer.py

  All three tracks merge at:
  T028 — wire game loop in snake/__main__.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 — Setup
2. Complete Phase 2 — Foundational (CRITICAL, blocks everything)
3. Complete Phase 3 — US1 (core gameplay loop)
4. **STOP & VALIDATE**: `python -m snake` runs a full playable game
5. Quickstart Scenarios 1, 7, 8 pass → MVP is shippable

### Incremental Delivery

1. Phase 1 + 2 → skeleton + primitives ready
2. Phase 3 → working game loop, turning, scoring (MVP ✅)
3. Phase 4 → collision detection, game-over / win screens
4. Phase 5 → restart / quit, complete session lifecycle
5. Phase 6 → polish and constitution audit

---

## Notes

- `[P]` = different files, no incomplete-task dependencies — can run concurrently
- `[US#]` = traceability to user story in `spec.md`
- Constitution Principle IV is NON-NEGOTIABLE: every implementation task that
  touches `game.py` must have a corresponding test task preceding it, and those
  tests MUST fail before implementation starts
- Commit after each phase checkpoint at minimum; commit after each task
  group where practical
- `renderer.py` and `input_handler.py` are not unit-tested (terminal I/O) —
  they are verified via manual quickstart scenarios
- `test_integration.py` tests drive `GameSession` with no terminal — they are
  the smoke tests for wiring correctness

---

## Phase 7: Convergence

- [x] T046 Handle terminal resize during active gameplay in `snake/terminal.py` and `snake/__main__.py`: on POSIX register a `signal.SIGWINCH` handler that sets a shared flag; in the main game loop check the flag each tick and call `check_terminal_size()` — if now too small, write the standard "terminal too small" error to stderr, restore terminal, and exit with code 1; on Windows poll `shutil.get_terminal_size()` once per tick for the same check per research.md Decision 6, spec edge case "terminal resized during gameplay", Constitution II (partial)

- [x] T047 Remove dead variable `body_set` on line 25 of `snake/renderer.py` — it is assigned (`set(snake.body)`) but never read; `body_cells` (line 26) is the variable actually used in the render loop; delete the assignment and its comment (unrequested)
