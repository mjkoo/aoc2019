#!/usr/bin/env python3
import itertools
import re
import sys

from copy import deepcopy
from functools import reduce
from math import gcd


class Vec3D:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Vec3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __repr__(self):
        return f"(x={self.x}, y={self.y}, z={self.z})"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def energy(self):
        return abs(self.x) + abs(self.y) + abs(self.z)


class Moon:
    def __init__(self, pos):
        self.pos = pos
        self.vel = Vec3D(0, 0, 0)

    def __repr__(self):
        return f"Moon(pos={self.pos}, vel={self.vel})"

    def update_gravity(self, other):
        def delta(x0, x1):
            if x0 > x1:
                return -1
            elif x1 > x0:
                return 1
            else:
                return 0

        self.vel.x += delta(self.pos.x, other.pos.x)
        self.vel.y += delta(self.pos.y, other.pos.y)
        self.vel.z += delta(self.pos.z, other.pos.z)

    def apply_velocity(self):
        self.pos += self.vel

    def potential_energy(self):
        return self.pos.energy()

    def kinetic_energy(self):
        return self.vel.energy()

    def total_energy(self):
        return self.potential_energy() * self.kinetic_energy()


def step(moons):
    for m0, m1 in itertools.combinations_with_replacement(moons, 2):
        m0.update_gravity(m1)
        m1.update_gravity(m0)

    for m in moons:
        m.apply_velocity()


def lcm(*n):
    return reduce(lambda a, b: a * b // gcd(a, b), n)


def find_cycle(moons):
    def _find_cycle(start):
        moons = deepcopy(start)

        step(moons)
        count = 1
        while not all(m.pos == s.pos and m.vel == s.vel for m, s in zip(moons, start)):
            step(moons)
            count += 1

        return count

    # Calculate each axis separately
    x_moons = [Moon(Vec3D(m.pos.x, 0, 0)) for m in moons]
    x_steps = _find_cycle(x_moons)
    y_moons = [Moon(Vec3D(0, m.pos.y, 0)) for m in moons]
    y_steps = _find_cycle(y_moons)
    z_moons = [Moon(Vec3D(0, 0, m.pos.z)) for m in moons]
    z_steps = _find_cycle(z_moons)

    return lcm(x_steps, y_steps, z_steps)


def main(argv):
    moons = []
    line_re = re.compile(r"^<x=(?P<x>-?\d+), y=(?P<y>-?\d+), z=(?P<z>-?\d+)>$")
    with open(argv[1], "r") as f:
        for line in f:
            m = line_re.match(line)
            if not m:
                print("Invalid input format")
                sys.exit(1)

            x = int(m.group("x"))
            y = int(m.group("y"))
            z = int(m.group("z"))
            moons.append(Moon(Vec3D(x, y, z)))

    part_1_moons = deepcopy(moons)
    for _ in range(1000):
        step(part_1_moons)
    print(sum(m.total_energy() for m in part_1_moons))

    part_2_moons = deepcopy(moons)
    print(find_cycle(part_2_moons))


if __name__ == "__main__":
    main(sys.argv)
