import re

class _Rule:
    def __init__(self, pattern: str, replacement: str) -> None:
        self._regex = re.compile(pattern, re.IGNORECASE)
        self._replacement = replacement

    def apply(self, word: str) -> str | None:
        if self._regex.search(word) is None:
            return None

        return self._regex.sub(self._replacement, word)

class Vocabulary:
    def __init__(self) -> None:
        self._plurals: list[_Rule] = []
        self._singulars: list[_Rule] = []
        self._uncountables: list[str] = []

    def add_irregular(self, singular: str, plural: str, match_ending: bool = True):
        if match_ending:
            self.add_plural("(" + singular[0] + ")" + singular[1:] + "$", "\\1" + plural[1:])
            self.add_singular("(" + plural[0] + ")" + plural[1:] + "$", "\\1" + singular[1:])
        else:
            self.add_plural(f"^{singular}$", plural)
            self.add_singular(f"^{plural}$", singular)

    def add_uncountable(self, word: str):
        self._uncountables.append(word.lower())

    def add_plural(self, rule: str, replacement: str):
        self._plurals.append(_Rule(rule, replacement))

    def add_singular(self, rule: str, replacement: str):
        self._singulars.append(_Rule(rule, replacement))

    def pluralize(self, word: str, is_known_to_be_singular: bool = True) -> str:
        result = self._apply_rules(self._plurals, word, False)

        if is_known_to_be_singular:
            return result if result is not None else word

        # the singularity is unknown so we should check all possibilities
        as_singular = self._apply_rules(self._singulars, word, False)
        as_singular_as_plural = self._apply_rules(self._plurals, as_singular, False)
        if (
            as_singular is not None
            and as_singular != word
            and as_singular + "s" != word
            and as_singular_as_plural == word
            and result != word
        ):
            return word

        assert result is not None
        return result

    def singularize(self, word: str, is_known_to_be_plural: bool = True, skip_simple_words: bool = False) -> str:
        result = self._apply_rules(self._singulars, word, skip_simple_words)

        if is_known_to_be_plural:
            return result if result is not None else word

        # the plurality is unknown so we should check all possibilities
        as_plural = self._apply_rules(self._plurals, word, False)
        as_plural_as_singular = self._apply_rules(self._singulars, as_plural, False)
        if (
            as_plural != word
            and word + "s" != as_plural
            and as_plural_as_singular == word
            and result != word
        ):
            return word

        return result if result is not None else word

    def _apply_rules(self, rules: list[_Rule], word: str | None, skip_first_rule: bool) -> str | None:
        if word is None:
            return None

        if len(word) < 1:
            return word

        if self._is_uncountable(word):
            return word

        result = word
        for rule in reversed(rules[(1 if skip_first_rule else 0):]):
            result = rule.apply(word)
            if result != None:
                break

        return self._match_upper_case(word, result) if result is not None else None

    def _is_uncountable(self, word: str):
        return word.lower() in self._uncountables

    def _match_upper_case(self, word: str, replacement: str):
        return (replacement[0].upper() + replacement[1:]) if word[0].isupper() and replacement[0].islower() else replacement


def _generate_default_vocabulary() -> Vocabulary:
    default: Vocabulary = Vocabulary()

    default.add_plural("$", "s")
    default.add_plural("s$", "s")
    default.add_plural("(ax|test)is$", "\\1es")
    default.add_plural("(octop|vir|alumn|fung|cact|foc|hippopotam|radi|stimul|syllab|nucle)us$", "\\1i")
    default.add_plural("(alias|bias|iris|status|campus|apparatus|virus|walrus|trellis)$", "\\1es")
    default.add_plural("(buffal|tomat|volcan|ech|embarg|her|mosquit|potat|torped|vet)o$", "\\1oes")
    default.add_plural("([dti])um$", "\\1a")
    default.add_plural("sis$", "ses")
    default.add_plural("(?:([^f])fe|([lr])f)$", "\\1\\2ves")
    default.add_plural("(hive)$", "\\1s")
    default.add_plural("([^aeiouy]|qu)y$", "\\1ies")
    default.add_plural("(x|ch|ss|sh)$", "\\1es")
    default.add_plural("(matr|vert|ind|d)(ix|ex)$", "\\1ices")
    default.add_plural("(^[m|l])ouse$", "\\1ice")
    default.add_plural("^(ox)$", "\\1en")
    default.add_plural("(quiz)$", "\\1zes")
    default.add_plural("(buz|blit|walt)z$", "\\1zes")
    default.add_plural("(hoo|lea|loa|thie)f$", "\\1ves")
    default.add_plural("(alumn|alg|larv|vertebr)a$", "\\1ae")
    default.add_plural("(criteri|phenomen)on$", "\\1a")

    default.add_singular("s$", "")
    default.add_singular("(n)ews$", "\\1ews")
    default.add_singular("([dti])a$", "\\1um")
    default.add_singular("(analy|ba|diagno|parenthe|progno|synop|the|ellip|empha|neuro|oa|paraly)ses$", "\\1sis")
    default.add_singular("([^f])ves$", "\\1fe")
    default.add_singular("(hive)s$", "\\1")
    default.add_singular("(tive)s$", "\\1")
    default.add_singular("([lr]|hoo|lea|loa|thie)ves$", "\\1f")
    default.add_singular("(^zomb)?([^aeiouy]|qu)ies$", "\\2y")
    default.add_singular("(s)eries$", "\\1eries")
    default.add_singular("(m)ovies$", "\\1ovie")
    default.add_singular("(x|ch|ss|sh)es$", "\\1")
    default.add_singular("(^[m|l])ice$", "\\1ouse")
    default.add_singular("(?<!^[a-z])(o)es$", "\\1")
    default.add_singular("(shoe)s$", "\\1")
    default.add_singular("(cris|ax|test)es$", "\\1is")
    default.add_singular("(octop|vir|alumn|fung|cact|foc|hippopotam|radi|stimul|syllab|nucle)i$", "\\1us")
    default.add_singular("(alias|bias|iris|status|campus|apparatus|virus|walrus|trellis)es$", "\\1")
    default.add_singular("^(ox)en", "\\1")
    default.add_singular("(matr|d)ices$", "\\1ix")
    default.add_singular("(vert|ind)ices$", "\\1ex")
    default.add_singular("(quiz)zes$", "\\1")
    default.add_singular("(buz|blit|walt)zes$", "\\1z")
    default.add_singular("(alumn|alg|larv|vertebr)ae$", "\\1a")
    default.add_singular("(criteri|phenomen)a$", "\\1on")
    default.add_singular("([b|r|c]ook|room|smooth)ies$", "\\1ie")

    default.add_irregular("person", "people")
    default.add_irregular("man", "men")
    default.add_irregular("human", "humans")
    default.add_irregular("child", "children")
    default.add_irregular("sex", "sexes")
    default.add_irregular("glove", "gloves")
    default.add_irregular("move", "moves")
    default.add_irregular("goose", "geese")
    default.add_irregular("wave", "waves")
    default.add_irregular("foot", "feet")
    default.add_irregular("tooth", "teeth")
    default.add_irregular("curriculum", "curricula")
    default.add_irregular("database", "databases")
    default.add_irregular("zombie", "zombies")
    default.add_irregular("personnel", "personnel")
    default.add_irregular("cache", "caches")

    default.add_irregular("ex", "exes", match_ending=False)
    default.add_irregular("is", "are", match_ending=False)
    default.add_irregular("that", "those", match_ending=False)
    default.add_irregular("this", "these", match_ending=False)
    default.add_irregular("bus", "buses", match_ending=False)
    default.add_irregular("die", "dice", match_ending=False)
    default.add_irregular("tie", "ties", match_ending=False)

    default.add_uncountable("staff")
    default.add_uncountable("training")
    default.add_uncountable("equipment")
    default.add_uncountable("information")
    default.add_uncountable("corn")
    default.add_uncountable("milk")
    default.add_uncountable("rice")
    default.add_uncountable("money")
    default.add_uncountable("species")
    default.add_uncountable("series")
    default.add_uncountable("fish")
    default.add_uncountable("sheep")
    default.add_uncountable("deer")
    default.add_uncountable("aircraft")
    default.add_uncountable("oz")
    default.add_uncountable("tsp")
    default.add_uncountable("tbsp")
    default.add_uncountable("ml")
    default.add_uncountable("l")
    default.add_uncountable("water")
    default.add_uncountable("waters")
    default.add_uncountable("semen")
    default.add_uncountable("sperm")
    default.add_uncountable("bison")
    default.add_uncountable("grass")
    default.add_uncountable("hair")
    default.add_uncountable("mud")
    default.add_uncountable("elk")
    default.add_uncountable("luggage")
    default.add_uncountable("moose")
    default.add_uncountable("offspring")
    default.add_uncountable("salmon")
    default.add_uncountable("shrimp")
    default.add_uncountable("someone")
    default.add_uncountable("swine")
    default.add_uncountable("trout")
    default.add_uncountable("tuna")
    default.add_uncountable("corps")
    default.add_uncountable("scissors")
    default.add_uncountable("means")
    default.add_uncountable("mail")
    default.add_uncountable("metadata")

    return default

_default_vocabulary: Vocabulary | None = None
def default() -> Vocabulary:
    global _default_vocabulary
    if _default_vocabulary is None:
        _default_vocabulary = _generate_default_vocabulary()
    return _default_vocabulary
