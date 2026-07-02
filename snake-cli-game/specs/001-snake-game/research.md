# Research: Classic Terminal Snake Game

**Feature**: 001-snake-game
**Phase**: 0 — Technical Decisions
**Created**: 2026-07-01

---

## Decision 1: Implementation Language

**Decision**: Python 3.8+, standard library only.

**Rationale**:
- Python ships `tty`, `termios`, `select` (POSIX) and `msvcrt` (Windows) in
  its standard library, covering all three target platforms without external
  packages. No other major language offers equivalent stdlib cross-platform
  terminal I/O without a third-party crate/module.
- Python's `unittest` module provides a full test framework in stdlib, keeping
  Constitution Principle I satisfied end-to-end.
- Python 3.8+ is present on virtually every modern macOS and Linux install;
  Windows users install it from python.org with no additional setup.
- `collections.deque` (stdlib) is the ideal data structure for the snake body
  (O(1) head prepend and tail pop).

**Alternatives considered**:
- **Go**: `golang.org/x/term` is external; stdlib terminal control is thin.
- **Rust**: `crossterm`/`termion` are external crates.
- **C**: portable curses requires `ncurses` (external on many platforms).
- **Node.js**: `readline` is stdlib but ANSI raw mode requires platform-specific
  workarounds; test tooling (Jest) is external.

---

## Decision 2: Terminal Rendering Strategy

**Decision**: ANSI escape codes written directly to `sys.stdout`.

| Code | Purpose |
|------|---------|
| `\x1b[2J` | Clear entire screen |
| `\x1b[H` | Move cursor to top-left (home) |
| `\x1b[?25l` | Hide cursor during play |
| `\x1b[?25h` | Restore cursor on exit or game-over |
| `\x1b[{r};{c}H` | Move cursor to specific row, column (1-indexed) |

**Rationale**: ANSI sequences have been natively supported in Windows 10+
(build 14931+) cmd and PowerShell without any package. Writing full frames
to stdout via `\x1b[H` + full-screen redraw avoids flicker better than
line-by-line updates and keeps rendering logic simple to test.

**Alternative considered**: `curses` module — available on POSIX but absent
from Windows stdlib without `windows-curses` (a third-party package), ruling
it out under Constitution Principle I.

---

## Decision 3: Keyboard Input Handling

**Decision**: Daemon input thread + `threading.Lock`-protected shared variable.

### POSIX (Linux / macOS)

Modules: `tty`, `termios`, `select`, `sys`

1. Save original terminal attributes via `termios.tcgetattr(sys.stdin)`.
2. Set raw mode via `tty.setraw(sys.stdin.fileno())` — disables line buffering
   and echo.
3. In the input daemon thread, use `select.select([sys.stdin], [], [], 0.05)`
   to poll for input with a 50ms timeout (well under one tick).
4. On input available, read 1–3 bytes (arrow keys arrive as multi-byte ESC
   sequences).
5. On exit / game-over, restore attributes via `termios.tcsetattr(...)`.

**Arrow key encoding (POSIX)**:

| Key   | Byte sequence |
|-------|---------------|
| Up    | `\x1b[A`      |
| Down  | `\x1b[B`      |
| Right | `\x1b[C`      |
| Left  | `\x1b[D`      |

### Windows

Module: `msvcrt`

1. In the input daemon thread, loop calling `msvcrt.kbhit()` with a short
   `time.sleep(0.01)` between polls.
2. When `kbhit()` returns `True`, call `msvcrt.getch()`.
3. If the returned byte is `b'\xe0'` (extended key prefix), call `getch()`
   again for the direction byte.

**Arrow key encoding (Windows msvcrt)**:

| Key   | First byte | Second byte |
|-------|------------|-------------|
| Up    | `\xe0`     | `H`         |
| Down  | `\xe0`     | `P`         |
| Right | `\xe0`     | `M`         |
| Left  | `\xe0`     | `K`         |

### Shared State (last-key-wins)

The input thread writes to a single `pending_dir` field protected by a
`threading.Lock`. The game tick reads and clears `pending_dir` under the
same lock. This naturally implements the last-key-wins requirement (FR-005b):
each write overwrites any previously stored un-consumed key from the same
tick interval.

---

## Decision 4: Game Loop Architecture

**Decision**: Tick-based main loop with a daemon input thread.

```
Main thread:
  loop:
    tick_start = time.monotonic()
    acquire lock → read and clear pending_dir → release lock
    apply direction to game state
    advance snake, check collisions, update score
    render full frame to stdout
    elapsed = time.monotonic() - tick_start
    time.sleep(max(0, TICK_INTERVAL - elapsed))

Daemon input thread (started once, lives for process lifetime):
  loop:
    poll for keypress (with timeout ≤ TICK_INTERVAL / 4)
    if keypress:
      acquire lock → write pending_dir → release lock
```

**Tick interval**: `TICK_INTERVAL = 0.20` seconds (5 ticks/second, default).
Configurable via `--speed` (1–30). No busy-waiting: the main thread sleeps the
remainder of each tick interval.

**Rationale**: Simpler and more predictable than async event loops; `threading`
is stdlib; daemon thread dies automatically when main thread exits.

---

## Decision 5: Project Layout

**Decision**: Single Python package `snake/` runnable as `python -m snake`.

```
snake/
├── __main__.py       # Entry point: parses optional CLI args, starts game
├── game.py           # Pure game logic — GameSession, Snake, GameState, etc.
├── renderer.py       # ANSI rendering: draws board, score bar, overlays
├── input_handler.py  # Platform-specific input: abstracts POSIX vs. Windows
└── terminal.py       # Terminal setup/teardown: raw mode, cursor, resize check

tests/
├── test_game.py      # Unit tests for all pure game logic (Constitution IV)
└── test_integration.py  # Smoke test: start session, tick N times, exit cleanly
```

**Rationale**: Keeping game logic in `game.py` as pure functions (no I/O)
means it is fully unit-testable without any terminal. Renderer, input handler,
and terminal management are thin I/O wrappers that only need smoke testing.

---

## Decision 6: Minimum Terminal Size

**Decision**: Minimum 24 columns × 12 rows for the smallest supported board
(10 wide × 8 tall + 2 border + 1 score line + 1 margin).
Default board: 20 wide × 20 tall (requires ≥ 24 columns × 24 rows).

On launch and on terminal resize signal (`SIGWINCH` on POSIX; polling on
Windows), check `shutil.get_terminal_size()`. If below minimum, print an
error to stderr and exit with code 1 (Constitution Technology Constraints).

---

## Decision 7: Testing Strategy

**Decision**: `unittest` (stdlib) for all automated tests. Tests written
before implementation (Constitution Principle IV — NON-NEGOTIABLE).

Test targets:
- **Pure game logic** (`test_game.py`): All functions in `game.py` —
  direction turning table, 180° reversal detection, movement, growth,
  self-collision, wall collision, win condition, score increment, fruit
  respawn, board-full detection.
- **Smoke / integration** (`test_integration.py`): Construct a `GameSession`,
  drive it through multiple ticks programmatically (no terminal), verify state
  transitions.

**Not unit-tested** (impractical without a real terminal):
- `renderer.py` — verified via visual inspection during development + manual
  smoke test documented in `quickstart.md`.
- `input_handler.py` — platform-specific; verified in smoke test.
