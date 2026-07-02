"""Platform-abstracted keyboard input. Returns canonical key names."""

import os
import sys
import time
from typing import Optional

_WINDOWS = sys.platform == 'win32'

if not _WINDOWS:
    import select
else:
    import msvcrt


def get_key() -> Optional[str]:
    """
    Block for up to ~50 ms waiting for a keypress.
    Returns one of: "UP", "DOWN", "LEFT", "RIGHT", "QUIT", "RESTART", or None.
    """
    if _WINDOWS:
        return _get_key_windows()
    return _get_key_posix()


# ---------------------------------------------------------------------------
# POSIX implementation (Linux / macOS)
# ---------------------------------------------------------------------------

def _get_key_posix() -> Optional[str]:
    # Use the raw file descriptor, not sys.stdin (TextIOWrapper).
    # sys.stdin.read() goes through Python's line-buffered text layer which
    # waits for a newline that never arrives in raw mode — os.read() bypasses
    # that entirely and returns as soon as bytes are available.
    fd = sys.stdin.fileno()

    ready, _, _ = select.select([sys.stdin], [], [], 0.05)
    if not ready:
        return None

    ch = os.read(fd, 1)

    if ch == b'\x1b':
        r2, _, _ = select.select([sys.stdin], [], [], 0.01)
        if not r2:
            return None  # bare ESC — ignore
        ch2 = os.read(fd, 1)
        if ch2 != b'[':
            return None
        r3, _, _ = select.select([sys.stdin], [], [], 0.01)
        if not r3:
            return None
        ch3 = os.read(fd, 1)
        return {b'A': 'UP', b'B': 'DOWN', b'C': 'RIGHT', b'D': 'LEFT'}.get(ch3)

    if ch in (b'q', b'Q'):
        return 'QUIT'
    if ch in (b'r', b'R'):
        return 'RESTART'
    if ch == b'\x03':  # Ctrl+C in raw mode
        return 'QUIT'
    return None


# ---------------------------------------------------------------------------
# Windows implementation
# ---------------------------------------------------------------------------

def _get_key_windows() -> Optional[str]:
    # Poll with a short sleep to avoid busy-waiting
    for _ in range(5):
        if msvcrt.kbhit():
            ch = msvcrt.getch()
            if ch in (b'\xe0', b'\x00'):
                # Extended key: second byte is the direction code
                ch2 = msvcrt.getch()
                return {
                    b'H': 'UP',
                    b'P': 'DOWN',
                    b'M': 'RIGHT',
                    b'K': 'LEFT',
                }.get(ch2)
            if ch in (b'q', b'Q'):
                return 'QUIT'
            if ch in (b'r', b'R'):
                return 'RESTART'
            if ch == b'\x03':
                return 'QUIT'
            return None
        time.sleep(0.01)
    return None
