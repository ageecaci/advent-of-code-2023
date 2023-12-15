#!/usr/bin/env python3

from dataclasses import dataclass
import logging
import pathlib
import sys
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

from lib.class_text_coordinate_limits import TextCoordinateLimits as Limits
from lib.class_text_coordinate import TextCoordinate as Coordinate
import lib.helper_args as ha
import lib.helper_coord as hc
import lib.helper_file as hf
import lib.helper_log as hl

logger = logging.getLogger(__file.stem)


'''
.
J|L
-S-
7|F
'''


class Pipeline:
    def __init__(self, start: Coordinate):
        self.start = start
        self.chains: list[PipelinePipe] = []

    def contains(self, coord: Coordinate) -> bool:
        for chain in self.chains:
            if coord == chain[-1].coord:
                return True
        return False


@dataclass(frozen=True)
class PipelinePipe:
    coord: Coordinate
    type: str
    previous: Coordinate
    depth: int

    def get_next(self) -> Coordinate:
        if self.previous.above(self.coord):
            if self.type == 'J':
                return self.coord.left()
            elif self.type == '|':
                return self.coord.down()
            elif self.type == 'L':
                return self.coord.right()
            else:
                raise Exception(f'Pipe type {self.type} does not connect {self.previous} to {self.coord}')
        elif self.previous.below(self.coord):
            if self.type == '7':
                return self.coord.left()
            elif self.type == '|':
                return self.coord.up()
            elif self.type == 'F':
                return self.coord.right()
            else:
                raise Exception(f'Pipe type {self.type} does not connect {self.previous} to {self.coord}')
        elif self.previous.left_of(self.coord):
            if self.type == 'J':
                return self.coord.up()
            elif self.type == '-':
                return self.coord.right()
            elif self.type == '7':
                return self.coord.down()
            else:
                raise Exception(f'Pipe type {self.type} does not connect {self.previous} to {self.coord}')
        elif self.previous.right_of(self.coord):
            if self.type == 'L':
                return self.coord.up()
            elif self.type == '-':
                return self.coord.left()
            elif self.type == 'F':
                return self.coord.down()
            else:
                raise Exception(f'Pipe type {self.type} does not connect {self.previous} to {self.coord}')
        return False


def find_connected(coord: Coordinate, grid: list[str], limits: Limits) -> list[Coordinate]:
    connected_neighbours = []
    for neighbour in hc.valid_neighbours(coord, limits, diagonal=False):
        if connects_to(coord, neighbour, grid):
            connected_neighbours.append(neighbour)
    return connected_neighbours


def connects_to(source: Coordinate, destination: Coordinate, grid: list[str]) -> bool:
    destination_character = grid[destination.line][destination.character]
    if source.above(destination):
        return destination_character in 'J|L'
    elif source.below(destination):
        return destination_character in '7|F'
    elif source.left_of(destination):
        return destination_character in 'J-7'
    elif source.right_of(destination):
        return destination_character in 'L-F'
    return False


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    depth = len(lines)
    width = len(lines[0])
    limits = Limits(depth, width)

    grid = []
    start = None
    for line_index, line in enumerate(lines):
        grid.append(line.strip())
        try:
            start_index = line.index('S')
            start = Coordinate(line_index, start_index)
            logger.debug('Starting from %r', start)
        except:
            pass

    pipeline = Pipeline(start)
    current_depth = 1
    for neighbour in find_connected(start, grid, limits):
        pipe_type = hc.lookup_in(neighbour, grid)
        new_pipe = PipelinePipe(neighbour, pipe_type, start, current_depth)
        logger.debug('Connecting %r from start', new_pipe)
        pipeline.chains.append([new_pipe])

    while True:
        discovered_new_pipe = False
        current_depth += 1
        for chain in pipeline.chains:
            last_pipe = chain[-1]
            next_pipe_coords = last_pipe.get_next()
            if not pipeline.contains(next_pipe_coords):
                pipe_type = hc.lookup_in(next_pipe_coords, grid)
                new_pipe = PipelinePipe(next_pipe_coords, pipe_type, last_pipe.coord, current_depth)
                logger.debug('Connecting %r from %r', new_pipe, last_pipe)
                chain.append(new_pipe)
                discovered_new_pipe = True
        if not discovered_new_pipe:
            break

    furthest = 0
    for chain in pipeline.chains:
        if chain[-1].depth > furthest:
            furthest = chain[-1].depth

    print(furthest)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
