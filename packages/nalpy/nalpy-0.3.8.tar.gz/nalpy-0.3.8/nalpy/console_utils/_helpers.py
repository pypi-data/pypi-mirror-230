import sys
from nalpy.console_utils import ConsoleColor

ESCAPE = "\u001B"

def set_control(command: str):
    sys.stdout.write(command)

def set_csi(command: str):
    set_control(ESCAPE + "[" + command)

def set_seq(value: int, suffix: str):
    set_csi(f"{value}{suffix}")

def get_ansi_color(color: ConsoleColor, prefix_number: int) -> str:
    suffix = ""
    number = color.value
    if number >= 10:
        assert number < 20 # Just to make sure I haven't fucked something up in ConsoleColors
        suffix = ";1"
        number -= 10

    return f"{prefix_number}{number}{suffix}"

def set_sgr(command: str):
    set_csi(command + "m")

def erase_line(mode: int):
    set_seq(mode, "K")

def erase_display(mode: int):
    set_seq(mode, "J")
