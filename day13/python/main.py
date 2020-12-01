#!/usr/bin/env python3
import operator
import sys
import time

from collections import defaultdict, namedtuple
from queue import Empty, Queue
from threading import Event, Thread

Vec2D = namedtuple("Vec2D", ["x", "y"])


class Memory(list):
    def __getitem__(self, index):
        if index >= len(self):
            self.extend([0] * (index - len(self) + 1))
        return super(Memory, self).__getitem__(index)

    def __setitem__(self, index, value):
        if index >= len(self):
            self.extend([0] * (index - len(self) + 1))
        return super(Memory, self).__setitem__(index, value)


class Intcode:
    def __init__(self, mem, inq, outq):
        self.mem = Memory(mem)
        self.pc = 0
        self.rel_base = 0
        self.inq = inq
        self.outq = outq
        self.halt = Event()
        self.last_output = 0

    def _run(self):
        while not self.halt.is_set():
            opcode = self.mem[self.pc]
            ins = Instruction(opcode)
            off = ins.run(self)
            if off is None:
                self.halt.set()
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
        mode = self.modes[arg]
        addr = m.pc + arg + 1
        if mode == 0:
            return m.mem[m.mem[addr]]
        elif mode == 1:
            return m.mem[addr]
        elif mode == 2:
            return m.mem[m.rel_base + m.mem[addr]]
        else:
            raise Exception("Invalid parameter mode")

    def store(self, m, arg, value):
        mode = self.modes[arg]
        addr = m.pc + arg + 1
        if mode == 0:
            m.mem[m.mem[addr]] = value
        elif mode == 2:
            m.mem[m.rel_base + m.mem[addr]] = value
        else:
            raise Exception("Invalid parameter mode")

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

    def set_base(self, m):
        a = self.load(m, 0)
        m.rel_base += a
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
            9: self.set_base,
            99: self.halt,
        }
        return operations[self.opcode](m)


def num_blocks(mem):
    display = defaultdict(int)
    inq = Queue()
    outq = Queue()
    m = Intcode(mem.copy(), inq, outq)
    t = m.run()
    t.join()

    while True:
        try:
            x = outq.get_nowait()
            y = outq.get_nowait()
            tile_id = outq.get_nowait()

            display[Vec2D(x, y)] = tile_id
        except Empty:
            break

    return len([t for t in display.values() if t == 2])


def run_game(mem):
    mem = mem.copy()
    mem[0] = 2

    display = defaultdict(int)
    inq = Queue()
    outq = Queue()
    m = Intcode(mem, inq, outq)
    t = m.run()

    score = 0
    paddle = Vec2D(0, 0)
    while True:
        while True:
            try:
                x = outq.get_nowait()
                y = outq.get_nowait()
                tile_id = outq.get_nowait()

                if x == -1 and y == 0:
                    score = tile_id
                else:
                    display[Vec2D(x, y)] = tile_id

                if tile_id == 3:
                    paddle = Vec2D(x, y)
                elif tile_id == 4:
                    if paddle.x > x:
                        inq.put(-1)
                    elif paddle.x < x:
                        inq.put(1)
                    else:
                        inq.put(0)
            except Empty:
                break

        time.sleep(0.1)
        if 2 not in display.values():
            m.halt.set()
            break

    t.join()
    return score


def main(argv):
    with open(argv[1], "r") as f:
        mem = [int(n) for n in f.read().split(",")]

    print(num_blocks(mem))
    print(run_game(mem))


if __name__ == "__main__":
    main(sys.argv)
