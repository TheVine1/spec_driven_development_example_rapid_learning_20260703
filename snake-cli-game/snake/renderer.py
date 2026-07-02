"""ANSI rendering: score bar, board, game-over/win overlays. Monochrome only."""

import sys

from snake.game import GameBoard, GameSession, GameState, Position, Snake


def render(session: GameSession) -> None:
    draw_score_bar(session.score)
    if session.state == GameState.ACTIVE:
        draw_board(session.board, session.snake, session.fruit)
    else:
        draw_overlay(session.state, session.score, session.board)


def draw_score_bar(score: int) -> None:
    """Row 1: score line. Trailing spaces erase old wider numbers."""
    sys.stdout.write(f'\x1b[1;1HScore: {score}        ')
    sys.stdout.flush()


def draw_board(board: GameBoard, snake: Snake, fruit: Position) -> None:
    """Render the full play area starting at terminal row 2."""
    head       = snake.head
    body_cells = snake.body_cells  # excludes head

    parts = []
    # Top border — terminal row 2
    parts.append('\x1b[2;1H+' + '-' * board.width + '+')

    for r in range(board.height):
        # Terminal row = r + 3 (row 1 = score, row 2 = top border)
        parts.append(f'\x1b[{r + 3};1H|')
        for c in range(board.width):
            pos = Position(r, c)
            if pos == head:
                parts.append('O')
            elif pos in body_cells:
                parts.append('o')
            elif pos == fruit:
                parts.append('*')
            else:
                parts.append(' ')
        parts.append('|')

    # Bottom border
    parts.append(f'\x1b[{board.height + 3};1H+' + '-' * board.width + '+')

    sys.stdout.write(''.join(parts))
    sys.stdout.flush()


def draw_overlay(state: GameState, score: int, board: GameBoard) -> None:
    """Render the end-screen overlay (GAME OVER or YOU WIN!) over the board area."""
    w = board.width

    title      = 'YOU WIN!' if state == GameState.WIN else 'GAME OVER'
    score_line = f'Final Score: {score}'
    prompt     = 'R = Restart   Q = Quit'

    content = [title, score_line, '', prompt]

    def _center(text: str) -> str:
        pad   = max(0, w - len(text))
        left  = pad // 2
        right = pad - left
        return '|' + ' ' * left + text + ' ' * right + '|'

    inner_rows = board.height
    start_row  = (inner_rows - len(content)) // 2
    blank      = '|' + ' ' * w + '|'

    parts = ['\x1b[2;1H+' + '-' * w + '+']

    for i in range(inner_rows):
        offset = i - start_row
        line   = _center(content[offset]) if 0 <= offset < len(content) else blank
        parts.append(f'\x1b[{i + 3};1H{line}')

    parts.append(f'\x1b[{inner_rows + 3};1H+' + '-' * w + '+')

    sys.stdout.write(''.join(parts))
    sys.stdout.flush()
