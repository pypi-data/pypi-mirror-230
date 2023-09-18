import nalpy.console_utils._helpers as _helper

# NOTE: Remember to add to console_utils public imports


def cursor_up(count: int = 1):
    _helper.set_seq(count, "A")

def cursor_down(count: int = 1):
    _helper.set_seq(count, "B")

def cursor_forward(count: int = 1):
    _helper.set_seq(count, "C")

def cursor_back(count: int = 1):
    _helper.set_seq(count, "D")

def cursor_line_down(count: int = 1):
    _helper.set_seq(count, "E")

def cursor_line_up(count: int = 1):
    _helper.set_seq(count, "F")


def cursor_hide():
    _helper.set_csi("?25l")

def cursor_show():
    _helper.set_csi("?25h")


def clear():
    """Clear the entire screen and move to upperleft."""
    _helper.erase_display(2)
    cursor_set_pos(1, 1)

def lclear():
    """Clear from cursor to the beginning of the screen."""
    _helper.erase_display(1)

def rclear():
    """Clear from cursor to the end of screen."""
    _helper.erase_display(0)

def erase():
    """Clear the entire line."""
    _helper.erase_line(2)

def lerase():
    """Clear from cursor to beginning of the line."""
    _helper.erase_line(1)

def rerase():
    """Clear from cursor to the end of the line."""
    _helper.erase_line(0)


def scroll_up(lines: int):
    _helper.set_seq(lines, "S")

def scroll_down(lines: int):
    _helper.set_seq(lines, "T")


def cursor_set_pos(row_index: int, column_index: int):
    """rows and columns are 1-based"""
    _helper.set_csi(f"{row_index};{column_index}f")

def cursor_get_pos() -> tuple[int, int]:
    raise NotImplementedError()
