#!/usr/bin/env python3

import re
from fractions import Fraction
from html import unescape
from typing import Any

from nltk.stem.porter import PorterStemmer
from nltk.tag import pos_tag
from nltk.tokenize import RegexpTokenizer

from ._constants import AMBIGUOUS_UNITS, STRING_NUMBERS_REGEXES, UNITS

# Regex pattern for fraction parts.
# Matches 0+ numbers followed by 0+ white space characters followed by a number then
# a forward slash then another number.
FRACTION_PARTS_PATTERN = re.compile(r"(\d*\s*\d/\d+)")

# Regex pattern for checking if token starts with a capital letter.
CAPITALISED_PATTERN = re.compile(r"^[A-Z]")

# Regex pattern for finding quantity and units without space between them.
# Assumes the quantity is always a number and the units always a letter.
QUANTITY_UNITS_PATTERN = re.compile(r"(\d)\-?([a-zA-Z])")

# Regex pattern for matching a numeric range e.g. 1-2, 2-3.
RANGE_PATTERN = re.compile(r"\d+\s*[\-]\d+")

# Regex pattern for matching a range in string format e.g. 1 to 2, 8.5 to 12, 4 or 5.
# Assumes fake fractions and unicode fraction have already been replaced.
# Allows the range to include a hyphen, which are captured in separate groups.
# Captures the two number in the range in separate capture groups.
STRING_RANGE_PATTERN = re.compile(r"([\d\.]+)(\-)?\s*(to|or)\s*(\-)*\s*([\d\.]+(\-)?)")

# Regex pattern to match hyphen followed by a number. This is used to fix ranges
# following the replacement of unicode fractions with fake fractions.
# The pattern any characters up to a hyphen followed by a space followed by a number.
# The parts before and after that space are cpatured in groups so we can reconstitute
# the sentence without that middle space.
BROKEN_RANGE_PATTERN = re.compile(r"(.*\-)\s(\d.*)")

# Define tokenizer.
# We are going to split an sentence between substrings that match the following groups
# a) letters and any punctuation, except
# b) open and close parentheses, open and close brackets, open and close braces,
# quote, comma.
# The following punctuation is deliberately left out of the these groups so that
# they are removed: backslash.
group_a = r"[\w!\#\$\£\€%\&'\*\+\-\.>=<\?@\^_`\\\|\~’]+"
group_b = r"[\(\)\[\]\{\}\,\"/:;]"
REGEXP_TOKENIZER = RegexpTokenizer(rf"{group_a}|{group_b}", gaps=False)

STEMMER = PorterStemmer()


class PreProcessor:

    """Recipe ingredient sentence PreProcessor class.

    Performs the necessary preprocessing on a sentence to generate the features
    required for the ingredient parser model.

    Each input sentence goes through a cleaning process to tidy up the input into a
    standardised form.

    Notes
    -----

    The cleaning steps are as follows

    1. | Replace all en-dashes and em-dashes with hyphens.
    2. | Replace numbers given as words with the numeric equivalent.
       | e.g. one >> 1
    3. | Replace fractions given in html markup with the unicode representation.
       | e.g. &frac12; >> ½
    4. | Replace unicode fractions with the equivalent decimal form. Decimals are
       | rounded to 3 a maximum of decimal places.
       | e.g. ½ >> 0.5
    5. | Replace "fake" fractions represented by 1/2, 2/3 etc. with the equivalent
       | decimal form
       | e.g. 1/2 >> 0.5
    6. | A space is enforced between quantities and units
    7. | Remove trailing periods from units
       | e.g. tsp. >> tsp
    8. | Numeric ranges indicated in words using "to" or "or" are replaced with a
       | standard numeric form
       | e.g. 1 or 2 >> 1-2; 10 to 12 >> 10-12
    9. | Units are made singular. This step uses a predefined list of plural units and
       | their singular form.

    Following the cleaning of the input sentence, it is tokenized into a list of tokens.

    Each token is one of the following

    * A word, including most punctuation marks
    * Opening or closing parentheses, braces, brackets; comma; speech marks

    The features for each token are computed on demand using the ``sentence_features``
    method, which returns a list of dictionaries.
    Each dictionary is the feature set for each token.

    The sentence features can then be passed to the CRF model which will generate the
    parsed output.

    Parameters
    ----------
    input_sentence : str
        Input ingredient sentence.
    defer_pos_tagging : bool
        Defer part of speech tagging until feature generation.
        Part of speech tagging is an expensive operation and it's not always needed when
        using this class.
    show_debug_output : bool, optional
        If True, print out each stage of the sentence normalisation

    Attributes
    ----------
    defer_pos_tagging : bool
        Defer part of speech tagging until feature generation
    show_debug_output : bool
        If True, print out each stage of the sentence normalisation
    input : str
        Input ingredient sentence.
    pos_tags : list[str]
        Part of speech tag for each token in the tokenized sentence.
    sentence : str
        Input ingredient sentence, cleaned to standardised form.
    singularised_indices : list[int]
        Indices of tokens in tokenised sentence that have been converted from plural
        to singular
    tokenized_sentence : list[str]
        Tokenised ingredient sentence.
    """

    def __init__(
        self,
        input_sentence: str,
        defer_pos_tagging: bool = False,
        show_debug_output: bool = False,
    ):
        """Initialisation

        Parameters
        ----------
        input_sentence : str
            Input ingredient sentence
        defer_pos_tagging : bool, optional
            Defer part of speech tagging until feature generation
        show_debug_output : bool, optional
            If True, print out each stage of the sentence normalisation

        """
        self.show_debug_output = show_debug_output
        self.input: str = input_sentence
        self.sentence: str = self._normalise(input_sentence)

        _tokenised_sentence = REGEXP_TOKENIZER.tokenize(self.sentence)
        (
            self.tokenized_sentence,
            self.singularised_indices,
        ) = self._singlarise_units(_tokenised_sentence)

        self.defer_pos_tagging: bool = defer_pos_tagging
        if not defer_pos_tagging:
            self.pos_tags: list[str] = self._tag_partofspeech(self.tokenized_sentence)
        else:
            self.pos_tags = []

    def __repr__(self) -> str:
        """__repr__ method

        Returns
        -------
        str
            String representation of initialised object
        """
        return f'PreProcessor("{self.input}")'

    def __str__(self) -> str:
        """__str__ method

        Returns
        -------
        str
            Human readable string representation of object
        """
        _str = [
            "Pre-processed recipe ingredient sentence",
            f"\t    Input: {self.input}",
            f"\t  Cleaned: {self.sentence}",
            f"\tTokenized: {self.tokenized_sentence}",
        ]
        return "\n".join(_str)

    def _normalise(self, sentence: str) -> str:
        """Normalise sentence prior to feature extraction

        Parameters
        ----------
        sentence : str
            Ingredient sentence

        Returns
        -------
        str
            Normalised ingredient sentence
        """
        # List of functions to apply to sentence
        # Note that the order matters
        funcs = [
            self._replace_en_em_dash,
            self._replace_string_numbers,
            self._replace_html_fractions,
            self._replace_unicode_fractions,
            self._replace_fake_fractions,
            self._split_quantity_and_units,
            self._remove_unit_trailing_period,
            self._replace_string_range,
        ]

        for func in funcs:
            sentence = func(sentence)

            if self.show_debug_output:
                print(f"{func.__name__}: {sentence}")

        return sentence.strip()

    def _replace_en_em_dash(self, sentence: str) -> str:
        """Replace en-dashes and em-dashes with hyphens.

        Parameters
        ----------
        sentence : str
            Ingredient sentence

        Returns
        -------
        str
            Ingredient sentence with en and em dashes replaced with hyphens

        Examples
        --------
        >>> p = PreProcessor("")
        >>> p._replace_en_em_dash("2 cups flour – white or self-raising")
        "2 cups flour - white or self-raising"

        >>> p = PreProcessor("")
        >>> p._replace_en_em_dash("3–4 sirloin steaks")
        "3-4 sirloin steaks"
        """
        return sentence.replace("–", "-").replace("—", "-")

    def _replace_string_numbers(self, sentence: str) -> str:
        """Replace string numbers (e.g. one, two) with numeric values (e.g. 1, 2)

        Parameters
        ----------
        sentence : str
            Ingredient sentence

        Returns
        -------
        str
            Ingredient sentence with string numbers replace with numeric values

        Examples
        --------
        >>> p = PreProcessor("")
        >>> p._replace_string_numbers("three large onions")
        "3 large onions"

        >>> p = PreProcessor("")
        >>> p._replace_string_numbers("twelve bonbons")
        "12 bonbons"
        """

        # STRING_NUMBER_REGEXES is a dict where the values are a tuple of the compiled
        # regular expression for matching a string number e.g. 'one', 'two' and the
        # substitution numerical value for that string number.
        for regex, substitution in STRING_NUMBERS_REGEXES.values():
            sentence = regex.sub(rf"{substitution}", sentence)

        return sentence

    def _replace_html_fractions(self, sentence: str) -> str:
        """Replace html fractions e.g. &frac12; with unicode equivalents

        Parameters
        ----------
        sentence : str
            Ingredient sentence

        Returns
        -------
        str
            Ingredient sentence with html fractions replaced

        Examples
        --------
        >>> p = PreProcessor("")
        >>> p._replace_html_fractions("1&frac34; cups tomato ketchup")
        "1¾ cups tomato ketchup"
        """
        return unescape(sentence)

    def _replace_fake_fractions(self, sentence: str) -> str:
        """Attempt to parse fractions from sentence and convert to decimal
        This looks for fractions with the format of 1/2, 1/4, 1 1/2 etc.

        Parameters
        ----------
        sentence : str
            Ingredient sentence

        Returns
        -------
        str
            Ingredient sentence with fractions replaced with decimals

        Examples
        --------
        >>> p = PreProcessor("")
        >>> p._replace_fake_fractions("1/2 cup icing sugar")
        "0.5 cup icing sugar"

        >>> p = PreProcessor("")
        >>> p._replace_fake_fractions("2 3/4 pound chickpeas")
        "2.75 pound chickpeas"
        """
        matches = FRACTION_PARTS_PATTERN.findall(sentence)

        if not matches:
            return sentence

        # This is a bit of a hack.
        # If a fraction appears multiple times but in different forms e.g. 1/2 and
        # 1 1/2, then
        # we need to replace the longest one first, otherwise both instance of 1/2
        # would be replaced at the same time which would mean that the instance of
        # 1 1/2 would end up as 1 0.5 instead of 1.5
        # Before we sort, we need to strip any space from the start and end.
        matches = [match.strip() for match in matches]
        matches.sort(key=len, reverse=True)

        for match in matches:
            split = match.split()
            summed = float(sum(Fraction(s) for s in split))
            rounded = round(summed, 3)
            sentence = sentence.replace(match, f"{rounded:g}")

        return sentence

    def _replace_unicode_fractions(self, sentence: str) -> str:
        """Replace unicode fractions with a 'fake' ascii equivalent.
        The ascii equivalent is used because the replace_fake_fractions function can
        deal with spaces between an integer and the fraction.

        Parameters
        ----------
        sentence : str
            Ingredient sentence

        Returns
        -------
        str
            Ingredient sentence with unicode fractions replaced

        Examples
        --------
        >>> p = PreProcessor("")
        >>> p._replace_unicode_fractions("½ cup icing sugar")
        "1/2 cup icing sugar"

        >>> p = PreProcessor("")
        >>> p._replace_unicode_fractions("3⅓ cups warm water")
        "3 1/3 cups warm water"
        """
        fractions = {
            "\u215b": "1/8",
            "\u215c": "3/8",
            "\u215d": "5/8",
            "\u215e": "7/8",
            "\u2159": "1/6",
            "\u215a": "5/6",
            "\u2155": "1/5",
            "\u2156": "2/5",
            "\u2157": "3/5",
            "\u2158": "4/5",
            "\xbc": "1/4",
            "\xbe": "3/4",
            "\u2153": "1/3",
            "\u2154": "2/3",
            "\xbd": "1/2",
        }
        for f_unicode, f_ascii in fractions.items():
            # Insert space before ascii fraction to avoid merging into the
            # previous token.
            sentence = sentence.replace(f_unicode, f" {f_ascii}")

        # Because we inserted the space before the fake fraction, we might have broken
        # some ranges by adding a space after the hyphen, so let's fix that.
        sentence = BROKEN_RANGE_PATTERN.sub(r"\1\2", sentence)

        return sentence

    def _split_quantity_and_units(self, sentence: str) -> str:
        """Insert space between quantity and unit
        This currently finds any instances of a number followed directly by a letter
        with no space in between.

        Parameters
        ----------
        sentence : str
            Ingredient sentence

        Returns
        -------
        str
            Ingredient sentence with spaces inserted between quantity and units

        Examples
        --------
        >>> p = PreProcessor("")
        >>> p._split_quantity_and_units("100g green beans")
        "100 g green beans"

        >>> p = PreProcessor("")
        >>> p._split_quantity_and_units("2-pound red peppers, sliced")
        "2 pound red peppers, sliced"
        """
        return QUANTITY_UNITS_PATTERN.sub(r"\1 \2", sentence)

    def _remove_unit_trailing_period(self, sentence: str) -> str:
        """Remove trailing periods from units e.g. tsp. -> tsp

        Parameters
        ----------
        sentence : str
            Ingredient sentence

        Returns
        -------
        str
            Ingredient sentence with trailing periods from units removed

        Examples
        --------
        >>> p = PreProcessor("")
        >>> p._remove_unit_trailing_period("1 tsp. garlic powder")
        "1 tsp garlic powder"

        >>> p = PreProcessor("")
        >>> p._remove_unit_trailing_period("5 oz. chopped tomatoes")
        "5 oz chopped tomatoes"
        """
        units = ["tsp.", "tsps.", "tbsp.", "tbsps.", "lb.", "lbs.", "oz."]
        units.extend([u.capitalize() for u in units])
        for unit in units:
            unit_no_period = unit.replace(".", "")
            sentence = sentence.replace(unit, unit_no_period)

        return sentence

    def _replace_string_range(self, sentence: str) -> str:
        """Replace range in the form "<num> to <num" with
        standardised range "<num>-<num>".

        For example
        -----------
        1 to 2 -> 1-2
        8.5 to 12.5 -> 8.5-12.5
        16- to 9-

        Parameters
        ----------
        sentence : str
            Ingredient sentence

        Returns
        -------
        str
            Ingredient sentence with string ranges replaced with standardised range

        Examples
        --------
        >>> p = PreProcessor("")
        >>> p._replace_string_range("1 to 2 mashed bananas")
        "1-2 mashed bananas"

        >>> p = PreProcessor("")
        >>> p._replace_string_range("4- or 6- large apples")
        "5-6 large apples"
        """
        return STRING_RANGE_PATTERN.sub(r"\1-\5", sentence)

    def _singlarise_units(
        self, tokenised_sentence: list[str]
    ) -> tuple[list[str], list[int]]:
        """Singularise units in tokenised sentence and return list of singularised
        indices e.g. cups -> cup, tablespoons -> tablespoon

        Parameters
        ----------
        tokenised_sentence : list[str]
            Tokenised sentence

        Returns
        -------
        list[str]
            Tokenised sentence with units singularised
        list[int]
            List of indices of tokenised sentence that have been singularised
        """
        singularised_indices = []
        for idx, token in enumerate(tokenised_sentence):
            singular = UNITS.get(token, None)
            if singular is not None:
                tokenised_sentence[idx] = singular
                singularised_indices.append(idx)

        return (tokenised_sentence, singularised_indices)

    def _tag_partofspeech(self, tokens: list[str]) -> list[str]:
        """Tag tokens with part of speech using universal tagset

        This function manually fixes tags that are incorrect in the context of
        ----------------------------------------------------------------------
        1. Change tags of numeric ranges to CD
        2. Change tag of "ground" from NN to VBD e.g. ground almonds


        Parameters
        ----------
        tokens : list[str]
            Tokenized ingredient sentence

        Returns
        -------
        list[str]
            List of part of speech tags
        """
        tags = []
        # If we don't make each token lower case, that POS tag maybe different in
        # ways that are unhelpful. For example, if a sentence starts with a unit.
        for token, tag in pos_tag([t.lower() for t in tokens]):
            if RANGE_PATTERN.match(token):
                tag = "CD"
            if token in ["ground"]:
                tag = "VBD"
            tags.append(tag)
        return tags

    def _is_unit(self, token: str) -> bool:
        """Return True if token is a unit

        Parameters
        ----------
        token : str
            Token to check

        Returns
        -------
        bool
            True if token is a unit, else False

        Examples
        --------
        >>> p = PreProcessor("")
        >>> p._is_unit("cup")
        True

        >>> p = PreProcessor("")
        >>> p._is_unit("beef")
        False
        """
        return token.lower() in UNITS.values()

    def _is_numeric(self, token: str) -> bool:
        """Return True if token is numeric

        Parameters
        ----------
        token : str
            Token to check

        Returns
        -------
        bool
            True if token is numeric, else False

        Examples
        --------
        >>> p = PreProcessor("")
        >>> p._is_numeric("1")
        True

        >>> p = PreProcessor("")
        >>> p._is_numeric("1-2")
        True

        >>> p = PreProcessor("")
        >>> p._is_numeric("dozen")
        True

        >>> p = PreProcessor("")
        >>> p._is_numeric("beef")
        False
        """
        if "-" in token:
            parts = token.split("-")
            return all([self._is_numeric(part) for part in parts])

        if token == "dozen":
            return True

        try:
            float(token)
            return True
        except ValueError:
            return False

    def _follows_comma(self, index: int) -> bool:
        """Return True if token at index follows a comma (by any amount) in sentence
        If the token at index is a comma, treat it the same as any other token

        Parameters
        ----------
        index : int
            Index of token to check

        Returns
        -------
        bool
            True if token follows comma, else False
        """
        return "," in self.tokenized_sentence[:index]

    def _follows_plus(self, index: int) -> bool:
        """Return True if token at index follow "plus" by any amount in sentence.
        If the token at the index is "plus", it doesn't count as following.

        Parameters
        ----------
        index : int
            Index of token to check

        Returns
        -------
        bool
            True if token follows "plus", else False
        """
        return "plus" in self.tokenized_sentence[:index]

    def _is_capitalised(self, token: str) -> bool:
        """Return True if token starts with a capital letter

        Parameters
        ----------
        token : str
            Token to check

        Returns
        -------
        bool
            True if token starts with a capital letter, else False

        Examples
        --------
        >>> p = PreProcessor("")
        >>> p._is_capitalised("Chicken")
        True

        >>> p = PreProcessor("")
        >>> p._is_capitalised("chicken")
        False
        """
        return CAPITALISED_PATTERN.match(token) is not None

    def _is_inside_parentheses(self, index: int) -> bool:
        """Return True if token is inside parentheses within the sentence or is a
        parenthesis.

        Parameters
        ----------
        index : int
            Index of token to check

        Returns
        -------
        bool
            True if index is inside parentheses or is parenthesis, else False
        """
        # If it's "(" or ")", return True
        if self.tokenized_sentence[index] in ["(", ")", "[", "]"]:
            return True

        open_parens, closed_parens = [], []
        for i, token in enumerate((self.tokenized_sentence)):
            if token == "(" or token == "[":
                open_parens.append(i)
            elif token == ")" or token == "]":
                closed_parens.append(i)

        for start, end in zip(open_parens, closed_parens):
            if start < index < end:
                return True

        return False

    def _is_ambiguous_unit(self, token: str) -> bool:
        """Return True if token is in AMBIGUOUS_UNITS list

        Parameters
        ----------
        token : str
            Token to check

        Returns
        -------
        bool
            True if token is in AMBIGUOUS_UNITS, else False

        Examples
        --------
        >>> p = PreProcessor("")
        >>> p._is_ambiguous_unit("cloves")
        True

        >>> p = PreProcessor("")
        >>> p._is_ambiguous_unit("wedge")
        True

        >>> p = PreProcessor("")
        >>> p._is_ambiguous_unit("leaf")
        True
        """
        return token in AMBIGUOUS_UNITS

    def _token_features(self, index: int) -> dict[str, str | bool]:
        """Return the features for each token in the sentence

        Parameters
        ----------
        index : int
            Index of token to get features for.

        Returns
        -------
        dict[str, Any]
            Dictionary of features for token at index
        """
        token = self.tokenized_sentence[index]
        features = {
            "stem": STEMMER.stem(token),
            "pos": self.pos_tags[index],
            "is_capitalised": self._is_capitalised(token),
            "is_numeric": self._is_numeric(token),
            "is_unit": self._is_unit(token),
            "is_ambiguous": self._is_ambiguous_unit(token),
            "is_in_parens": self._is_inside_parentheses(index),
            "is_after_comma": self._follows_comma(index),
            "is_after_plus": self._follows_plus(index),
        }

        if index > 0:
            features["prev_pos"] = self.pos_tags[index - 1]
            features["prev_word"] = STEMMER.stem(self.tokenized_sentence[index - 1])

        if index > 1:
            features["prev_pos2"] = self.pos_tags[index - 2]
            features["prev_word2"] = STEMMER.stem(self.tokenized_sentence[index - 2])

        if index < len(self.tokenized_sentence) - 1:
            features["next_pos"] = self.pos_tags[index + 1]
            features["next_word"] = STEMMER.stem(self.tokenized_sentence[index + 1])

        if index < len(self.tokenized_sentence) - 2:
            features["next_pos2"] = self.pos_tags[index + 2]
            features["next_word2"] = STEMMER.stem(self.tokenized_sentence[index + 2])

        return features

    def sentence_features(self) -> list[dict[str, Any]]:
        """Return features for all tokens in sentence

        Returns
        -------
        list[dict[str, Any]]
            List of features for each token in sentence
        """
        if self.defer_pos_tagging:
            # If part of speech tagging was deferred, do it now
            self.pos_tags = self._tag_partofspeech(self.tokenized_sentence)

        features = []
        for idx, _ in enumerate(self.tokenized_sentence):
            features.append(self._token_features(idx))

        return features
