#!/usr/bin/env python3
import sys

WIDTH = 25
HEIGHT = 6


def main(argv):
    with open(argv[1], "r") as f:
        img = [int(c) for c in f.read().strip()]

    layer_size = WIDTH * HEIGHT
    layers = [img[i : i + layer_size] for i in range(0, len(img), layer_size)]
    selected_layer = min(layers, key=lambda l: l.count(0))

    print(selected_layer.count(1) * selected_layer.count(2))

    composite = [next(p for p in pixel if p != 2) for pixel in zip(*layers)]
    rendered = "\n".join(
        "".join(" " if p == 0 else "X" for p in composite[i : i + WIDTH])
        for i in range(0, len(composite), WIDTH)
    )

    print(rendered)


if __name__ == "__main__":
    main(sys.argv)
