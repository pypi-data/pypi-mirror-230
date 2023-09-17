import re
from nalpy.humanizer.numbers.enums import NumberFormat
from nalpy.humanizer.numbers import number_to_words_converter, number_to_roman_converter

def _format(num: int, format_: NumberFormat) -> str:
    match format_:
        case NumberFormat.NONE:
            return ""
        case NumberFormat.NUMERALS:
            return str(num)
        case NumberFormat.SPACED_NUMERALS:
            return to_spaced_numerals(num)
        case NumberFormat.WORDS:
            return to_words(num)
        case _:
            raise NotImplementedError(f"No formatter implemented for format '{format_.name}'")

def ordinalize(num: int, format_: NumberFormat = NumberFormat.NUMERALS) -> str:
    if num < 1:
        raise ValueError("Number cannot be less than one!")

    if format_ == NumberFormat.WORDS:
        return to_ordinal_words(num)

    out: str = _format(num, format_)
    last_digit: int = num % 10

    if last_digit == 1:
        return out + "st"
    if last_digit == 2:
        return out + "nd"
    if last_digit == 3:
        return out + "rd"
    return out + "th"

def to_spaced_numerals(num: int):
    reversed_str: str = "".join(reversed(str(num)))
    joined = ' '.join(re.findall(r'.{1,3}', reversed_str))
    return "".join(reversed(joined))

def to_words(num: int, add_and: bool = True) -> str:
    return number_to_words_converter.convert(num, False, add_and)

def to_ordinal_words(num: int) -> str:
    return number_to_words_converter.convert(num, True)

def to_roman(num: int) -> str:
    return number_to_roman_converter.to_roman(num)

def to_percent(num: int | float, format_: NumberFormat = NumberFormat.NUMERALS) -> str:
    if isinstance(num, float):
        num = round(num * 100)

    if format_ == NumberFormat.SPACED_NUMERALS:
        return f"{_format(num, format_)} %"
    if format_ == NumberFormat.WORDS:
        return f"{to_words(num)} percent"
    return f"{_format(num, format_)}%"

def tupleize(count: int) -> str:
    match count:
        case 1:
            return "single"
        case 2:
            return "double"
        case 3:
            return "triple"
        case 4:
            return "quadruple"
        case 5:
            return "quintuple"
        case 6:
            return "sextuple"
        case 7:
            return "septuple"
        case 8:
            return "octuple"
        case 9:
            return "nonuple"
        case 10:
            return "decuple"
        case 100:
            return "centuple"
        case 1000:
            return "milluple"
        case _:
            return f"{count}-tuple"
