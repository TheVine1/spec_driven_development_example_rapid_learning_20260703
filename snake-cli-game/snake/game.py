import collections
import enum
import random
import threading
from typing import FrozenSet, List, Optional


class Position:
    """Immutable (row, col) cell on the game board."""

    __slots__ = ('_row', '_col')

    def __init__(self, row: int, col: int) -> None:
        object.__setattr__(self, '_row', row)
        object.__setattr__(self, '_col', col)

    def __setattr__(self, name, value):
        raise AttributeError('Position is immutable')

    @property
    def row(self) -> int:
        return self._row

    @property
    def col(self) -> int:
        return self._col

    def is_out_of_bounds(self, width: int, height: int) -> bool:
        return self._row < 0 or self._row >= height or self._col < 0 or self._col >= width

    def __eq__(self, other) -> bool:
        if not isinstance(other, Position):
            return NotImplemented
        return self._row == other._row and self._col == other._col

    def __hash__(self) -> int:
        return hash((self._row, self._col))

    def __repr__(self) -> str:
        return f'Position({self._row}, {self._col})'


class Direction(enum.Enum):
    UP    = (-1,  0)
    DOWN  = ( 1,  0)
    LEFT  = ( 0, -1)
    RIGHT = ( 0,  1)

    @property
    def delta(self):
        return self.value

    def is_opposite(self, other: 'Direction') -> bool:
        return _OPPOSITE[self] is other


_OPPOSITE = {
    Direction.UP:    Direction.DOWN,
    Direction.DOWN:  Direction.UP,
    Direction.LEFT:  Direction.RIGHT,
    Direction.RIGHT: Direction.LEFT,
}

_KEY_TO_DIR = {
    'UP':    Direction.UP,
    'DOWN':  Direction.DOWN,
    'LEFT':  Direction.LEFT,
    'RIGHT': Direction.RIGHT,
}


class Snake:
    """Player-controlled snake; body[0] is the head."""

    def __init__(self, body: List[Position], direction: Direction) -> None:
        self.body: collections.deque = collections.deque(body)
        self.direction: Direction = direction

    @property
    def head(self) -> Position:
        return self.body[0]

    @property
    def body_cells(self):
        """Set of all body positions excluding the head."""
        it = iter(self.body)
        next(it)  # skip head
        return set(it)

    def move(self, new_head: Position) -> None:
        """Advance the snake: prepend new head, remove tail."""
        self.body.appendleft(new_head)
        self.body.pop()

    def grow(self, new_head: Position) -> None:
        """Grow the snake by one: prepend new head, keep tail."""
        self.body.appendleft(new_head)


class GameState(enum.Enum):
    ACTIVE    = 'active'
    GAME_OVER = 'game_over'
    WIN       = 'win'


class GameBoard:
    """Immutable play-area dimensions."""

    def __init__(self, width: int, height: int) -> None:
        self.width  = width
        self.height = height

    def all_cells(self) -> FrozenSet[Position]:
        return frozenset(
            Position(r, c)
            for r in range(self.height)
            for c in range(self.width)
        )


class GameSession:
    """Top-level mutable game state for one or more rounds."""

    INITIAL_LENGTH = 3

    def __init__(self, board: GameBoard) -> None:
        self.board  = board
        self._lock  = threading.Lock()
        self._init_round()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _init_round(self) -> None:
        mid_row = self.board.height // 2
        mid_col = self.board.width  // 2
        body_len = min(self.INITIAL_LENGTH, mid_col + 1)
        body = [Position(mid_row, mid_col - i) for i in range(body_len)]
        self.snake       = Snake(body, Direction.RIGHT)
        self.state       = GameState.ACTIVE
        self.score       = 0
        self.pending_dir: Optional[Direction] = None
        self.fruit       = self._random_fruit()

    def _random_fruit(self) -> Position:
        free = list(self.board.all_cells() - set(self.snake.body))
        return random.choice(free)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def handle_input(self, key: str) -> None:
        """Called from the input thread; stores last valid direction (last-key-wins).

        Absolute mapping: each arrow key → fixed screen direction.
        Reversals (180°) are discarded here before being stored.
        """
        new_dir = _KEY_TO_DIR.get(key)
        if new_dir is None:
            return
        with self._lock:
            if not self.snake.direction.is_opposite(new_dir):
                self.pending_dir = new_dir
            # else: 180° reversal — silently discarded (FR-005)

    def tick(self) -> None:
        """Advance game state by one tick. No-op if not ACTIVE."""
        if self.state != GameState.ACTIVE:
            return

        # Consume pending direction under lock (reversals already filtered by handle_input)
        with self._lock:
            pending          = self.pending_dir
            self.pending_dir = None
        if pending is not None:
            self.snake.direction = pending

        dr, dc   = self.snake.direction.delta
        new_head = Position(self.snake.head.row + dr, self.snake.head.col + dc)

        # Wall collision (FR-011)
        if new_head.is_out_of_bounds(self.board.width, self.board.height):
            self.state = GameState.GAME_OVER
            return

        # Self-collision (FR-010)
        if new_head in self.snake.body_cells:
            self.state = GameState.GAME_OVER
            return

        # Fruit collision (FR-007)
        if new_head == self.fruit:
            self.snake.grow(new_head)
            self.score += 1
            free = list(self.board.all_cells() - set(self.snake.body))
            if not free:
                self.state = GameState.WIN
                self.fruit = None          # board is full; no new fruit
            else:
                self.fruit = random.choice(free)
        else:
            self.snake.move(new_head)

    def reset(self) -> None:
        """Start a fresh game round without relaunching the process (FR-014)."""
        self._init_round()
