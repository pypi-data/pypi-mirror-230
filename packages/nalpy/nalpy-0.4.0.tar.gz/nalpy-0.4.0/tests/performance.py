from timeit import timeit
from typing import NamedTuple
from nalpy.math import Vector2, Vector2Int, MVector2, MVector2Int
from nalpy.math import _Legacy_Vector2, _Legacy_Vector2Int, _Legacy_MVector2, _Legacy_MVector2Int # pyright: ignore [reportPrivateUsage]
from nalpy import math
from nalpy.console_utils import set_foreground_color, set_background_color, reset_attributes, ConsoleColor, set_style, ConsoleStyle

setup: str = "x=Vector2(69, 420); y=Vector2(-4, -5); _mutable=Vector2(69, 69); _variant2 = __Variant2(69, 420) if __Variant2 is not None else ..."
commands: tuple[str, ...] = (
#     "Vector2(0, 0)",
#     "x[0]",
#     "x[1]",
#     "x[index_obj]",
#     "x.x",
#     "x.y",
#     "x == x",
#     "x == y",
#     "x.magnitude",

    # Vector specific
#     "Vector2.zero",
#     "x + y",
#     "x - y",
#     "x * y",
#     "x * 2",
#     "2 * x",
#     "x / y",
#     "x / 2",
#     "x // y",
#     "x // 2",
#     "x % y",
#     "x % 2",
#     "divmod(x, y)",
#     "divmod(x, 2)",
#     "-x",
#     "abs(x)",
#     "abs(y)",
#     "hash(x)",
    "for _ in x: pass",

    # MVector specific
#     "Vector2.zero()",
#     "x.copy()",
#     "_mutable.x += 5", # Mutable is reset before the next command, but will be mutated during the different runs of this command.
#     "_mutable.x -= 5",
#     "_mutable += y",
#     "_mutable -= y",
#     "_mutable *= 2",
#     "_mutable //= 2",
#     "_mutable //= 2",
#     "Vector2.from_immutable(_variant2)",
#     "x.to_immutable()"

    # MVector2 Specific
#     "x.normalize()",
#     "x.normalized"

    # Vector2 Specific
#     "x.normalized",
#     "Vector2.dot(x, y)",
#     "Vector2.lerp(x, y, 0.5)",
#     "Vector2.lerp_unclamped(x, y, 1.5)",
#     "Vector2.move_towards(y, x, 15.5)",
#     "Vector2.perpendicular(x)",
#     "Vector2.reflect(x, y)",
#     "Vector2.angle(x, y)",
#     "Vector2.signed_angle(x, y)",
#     "Vector2.distance(x, y)",

    # Vector2Int Specific
#     "Vector2.min(x, y)",
#     "Vector2.max(x, y)",
#     "Vector2.ceil(_math.Vector2(7.5, 6.23))",
#     "Vector2.floor(_math.Vector2(7.5, 6.23))",
#     "Vector2.trunc(_math.Vector2(7.5, 6.23))",
#     "Vector2.round(_math.Vector2(7.5, 6.23))"
)

class Configuration(NamedTuple):
    name: str
    vector2Implementation: type
    variant2: type | None = None

configurations: tuple[Configuration, ...] = (
#     Configuration("Old Vector2", _Legacy_Vector2),
    Configuration("New Vector2", Vector2),
#     Configuration("Old Vector2Int", _Legacy_Vector2Int),
#     Configuration("New Vector2Int", Vector2Int),
#     Configuration("Old MVector2", _Legacy_MVector2, _Legacy_Vector2),
#     Configuration("New MVector2", MVector2, Vector2),
#     Configuration("Old MVector2Int", _Legacy_MVector2Int, _Legacy_Vector2Int),
#     Configuration("New MVector2Int", MVector2Int, Vector2Int)
)

n = 500_000
runs = 50

DELIM: str = 75 * "-"

class _IndexObj:
    def __index__(self) -> int:
        return 0

def run_cmd(cmd: str, config: Configuration, index: int, total: int) -> float:
    gbls = {
        "Vector2": config.vector2Implementation,
        "_math": math,
        "__Variant2": config.variant2,
        "index_obj": _IndexObj()
    }
    secs = timeit(cmd, setup=setup, globals=gbls, number=n)

    print(f"({index + 1} / {total}) {config.name}: {secs} seconds for {n} repetitions")
    return secs

class CommandRan(NamedTuple):
    command: str
    config_run_seconds: tuple[tuple[Configuration, float], ...]

    def get_percent_faster(self) -> tuple[Configuration, Configuration, float]:
        """Returns the percentage of which the first configuration is faster than the last."""
        first_config, first_time = self.config_run_seconds[0]
        last_config, last_time = self.config_run_seconds[-1]
        percent_faster: float = (1 - (last_time / first_time)) * 100
        return (first_config, last_config, percent_faster)

cmds_ran: list[CommandRan] = []

for i, cmd in enumerate(commands):
    print(f"Command: {cmd} ({i + 1} / {len(commands)})")
    configruns: list[tuple[Configuration, float]] = []
    for config in configurations:
        runsofthisconfig: list[float] = []
        for i in range(runs):
            timetaken_seconds: float = run_cmd(cmd, config, i, runs)
            runsofthisconfig.append(timetaken_seconds)
        configruns.append((config, min(runsofthisconfig)))

    cmds_ran.append(CommandRan(cmd, tuple(configruns)))
    print(DELIM)

ran_sorted: tuple[CommandRan, ...] = tuple(sorted(cmds_ran, key=lambda r: r.get_percent_faster()))

def value_to_console_color(value: float):
    if value > 0.0:
        return ConsoleColor.GREEN
    if value < 0.0:
        return ConsoleColor.RED
    return ConsoleColor.YELLOW

for run in ran_sorted:
    set_foreground_color(ConsoleColor.CYAN)
    set_style(ConsoleStyle.BOLD)
    print(run.command, end="")
    reset_attributes()
    print()
    for config, seconds in run.config_run_seconds:
        print(f"{config.name}: {seconds} seconds / {n} runs")
    slowest_config, fastest_config, percent_faster = run.get_percent_faster()
    set_foreground_color(value_to_console_color(percent_faster))
    print(f"{percent_faster}% faster ({slowest_config.name} => {fastest_config.name})", end="")
    reset_attributes()
    print("\n" + DELIM)
