import collections
import unittest

from snake.game import (
    Direction, GameBoard, GameSession, GameState, Position, Snake,
)


# ---------------------------------------------------------------------------
# T009 — Direction tests
# ---------------------------------------------------------------------------

class TestDirection(unittest.TestCase):

    def test_reversal_is_opposite(self):
        self.assertTrue(Direction.UP.is_opposite(Direction.DOWN))
        self.assertTrue(Direction.DOWN.is_opposite(Direction.UP))
        self.assertTrue(Direction.LEFT.is_opposite(Direction.RIGHT))
        self.assertTrue(Direction.RIGHT.is_opposite(Direction.LEFT))
        self.assertFalse(Direction.UP.is_opposite(Direction.LEFT))
        self.assertFalse(Direction.UP.is_opposite(Direction.RIGHT))
        self.assertFalse(Direction.RIGHT.is_opposite(Direction.UP))


# ---------------------------------------------------------------------------
# T010 — Position tests
# ---------------------------------------------------------------------------

class TestPosition(unittest.TestCase):

    def test_position_equality(self):
        self.assertEqual(Position(0, 0), Position(0, 0))
        self.assertNotEqual(Position(0, 0), Position(0, 1))
        self.assertNotEqual(Position(1, 0), Position(0, 0))

    def test_position_out_of_bounds_detection(self):
        # width=10, height=5 → valid rows 0-4, valid cols 0-9
        self.assertFalse(Position(0, 0).is_out_of_bounds(10, 5))
        self.assertFalse(Position(4, 9).is_out_of_bounds(10, 5))
        self.assertTrue(Position(-1, 0).is_out_of_bounds(10, 5))
        self.assertTrue(Position(5, 0).is_out_of_bounds(10, 5))
        self.assertTrue(Position(0, -1).is_out_of_bounds(10, 5))
        self.assertTrue(Position(0, 10).is_out_of_bounds(10, 5))


# ---------------------------------------------------------------------------
# T011 — Snake tests
# ---------------------------------------------------------------------------

class TestSnake(unittest.TestCase):

    def _make_snake(self):
        body = [Position(5, 5), Position(5, 4), Position(5, 3)]
        return Snake(body, Direction.RIGHT)

    def test_snake_initial_length_is_3(self):
        self.assertEqual(len(self._make_snake().body), 3)

    def test_snake_head_is_first_body_element(self):
        self.assertEqual(self._make_snake().head, Position(5, 5))

    def test_snake_move_does_not_change_length(self):
        snake = self._make_snake()
        snake.move(Position(5, 6))
        self.assertEqual(len(snake.body), 3)
        self.assertEqual(snake.head, Position(5, 6))

    def test_snake_grow_increases_length_by_one(self):
        snake = self._make_snake()
        snake.grow(Position(5, 6))
        self.assertEqual(len(snake.body), 4)
        self.assertEqual(snake.head, Position(5, 6))

    def test_snake_body_cells_excludes_head(self):
        snake = self._make_snake()
        self.assertNotIn(Position(5, 5), snake.body_cells)  # head excluded
        self.assertIn(Position(5, 4), snake.body_cells)
        self.assertIn(Position(5, 3), snake.body_cells)


# ---------------------------------------------------------------------------
# T015 — GameBoard and GameSession init tests
# ---------------------------------------------------------------------------

class TestGameBoardAndSessionInit(unittest.TestCase):

    def test_gameboard_free_cells_excludes_snake_and_fruit(self):
        board = GameBoard(10, 5)
        session = GameSession(board)
        free = board.all_cells() - set(session.snake.body) - {session.fruit}
        expected = board.width * board.height - len(session.snake.body) - 1
        self.assertEqual(len(free), expected)

    def test_gamesession_initial_state_is_active(self):
        self.assertEqual(GameSession(GameBoard(20, 20)).state, GameState.ACTIVE)

    def test_gamesession_initial_score_is_zero(self):
        self.assertEqual(GameSession(GameBoard(20, 20)).score, 0)


# ---------------------------------------------------------------------------
# T019 — GameSession.tick() movement tests
# ---------------------------------------------------------------------------

class TestGameSessionTickMovement(unittest.TestCase):

    def _session(self, w=20, h=20):
        return GameSession(GameBoard(w, h))

    def test_tick_moves_snake_forward(self):
        session = self._session()
        original_head = session.snake.head
        dr, dc = session.snake.direction.delta
        session.tick()
        expected = Position(original_head.row + dr, original_head.col + dc)
        self.assertEqual(session.snake.head, expected)

    def test_tick_applies_pending_dir_and_clears_it(self):
        session = self._session()
        # Snake heading RIGHT; press UP (absolute UP — valid, not a reversal)
        session.handle_input('UP')
        self.assertIsNotNone(session.pending_dir)
        session.tick()
        self.assertIsNone(session.pending_dir)
        self.assertEqual(session.snake.direction, Direction.UP)

    def test_tick_discards_reversal_input(self):
        session = self._session()
        # Snake heading RIGHT; press LEFT (absolute LEFT = 180° reversal)
        session.handle_input('LEFT')
        # Reversal must be discarded at handle_input time — pending stays None
        self.assertIsNone(session.pending_dir)
        session.tick()
        self.assertEqual(session.snake.direction, Direction.RIGHT)

    def test_last_key_wins_two_inputs_same_tick(self):
        session = self._session()
        # Heading RIGHT; press UP then DOWN (both valid vs RIGHT); last wins
        session.handle_input('UP')    # pending = UP
        session.handle_input('DOWN')  # pending = DOWN (overwrites)
        session.tick()
        self.assertEqual(session.snake.direction, Direction.DOWN)


# ---------------------------------------------------------------------------
# T020 — Fruit collection tests
# ---------------------------------------------------------------------------

class TestFruitCollection(unittest.TestCase):

    def _session_with_fruit_ahead(self):
        session = GameSession(GameBoard(20, 20))
        head = session.snake.head
        dr, dc = session.snake.direction.delta
        session.fruit = Position(head.row + dr, head.col + dc)
        return session

    def test_fruit_eat_grows_snake(self):
        session = self._session_with_fruit_ahead()
        initial_len = len(session.snake.body)
        session.tick()
        self.assertEqual(len(session.snake.body), initial_len + 1)

    def test_fruit_eat_increments_score_by_one(self):
        session = self._session_with_fruit_ahead()
        session.tick()
        self.assertEqual(session.score, 1)

    def test_new_fruit_not_on_snake_after_eat(self):
        session = self._session_with_fruit_ahead()
        session.tick()
        if session.state == GameState.ACTIVE:
            self.assertNotIn(session.fruit, set(session.snake.body))

    def test_fruit_spawns_in_random_free_cell(self):
        session = self._session_with_fruit_ahead()
        session.tick()
        if session.state == GameState.ACTIVE:
            self.assertFalse(session.fruit.is_out_of_bounds(
                session.board.width, session.board.height))
            self.assertNotIn(session.fruit, set(session.snake.body))


# ---------------------------------------------------------------------------
# T029 — Collision detection tests
# ---------------------------------------------------------------------------

class TestCollisionDetection(unittest.TestCase):

    def _session(self):
        return GameSession(GameBoard(20, 20))

    def test_self_collision_sets_game_over(self):
        session = self._session()
        # Head at (10,10) heading RIGHT; body contains (10,11) → immediate collision
        session.snake.body = collections.deque([
            Position(10, 10),
            Position(10, 11),
            Position(10, 12),
        ])
        session.snake.direction = Direction.RIGHT
        session.fruit = Position(0, 0)
        session.tick()
        self.assertEqual(session.state, GameState.GAME_OVER)

    def test_wall_collision_top(self):
        session = self._session()
        session.snake.body = collections.deque([
            Position(0, 10), Position(1, 10), Position(2, 10),
        ])
        session.snake.direction = Direction.UP
        session.fruit = Position(19, 19)
        session.tick()
        self.assertEqual(session.state, GameState.GAME_OVER)

    def test_wall_collision_bottom(self):
        session = self._session()
        session.snake.body = collections.deque([
            Position(19, 10), Position(18, 10), Position(17, 10),
        ])
        session.snake.direction = Direction.DOWN
        session.fruit = Position(0, 0)
        session.tick()
        self.assertEqual(session.state, GameState.GAME_OVER)

    def test_wall_collision_left(self):
        session = self._session()
        session.snake.body = collections.deque([
            Position(10, 0), Position(10, 1), Position(10, 2),
        ])
        session.snake.direction = Direction.LEFT
        session.fruit = Position(19, 19)
        session.tick()
        self.assertEqual(session.state, GameState.GAME_OVER)

    def test_wall_collision_right(self):
        session = self._session()
        session.snake.body = collections.deque([
            Position(10, 19), Position(10, 18), Position(10, 17),
        ])
        session.snake.direction = Direction.RIGHT
        session.fruit = Position(0, 0)
        session.tick()
        self.assertEqual(session.state, GameState.GAME_OVER)


# ---------------------------------------------------------------------------
# T030 — Win condition test
# ---------------------------------------------------------------------------

class TestWinCondition(unittest.TestCase):

    def test_win_when_no_free_cells_after_eat(self):
        # 3×1 board, 3 total cells.
        # Snake occupies 2 cells; fruit at the 3rd.
        # Eating it grows snake to 3 → fills board → WIN.
        session = GameSession(GameBoard(3, 1))
        # After init the snake is at most 2 cells on a 3×1 board.
        session.snake.body = collections.deque([
            Position(0, 1), Position(0, 0),
        ])
        session.snake.direction = Direction.RIGHT
        session.fruit = Position(0, 2)  # only free cell
        session.tick()
        self.assertEqual(session.state, GameState.WIN)
        self.assertIsNone(session.fruit)


# ---------------------------------------------------------------------------
# T036 — GameSession.reset() tests
# ---------------------------------------------------------------------------

class TestGameSessionReset(unittest.TestCase):

    def _ended_session(self):
        session = GameSession(GameBoard(20, 20))
        session.state = GameState.GAME_OVER
        session.score = 5
        return session

    def test_reset_sets_score_to_zero(self):
        session = self._ended_session()
        session.reset()
        self.assertEqual(session.score, 0)

    def test_reset_sets_state_to_active(self):
        session = self._ended_session()
        session.reset()
        self.assertEqual(session.state, GameState.ACTIVE)

    def test_reset_creates_new_snake_at_start_length(self):
        session = self._ended_session()
        session.reset()
        self.assertEqual(len(session.snake.body), GameSession.INITIAL_LENGTH)

    def test_reset_places_new_fruit(self):
        session = self._ended_session()
        session.reset()
        self.assertIsNotNone(session.fruit)
        self.assertNotIn(session.fruit, set(session.snake.body))


if __name__ == '__main__':
    unittest.main()
