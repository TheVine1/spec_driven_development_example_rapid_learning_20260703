"""Entry point: python -m snake [--width W] [--height H] [--speed S]"""

import argparse
import sys
import threading
import time
import traceback

from snake import input_handler, renderer, terminal
from snake.game import GameBoard, GameSession, GameState


def _start_input_thread(
    session: GameSession,
    stop_event: threading.Event,
    restart_event: threading.Event,
) -> threading.Thread:
    """Daemon thread: reads keys and routes them to the correct handler."""

    def _loop():
        while not stop_event.is_set():
            key = input_handler.get_key()
            if key is None:
                continue
            if key == 'QUIT':
                stop_event.set()
                return
            if key == 'RESTART':
                restart_event.set()
            elif key in ('UP', 'DOWN', 'LEFT', 'RIGHT'):
                if session.state == GameState.ACTIVE:
                    session.handle_input(key)

    t = threading.Thread(target=_loop, daemon=True, name='snake-input')
    t.start()
    return t


def main() -> None:
    parser = argparse.ArgumentParser(
        prog='python -m snake',
        description='Classic terminal Snake game — zero dependencies, runs everywhere.',
        epilog=(
            'Controls: Arrow keys = move in that direction  '
            '|  Q = Quit at any time  |  R = Restart after game over or win'
        ),
    )
    parser.add_argument(
        '--width', type=int, default=20,
        help='Board width in cells (default: 20, min: 10)',
    )
    parser.add_argument(
        '--height', type=int, default=20,
        help='Board height in cells (default: 20, min: 8)',
    )
    parser.add_argument(
        '--speed', type=int, default=5,
        help='Ticks per second (default: 5, range: 1-30)',
    )
    args = parser.parse_args()

    width  = max(10,  min(args.width,  200))
    height = max(8,   min(args.height, 200))
    speed  = max(1,   min(args.speed,   30))
    tick_interval = 1.0 / speed

    # T042: Minimum terminal size check before entering raw mode
    min_cols = width  + 2           # left + right border
    min_rows = height + 4           # score bar + top border + rows + bottom border
    ok, cur_w, cur_h = terminal.check_terminal_size(min_cols, min_rows)
    if not ok:
        print(
            f'Error: terminal too small. '
            f'Minimum {min_cols}x{min_rows} required; '
            f'current terminal is {cur_w}x{cur_h}.',
            file=sys.stderr,
        )
        sys.exit(1)

    board   = GameBoard(width, height)
    session = GameSession(board)

    stop_event    = threading.Event()
    restart_event = threading.Event()
    resize_error: list = []   # set to (cur_w, cur_h) if resize-below-minimum occurs

    try:
        with terminal.TerminalContext():
            # Clear screen before first render
            sys.stdout.write('\x1b[2J\x1b[H')
            sys.stdout.flush()

            # Register SIGWINCH handler (POSIX) so resize events are caught promptly.
            # On Windows resize_pending() always returns True and we poll each tick.
            terminal.register_resize_handler()

            _start_input_thread(session, stop_event, restart_event)

            while not stop_event.is_set():
                # Check for terminal resize (T046).
                # POSIX: only runs the size check when SIGWINCH has fired.
                # Windows: polls check_terminal_size() on every iteration.
                if terminal.resize_pending():
                    ok, cur_w, cur_h = terminal.check_terminal_size(min_cols, min_rows)
                    if not ok:
                        resize_error[:] = [cur_w, cur_h]
                        stop_event.set()
                        break

                if session.state == GameState.ACTIVE:
                    tick_start = time.monotonic()
                    session.tick()
                    renderer.render(session)
                    elapsed    = time.monotonic() - tick_start
                    sleep_time = max(0.0, tick_interval - elapsed)
                    time.sleep(sleep_time)
                else:
                    # T035: Show end screen; wait for RESTART or QUIT
                    renderer.render(session)
                    while not stop_event.is_set():
                        if restart_event.is_set():
                            restart_event.clear()
                            session.reset()   # T038: in-session restart (FR-014)
                            break
                        time.sleep(0.05)

    except KeyboardInterrupt:
        # T039: Ctrl+C exits cleanly; TerminalContext.__exit__ restores terminal
        pass
    except Exception:
        # T044: Unexpected errors → traceback to stderr, exit code 2
        traceback.print_exc(file=sys.stderr)
        sys.exit(2)

    # Report resize-triggered exit after terminal has been restored (T046)
    if resize_error:
        cur_w, cur_h = resize_error
        print(
            f'Error: terminal too small. '
            f'Minimum {min_cols}x{min_rows} required; '
            f'current terminal is {cur_w}x{cur_h}.',
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == '__main__':
    main()
