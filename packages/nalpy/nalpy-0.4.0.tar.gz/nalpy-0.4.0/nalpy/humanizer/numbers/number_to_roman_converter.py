_ROMAN_NUMERALS: dict[str, int] = {
    "M":  1000,
    "CM": 900,
    "D":  500,
    "CD": 400,
    "C":  100,
    "XC": 90,
    "L":  50,
    "XL": 40,
    "X":  10,
    "IX": 9,
    "V":  5,
    "IV": 4,
    "I":  1
}

def to_roman(num: int) -> str:
    if not (1 <= num <= 3999):
        raise ValueError("Number out of range.")

    output = ""
    for letters, value in _ROMAN_NUMERALS.items():
        while (num // value) > 0:
            output += letters
            num -= value

    return output
