#!/usr/bin/env python3
import operator
import sys

TARGET = 19690720


def intcode(mem):
    def alu(pc, op):
        mem[mem[pc + 3]] = op(mem[mem[pc + 1]], mem[mem[pc + 2]])
        return 4

    opcodes = {
        1: lambda pc: alu(pc, operator.add),
        2: lambda pc: alu(pc, operator.mul),
        99: lambda pc: -1,
    }

    pc = 0
    while True:
        op = opcodes[mem[pc]]
        off = op(pc)
        if off < 0:
            break
        pc += off

    return mem[0]


def init_and_run(mem, noun, verb):
    mem[1] = noun
    mem[2] = verb
    return intcode(mem)


def main(argv):
    with open(argv[1], "r") as f:
        mem = [int(n) for n in f.read().split(",")]

    print(init_and_run(mem.copy(), 12, 2))

    for noun in range(100):
        for verb in range(100):
            if init_and_run(mem.copy(), noun, verb) == TARGET:
                print(100 * noun + verb)
                return

    print("No solutions found")


if __name__ == "__main__":
    main(sys.argv)
