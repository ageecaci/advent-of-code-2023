#!/usr/bin/env python3

from dataclasses import dataclass
import logging
import math
import operator
import pathlib
import sys
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

import lib.helper_args as ha
import lib.helper_file as hf
import lib.helper_log as hl


@dataclass(frozen=True)
class DesertNode:
    id: int
    left: int
    right: int


def node_is_starting_point(node: DesertNode) -> bool:
    return node.id.endswith('A')


def node_is_terminus(node: DesertNode) -> bool:
    return node.id.endswith('Z')


go_left = operator.attrgetter('left')
go_right = operator.attrgetter('right')


def make_move(node: DesertNode, direction: str, node_map: dict[str, DesertNode]) -> None:
    if direction == 'L':
        next_node_id = go_left(node)
    elif direction == 'R':
        next_node_id = go_right(node)
    else:
        raise Exception(f'invalid direction {direction}')
    return node_map[next_node_id]


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))
    path = lines[0].strip()
    assert len(path.replace('L', '').replace('R', '')) == 0
    nodes = lines[2:]

    node_map = {}
    starting_node_ids = set()
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
            starting_node_ids.add(desert_node.id)

    starting_node_steps = {}
    for starting_node_id in starting_node_ids:
        i = 0
        cycles = 0
        current_node = node_map[starting_node_id]
        while not node_is_terminus(current_node):
            next_node = make_move(current_node, path[i], node_map)
            logging.debug('Travelling from %s to %s', current_node.id, next_node.id)
            current_node = next_node
            i += 1
            if i >= len(path):
                cycles += 1
                i = 0
        journey_length = cycles * len(path) + i
        logging.debug('Journey from %s took %d steps', starting_node_id, journey_length)
        starting_node_steps[starting_node_id] = journey_length

    logging.warning('This is the solution to the AoC problem, not the generalised problem statement.')
    print(math.lcm(*list(starting_node_steps.values())))


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
