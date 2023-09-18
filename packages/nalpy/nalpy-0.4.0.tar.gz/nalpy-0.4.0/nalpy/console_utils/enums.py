from enum import IntEnum

# Add new enums to __init__.py imports

class ConsoleColor(IntEnum):
    BLACK = 0
    DARK_RED = 1
    DARK_GREEN = 2
    DARK_YELLOW = 3
    DARK_BLUE = 4
    DARK_MAGENTA = 5
    DARK_CYAN = 6
    GRAY = 7

    DARK_GRAY = 10
    RED = 11
    GREEN = 12
    YELLOW = 13
    BLUE = 14
    MAGENTA = 15
    CYAN = 16
    WHITE = 17

class ConsoleStyle(IntEnum):
    BOLD = 1
    FAINT = 2
    ITALIC = 3
    UNDERLINE = 4
    STRIKE = 9
