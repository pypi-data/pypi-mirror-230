import typing as _typing

from nalpy import math as _math
from nalpy import console_utils as _console_utils


class ProgressbarStyle(_typing.NamedTuple):
    width: int = 32
    bar_prefix: str = ' '
    bar_suffix: str = ' '
    empty_fill: str = '∙'
    fill: str = '█'
    color: _console_utils.ConsoleColor | None = None
    hide_cursor: bool = True

    @classmethod
    @property
    def default(cls) -> _typing.Self:
        return ProgressbarStyle()

class Progressbar:
    def __init__(self, style: ProgressbarStyle) -> None:
        self._style: ProgressbarStyle = style
        self._cursor_hidden: bool = False
        self._default_message: str | None = None
        self._started: bool = False

    def __enter__(self) -> _typing.Self:
        self.start()
        return self

    def __exit__(self, *_) -> bool:
        self.stop()
        return False

    def start(self, *, default_message: str | None = None):
        """Hides the cursor if it is requested by style.

        Args:
            default_message (str | None, optional): An optional default message to give. Will be written to the console before this progressbar is rendered if provided. Defaults to None.
        """
        if self._started:
            raise RuntimeError("Started already.")

        if self._style.hide_cursor:
            _console_utils.cursor_hide()
            self._cursor_hidden = True

        self._default_message = default_message
        if self._default_message is not None:
            print(self._default_message, end="")

        self._started = True

    def update(self, message: str | None, progress: float, _min: float = 0.0, _max: float = 1.0) -> None:
        """Update this `ProgressBar` instance.

        Args:
            message (str | None): The message to display, use None to display default message.
            progress (float): The progress where _min <= progress <= _max.
            _min (float, optional): The progress minimum value. Defaults to 0.0.
            _max (float, optional): The progress maximum value. Defaults to 1.0.
        """
        if not self._started:
            raise RuntimeError("Not started.")

        if message is None:
            if self._default_message is None:
                err = ValueError("No message provided.")
                err.add_note("No default message given as replacement.")
                raise err
            message = self._default_message

        t = _math.clamp01(_math.remap01(progress, _min, _max))
        filled_length = int(self._style.width * t)
        empty_length = self._style.width - filled_length

        bar = self._style.fill * filled_length
        empty = self._style.empty_fill * empty_length
        suffix = f"{round(t * 100)}%"

        _console_utils.carriage_return()
        print(message, self._style.bar_prefix, sep="", end="")
        if self._style.color is not None:
            _console_utils.set_foreground_color(self._style.color)
        print(bar, end="")
        _console_utils.reset_attributes()
        print(empty, self._style.bar_suffix, suffix, sep="", end="")

    def stop(self, *, end: str | None = "\n") -> None:
        """Resets the cursor visibility if it was modified.

        Args:
            end (str | None, optional): Prints `end` to console using `print` function's rules. Defaults to "\\n".
        """
        if not self._started:
            raise RuntimeError("Not started.")
        self._started = False

        if self._cursor_hidden:
            _console_utils.cursor_show()
            self._cursor_hidden = False

        print(end=end)
