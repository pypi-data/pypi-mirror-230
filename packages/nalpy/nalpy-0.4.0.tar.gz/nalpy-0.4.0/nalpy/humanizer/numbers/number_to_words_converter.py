units_map: tuple[str, ...] = ( "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen" )
tens_map: tuple[str, ...] = ( "zero", "ten", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety" )
ordinal_exceptions: dict[int, str] = {
    1: "first",
    2: "second",
    3: "third",
    4: "fourth",
    5: "fifth",
    8: "eighth",
    9: "ninth",
    12: "twelfth"
}

def convert(number: int, is_ordinal: bool = False, add_and: bool = True) -> str:
    if number == 0:
        return _get_unit_value(0, is_ordinal)

    if number < 0:
        return f"minus {convert(-number)}"

    parts: list[str] = []

    if int(number / 1_000_000_000_000_000_000) > 0:
        parts.append(f"{convert(int(number / 1_000_000_000_000_000_000))} quintillion")
        number %= 1_000_000_000_000_000_000

    if int(number / 1_000_000_000_000_000) > 0:
        parts.append(f"{convert(int(number / 1_000_000_000_000_000))} quadrillion")
        number %= 1_000_000_000_000_000

    if int(number / 1_000_000_000_000) > 0:
        parts.append(f"{convert(int(number / 1_000_000_000_000))} trillion")
        number %= 1_000_000_000_000

    if int(number / 1000000000) > 0:
        parts.append(f"{convert(int(number / 1000000000))} billion")
        number %= 1000000000

    if int(number / 1000000) > 0:
        parts.append(f"{convert(int(number / 1000000))} million")
        number %= 1000000

    if int(number / 1000) > 0:
        parts.append(f"{convert(int(number / 1000))} thousand")
        number %= 1000

    if int(number / 100) > 0:
        parts.append(f"{convert(int(number / 100))} hundred")
        number %= 100

    if number > 0:
        if len(parts) > 0 and add_and:
            parts.append("and")

        if number < 20:
            parts.append(_get_unit_value(number, is_ordinal))
        else:
            last_part = tens_map[int(number / 10)]
            if (number % 10) > 0:
                last_part += f"-{_get_unit_value(number % 10, is_ordinal)}"
            elif is_ordinal:
                last_part = last_part.rstrip("y") + "ieth"

            parts.append(last_part)
    elif is_ordinal:
        parts[-1] += "th"

    to_words = " ".join(parts)

    if is_ordinal:
        to_words = _remove_one_prefix(to_words)

    return to_words



def _get_unit_value(number: int, is_ordinal: bool) -> str:
    if is_ordinal:
        if number in ordinal_exceptions:
            return ordinal_exceptions[number]

        return units_map[number] + "th"

    return units_map[number]

def _remove_one_prefix(to_words: str) -> str:
    if to_words.casefold().startswith("one".casefold()):
        return to_words[4:]
    return to_words
