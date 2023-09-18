from .comparators import div_mod


class Numbertext(int):
    def __init__(self, value):
        self._value = value

    def __int__(self):
        return self._value

    def __repr__(self):
        if self == 0:
            return Numbertext.Units[self]

        clause = ""
        large_exponents = Numbertext._generate_large_exponents()
        large_exponent = 10 ** (self._exponent // 3 * 3)
        to_process, to_save = self << div_mod >> large_exponent
        hundreds, rem = to_process << div_mod >> 100
        tens, units = rem << div_mod >> 10

        if hundreds:
            clause += f"{Numbertext.Units[hundreds]} {Numbertext.Hundred}"
        if hundreds and rem:
            clause += " and "
        if rem:
            if rem < 10:
                clause += Numbertext.Units[units]
            elif rem < 20:
                clause += Numbertext.Teens[units]
            elif units:
                clause += f"{Numbertext.Tens[tens]}-{Numbertext.Units[units]}"
            else:
                clause += Numbertext.Tens[tens]
        if large_exponent > 1:
            clause += f" {large_exponents[self._exponent // 3 - 1]}"

        if to_save:
            further_clauses = repr(Numbertext(to_save))
            conj = "," if " and " in further_clauses or self % 1000 == 0 else " and"
            return f"{clause}{conj} {further_clauses}"
        else:
            return clause

    @property
    def _exponent(self):
        return len(str(self._value)) - 1

    @staticmethod
    def _generate_large_exponents():
        swaps = {
            "sesd": "sed",
            "env": "emv",
            "nn": "n",
            "ret": "rest",
            "rev": "resv",
        }

        output = [*Numbertext.LargeExponents]

        for suffix in Numbertext.LargerSuffixes:
            for prefix in Numbertext.LargerPrefixes:
                word = f"{prefix}{suffix}illion"
                for k, v in swaps.items():
                    word = word.replace(k, v)
                output.append(word)

        return output

    Units = (
        "zero",
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine",
    )
    Teens = (
        "ten",
        "eleven",
        "twelve",
        "thirteen",
        "fourteen",
        "fifteen",
        "sixteen",
        "seventeen",
        "eighteen",
        "nineteen",
    )
    Tens = (
        "none",
        "ten",
        "twenty",
        "thirty",
        "forty",
        "fifty",
        "sixty",
        "seventy",
        "eighty",
        "ninety",
    )
    Hundred = "hundred"
    LargeExponents = (
        "thousand",
        "million",
        "billion",
        "trillion",
        "quadrillion",
        "quintillion",
        "sextillion",
        "septillion",
        "octillion",
        "nonillion",
    )
    LargerPrefixes = (
        "",
        "un",
        "duo",
        "tre",
        "quattuor",
        "quin",
        "ses",
        "septen",
        "octo",
        "noven",
    )
    LargerSuffixes = (
        "dec",
        "vigint",
        "trigint",
        "quadragint",
        "quinquagint",
        "sexagint",
        "septuagint",
        "octogint",
        "nonagint",
    )
