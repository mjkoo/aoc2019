#!/usr/bin/env python3
import sys
import operator


def decode(opcode):
    d = 10000
    m3, opcode, d = opcode // d, opcode % d, d // 10
    m2, opcode, d = opcode // d, opcode % d, d // 10
    m1, opcode, d = opcode // d, opcode % d, d // 10
    return (m1, m2, m3, opcode)


def intcode(mem, inputs):
    outputs = []

    def load(mode, addr):
        return addr if mode else mem[addr]

    def store(addr, value):
        mem[addr] = value

    def alu(m1, m2, m3, pc, op):
        assert m3 == 0
        a = load(m1, mem[pc + 1])
        b = load(m2, mem[pc + 2])
        store(mem[pc + 3], op(a, b))
        return 4

    def add(m1, m2, m3, pc):
        return alu(m1, m2, m3, pc, operator.add)

    def mul(m1, m2, m3, pc):
        return alu(m1, m2, m3, pc, operator.mul)

    def lt(m1, m2, m3, pc):
        return alu(m1, m2, m3, pc, lambda a, b: 1 if a < b else 0)

    def eq(m1, m2, m3, pc):
        return alu(m1, m2, m3, pc, lambda a, b: 1 if a == b else 0)

    def jmp(m1, m2, m3, pc, cnd):
        a = load(m1, mem[pc + 1])
        b = load(m2, mem[pc + 2])
        return b - pc if cnd(a) else 3

    def jnz(m1, m2, m3, pc):
        return jmp(m1, m2, m3, pc, lambda a: a)

    def jz(m1, m2, m3, pc):
        return jmp(m1, m2, m3, pc, lambda a: not a)

    def read(m1, m2, m3, pc):
        assert m1 == 0
        store(mem[pc + 1], inputs.pop())
        return 2

    def write(m1, m2, m3, pc):
        a = load(m1, mem[pc + 1])
        outputs.append(a)
        return 2

    def halt(m1, m2, m3, pc):
        return -1

    opcodes = {1: add, 2: mul, 3: read, 4: write, 5: jnz, 6: jz, 7: lt, 8: eq, 99: halt}

    pc = 0
    while True:
        m1, m2, m3, opcode = decode(mem[pc])
        op = opcodes[opcode]
        off = op(m1, m2, m3, pc)

        if off < 0:
            break
        pc += off

    return outputs


def main(argv):
    with open(argv[1], "r") as f:
        mem = [int(n) for n in f.read().split(",")]

    print(intcode(mem.copy(), [1])[-1])
    print(intcode(mem.copy(), [5])[-1])


if __name__ == "__main__":
    main(sys.argv)
