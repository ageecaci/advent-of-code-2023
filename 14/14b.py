#!/usr/bin/env python3

from collections.abc import Iterable
from dataclasses import dataclass
from functools import cache
import logging
import math
import operator
import pathlib
import sys
from typing import Optional
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

from bidict import bidict
import numpy as np

from lib.class_text_coordinate_limits import TextCoordinateLimits as Limits
from lib.class_text_coordinate import TextCoordinate as Coordinate
import lib.helper_args as ha
import lib.helper_file as hf
import lib.helper_log as hl

logger = logging.getLogger(__file.stem)

blank_character = '.'
block_character = '#'
rollable_character = 'O'

getter_by_line = operator.attrgetter('line')
getter_by_character = operator.attrgetter('character')
getter_by_coordinate = operator.attrgetter('line', 'character')

north = 'north'
south = 'south'
east = 'east'
west = 'west'
directions = [north, west, south, east]


@dataclass(frozen=True)
class TiltOperationState:
    rollables: tuple[Coordinate]
    direction: str
    blocks: tuple[Coordinate]
    limits: Limits


@cache
def cycle(state: TiltOperationState) -> tuple[Coordinate]:
    rollables = state.rollables
    for direction in directions:
        sorted_rollables = sort_for_direction(tuple(rollables), direction)
        rollables = tilt(TiltOperationState(
            sorted_rollables,
            direction,
            state.blocks,
            state.limits))
    return rollables


@cache
def tilt(state: TiltOperationState) -> tuple[Coordinate]:
    blocks = set(state.blocks)
    new_positions = set()
    # assumes the rollables are pre-sorted, also necessary for caching
    for rollable in state.rollables:
        logger.log(hl.EXTRA_NOISY, 'Checking rollable starting from %r', rollable)
        last_checked = rollable
        for to_test in coordinates_to_check(rollable, state.direction, state.limits):
            if to_test in blocks or to_test in new_positions:
                break
            last_checked = to_test
        logger.log(hl.EXTRA_NOISY, 'rolling to %r', last_checked)
        new_positions.add(last_checked)
    return sort_canonically(new_positions)


# Provide a "canonical" sorting to make use of caching
def sort_canonically(rocks: Iterable[Coordinate]) -> tuple[Coordinate]:
    return tuple(sorted(rocks, key=getter_by_coordinate))


@cache
def sort_for_direction(rollables: tuple[Coordinate], direction: str) -> tuple[Coordinate]:
    if direction == north:
        return tuple(sorted(rollables, key=getter_by_line))
    if direction == south:
        return tuple(sorted(rollables, key=getter_by_line, reverse=True))
    if direction == west:
        return tuple(sorted(rollables, key=getter_by_character))
    if direction == east:
        return tuple(sorted(rollables, key=getter_by_character, reverse=True))
    raise Exception(f'Invalid direction: {direction}')


def coordinates_to_check(start: Coordinate, direction: str, limits: Limits) -> Iterable[Coordinate]:
    if direction == north:
        for line in range(start.line - 1, limits.min_line - 1, -1):
            yield Coordinate(line, start.character)
    elif direction == south:
        for line in range(start.line + 1, limits.max_line):
            yield Coordinate(line, start.character)
    elif direction == west:
        for character in range(start.character - 1, limits.min_character - 1, -1):
            yield Coordinate(start.line, character)
    elif direction == east:
        for character in range(start.character + 1, limits.max_character):
            yield Coordinate(start.line, character)


class Platform:
    def __init__(self, limits: Limits):
        self.blocks: set[Coordinate] = set()
        self._blocks: Optional[tuple[Coordinate]] = None
        self.rollables: set[Coordinate] = set()
        self._rollables: Optional[tuple[Coordinate]] = None
        self.limits: Limits = limits
        self.previous_states: bidict[tuple(Coordinate), int] = bidict()

    def add_block(self, coord: Coordinate):
        self._blocks = None
        self.blocks.add(coord)

    def get_blocks(self) -> tuple[Coordinate]:
        if self._blocks is None:
            self._blocks = sort_canonically(self.blocks)
        return self._blocks

    def add_rollable(self, coord: Coordinate):
        self._rollables = None
        self.rollables.add(coord)

    @property
    def load(self):
        rollables = self._rollables if self._rollables is not None else self.rollables
        subtotal = 0
        for rock in rollables:
            distance_from_bottom = self.limits.max_line - rock.line
            subtotal += distance_from_bottom
            logger.log(hl.EXTRA_NOISY, 'Adding %d to subtotal', distance_from_bottom)
        return subtotal

    def cycle(self, iterations: int):
        if self._rollables is None:
            self._rollables = sort_canonically(self.rollables)
        for i in range(iterations):
            state = TiltOperationState(
                self._rollables, '',
                self.get_blocks(), self.limits)
            self._rollables = cycle(state)
            if logger.isEnabledFor(hl.EXTRA_DETAIL):
                logger.log(hl.EXTRA_DETAIL, 'Platform after %d cycles: \n%s', i + 1, self.visualise())
                logger.log(hl.EXTRA_DETAIL, 'Platform load after %d cycles: %d', i + 1, self.load)
            if self._rollables in self.previous_states:
                # found a loop: skip to the end
                loop_start = self.previous_states[self._rollables]
                loop_end = i
                logger.debug('loop found from %d to %d', loop_start, loop_end)
                loop_length = loop_end - loop_start
                offset_iterations = iterations - loop_start
                repeats = math.floor(offset_iterations / loop_length)
                end_of_looping = loop_start + repeats * loop_length
                logger.debug('looping fast-forwards from %d to %d', i, end_of_looping)
                final_state_index = iterations - end_of_looping - 1 + loop_start
                logger.debug('using state from %d', final_state_index)
                self._rollables = self.previous_states.inverse[final_state_index]
                break
            else:
                self.previous_states[self._rollables] = i
            if (i + 1) % 100 == 0:
                logger.info('completed cycle %d of %d', i + 1, iterations)
        self.rollables = set(self._rollables)

    def visualise(self) -> str:
        grid = np.full((self.limits.max_line, self.limits.max_character), blank_character)
        for block in self.blocks:
            grid[block.line][block.character] = block_character
        rollables = self._rollables if self._rollables is not None else self.rollables
        for rollable in rollables:
            grid[rollable.line][rollable.character] = rollable_character
        return '\n'.join(''.join(grid[line_index]) for line_index in range(self.limits.max_line))


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    depth = len(lines)
    width = len(lines[0].strip())

    platform = Platform(Limits(depth, width))
    for line_index, line in enumerate(lines):
        grid_line = line.strip()
        for character_index, character in enumerate(grid_line):
            if character == block_character:
                coord = Coordinate(line_index, character_index)
                logger.log(hl.EXTRA_DETAIL, 'Discovered block at %r', coord)
                platform.add_block(coord)
            elif character == rollable_character:
                coord = Coordinate(line_index, character_index)
                logger.log(hl.EXTRA_DETAIL, 'Discovered rollable at %r', coord)
                platform.add_rollable(coord)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug('Starting grid: \n%s', platform.visualise())

    # platform.cycle(3)
    # platform.cycle(10)
    # platform.cycle(1000)
    platform.cycle(1000000000)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug('Final grid: \n%s', platform.visualise())
    subtotal = platform.load

    print(subtotal)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
