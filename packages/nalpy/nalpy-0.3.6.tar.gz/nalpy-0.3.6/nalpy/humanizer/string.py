import typing as _typing

class _Helpers:
    @staticmethod
    def parse_pascal_or_camel(pascal_or_camel: str) -> str:
        def generator() -> _typing.Iterable[str]:
            characters = list(pascal_or_camel)
            for i in range(len(characters)):
                if i == 0:
                    yield characters[i].upper()
                elif characters[i].isupper() and not characters[i - 1].isupper():
                    yield " "
                    if i + 1 >= len(characters) or not characters[i + 1].isupper():
                        yield characters[i].lower()
                    else:
                        yield characters[i]
                else:
                    yield characters[i]

        return "".join(generator())

    @staticmethod
    def generate_pascal_or_camel(sentence: str, first_is_upper: bool):
        words = sentence.strip(" ").split(" ")

        if len(words) > 0:
            first_char = words[0][0].lower()
            if first_is_upper:
                first_char = first_char.upper()
            words[0] = first_char + words[0][1:]

        for i in range(1, len(words)):
            words[i] = words[i].capitalize() if not words[i].isupper() else words[i]
        return "".join(words)


    @staticmethod
    def parse_snake_or_kebab(snake_or_kebab: str, delimiter: str):
        low = " ".join(snake_or_kebab.split(delimiter))
        return low[0].upper() + low[1:]

    @staticmethod
    def generate_snake_or_kebab(sentence: str, delimiter: str):
        return delimiter.join(sentence.lower().split(" "))


def pascal_case_to_sentence(pascal: str) -> str:
    if len(pascal) < 1:
        return ""

    if " " in pascal or not pascal[0].isupper():
        raise ValueError("Not PascalCase!")

    return "".join(_Helpers.parse_pascal_or_camel(pascal))

def sentence_to_pascal_case(sentence: str) -> str:
    return _Helpers.generate_pascal_or_camel(sentence, True)


def camel_case_to_sentence(camel: str) -> str:
    if len(camel) < 1:
        return ""

    if " " in camel or not camel[0].islower():
        raise ValueError("Not camelCase!")

    return "".join(_Helpers.parse_pascal_or_camel(camel))

def sentence_to_camel_case(sentence: str) -> str:
    return _Helpers.generate_pascal_or_camel(sentence, False)


def snake_case_to_sentence(snake: str) -> str:
    if not snake.islower() or " " in snake:
        raise ValueError("Not snake_case!")

    return _Helpers.parse_snake_or_kebab(snake, "_")

def sentence_to_snake_case(sentence: str) -> str:
    return _Helpers.generate_snake_or_kebab(sentence, "_")


def kebab_case_to_sentence(kebab: str) -> str:
    if not kebab.islower() or " " in kebab:
        raise ValueError("Not kebab-case!")

    return _Helpers.parse_snake_or_kebab(kebab, "-")

def sentence_to_kebab_case(sentence: str) -> str:
    return _Helpers.generate_snake_or_kebab(sentence, "-")


def upper_snake_case_to_sentence(upper_snake: str) -> str:
    if not upper_snake.isupper() or " " in upper_snake:
        raise ValueError("Not UPPER_SNAKE_CASE!")

    return _Helpers.parse_snake_or_kebab(upper_snake.lower(), "_")

def sentence_to_upper_snake_case(sentence: str) -> str:
    return _Helpers.generate_snake_or_kebab(sentence, "_").upper()

def truncate(string: str, length: int, truncation_string: str = "...", include_suffix: bool = True, remove_whitespace: bool = True) -> str:
    """Truncate string to specified length from the right.

    Args:
        string (str): The string to truncate
        length (int): The length to truncate to
        truncation_string (str, optional): The string to append at the end of truncation. Defaults to "...".
        include_suffix (bool, optional): Include the length of `truncation_string` in the total length of the string. Defaults to True.
        remove_whitespace (bool, optional): Remove all whitespace inbetween the truncated string and truncation_string. Defaults to True.

    Returns:
        str: The truncated string
    """
    target_length = length
    if include_suffix:
        target_length -= len(truncation_string)

    if len(string) <= target_length:
        return string

    txt = string[:target_length]
    if remove_whitespace:
        txt = txt.rstrip()
    return txt + truncation_string

def ltruncate(string: str, length: int, truncation_string: str = "...", include_prefix: bool = True, remove_whitespace: bool = True):
    """Truncate string to specified length from the left.

    Args:
        string (str): The string to truncate
        length (int): The length to truncate to
        truncation_string (str, optional): The string to append at the end of truncation. Defaults to "...".
        include_prefix (bool, optional): Include the length of `truncation_string` in the total length of the string. Defaults to True.
        remove_whitespace (bool, optional): Remove all whitespace inbetween the truncated string and truncation_string. Defaults to True.

    Returns:
        str: The truncated string
    """
    target_length = length
    if include_prefix:
        target_length -= len(truncation_string)

    string_length: int = len(string)
    if string_length <= target_length:
        return string

    start_index = string_length - target_length
    txt = string[start_index:]
    if remove_whitespace:
        txt = txt.lstrip()
    return truncation_string + txt
