from infix import shift_infix as infix  # type: ignore
from .primes import Primes


@infix
def div_mod(num, divisor):
    return (num // divisor, num % divisor)


def have_common_divisor(num1, num2):
    if num1 == num2:
        return True
    if Primes.include(max(num1, num2)):
        return False
    for testnum in Primes.up_to(min(num1, num2)):
        if num1 % testnum == 0 and num2 % testnum == 0:
            return True
    return False
