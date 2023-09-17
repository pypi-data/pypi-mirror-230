"""
Provides C#-like Events.
"""

import typing as _typing


ParamsT = _typing.ParamSpec("ParamsT")

class Event(_typing.Generic[ParamsT]):
    """
    The event class on which other methods can subscribe using the `+=` operator and unsubscribe using `-=`. Can be typehinted.
    """
    def __init__(self, values: _typing.Iterable[_typing.Callable[ParamsT, _typing.Any]] = []) -> None:
        self.listeners = [v for v in values]

    def __iadd__(self, value: _typing.Callable[ParamsT, _typing.Any]) -> _typing.Self:
        if not callable(value):
            raise TypeError(f"Value of type {type(value)} is not callable!")

        if value in self.listeners:
            raise ValueError(f"Value {value} already in events!")

        self.listeners.append(value)

        return self

    def __isub__(self, value: _typing.Callable[ParamsT, _typing.Any])  -> _typing.Self:
        if not callable(value):
            raise TypeError(f"Value of type {type(value)} is not callable!")

        while value in self.listeners:
            self.listeners.remove(value)

        return self

    def __contains__(self, value: _typing.Callable[ParamsT, _typing.Any]) -> bool:
        return value in self.listeners

    def __len__(self) -> int:
        return len(self.listeners)

    def Invoke(self, *args: ParamsT.args, **kwargs: ParamsT.kwargs) -> None:
        for listener in self.listeners.copy(): # copying so that if someone removes themselves from the list, it still works
            listener(*args, **kwargs)
