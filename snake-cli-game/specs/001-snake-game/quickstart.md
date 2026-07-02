# Quickstart & Validation Guide: Classic Terminal Snake Game

**Feature**: 001-snake-game
**Created**: 2026-07-01

---

## Prerequisites

- Python 3.8 or later (`python3 --version`)
- A terminal emulator with ANSI escape code support:
  - Linux/macOS: any standard terminal (gnome-terminal, iTerm2, Terminal.app, etc.)
  - Windows: Windows Terminal, PowerShell, or cmd on Windows 10+ (build 14931+)
- Terminal size: at least 24 columns × 24 rows for the default board

---

## Running the Game

```bash
# Clone the repo (once)
git clone <repo-url>
cd snake-cli-game

# Run with default board (20×20, 5 ticks/sec)
python -m snake

# Custom board size
python -m snake --width 30 --height 20

# Slower speed (5 ticks/sec)
python -m snake --speed 5
```

---

## Controls

| Key | Action |
|-----|--------|
| Left arrow  | Turn left relative to snake's heading |
| Right arrow | Turn right relative to snake's heading |
| Q           | Quit at any time |
| R           | Restart after game over or win |

---

## Validation Scenarios

Use these scenarios to verify the game works end-to-end after implementation.
Each maps directly to a user story in `spec.md`.

### Scenario 1 — Core Gameplay Loop (US1, P1)

**Goal**: Confirm continuous movement, relative turning, fruit collection, and live score.

1. Launch: `python -m snake`
2. Observe: snake starts moving right without any key press. ✓
3. Press Left arrow: snake turns upward (relative turn, not absolute). ✓
4. Press Right arrow: snake turns right (relative to new heading). ✓
5. Steer the snake into the `*` fruit.
6. Observe: snake grows by one segment, score at top increases by 1. ✓
7. Observe: a new `*` appears immediately in a different empty cell. ✓

Expected display after eating one fruit:
```
Score: 1
+--------------------+
|                    |
|  *                 |
|      oooO          |
|                    |
+--------------------+
```

---

### Scenario 2 — Self-Collision Game Over (US2, P2)

**Goal**: Confirm self-collision ends the game and shows the correct screen.

1. Launch: `python -m snake --speed 3` (slow speed for easier control)
2. Let the snake grow to at least 5 segments.
3. Steer the snake into its own body.
4. Observe: game stops immediately. ✓
5. Observe: "GAME OVER" and "Final Score: N" displayed. ✓
6. Observe: score bar still shows correct score. ✓

---

### Scenario 3 — Wall Collision Game Over (US2, P2)

**Goal**: Confirm wall collision ends the game.

1. Launch: `python -m snake --speed 5`
2. Do nothing — let the snake drive into the right wall.
3. Observe: "GAME OVER" displayed once the head hits the border. ✓

---

### Scenario 4 — Restart After Game Over (US3, P3)

**Goal**: Confirm restart works without relaunching.

1. Trigger a game over (see Scenario 2 or 3).
2. On the GAME OVER screen, press R.
3. Observe: new game starts with score 0, snake back to starting state. ✓
4. Observe: no relaunch of `python -m snake` was needed. ✓

---

### Scenario 5 — Quit

**Goal**: Confirm terminal is restored on exit.

1. During active play, press Q.
2. Observe: program exits, cursor is visible, terminal input/echo is restored. ✓
3. Verify exit code: `echo $?` (Linux/macOS) → should print `0`. ✓

---

### Scenario 6 — Terminal Too Small

**Goal**: Confirm graceful failure when terminal is too small.

1. Resize terminal to 10 columns × 5 rows.
2. Run: `python -m snake`
3. Observe: error message on stderr, program exits with code 1. ✓
4. Observe: terminal is not left in raw mode. ✓

---

### Scenario 7 — Input Timing (Last-Key-Wins)

**Goal**: Confirm rapid key presses don't queue up unexpectedly.

1. Launch: `python -m snake --speed 3`
2. Press Left then immediately Right (both before next tick).
3. Observe: only the Right turn takes effect on the next move. ✓

---

### Scenario 8 — 180° Reversal Suppression

**Goal**: Confirm the snake cannot instantly reverse.

1. Launch: `python -m snake --speed 3`
2. Snake starts heading right; press Left twice rapidly.
3. Observe: snake turns up (first Left), then left (second Left — relative
   turn from UP → LEFT). It does NOT reverse directly back on itself. ✓

*Note*: A single Left press from heading RIGHT turns the snake UP, which is
valid. Two rapid Left presses should result in UP then LEFT, not a reversal.

---

## Running Automated Tests

```bash
# Run all unit tests (game logic only — no terminal required)
python -m unittest discover -s tests -p "test_*.py" -v

# Expected output:
# test_collision_self ... ok
# test_collision_wall ... ok
# test_direction_turn_left ... ok
# test_direction_turn_right ... ok
# test_direction_reversal_suppressed ... ok
# test_fruit_eat_grow_score ... ok
# test_fruit_respawn_random ... ok
# test_win_board_full ... ok
# test_game_over_resets_on_restart ... ok
# ...
# Ran N tests in 0.00Xs
# OK
```

---

## Reference

- Data model: [data-model.md](data-model.md)
- CLI contract: [contracts/cli-contract.md](contracts/cli-contract.md)
- Input contract: [contracts/input-contract.md](contracts/input-contract.md)
- Specification: [spec.md](spec.md)
