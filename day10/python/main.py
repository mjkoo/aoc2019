#!/usr/bin/env python3
import math
import sys

from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])


def is_point_on_line(origin, dest, test):
    if dest.x == origin.x:
        return True

    a = (dest.y - origin.y) / (dest.x - origin.x)
    # (y - y_0) = a * (x - x_0) => y = a * x - (a * x_0 + y_0)
    b = a * origin.x + origin.y
    return math.isclose(test.y, a * test.x + b)


def distance(origin, dest):
    return math.sqrt((dest.x - origin.x) ** 2 + (dest.y - origin.y) ** 2)


def num_visible(origin, asteroids):
    count = 0
    for dest in asteroids:
        if dest == origin:
            continue

        visible = True
        for test in asteroids:
            if test == origin or test == dest:
                continue

            on_line = is_point_on_line(origin, dest, test)
            closer = distance(origin, dest) > distance(origin, test)
            if on_line and closer:
                visible = False

        if visible:
            count += 1

    print(origin, count)
    return count


def slope(origin, dest):
    if dest.x != origin.x:
        return (dest.y - origin.y) / (dest.x - origin.x)
    else:
        return float("inf")


def visible(origin, asteroids):
    ret = len({slope(origin, dest) for dest in asteroids if dest != origin})
    print(origin, ret)
    return ret


def main(argv):
    with open(argv[1], "r") as f:
        asteroids = {
            Point(x, y)
            for y, row in enumerate(f.readlines())
            for x, cell in enumerate(row)
            if cell == "#"
        }

    print(len(asteroids))
    #print(sorted(asteroids))
    best = max(visible(origin, asteroids) for origin in asteroids)
    print(best)


if __name__ == "__main__":
    main(sys.argv)
