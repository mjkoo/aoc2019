#!/usr/bin/env python3
import sys
import operator


class Intcode:
    def __init__(self, mem, inputs):
        self.mem = mem
        self.pc = 0
        self.inputs = inputs
        self.outputs = []

    def run(self):
        while True:
            opcode = self.mem[self.pc]
            ins = Instruction(opcode)
            off = ins.run(self)
            if off is None:
                break
            self.pc += off

        return self.outputs


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
        self.store(m, 0, m.inputs.pop())
        return 2

    def write(self, m):
        a = self.load(m, 0)
        m.outputs.append(a)
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


def main(argv):
    with open(argv[1], "r") as f:
        mem = [int(n) for n in f.read().split(",")]

    print(Intcode(mem.copy(), [1]).run()[-1])
    print(Intcode(mem.copy(), [5]).run()[-1])


if __name__ == "__main__":
    main(sys.argv)
