from nalpy.humanizer.inflections import vocabulary as _vocabulary
from nalpy.humanizer.numbers import count as _n_count
from nalpy.humanizer.numbers import enums as _n_enums

def pluralize(word: str, is_known_to_be_singular: bool = True) -> str:
    return _vocabulary.default().pluralize(word, is_known_to_be_singular)

def singularize(word: str, is_known_to_be_plural: bool = True) -> str:
    return _vocabulary.default().singularize(word, is_known_to_be_plural)

def quantisize(singular_word: str, amount: int, _number_format: _n_enums.NumberFormat = _n_enums.NumberFormat.NUMERALS) -> str:
    """Pluralizes the word with complex rules."""
    word: str
    if amount == 1:
        word = singular_word
    else:
        word = pluralize(singular_word)

    num: str = _n_count._format(amount, _number_format)
    if len(num) > 0:
        return f"{num} {word}"
    else:
        return word

def quick_quantisize(singular_word: str, amount: int, _number_format: _n_enums.NumberFormat = _n_enums.NumberFormat.NUMERALS) -> str:
    """Pluralizes the word by simply adding character ``s`` at the end of the word."""
    word = singular_word
    if amount != 1:
        word += "s"

    num: str = _n_count._format(amount, _number_format)
    if len(num) > 0:
        return f"{num} {word}"
    else:
        return word
