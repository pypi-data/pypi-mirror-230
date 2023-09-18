import math


class Primes:
    @staticmethod
    def up_to(max):
        """Calculates all prime numbers up to a maximum value using the Sieve of Eratosthenes method"""

        potentials = list(range(2, max + 1))

        for i in range(2, int(math.sqrt(max)) + 1):
            for j in range(2, int(max / i) + 1):
                if (i * j) in potentials:
                    potentials.remove(i * j)

        return potentials

    @staticmethod
    def include(num):
        return num > 1 and not any(
            [num % i == 0 for i in range(2, int(math.sqrt(num) + 1))]
        )
