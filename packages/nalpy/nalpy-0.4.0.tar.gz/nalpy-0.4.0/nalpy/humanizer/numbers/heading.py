from typing import Sequence


def to_heading(degrees: float) -> str:
    return _get_heading_from_set(degrees, _HEADINGS_LONG)

def to_abbreviated_heading(degrees: float) -> str:
    return _get_heading_from_set(degrees, _HEADINGS_SHORT)

def to_heading_arrow(degrees: float) -> str:
    return _get_heading_from_set(degrees, _HEADINGS_ARROW)


_HEADINGS_LONG = ( "north", "north-northeast", "northeast", "east-northeast", "east", "east-southeast", "southeast", "south-southeast", "south", "south-southwest", "southwest", "west-southwest", "west", "west-northwest", "northwest", "north-northwest" )
_HEADINGS_SHORT = ( "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW" )
_HEADINGS_ARROW = ( '↑', '↗', '→', '↘', '↓', '↙', '←', '↖' )

def _get_heading_from_set(heading: float, collection: Sequence[str]):
    ln = len(collection)
    val = round(heading / (360 / ln))
    return collection[val % ln]
