#!/usr/bin/env python3

from dataclasses import dataclass
import logging
import operator
import pathlib
import sys
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

import lib.helper_args as ha
import lib.helper_file as hf
import lib.helper_log as hl


start = 'AAA'
end = 'ZZZ'


@dataclass(frozen=True)
class DesertNode:
    id: int
    left: int
    right: int


def node_is_starting_point(node: DesertNode) -> bool:
    return node.id[2] == 'A'


def node_is_terminus(node: DesertNode) -> bool:
    return node.id[2] == 'Z'


class DesertNodeSet:
    def __init__(self):
        self._set = []

    def add(self, node: DesertNode) -> None:
        self._set.append(node)

    def progress(self, direction: str, node_map: dict[str, DesertNode]) -> None:
        if direction == 'L':
            mapper = operator.attrgetter('left')
        elif direction == 'R':
            mapper = operator.attrgetter('right')
        else:
            raise Exception(f'invalid direction {direction}')
        self._set = [node_map[mapper(node)] for node in self._set]

    def escaped(self) -> bool:
        return all(map(node_is_terminus, self._set))


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))
    path = lines[0].strip()
    assert len(path.replace('L', '').replace('R', '')) == 0
    nodes = lines[2:]

    node_map = {}
    current_node_set = DesertNodeSet()
    for node in nodes:
        id, paths = node.split('=', 1)
        paths = paths.split('(', 1)[1].split(')', 1)[0]
        left, right = paths.split(',')
        desert_node = DesertNode(id.strip(), left.strip(), right.strip())
        if desert_node.id in node_map:
            raise Exception(f'Duplicate node detected: {desert_node.id}')
        logging.debug('Adding to map: %r', desert_node)
        node_map[desert_node.id] = desert_node
        if node_is_starting_point(desert_node):
            current_node_set.add(desert_node.id)

    i = 0
    cycles = 0
    while not current_node_set.escaped():
        next_step = path[i]
        current_node_set.progress(next_step, node_map)
        i += 1
        if i >= len(path):
            cycles += 1
            i = 0

    print(cycles * len(path) + i)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
