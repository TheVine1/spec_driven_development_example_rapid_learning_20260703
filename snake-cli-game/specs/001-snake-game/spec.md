# Feature Specification: Classic Terminal Snake Game

**Feature Branch**: `001-snake-game`

**Created**: 2026-06-30

**Status**: Active

**Input**: User description: "Build a CLI-based Snake game for the terminal. The game should follow standard Snake gameplay rules: the snake moves continuously, eating a fruit increases its length by one unit, and colliding with its own body ends the game. The current score should be displayed at the top of the screen and updated in real time as fruits are collected. The visual presentation should be simple and monochrome, using only black and white. The snake should be controlled using the arrow keys (only turning left and right) and the turning of the snake head is to be relative to its heading. The gameplay should feel responsive and visually clear in a terminal environment. Include expected handling for game-over state and score display throughout the session."

## Clarifications

### Session 2026-07-01

- Q: Are arrow-key controls relative to the snake's current heading (not fixed screen directions)? → A: **Revised 2026-07-02**: No. All four arrow keys map to absolute screen directions (UP arrow = move up the screen, DOWN = move down, LEFT = move left, RIGHT = move right), regardless of the snake's current heading.
- Q: Can the player instantly reverse the snake's direction? → A: No. Any input that would reverse the snake onto the segment immediately behind its head (i.e., the arrow key pointing directly opposite to the current heading) is silently discarded; the snake continues in its current heading.
- Q: What are the end conditions for a round? → A: Exactly two — self-collision (head enters a cell occupied by any body segment) and wall collision (head moves past the outer board boundary). Both end the game immediately.
- Q: How does fruit respawning work? → A: A new fruit is placed at a uniformly random position among all currently unoccupied cells on the board.
- Q: By how much does the score increase per fruit? → A: Exactly 1 point per fruit eaten; score starts at 0 when each game begins.
- Q: What options does the player have after game over? → A: Exactly two — restart (new game, score resets to 0) or quit (program exits cleanly). No other post-game-over options are presented.
- Q: What is the visual style requirement? → A: Strictly monochrome (black and white only); all game elements must be individually legible in a standard terminal without colour, contrast aids, or graphical glyphs beyond basic ASCII/Unicode box characters.
- Q: When multiple direction keys are pressed within the same tick, which takes effect? → A: Last key wins — only the most recently pressed valid key (non-reversal) before the tick fires is applied; earlier keys within the same tick are discarded.
- Q: If the snake fills the entire board with no free cell left for fruit respawn, what happens? → A: Win state — the game ends immediately as a victory; the screen shows the final score alongside a distinct "You Win" indication rather than "Game Over".

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Play a Round of Snake (Priority: P1)

A player launches the game in their terminal and controls a continuously moving
snake, steering it left or right relative to its current heading to guide it
toward fruit. Each fruit eaten grows the snake and increases the score, which is
visible at all times.

**Why this priority**: This is the core gameplay loop. Without continuous
movement, turning, growth, and live scoring, there is no game.

**Independent Test**: Launch the game, use the left/right arrow keys to steer
the snake into a fruit, and confirm the snake grows by one segment and the
on-screen score increases immediately.

**Acceptance Scenarios**:

1. **Given** the game has just started, **When** no key is pressed, **Then**
   the snake keeps moving forward in its current heading without stopping.
2. **Given** the snake is moving, **When** the player presses any arrow key,
   **Then** the snake's head moves in the corresponding absolute screen
   direction (UP arrow = upward on screen, DOWN = downward, LEFT = leftward,
   RIGHT = rightward), provided it is not the direct reverse of the current
   heading.
3. **Given** the snake's head reaches the same position as the fruit, **When**
   the next move completes, **Then** the snake's length increases by one
   segment, the score increases, and a new fruit appears at a different open
   position on the board.
4. **Given** the score has just increased, **When** the screen next redraws,
   **Then** the updated score is visible at the top of the screen with no
   noticeable delay.

---

### User Story 2 - Round End: Collision or Victory (Priority: P2)

While playing, the player either collides with their own body or a wall
(game over), or fills the entire board (win). In both cases the game ends
immediately, clearly communicates the outcome, and shows the final score.

**Why this priority**: Defining clear end conditions is essential to
"standard Snake gameplay rules" and gives every round a definitive outcome.

**Independent Test**: Deliberately steer the snake into its own body and
confirm a game-over indication is shown with the final score; separately,
fill the board in a test fixture and confirm a "You Win" screen is shown.

**Acceptance Scenarios**:

1. **Given** the snake is moving, **When** its head moves into a cell occupied
   by any other segment of its own body, **Then** the game ends immediately.
2. **Given** the snake is moving, **When** its head moves past the outer edge
   of the game board, **Then** the game ends immediately, the same as a
   self-collision.
3. **Given** the game has just ended, **When** the end-of-game screen is shown,
   **Then** it clearly states the game is over and displays the final score.
4. **Given** the game has ended, **When** the player takes no further action,
   **Then** the snake stops moving and the board no longer updates.
5. **Given** the snake's head would move onto the fruit's cell and no other
   unoccupied cell exists on the board, **When** that move completes, **Then**
   the game ends immediately as a win state displaying "You Win" and the
   final score, not "Game Over".

---

### User Story 3 - Start a New Game After Game Over (Priority: P3)

After a game ends, the player starts a fresh round without having to relaunch
the program, so they can keep playing across multiple rounds in one sitting.

**Why this priority**: Improves session continuity and replayability, but the
game is still fully playable and testable without it (P1 and P2 deliver a
complete single-round experience).

**Independent Test**: From the game-over screen, trigger a restart action and
confirm a new round begins with the snake, board, and score reset to their
starting state.

**Acceptance Scenarios**:

1. **Given** the game-over screen is displayed, **When** the player performs
   the documented restart action, **Then** a new game begins with a freshly
   reset snake, board, and a score of zero.
2. **Given** the game-over screen is displayed, **When** the player performs
   the documented exit action, **Then** the program closes without error.

---

### Edge Cases

- If the snake fills the board entirely (zero unoccupied cells), the game
  ends immediately as a win state: score and "You Win" are displayed instead
  of "Game Over". The player then has the same restart or quit options.
- When multiple direction keys are pressed within the same tick, only the
  last valid (non-reversal) key received before the tick fires takes effect;
  all earlier keys within that tick are silently discarded.
- What happens if the terminal window is resized while a game is in progress?
- What happens if the player launches the game in a terminal smaller than the
  minimum supported board size?
- What happens if the player holds a direction key down continuously rather
  than pressing it once?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST render the game board and all gameplay elements
  using only monochrome (black and white) text/character-based visuals.
- **FR-002**: System MUST display the snake as a visually distinct, continuous
  chain of segments on the game board.
- **FR-003**: The snake MUST move continuously in its current heading at a
  regular interval, without requiring repeated player input to keep moving.
- **FR-004**: System MUST let the player change the snake's heading using all
  four arrow keys, where each key maps to the corresponding absolute screen
  direction: UP arrow = upward, DOWN arrow = downward, LEFT arrow = leftward,
  RIGHT arrow = rightward. The control scheme is absolute, not relative to the
  snake's current heading.
- **FR-005**: System MUST silently discard any direction input that would
  reverse the snake directly onto the segment immediately behind its head;
  the snake MUST continue in its current heading as if no key was pressed.
- **FR-005b**: When multiple direction keys are received within a single game
  tick, system MUST apply only the last valid (non-reversal) key received
  before the tick fires; earlier keys from that tick are discarded (last-valid-key-wins).
- **FR-006**: System MUST display exactly one fruit on the board at any time
  during active gameplay.
- **FR-007**: When the snake's head moves onto the fruit's position, system
  MUST increase the snake's length by exactly one segment, increase the
  score by exactly 1 point, and place a new fruit at a uniformly random
  open (unoccupied) cell on the board.
- **FR-008**: System MUST display the player's current score at the top of
  the screen at all times during active gameplay.
- **FR-009**: System MUST update the displayed score in the same visual
  update in which the fruit is eaten, with no perceptible delay.
- **FR-010**: System MUST end the current game immediately when the snake's
  head moves into a cell occupied by any other segment of its own body.
- **FR-011**: System MUST end the current game immediately when the snake's
  head reaches the outer boundary of the game board, treating it as a
  game-ending collision equivalent to a self-collision (no wrap-around).
- **FR-012**: Upon game over, system MUST clearly indicate that the game has
  ended and display the final score achieved in that round.
- **FR-013**: System MUST keep the final score visible on screen after game
  over until the player takes an explicit restart or exit action.
- **FR-014**: After any round ends (game over or win), system MUST offer
  exactly two options: restart (begins a new game with score reset to 0) or
  quit (exits the program cleanly). No other post-round choices are presented.
- **FR-016**: System MUST detect when the entire board is filled (zero
  unoccupied cells after the snake eats the last fruit) and immediately end
  the round as a win state, displaying "You Win" and the final score rather
  than "Game Over".
- **FR-015**: System MUST let the player exit the program cleanly at any
  point via a clearly documented action; the terminal MUST be restored to
  its original state on exit.

### Key Entities

- **Snake**: The player-controlled chain of segments; has a head, a body, a
  current heading, and a length that grows over time.
- **Fruit**: A single collectible item placed on the board; consumed by the
  snake to trigger growth and scoring.
- **Game Board**: The bounded play area within the terminal where the snake
  and fruit are rendered.
- **Score**: A running numeric count of fruit eaten during the current game,
  displayed continuously during play.
- **Game Session**: The lifecycle of play from launch through one or more
  rounds (active play → game over → restart or exit).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A first-time player can begin steering the snake within 10
  seconds of launching the game, using only the documented controls.
- **SC-002**: 100% of fruit-eaten events result in the score visibly updating
  within the same on-screen update as the snake's growth.
- **SC-003**: 100% of self-collisions are detected and end the game; no
  self-collision goes undetected and no game ends without one of the defined
  end conditions occurring.
- **SC-004**: Players can correctly identify the snake, the fruit, the board
  boundary, and the current score at a glance, using only black-and-white
  visuals, without needing additional instructions.
- **SC-005**: A player can complete a full session of multiple consecutive
  games, moving from any end state (game over or win) to a new active game
  in a single action, without ever needing to relaunch the program.
- **SC-006**: When a board-full win is triggered, the game MUST display a
  visually distinct "You Win" indication (not "Game Over") 100% of the time,
  with the correct final score, verifiable via automated test.

## Assumptions

- A single play session supports multiple consecutive games: after game over,
  the player can restart without relaunching the program.
- The snake's movement speed (tick rate) stays constant within a single game
  rather than increasing as the score rises, favoring simple, predictable
  difficulty over escalating challenge. The default rate is 5 moves per second
  (configurable via `--speed`).
- The game board uses a fixed default size suitable for common terminal
  windows; exact dimensions are a presentation detail to be settled during
  planning, not a business requirement.
- No score history or high score persists between separate program launches;
  only the score(s) within the current session need to be tracked.
- Exactly one fruit exists on the board at any given time.
- The game is single-player only; no multiplayer or networked play is in
  scope.
