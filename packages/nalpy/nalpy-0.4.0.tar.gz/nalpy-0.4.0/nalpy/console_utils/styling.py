from nalpy.console_utils import ConsoleColor, ConsoleStyle
import nalpy.console_utils._helpers as _helper

# NOTE: Remember to add to console_utils public imports

def set_foreground_color(color: ConsoleColor):
    ansi = _helper.get_ansi_color(color, prefix_number=3)
    _helper.set_sgr(ansi)

def set_background_color(color: ConsoleColor): # NOTE: This leaves a long colored line in VSCode for some reason
    ansi = _helper.get_ansi_color(color, prefix_number=4)
    _helper.set_sgr(ansi)

def set_style(style: ConsoleStyle):
    _helper.set_sgr(str(style))

def reset_attributes():
    _helper.set_sgr("0")
