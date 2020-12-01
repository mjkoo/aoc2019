#!/usr/bin/env python3
import re
import sys

from collections import defaultdict


def produce(amount, product, recipes, stock):
    if product == "ORE":
        return

    per_batch, recipe = recipes[product]
    required = amount - stock[product]

    if required > 0:
        batches, r = divmod(required, per_batch)
        batches += 1 if r else 0

        for a, i in recipe:
            produce(a * batches, i, recipes, stock)
            stock[i] -= a * batches

        stock[product] += batches * per_batch


def main(argv):
    recipes = {}
    with open(argv[1], "r") as f:
        for line in f:
            terms = re.findall(r"(\d+) ([A-Z]+)", line)

            per_batch, product = terms[-1]
            recipes[product] = (
                int(per_batch),
                [(int(amount), ingredient) for amount, ingredient in terms[:-1]],
            )

    print(recipes)
    stock = defaultdict(int)
    produce(1, "FUEL", recipes, stock)
    print(-stock["ORE"])

    for i in range(2125000, 2250000):
        stock = defaultdict(int)
        produce(i, "FUEL", recipes, stock)
        if -stock["ORE"] > 1000000000000:
            print(i - 1)
            break


if __name__ == "__main__":
    main(sys.argv)
