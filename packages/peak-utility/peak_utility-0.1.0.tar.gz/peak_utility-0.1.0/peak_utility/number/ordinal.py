from collections import defaultdict
from .numbertext import Numbertext


class Ordinal(int):
    REGEX = r"\d+(?:st|nd|rd|th)"

    def __new__(cls, value):
        return int.__new__(cls, value)

    def __repr__(self):
        return f"{int(self)}{self._suffix}"

    def __str__(self):
        stem = str(Numbertext(int(self)))

        swaps = {
            "one": "fir",
            "two": "seco",
            "three": "thi",
            "ve": "f",
            "ne": "n",
            "ty": "tie",
        }

        for k, v in swaps.items():
            if stem[-len(k) :] == k:
                stem = stem[: -len(k)] + v

        return (stem + self._suffix).replace("tt", "t")

    @property
    def _suffix(self):
        SUFFIXES = defaultdict(lambda: "th")
        SUFFIXES[1] = "st"
        SUFFIXES[2] = "nd"
        SUFFIXES[3] = "rd"

        return SUFFIXES[self % 100 if self % 100 < 20 else self % 10]
