#!/usr/bin/env python3

from dataclasses import dataclass
import logging
import pathlib
import sys
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

import lib.helper_args as ha
import lib.helper_file as hf
import lib.helper_log as hl

logger = logging.getLogger(__file.stem)

start = 'AAA'
end = 'ZZZ'


@dataclass(frozen=True)
class DesertNode:
    id: int
    left: int
    right: int


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))
    path = lines[0].strip()
    nodes = lines[2:]

    node_map = {}
    for node in nodes:
        id, paths = node.split('=', 1)
        paths = paths.split('(', 1)[1].split(')', 1)[0]
        left, right = paths.split(',')
        desert_node = DesertNode(id.strip(), left.strip(), right.strip())
        logger.debug('Adding to map: %r', desert_node)
        node_map[desert_node.id] = desert_node

    current_location = node_map[start]
    i = 0
    cycles = 0
    while current_location.id != end:
        next_step = path[i]
        if next_step == 'L':
            next_location = node_map[current_location.left]
        elif next_step == 'R':
            next_location = node_map[current_location.right]
        else:
            raise Exception(f'invalid next step {next_step} from {current_location.id} (idx: {i})')
        logger.debug('Moving from %s to %s (idx: %d, cycle %d)', current_location.id, next_location.id, i, cycles)
        current_location = next_location
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
