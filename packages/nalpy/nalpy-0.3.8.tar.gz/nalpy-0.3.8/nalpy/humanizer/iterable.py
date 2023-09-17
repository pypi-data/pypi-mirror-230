import typing as _typing

_T = _typing.TypeVar("_T")

def humanize_iterable(iterable: _typing.Iterable[_T], separator: str = "and", formatter: _typing.Callable[[_T], str] | None = None) -> str:
    if formatter is None:
        formatter = str

    return _humanize_display_strings((formatter(o) for o in iterable), separator)

def _humanize_display_strings(strings: _typing.Iterable[str], separator: str) -> str:
    items: tuple[str, ...] = tuple(s for s in strings if len(s) > 0 and not s.isspace())

    count: int = len(items)

    if count == 0:
        return ""

    if count == 1:
        return items[0]

    before_last: tuple[str, ...] = items[:-1]
    last: str = items[-1]

    before_last_joined: str = ", ".join(before_last)

    return _get_conjunction_format_string(count).format(before_last=before_last_joined, sep=separator, last=last)

def _get_conjunction_format_string(item_count: int) -> str:
    if item_count > 2:
        return "{before_last}, {sep} {last}"

    return "{before_last} {sep} {last}"

