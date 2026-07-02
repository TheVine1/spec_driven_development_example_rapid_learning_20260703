# CLI Contract: Classic Terminal Snake Game

**Feature**: 001-snake-game
**Created**: 2026-07-01

---

## Invocation

```
python -m snake [--width W] [--height H] [--speed S]
```

All arguments are optional. The game runs interactively; it does not read
from stdin pipes and does not produce machine-readable stdout output.

### Arguments

| Argument | Type | Default | Constraints | Description |
|----------|------|---------|-------------|-------------|
| `--width W` | int | 20 | 10 ≤ W ≤ terminal_cols − 2 | Board width in cells |
| `--height H` | int | 20 | 8 ≤ H ≤ terminal_rows − 3 | Board height in cells |
| `--speed S` | int | 5  | 1 ≤ S ≤ 30 | Ticks per second |

### Exit Codes

| Code | Condition |
|------|-----------|
| 0 | Player chose to quit cleanly (Q key) |
| 1 | Terminal too small to render the board; message written to stderr |
| 2 | Unexpected runtime error; traceback written to stderr |

---

## Terminal Requirements

- **Minimum columns**: `board.width + 4` (2 border + 2 padding)
- **Minimum rows**: `board.height + 4` (2 border + 1 score line + 1 margin)
- **Minimum absolute**: 24 columns × 12 rows for smallest allowed board
- **Default board**: requires ≥ 24 columns × 24 rows
- **Color support**: not required; game is monochrome only
- **Mouse support**: not required; game uses keyboard only

If the terminal is smaller than the minimum, the game MUST print to stderr:

```
Error: terminal too small. Minimum NNxNN required; current terminal is NNxNN.
```

and exit with code 1 without entering raw mode.

---

## Screen Layout

```
Score: 42
+--------------------+
|                    |
|       *            |
|    oooO            |
|                    |
+--------------------+
```

**Row 0 (score bar)**: `Score: {N}` — always visible during ACTIVE state.

**Rows 1..height+2**: game board with border and content:
- `+` — board corner
- `-` — top/bottom border
- `|` — left/right border
- `O` — snake head (capital O)
- `o` — snake body segment (lowercase o)
- `*` — fruit
- ` ` (space) — empty cell

---

## Game-Over Overlay

Replaces board content when `state == GAME_OVER`:

```
+--------------------+
|                    |
|     GAME OVER      |
|   Final Score: 42  |
|                    |
| R = Restart        |
| Q = Quit           |
|                    |
+--------------------+
```

- Score bar row is retained: `Score: 42`
- Overlay text is centered horizontally within the board area
- All other cells are blank

---

## Win Overlay

Replaces board content when `state == WIN`:

```
+--------------------+
|                    |
|     YOU WIN!       |
|   Final Score: 42  |
|                    |
| R = Restart        |
| Q = Quit           |
|                    |
+--------------------+
```

- Visually distinct from GAME OVER; "YOU WIN!" is the indicator text
- Same restart/quit prompt as game-over

---

## Terminal State Contract

The program MUST:
- Hide the cursor on entry to gameplay (`\x1b[?25l`) and restore it on exit
  (`\x1b[?25h`).
- Restore the terminal to its original mode (cooked, echo) on any exit path —
  clean quit, error, or interrupt (`KeyboardInterrupt` / SIGINT).
- Clear the screen and move the cursor to row 0, col 0 on startup.
- Not leave the terminal in raw mode if the process is killed.
