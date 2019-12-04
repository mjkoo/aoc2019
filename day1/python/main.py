#!/usr/bin/env python3
import sys


def calc_fuel(mass):
    return mass // 3 - 2


def total_fuel(mass):
    def iter_fuel(mass):
        fuel = calc_fuel(mass)
        while fuel > 0:
            yield fuel
            fuel = calc_fuel(fuel)

    return sum(iter_fuel(mass))


def main(argv):
    with open(argv[1], "r") as f:
        masses = [int(line) for line in f]

    print(sum(calc_fuel(mass) for mass in masses))
    print(sum(total_fuel(mass) for mass in masses))


if __name__ == "__main__":
    main(sys.argv)
