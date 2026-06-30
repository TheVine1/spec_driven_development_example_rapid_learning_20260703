# Feature Specification: Classic Terminal Snake Game

**Feature Branch**: `001-snake-game`

**Created**: 2026-06-30

**Status**: Draft

**Input**: User description: "Build a CLI-based Snake game for the terminal. The game should follow standard Snake gameplay rules: the snake moves continuously, eating a fruit increases its length by one unit, and colliding with its own body ends the game. The current score should be displayed at the top of the screen and updated in real time as fruits are collected. The visual presentation should be simple and monochrome, using only black and white. The snake should be controlled using the arrow keys (only turning left and right) and the turning of the snake head is to be relative to its heading. The gameplay should feel responsive and visually clear in a terminal environment. Include expected handling for game-over state and score display throughout the session."

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
2. **Given** the snake is moving, **When** the player presses the left or
   right arrow key, **Then** the snake's head turns 90 degrees relative to its
   current heading (not to a fixed screen direction).
3. **Given** the snake's head reaches the same position as the fruit, **When**
   the next move completes, **Then** the snake's length increases by one
   segment, the score increases, and a new fruit appears at a different open
   position on the board.
4. **Given** the score has just increased, **When** the screen next redraws,
   **Then** the updated score is visible at the top of the screen with no
   noticeable delay.

---

### User Story 2 - Game Over on Self-Collision (Priority: P2)

While playing, the player steers the snake into its own body, ending the game.
The game clearly communicates that the game has ended and shows the final
score the player achieved.

**Why this priority**: Defining a clear failure condition and end state is
essential to "standard Snake gameplay rules" and gives every round a
definitive outcome.

**Independent Test**: Deliberately steer the snake into its own body and
confirm the game stops, a game-over indication is shown, and the final score
remains visible on screen.

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

- What happens when the snake grows long enough that very few open cells
  remain for a new fruit to spawn into?
- How does the system handle a direction key press that arrives in the same
  tick as the previous, unprocessed direction change (e.g., two turns queued
  before the next move)?
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
- **FR-004**: System MUST let the player change the snake's heading using only
  the left and right arrow keys, where each press turns the snake's head 90
  degrees relative to its current heading rather than to a fixed screen
  direction (e.g., "up arrow").
- **FR-005**: System MUST prevent the snake from reversing directly onto the
  segment immediately behind its head as a result of a direction input.
- **FR-006**: System MUST display exactly one fruit on the board at any time
  during active gameplay.
- **FR-007**: When the snake's head moves onto the fruit's position, system
  MUST increase the snake's length by one segment, increase the score, and
  place a new fruit at a random open (unoccupied) position on the board.
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
- **FR-014**: System MUST let the player start a new game after game over
  without relaunching the program.
- **FR-015**: System MUST let the player exit the program at any time via a
  clearly documented action.

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
  games, moving from game-over to a new active game in a single action, without
  ever needing to relaunch the program.

## Assumptions

- A single play session supports multiple consecutive games: after game over,
  the player can restart without relaunching the program.
- The snake's movement speed (tick rate) stays constant within a single game
  rather than increasing as the score rises, favoring simple, predictable
  difficulty over escalating challenge.
- The game board uses a fixed default size suitable for common terminal
  windows; exact dimensions are a presentation detail to be settled during
  planning, not a business requirement.
- No score history or high score persists between separate program launches;
  only the score(s) within the current session need to be tracked.
- Exactly one fruit exists on the board at any given time.
- The game is single-player only; no multiplayer or networked play is in
  scope.
