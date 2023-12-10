#!/usr/bin/env python3

from dataclasses import dataclass
import logging
import operator
import os
import sys
sys.path.append(os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..')))

from lib.class_text_coordinate_limits import TextCoordinateLimits as Limits
from lib.class_text_coordinate import TextCoordinate as Coordinate
import lib.helper_args as ha
import lib.helper_coord as hc
import lib.helper_file as hf
import lib.helper_log as hl


'''
.
J|L
-S-
7|F
'''


class Pipeline:
    def __init__(self, start: Coordinate, grid: list[str]):
        self.start = start
        self.grid = grid
        self.chains: list[PipelinePipe] = []
        self.coordinates: set[Coordinate] = set()
        self.coordinates.add(start)

    def add(self, coord: Coordinate):
        self.coordinates.add(coord)

    def contains(self, coord: Coordinate) -> bool:
        return coord in self.coordinates


@dataclass
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


def determine_pipe_type_from_connected(target: Coordinate, connectors: list[PipelinePipe]) -> str:
    if connectors[0].coord.above(target):
        if connectors[1].coord.below(target):
            return '|'
        elif connectors[1].coord.left_of(target):
            return 'J'
        elif connectors[1].coord.right_of(target):
            return 'L'
    elif connectors[0].coord.below(target):
        if connectors[1].coord.above(target):
            return '|'
        elif connectors[1].coord.left_of(target):
            return '7'
        elif connectors[1].coord.right_of(target):
            return 'F'
    elif connectors[0].coord.left_of(target):
        if connectors[1].coord.above(target):
            return 'J'
        elif connectors[1].coord.below(target):
            return '7'
        elif connectors[1].coord.right_of(target):
            return '-'
    elif connectors[0].coord.right_of(target):
        if connectors[1].coord.above(target):
            return 'L'
        elif connectors[1].coord.below(target):
            return 'F'
        elif connectors[1].coord.left_of(target):
            return '-'
    raise Exception(f'Invalid neighbour configuration between {target} and {connectors}')


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
            logging.debug('Starting from %r', start)
        except:
            pass

    pipeline = Pipeline(start, grid)
    current_depth = 1
    for neighbour in find_connected(start, grid, limits):
        pipe_type = hc.lookup_in(neighbour, grid)
        new_pipe = PipelinePipe(neighbour, pipe_type, start, current_depth)
        logging.debug('Connecting %r from start', new_pipe)
        pipeline.add(neighbour)
        pipeline.chains.append([new_pipe])

    start_type = determine_pipe_type_from_connected(start, [chain[0] for chain in pipeline.chains])
    logging.debug('Start point is type: %s', start_type)
    grid[start.line] = (
        grid[start.line][:start.character]
        + start_type
        + grid[start.line][start.character+1:])

    while True:
        discovered_new_pipe = False
        current_depth += 1
        for chain in pipeline.chains:
            last_pipe = chain[-1]
            next_pipe_coords = last_pipe.get_next()
            if not pipeline.contains(next_pipe_coords):
                pipe_type = hc.lookup_in(next_pipe_coords, grid)
                new_pipe = PipelinePipe(next_pipe_coords, pipe_type, last_pipe.coord, current_depth)
                logging.debug('Connecting %r from %r', new_pipe, last_pipe)
                pipeline.add(next_pipe_coords)
                chain.append(new_pipe)
                discovered_new_pipe = True
        if not discovered_new_pipe:
            break

    count = 0
    for line_index, line in enumerate(grid):
        perpendicular_crossings = 0
        last_corner = ''
        debug_line = []
        for character_index, character in enumerate(line):
            coord = Coordinate(line_index, character_index)
            if not pipeline.contains(coord):
                # A point is inside a polygon if and only iff the number of "crossings" from a ray is odd.
                if perpendicular_crossings % 2 == 1:
                    debug_line.append('I')
                    logging.debug('Pipeline encloses %r', coord)
                    count += 1
                else:
                    debug_line.append('O')
            else:
                debug_line.append(character)
                # Progressively keep track of how many crossings there have been since the edge of the grid.
                if character == '|':
                    perpendicular_crossings += 1
                elif character in 'JL7F':
                    # Corners always come in pairs.
                    # If the pipeline returns in the same direction after two corners, no crossing was present.
                    # If the pipeline continues in the opposite direction after two corners, we found an "extruded" crossing.
                    if last_corner == '':
                        last_corner = character
                    else:
                        # This includes general cases, but we could simplify as we scan left,
                        # so we always encounter corners in the same order.
                        if character in 'JL' and last_corner in '7F':
                            perpendicular_crossings += 1
                        elif character in '7F' and last_corner in 'JL':
                            perpendicular_crossings += 1
                        last_corner = ''
        logging.debug('Finished scanning line %d: %d crossings; %s', line_index, perpendicular_crossings, ''.join(debug_line))
        assert last_corner == ''
        assert perpendicular_crossings % 2 == 0

    print(count)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
