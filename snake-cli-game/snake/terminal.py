"""Terminal lifecycle: raw mode, cursor visibility, size checking."""

import atexit
import shutil
import signal
import sys
import threading

_WINDOWS = sys.platform == 'win32'

if not _WINDOWS:
    import termios
    import tty

# ---------------------------------------------------------------------------
# Resize detection
# ---------------------------------------------------------------------------

_resize_flag = threading.Event()


def _sigwinch_handler(*_) -> None:
    _resize_flag.set()


def register_resize_handler() -> None:
    """On POSIX, register a SIGWINCH handler to detect terminal resize.
    No-op on Windows (caller polls check_terminal_size() each tick instead)."""
    if not _WINDOWS:
        signal.signal(signal.SIGWINCH, _sigwinch_handler)


def resize_pending() -> bool:
    """Return True if a resize event has occurred since the last call.

    POSIX: True when SIGWINCH fired and flag is set (then clears the flag).
    Windows: always True so the caller polls check_terminal_size() each tick.
    """
    if _WINDOWS:
        return True
    if _resize_flag.is_set():
        _resize_flag.clear()
        return True
    return False

_original_attrs = None


def check_terminal_size(min_cols: int, min_rows: int):
    """Return (ok, current_cols, current_rows)."""
    size = shutil.get_terminal_size(fallback=(0, 0))
    ok = size.columns >= min_cols and size.lines >= min_rows
    return ok, size.columns, size.lines


def enter_raw_mode() -> None:
    global _original_attrs
    if _WINDOWS:
        return
    fd = sys.stdin.fileno()
    _original_attrs = termios.tcgetattr(fd)
    tty.setraw(fd)


def exit_raw_mode() -> None:
    global _original_attrs
    if _WINDOWS or _original_attrs is None:
        return
    termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, _original_attrs)
    _original_attrs = None


def hide_cursor() -> None:
    sys.stdout.write('\x1b[?25l')
    sys.stdout.flush()


def show_cursor() -> None:
    sys.stdout.write('\x1b[?25h')
    sys.stdout.flush()


class TerminalContext:
    """Context manager: enters raw mode + hides cursor; restores on exit."""

    def __enter__(self):
        atexit.register(show_cursor)      # T041: safety-net for abnormal exit
        atexit.register(exit_raw_mode)    # T041: safety-net for abnormal exit
        enter_raw_mode()
        hide_cursor()
        return self

    def __exit__(self, *args):
        show_cursor()
        exit_raw_mode()
        # Clear screen and return cursor to top-left for clean shell prompt
        sys.stdout.write('\x1b[2J\x1b[H')
        sys.stdout.flush()
