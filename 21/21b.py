#!/usr/bin/env python3

from dataclasses import dataclass
from dataclasses import dataclass
from functools import cached_property
import logging
import pathlib
import sys
from typing import Optional
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

import numpy as np

from lib.class_text_coordinate_limits import TextCoordinateLimits as Limits
from lib.class_text_coordinate import TextCoordinate as Coordinate
import lib.helper_args as ha
import lib.helper_coord as hc
import lib.helper_file as hf
import lib.helper_log as hl

logger = logging.getLogger(__file.stem)

tile_garden = '.'
tile_rock = '#'
tile_start = 'S'
tile_location = 'O'


@dataclass(frozen=True, order=True)
class MapSuperPosition:
    locations: tuple[Coordinate]

    @property
    def count(self):
        return len(self.locations)


@dataclass(frozen=True)
class Map:
    grid: list[str]
    rocks: set[Coordinate]

    @cached_property
    def limits(self) -> Limits:
        return Limits(len(self.grid), len(self.grid[0]))

    def walk(self, state: MapSuperPosition) -> MapSuperPosition:
        neighbours: set[Coordinate] = set()
        for location in state.locations:
            neighbours.update(hc.valid_neighbours(location, self.limits, diagonal=False))
        neighbours.difference_update(self.rocks)
        result = tuple(sorted(neighbours))
        return MapSuperPosition(result)

    def visualise(self, state: MapSuperPosition) -> str:
        output = [line for line in self.grid]
        for rock in self.rocks:
            line = output[rock.line]
            new_line = (
                line[:rock.character]
                + tile_rock
                + line[rock.character+1:])
            output[rock.line] = new_line
        for super_position in state.locations:
            line = output[super_position.line]
            new_line = (
                line[:super_position.character]
                + tile_location
                + line[super_position.character+1:])
            output[super_position.line] = new_line
        return '\n'.join(output)


class History:
    def __init__(self, map: Map, initial_state: MapSuperPosition):
        self.map = map
        self.states: list[MapSuperPosition] = [initial_state]
        self.state_indices: dict[MapSuperPosition, int] = { initial_state: 0 }
        self.loops = False
        self._loop_start_index = -1
        self._loop_end_index = -1
        self._loop_length = -1

    def include(self, state: MapSuperPosition):
        index = len(self.states)
        if state in self.state_indices and self.state_indices[state] != index:
            self.loops = True
            self._loop_start_index = self.state_indices[state]
            self._loop_end_index = index
            logger.debug('Loop discovered from step %d to step %d', self._loop_start_index, self._loop_end_index)
            self._loop_length = self._loop_end_index - self._loop_start_index
        else:
            self.states.append(state)

    def get_state_for(self, terminus: int):
        index = len(self.states) - 1
        while index < terminus and not self.loops:
            if index % 100 == 0:
                logger.debug('Calculating step %d', index)
            self.include(self.map.walk(self.states[index]))
            index += 1
        if index < terminus:
            loops_required = (terminus - self._loop_end_index) // self._loop_length
            index_after_loops = self._loop_end_index + (self._loop_length * loops_required)
            index = terminus - index_after_loops
        return self.states[index]


def main(props):
    if props.use_examples:
        raise Exception('Solution does not support the example input')
    lines = hf.load_lines(hf.find_input_file(props))
    depth = len(lines)
    width = len(lines[0])
    logger.debug('Input grid is %d x %d', width, depth)
    assert depth == width

    starting_point: Optional[Coordinate] = None
    rock_locations: set[Coordinate] = set()
    for line_index, line in enumerate(lines):
        for character_index, character in enumerate(line):
            if character == tile_rock:
                rock_locations.add(Coordinate(line_index, character_index))
            elif character == tile_start:
                starting_point = Coordinate(line_index, character_index)
                line = (line[:character_index] + tile_garden + line[character_index+1:])
                lines[line_index] = line

    grid = [line * 5 for line in lines] * 5
    starting_point = Coordinate(starting_point.line + 2 * depth, starting_point.character + 2 * width)
    all_rocks: set[Coordinate] = set()
    for i in range(5):
        for j in range(5):
            all_rocks.update(
                Coordinate(rock.line + i * width, rock.character + j * depth)
                for rock in rock_locations)
    map = Map(grid, all_rocks)
    initial_state = MapSuperPosition((starting_point,))
    history = History(map, initial_state)

    number_of_steps = 26501365
    offset = number_of_steps % width
    multiples = number_of_steps // width
    logger.debug('Target %d = %d * %d + %d', number_of_steps, width, multiples, offset)

    state_for_first_offset = history.get_state_for(offset)
    logger.debug('Count of positions after step %d: %d', offset, state_for_first_offset.count)
    state_for_second_offset = history.get_state_for(offset + width)
    logger.debug('Count of positions after step %d: %d', offset + width, state_for_second_offset.count)
    state_for_third_offset = history.get_state_for(offset + width * 2)
    logger.debug('Count of positions after step %d: %d', offset + width * 2, state_for_third_offset.count)

    vandermonde = np.matrix([[0, 0, 1], [1, 1, 1], [4, 2, 1]])
    ys = np.array([state_for_first_offset.count, state_for_second_offset.count, state_for_third_offset.count])
    coefficients = np.linalg.solve(vandermonde, ys).astype(np.int64)
    result = coefficients[0] * (multiples * multiples) + coefficients[1] * multiples + coefficients[2]
    logger.debug('Coefficients of interpolating polynomial: %r', coefficients)

    print(result)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
