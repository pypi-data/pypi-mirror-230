import nalpy.console_utils._helpers as _helper

# NOTE: Remember to add to console_utils public imports

def bell():
    """Makes an audible noise."""
    _helper.set_control("\u0007")

def backspace():
    """Moves the cursor one left to enable overwriting of following characters."""
    _helper.set_control("\u0008")

def tab():
    _helper.set_control("\u0009")

def line_feed():
    """Moves to next line, scrolls the display up if at bottom of the screen."""
    _helper.set_control("\u000A")

def form_feed():
    """Move a printer to top of next page."""
    _helper.set_control("\u000C")

def carriage_return():
    """Moves the cursor to column zero."""
    _helper.set_control("\u000D")
