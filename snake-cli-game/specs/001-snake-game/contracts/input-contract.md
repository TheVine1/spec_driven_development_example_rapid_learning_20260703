# Input Contract: Classic Terminal Snake Game

**Feature**: 001-snake-game
**Created**: 2026-07-01

---

## Key Bindings

### During ACTIVE gameplay

| Key | Action | Notes |
|-----|--------|-------|
| Up arrow    | Move snake upward on screen          | Discarded if snake is heading DOWN (reversal; FR-005) |
| Down arrow  | Move snake downward on screen        | Discarded if snake is heading UP (reversal; FR-005) |
| Left arrow  | Move snake leftward on screen        | Discarded if snake is heading RIGHT (reversal; FR-005) |
| Right arrow | Move snake rightward on screen       | Discarded if snake is heading LEFT (reversal; FR-005) |
| Q / q       | Quit program immediately             | Terminal restored before exit |
| Ctrl+C      | Quit program immediately             | Treated as quit; terminal restored |

All other keys are silently ignored during ACTIVE state.

### On GAME OVER or WIN screen

| Key | Action |
|-----|--------|
| R / r | Start a new game (score resets to 0) |
| Q / q | Quit program cleanly (exit code 0) |
| Ctrl+C | Quit program (exit code 0) |

All other keys are silently ignored on end screens.

---

## Input Timing Rules

- **Last-key-wins (FR-005b)**: If multiple direction keys arrive between two
  consecutive ticks, only the last received key is applied; earlier keys from
  the same inter-tick interval are discarded.
- **180° reversal suppression (FR-005)**: A direction key that would reverse
  the snake onto its immediately trailing segment is silently discarded; the
  snake continues in its current heading.
- **Non-direction keys (Q, Ctrl+C)**: Processed immediately on receipt,
  bypassing the tick cycle.

---

## Absolute Direction Mapping

Each arrow key maps directly to a fixed screen direction regardless of the
snake's current heading:

| Arrow key | Canonical name | Screen direction |
|-----------|---------------|-----------------|
| Up        | `"UP"`        | Toward row 0 (top of board) |
| Down      | `"DOWN"`      | Toward row height−1 (bottom) |
| Left      | `"LEFT"`      | Toward col 0 (left edge) |
| Right     | `"RIGHT"`     | Toward col width−1 (right edge) |

**Reversal pairs (silently discarded at input time):**
- Heading UP   + DOWN input → discard
- Heading DOWN + UP input   → discard
- Heading LEFT + RIGHT input → discard
- Heading RIGHT + LEFT input → discard

---

## Platform-Specific Key Encoding

### POSIX (Linux / macOS)

Arrow keys arrive as 3-byte ESC sequences from `sys.stdin` in raw mode:

| Key   | Bytes (hex)         | Bytes (repr)   |
|-------|---------------------|----------------|
| Up    | `1B 5B 41`          | `\x1b[A`       |
| Down  | `1B 5B 42`          | `\x1b[B`       |
| Right | `1B 5B 43`          | `\x1b[C`       |
| Left  | `1B 5B 44`          | `\x1b[D`       |

Reading strategy: call `select.select` with a short timeout; if stdin is
readable, read 1 byte; if it is `\x1b`, read 2 more bytes (with a very short
second timeout to distinguish a bare ESC from an arrow sequence).

### Windows

Arrow keys arrive as two sequential `msvcrt.getch()` calls:

| Key   | First call | Second call |
|-------|------------|-------------|
| Up    | `b'\xe0'`  | `b'H'`      |
| Down  | `b'\xe0'`  | `b'P'`      |
| Right | `b'\xe0'`  | `b'M'`      |
| Left  | `b'\xe0'`  | `b'K'`      |

Q key: `b'q'` or `b'Q'`
R key: `b'r'` or `b'R'`
Ctrl+C: raises `KeyboardInterrupt` (Python handles this automatically).

---

## Input Abstraction Contract

The `input_handler` module MUST expose a single platform-agnostic interface:

```
get_key() -> str | None
```

Returns one of the canonical key names below, or `None` if no key was
pressed within the polling window:

| Canonical name | Meaning |
|---------------|---------|
| `"UP"`        | Up arrow key |
| `"DOWN"`      | Down arrow key |
| `"LEFT"`      | Left arrow key |
| `"RIGHT"`     | Right arrow key |
| `"QUIT"`      | Q, q, or Ctrl+C |
| `"RESTART"`   | R or r |
| `None`        | No input in polling window |

The caller (game loop) MUST NOT depend on platform-specific byte values.
