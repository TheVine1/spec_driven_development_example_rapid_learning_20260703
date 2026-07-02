import collections
import unittest

from snake.game import Direction, GameBoard, GameSession, GameState, Position


class TestIntegration(unittest.TestCase):

    def test_session_ticks_50_times_without_exception(self):
        session = GameSession(GameBoard(20, 20))
        for _ in range(50):
            if session.state == GameState.ACTIVE:
                session.tick()

    def test_state_transition_active_to_game_over(self):
        board = GameBoard(20, 20)
        session = GameSession(board)
        session.snake.body = collections.deque([
            Position(0, 10), Position(1, 10), Position(2, 10),
        ])
        session.snake.direction = Direction.UP
        session.fruit = Position(19, 19)
        session.tick()
        self.assertEqual(session.state, GameState.GAME_OVER)

    def test_reset_after_game_over_returns_to_active(self):
        session = GameSession(GameBoard(20, 20))
        session.state = GameState.GAME_OVER
        session.reset()
        self.assertEqual(session.state, GameState.ACTIVE)
        for _ in range(5):
            session.tick()


if __name__ == '__main__':
    unittest.main()
