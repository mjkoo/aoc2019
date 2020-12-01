#!/usr/bin/env python3
import operator
import sys

from collections import defaultdict, namedtuple
from queue import Empty, Queue
from threading import Thread

import networkx as nx

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


def run_robot(mem):
    inq = Queue()
    outq = Queue()
    m = Intcode(mem.copy(), inq, outq)
    t = m.run()

    directions = [Vec2D(0, 1), Vec2D(0, -1), Vec2D(-1, 0), Vec2D(1, 0)]
    opposites = {1: 2, 2: 1, 3: 4, 4: 3}

    cur_pos = Vec2D(0, 0)
    moves = []
    ship_map = {}
    unexplored = defaultdict(lambda: [1, 2, 3, 4])
    backtrack = False

    while True:
        try:
            if unexplored[cur_pos]:
                backtrack = False
                move = unexplored[cur_pos].pop()
            else:
                backtrack = True
                if not moves:
                    return ship_map

                move = opposites[moves.pop()]

            inq.put(move)
            status = outq.get()

            if status == 1 or status == 2:
                cur_pos = Vec2D(
                    cur_pos.x + directions[move - 1].x,
                    cur_pos.y + directions[move - 1].y,
                )
                ship_map[cur_pos] = status

                if not backtrack:
                    moves.append(move)

        except Empty:
            break

    t.join()

    return ship_map


def render_map(ship_map):
    min_x = min(p.x for p in ship_map.keys())
    max_x = max(p.x for p in ship_map.keys())
    min_y = min(p.y for p in ship_map.keys())
    max_y = max(p.y for p in ship_map.keys())

    retargeted_map = defaultdict(int)
    for coord, tile in ship_map.items():
        retargeted_map[Vec2D(coord.x - min_x, coord.y - min_y)] = tile

    tiles = ["#", " ", "o"]

    for y in range(max_y - min_y, -1, -1):
        for x in range(0, max_x - min_x + 1):
            if (x, y) == (0, 0):
                sys.stdout.write('x')
            else:
                sys.stdout.write(tiles[retargeted_map[Vec2D(x, y)]])

        print()


def to_graph(ship_map):
    g = nx.Graph()
    end = Vec2D(0, 0)
    min_x = min(p.x for p in ship_map.keys())
    max_x = max(p.x for p in ship_map.keys())
    min_y = min(p.y for p in ship_map.keys())
    max_y = max(p.y for p in ship_map.keys())

    directions = [Vec2D(0, 1), Vec2D(0, -1), Vec2D(-1, 0), Vec2D(1, 0)]

    retargeted_map = defaultdict(int)
    for coord, tile in ship_map.items():
        retargeted_map[Vec2D(coord.x - min_x, coord.y - min_y)] = tile

    for y in range(max_y - min_y, -1, -1):
        for x in range(0, max_x - min_x + 1):
            node = Vec2D(x, y)
            if retargeted_map[node]:
                g.add_node(node)

                if retargeted_map[node] == 2:
                    end = node

                for d in directions:
                    neighbor = Vec2D(x + d.x, y + d.y)
                    if retargeted_map[neighbor]:
                        g.add_edge(node, neighbor)

    return g, end


def main(argv):
    with open(argv[1], "r") as f:
        mem = [int(n) for n in f.read().split(",")]

    ship_map = run_robot(mem)
    render_map(ship_map)
    g, end = to_graph(ship_map)
    print(end)
    print(nx.shortest_path(g, Vec2D(0, 0), end))
    print(len(nx.shortest_path(g, Vec2D(0, 0), end)))
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv)
