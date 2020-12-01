#!/usr/bin/env python3
import operator
import sys

from collections import defaultdict, namedtuple
from queue import Empty, Queue
from threading import Thread

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


def run_robot(mem, white=False):
    board = defaultdict(int)
    inq = Queue()
    outq = Queue()
    m = Intcode(mem.copy(), inq, outq)
    t = m.run()

    turns = [Vec2D(0, 1), Vec2D(1, 0), Vec2D(0, -1), Vec2D(-1, 0)]

    cur_dir = 0
    cur_pos = Vec2D(0, 0)

    if white:
        board[cur_pos] = 1

    while True:
        try:
            inq.put(board[cur_pos])
            color = outq.get(timeout=1)
            turn = outq.get(timeout=1)

            board[cur_pos] = color
            cur_dir += 1 if turn else -1
            cur_dir %= len(turns)
            cur_pos = Vec2D(cur_pos.x + turns[cur_dir].x, cur_pos.y + turns[cur_dir].y)
        except Empty:
            break

    t.join()

    return board


def render_board(board):
    min_x = min(p.x for p in board.keys())
    max_x = max(p.x for p in board.keys())
    min_y = min(p.y for p in board.keys())
    max_y = max(p.y for p in board.keys())

    retargeted_board = defaultdict(int)
    for coord, color in board.items():
        retargeted_board[Vec2D(coord.x - min_x, coord.y - min_y)] = color

    for y in range(max_y - min_y, -1, -1):
        for x in range(0, max_x - min_x + 1):
            if retargeted_board[Vec2D(x, y)]:
                sys.stdout.write('#')
            else:
                sys.stdout.write(' ')

        print()


def main(argv):
    with open(argv[1], "r") as f:
        mem = [int(n) for n in f.read().split(",")]

    black_board = run_robot(mem, False)
    print(len(black_board.keys()))

    white_board = run_robot(mem, True)
    render_board(white_board)


if __name__ == "__main__":
    main(sys.argv)
