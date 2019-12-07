#!/usr/bin/env python3
import operator
import sys
import time

from itertools import permutations
from queue import Queue
from threading import Thread


class Intcode:
    def __init__(self, mem, inq, outq):
        self.mem = mem
        self.pc = 0
        self.inq = inq
        self.outq = outq
        self.halted = False
        self.last_output = 0

    def _run(self):
        while not self.halted:
            opcode = self.mem[self.pc]
            ins = Instruction(opcode)
            off = ins.run(self)
            if off is None:
                self.halted = True
            else:
                self.pc += off

    def run(self):
        t = Thread(target=self._run, args=())
        t.start()
        return t


class Instruction:
    def __init__(self, opcode):
        d = 10000
        m3, opcode, d = opcode // d, opcode % d, d // 10
        m2, opcode, d = opcode // d, opcode % d, d // 10
        m1, opcode, d = opcode // d, opcode % d, d // 10

        self.modes = [m1, m2, m3]
        self.opcode = opcode

    def load(self, m, arg):
        addr = m.pc + arg + 1
        return m.mem[addr] if self.modes[arg] else m.mem[m.mem[addr]]

    def store(self, m, arg, value):
        assert self.modes[arg] == 0
        addr = m.mem[m.pc + arg + 1]
        m.mem[addr] = value

    def _alu(self, m, f):
        a = self.load(m, 0)
        b = self.load(m, 1)
        self.store(m, 2, f(a, b))
        return 4

    def add(self, m):
        return self._alu(m, operator.add)

    def mul(self, m):
        return self._alu(m, operator.mul)

    def lt(self, m):
        return self._alu(m, lambda a, b: 1 if a < b else 0)

    def eq(self, m):
        return self._alu(m, lambda a, b: 1 if a == b else 0)

    def _jmp(self, m, f):
        a = self.load(m, 0)
        b = self.load(m, 1)
        return b - m.pc if f(a) else 3

    def jnz(self, m):
        return self._jmp(m, lambda a: a)

    def jz(self, m):
        return self._jmp(m, lambda a: not a)

    def read(self, m):
        self.store(m, 0, m.inq.get())
        return 2

    def write(self, m):
        a = self.load(m, 0)
        m.outq.put(a)
        m.last_output = a
        return 2

    def halt(self, m):
        return None

    def run(self, m):
        operations = {
            1: self.add,
            2: self.mul,
            3: self.read,
            4: self.write,
            5: self.jnz,
            6: self.jz,
            7: self.lt,
            8: self.eq,
            99: self.halt,
        }
        return operations[self.opcode](m)


def run_amplifiers_serial(mem, p):
    qs = [Queue() for _ in range(6)]
    ms = [Intcode(mem.copy(), qs[i], qs[i + 1]) for i in range(5)]
    ts = [m.run() for m in ms]

    for s, q in zip(p, qs[:-1]):
        q.put(s)

    qs[0].put(0)

    for t in ts:
        t.join()

    return qs[-1].get()


def run_amplifiers_feedback(mem, p):
    qs = [Queue() for _ in range(5)]
    ms = [Intcode(mem.copy(), qs[i], qs[(i + 1) % 5]) for i in range(5)]
    ts = [m.run() for m in ms]

    for s, q in zip(p, qs):
        q.put(s)

    qs[0].put(0)

    for t in ts:
        t.join()

    return ms[-1].last_output


def main(argv):
    with open(argv[1], "r") as f:
        mem = [int(n) for n in f.read().split(",")]

    max_output_part_1 = max(
        run_amplifiers_serial(mem, p) for p in permutations(range(5))
    )
    print(max_output_part_1)

    max_output_part_2 = max(
        run_amplifiers_feedback(mem, p) for p in permutations(range(5, 10))
    )
    print(max_output_part_2)


if __name__ == "__main__":
    main(sys.argv)
