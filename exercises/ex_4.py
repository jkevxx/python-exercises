"""
Programa un lanzamiento de "Heads or Tails" trucado para que salga "Heads" más veces
"""

import random

dictResults = {'heads': 0, 'tails': 0}
# print(f"Before -> {dictResults['tails']}")
# print(f"Before -> {dictResults.keys()}")


def launching():
    if random.random() < 0.7:
        return 'heads'
    return 'tails'


for x in range(10):
    result = launching()
    dictResults[result] += 1
    print(result)

print(f"After {dictResults}")
