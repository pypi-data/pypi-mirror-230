from enum import Enum


class Roman(int):
    class Numeral(Enum):
        I = 1, "\u2160"
        V = 5, "\u2164"
        X = 10, "\u2169"
        L = 50, "\u216C"
        C = 100, "\u216D"
        D = 500, "\u216E"
        M = 1000, "\u216F"

        def __new__(cls, *args):
            obj = object.__new__(cls)
            obj._value_ = args[0]
            return obj

        def __init__(self, _, unicode):
            self._unicode = unicode

        def __repr__(self):
            return self._unicode

        def __str__(self):
            return self.name

        def __int__(self):
            return self.value

        def __add__(self, other):
            return int(self) + other

        def __radd__(self, other):
            return self.__add__(other)

        def __eq__(self, other):
            return int(self) == other

        def __lt__(self, other):
            return int(self) < other

        def __gt__(self, other):
            return int(self) < other

    def __new__(cls, value):
        if not 0 < value < 4000:
            raise ValueError("value out of range for Roman numerals")
        return int.__new__(cls, value)

    def __repr__(self):
        return "".join([repr(x) for x in self._numerals])

    def __str__(self):
        return "".join([str(x) for x in self._numerals])

    @property
    def _numerals(self):
        numerals = []
        rem = self
        unit = 1000

        while unit >= 1:
            digit = rem // unit
            rem = rem % unit

            if digit == 4:
                numerals += [Roman.Numeral(unit), Roman.Numeral(unit * 5)]
            elif digit == 9:
                numerals += [Roman.Numeral(unit), Roman.Numeral(unit * 10)]
            else:
                ones = digit % 5
                if unit < 1000 and digit >= 5:
                    numerals += [Roman.Numeral(unit * 5)]
                numerals += [Roman.Numeral(unit) for _ in range(ones)]

            unit = unit // 10

        return numerals

    @classmethod
    def parse(cls, roman_numerals):
        symbol_to_alpha = {repr(x): str(x) for x in Roman.Numeral}
        individual_numerals = [
            Roman.Numeral.__members__.get(x, None) or Roman.Numeral[symbol_to_alpha[x]]
            for x in list(roman_numerals)
        ]

        sum = 0
        for index, numeral in enumerate(individual_numerals):
            not_last_numeral = index != len(individual_numerals) - 1
            if (
                not_last_numeral
                and numeral.value < individual_numerals[index + 1].value
            ):
                sum -= numeral.value
            else:
                sum += numeral.value

        return cls(sum)
