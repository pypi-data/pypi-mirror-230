#!/usr/bin/env python3

import re

# Plural and singular units
UNITS = {
    "bags": "bag",
    "bars": "bar",
    "baskets": "basket",
    "batches": "batch",
    "blocks": "block",
    "bottles": "bottle",
    "boxes": "box",
    "branches": "branch",
    "bulbs": "bulb",
    "bunches": "bunch",
    "bundles": "bundle",
    "cans": "can",
    "chops": "chop",
    "chunks": "chunk",
    "cloves": "clove",
    "clusters": "cluster",
    "cm": "cm",
    "cubes": "cube",
    "cups": "cup",
    "cutlets": "cutlet",
    "dashes": "dash",
    "dollops": "dollop",
    "drops": "drop",
    "ears": "ear",
    "envelopes": "envelope",
    "feet": "foot",
    "fillets": "fillet",
    "g": "g",
    "gallons": "gallon",
    "glasses": "glass",
    "grams": "gram",
    "grinds": "grind",
    "handfuls": "handful",
    "heads": "head",
    "inches": "inch",
    "jars": "jar",
    "kg": "kg",
    "kilograms": "kilogram",
    "knobs": "knob",
    "lbs": "lb",
    "leaves": "leaf",
    "lengths": "length",
    "links": "link",
    "l": "l",
    "liters": "liter",
    "litres": "litre",
    "loaves": "loaf",
    "milliliters": "milliliter",
    "ml": "ml",
    "mugs": "mug",
    "ounces": "ounce",
    "oz": "oz",
    "packs": "pack",
    "packages": "package",
    "packets": "packet",
    "pairs": "pair",
    "pieces": "piece",
    "pinches": "pinch",
    "pints": "pint",
    "pods": "pod",
    "pounds": "pound",
    "racks": "rack",
    "rashers": "rasher",
    "recipes": "recipe",
    "rectangles": "rectangle",
    "ribs": "rib",
    "quarts": "quart",
    "scoops": "scoop",
    "segments": "segment",
    "shakes": "shake",
    "sheets": "sheet",
    "shots": "shot",
    "shoots": "shoot",
    "slabs": "slab",
    "slices": "slice",
    "sprigs": "sprig",
    "squares": "square",
    "stalks": "stalk",
    "steaks": "steak",
    "stems": "stem",
    "sticks": "stick",
    "strips": "strip",
    "tablespoons": "tablespoon",
    "tbsps": "tbsp",
    "tbs": "tb",
    "teaspoons": "teaspoon",
    "tsps": "tsp",
    "twists": "twist",
    "wedges": "wedge",
    "wheels": "wheel",
}
# Generate capitalized version of each entry in the UNITS dictionary
_capitalized_units = {}
for plural, singular in UNITS.items():
    _capitalized_units[plural.capitalize()] = singular.capitalize()
UNITS = UNITS | _capitalized_units

# Words that can modify a unit
UNIT_MODIFIERS = [
    "big",
    "fat",
    "generous",
    "healthy",
    "heaped",
    "heaping",
    "large",
    "medium",
    "medium-size",
    "medium-sized",
    "scant",
    "small",
    "thick",
    "thin",
]

# Units that can be part of the name
# e.g. 1 teaspoon ground cloves, or 5 bay leaves
AMBIGUOUS_UNITS = [
    "cloves",
    "leaves",
    "slabs",
    "wedges",
]
# Extend list automatically to include singular and capitalized forms
_ambiguous_units_alt_forms = []
for amb_unit in AMBIGUOUS_UNITS:
    _ambiguous_units_alt_forms.append(amb_unit.capitalize())
    _ambiguous_units_alt_forms.append(UNITS[amb_unit])
    _ambiguous_units_alt_forms.append(UNITS[amb_unit.capitalize()])

AMBIGUOUS_UNITS.extend(_ambiguous_units_alt_forms)


# Strings and their numeric representation
STRING_NUMBERS = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "eleven": "11",
    "twelve": "12",
    "thirteen": "13",
    "fourteen": "14",
    "fifteen": "15",
    "sixteen": "16",
    "seventeen": "17",
    "eighteen": "18",
    "nineteen": "19",
}
# Precompile the regular expressions for matching the string numbers
STRING_NUMBERS_REGEXES = {}
for s, n in STRING_NUMBERS.items():
    # This is case insensitive so it replace e.g. "one" and "One"
    # Only match if the string is preceded by a non-word character or is at
    # the start of the sentence
    STRING_NUMBERS_REGEXES[s] = (re.compile(rf"\b({s})\b", flags=re.IGNORECASE), n)
