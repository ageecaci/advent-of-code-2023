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
    def limits(self):
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
            self.include(self.map.walk(self.states[index]))
            index += 1
        if index < terminus:
            loops_required = (terminus - self._loop_end_index) // self._loop_length
            index_after_loops = self._loop_end_index + (self._loop_length * loops_required)
            index = terminus - index_after_loops
        return self.states[index]


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

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

    map = Map(lines, rock_locations)
    initial_state = MapSuperPosition((starting_point,))
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug('Initial state: \n%s', map.visualise(initial_state))
    history = History(map, initial_state)
    if props.use_examples and logger.isEnabledFor(logging.DEBUG):
        for i in range(1, 4):
            state = history.get_state_for(i)
            logger.debug('State after %d steps: \n%s', i, map.visualise(state))
    number_of_steps = 64
    if props.use_examples:
        number_of_steps = 6
    final_state = history.get_state_for(number_of_steps)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug('Final state after %d steps: \n%s', number_of_steps, map.visualise(final_state))

    print(final_state.count)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
