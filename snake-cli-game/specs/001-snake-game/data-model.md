# Data Model: Classic Terminal Snake Game

**Feature**: 001-snake-game
**Created**: 2026-07-01
**Source**: spec.md + clarifications session 2026-07-01

---

## Entities

### Position

An immutable 2-tuple representing a single cell on the game board.

| Field | Type | Constraints |
|-------|------|-------------|
| row   | int  | 0 ≤ row < board.height |
| col   | int  | 0 ≤ col < board.width  |

Represented as a `NamedTuple` or plain `(row, col)` tuple. Immutable.
Two Positions are equal iff both row and col match.

---

### Direction

An enumeration of the four possible headings the snake can travel.

| Value | Meaning               | Row delta | Col delta |
|-------|-----------------------|-----------|-----------|
| UP    | Toward row 0          | −1        | 0         |
| DOWN  | Toward row height−1   | +1        | 0         |
| LEFT  | Toward col 0          | 0         | −1        |
| RIGHT | Toward col width−1    | 0         | +1        |

**Absolute key mapping** (FR-004): each arrow key maps directly to a screen direction.

| Arrow key pressed | New heading |
|-------------------|-------------|
| UP                | UP          |
| DOWN              | DOWN        |
| LEFT              | LEFT        |
| RIGHT             | RIGHT       |

**Reversal detection** (FR-005): an input is a 180° reversal iff the requested
direction is the exact opposite of the current heading (`{UP↔DOWN, LEFT↔RIGHT}`).
Such inputs are silently discarded at input-handling time.

---

### Snake

The player-controlled entity. Modelled as an ordered sequence of Positions.

| Field     | Type                     | Invariant |
|-----------|--------------------------|-----------|
| body      | `deque[Position]`        | `len(body) ≥ 1` at all times; `body[0]` is the head |
| direction | Direction                | Current heading; any absolute direction except the exact reverse is valid |

**Operations:**

- `move(new_head: Position)` — prepend new_head to body, remove tail (`popleft` / `append` + `pop`)
- `grow(new_head: Position)` — prepend new_head, tail is retained (length increases by 1)
- `head → body[0]`
- `body_cells → set(body[1:])` — cells occupied by the body excluding head (used for collision check)

**Initial state**: length 3, centered on board, heading RIGHT.

---

### Fruit

A single collectible cell. Has exactly one attribute.

| Field    | Type     | Constraints |
|----------|----------|-------------|
| position | Position | Must be in an unoccupied cell (not in snake.body) at all times |

Exactly one Fruit exists during ACTIVE state. Spawned at a uniformly random
unoccupied cell after collection (FR-007). If zero unoccupied cells exist,
the win condition is triggered instead (FR-016).

---

### GameBoard

Defines the bounded play area. Immutable per game session.

| Field  | Type | Constraints | Default |
|--------|------|-------------|---------|
| width  | int  | ≥ 10        | 20      |
| height | int  | ≥ 8         | 20      |

**Boundary collision** (FR-011): a Position is out-of-bounds iff
`row < 0 or row ≥ height or col < 0 or col ≥ width`.

**Minimum terminal size** (Constitution II / Technology Constraints):
- Required terminal columns ≥ `board.width + 2` (borders) + 0 padding
- Required terminal rows ≥ `board.height + 2` (borders) + 1 (score line) + 1 (margin)
- Minimum absolute terminal: 22 columns × 24 rows for default 20×20 board

---

### Score

A non-negative integer, incremented by exactly 1 each time the snake eats
a fruit (FR-007). Resets to 0 at the start of every new game (FR-014).

| Field | Type | Constraints |
|-------|------|-------------|
| value | int  | ≥ 0; starts at 0 per game |

---

### GameState

An enumeration representing the current phase of a game round.

| Value     | Description |
|-----------|-------------|
| ACTIVE    | Game is running; snake moves each tick |
| GAME_OVER | Round ended by self-collision or wall collision |
| WIN       | Round ended by board-full condition |

Transitions:
```
ACTIVE → GAME_OVER  (self-collision or wall-collision detected)
ACTIVE → WIN        (fruit eaten and zero free cells remain for respawn)
GAME_OVER → ACTIVE  (player chooses restart)
WIN       → ACTIVE  (player chooses restart)
```

---

### GameSession

The top-level container for a single round's mutable state.

| Field       | Type       | Description |
|-------------|------------|-------------|
| board       | GameBoard  | Immutable play area dimensions |
| snake       | Snake      | Current snake state |
| fruit       | Position   | Current fruit location |
| state       | GameState  | Current phase |
| score       | Score      | Points accumulated this round |
| pending_dir | Direction \| None | Latest unprocessed turn input (last-key-wins; FR-005b) |

**Tick operation** (drives all game logic):
1. Resolve `pending_dir` into next direction (apply relative turn; discard 180° reversals; clear `pending_dir`)
2. Compute `new_head = snake.head + direction.delta`
3. Check wall collision → GAME_OVER if out-of-bounds
4. Check self-collision → GAME_OVER if `new_head in snake.body_cells`
5. Check fruit collision:
   - If yes: `snake.grow(new_head)`, `score += 1`, attempt fruit respawn
     - If free cells exist: place fruit at random free cell
     - If no free cells: state → WIN
   - If no: `snake.move(new_head)`
6. Update `state` accordingly

---

## Relationships

```
GameSession
├── board: GameBoard          (1:1, immutable for session lifetime)
├── snake: Snake              (1:1, mutable each tick)
│   └── body: deque[Position] (ordered, head-first)
├── fruit: Position           (1:1, changes on each eat)
├── state: GameState          (1:1, transitions on events)
├── score: int                (1:1, monotonically increasing within round)
└── pending_dir: Direction?   (1:1, consumed each tick)
```

---

## Derived / Computed Values

| Value | Derived From | Used For |
|-------|-------------|----------|
| `snake.head` | `snake.body[0]` | Collision detection, movement |
| `snake.body_cells` | `set(snake.body[1:])` | Self-collision check |
| `free_cells` | All board positions minus `set(snake.body)` minus `{fruit}` | Fruit respawn |
| `occupied_count` | `len(snake.body)` | Board-full win check |

---

## State Validation Rules

- `snake.body` MUST have no duplicate Positions (no self-overlap at start; enforced by collision detection during play).
- `fruit.position` MUST NOT be in `snake.body` at the start of each tick.
- `score.value` MUST equal `len(snake.body) - initial_snake_length` at all times during ACTIVE state.
- `pending_dir` MUST be consumed (set to None) on each tick, regardless of whether it was valid.
