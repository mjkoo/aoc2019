#!/usr/bin/env python3
import sys


def path_to_com(orbits, source):
    ret = []
    cur = source
    while cur != "COM":
        ret.append(cur)
        cur = orbits[cur]
    return ret


def num_transfers(orbits, source, dest):
    # Ignore YOU and SAN
    source_to_com = path_to_com(orbits, source)[1:]
    dest_to_com = path_to_com(orbits, dest)[1:]

    prefix_len = 0
    for a, b in zip(reversed(source_to_com), reversed(dest_to_com)):
        if a == b:
            prefix_len += 1

    # Strip common suffix, add one for rendezvous point, subtract one to get
    # number of transfers rather than number of stops
    return len(source_to_com) + len(dest_to_com) - 2 * prefix_len


def main(argv):
    orbits = {}
    with open(argv[1], "r") as f:
        for line in f:
            parent, child = line.strip().split(")")
            orbits[child] = parent

    count = 0
    for obj in orbits.keys():
        cur = obj
        while cur != "COM":
            count += 1
            cur = orbits[cur]

    print(count)
    print(num_transfers(orbits, "YOU", "SAN"))


if __name__ == "__main__":
    main(sys.argv)
