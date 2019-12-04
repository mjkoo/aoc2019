#!/usr/bin/env python3
import sys


def is_valid(x, low, high, part1):
    digits = [int(c) for c in str(x)]

    if len(digits) != 6:
        return False

    if x < low or x > high:
        return False

    if not any(digits[i] == digits[i - 1] for i in range(1, 6)):
        return False

    if any(digits[i] < digits[i - 1] for i in range(1, 6)):
        return False

    if not part1:
        runs = []
        for d in digits:
            if not runs or d != runs[-1][0]:
                runs.append((d, 1))
            else:
                runs[-1] = (d, runs[-1][1] + 1)

        if not any(r[1] == 2 for r in runs):
            return False

    return True


def main(argv):
    with open(argv[1], "r") as f:
        low, high = (int(x) for x in f.read().split("-"))

    candidates = [x for x in range(low, high + 1) if is_valid(x, low, high, True)]
    print(len(candidates))

    candidates = [x for x in range(low, high + 1) if is_valid(x, low, high, False)]
    print(len(candidates))


if __name__ == "__main__":
    main(sys.argv)
