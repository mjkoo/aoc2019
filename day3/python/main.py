#!/usr/bin/env python3
import sys


DIRECTIONS = {"U": (0, 1), "D": (0, -1), "R": (1, 0), "L": (-1, 0)}


class Wire:
    def __init__(self, steps):
        self.inner = {}
        pos = (0, 0)
        num_steps = 0

        for s in steps:
            direction = s[0]
            distance = int(s[1:])

            for _ in range(distance):
                num_steps += 1
                pos = tuple(map(sum, zip(pos, DIRECTIONS[direction])))
                if pos not in self.inner:
                    self.inner[pos] = num_steps

    def points(self):
        return set(self.inner.keys())

    def num_steps(self, point):
        return self.inner[point]


def main(argv):
    with open(argv[1], "r") as f:
        wires = [Wire(line.split(",")) for line in f]

    intersections = set.intersection(*[w.points() for w in wires])
    min_distance = min(abs(x) + abs(y) for (x, y) in intersections)
    print(min_distance)

    min_signal_delay = min(
        sum(w.num_steps(pos) for w in wires) for pos in intersections
    )
    print(min_signal_delay)


if __name__ == "__main__":
    main(sys.argv)
