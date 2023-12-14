#!/usr/bin/env python3

import logging
import operator
import os
import sys
sys.path.append(os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..')))

import numpy as np

from lib.class_text_coordinate_limits import TextCoordinateLimits as Limits
from lib.class_text_coordinate import TextCoordinate as Coordinate
import lib.helper_args as ha
import lib.helper_file as hf
import lib.helper_log as hl

logger = logging.getLogger(__name__)

blank_character = '.'
block_character = '#'
rollable_character = 'O'

getter_by_line = operator.attrgetter('line')


class Platform:
    def __init__(self, limits: Limits):
        self.blocks: set[Coordinate] = set()
        self.rollables: set[Coordinate] = set()
        self.limits: Limits = limits

    def add_block(self, coord: Coordinate):
        self.blocks.add(coord)

    def add_rollable(self, coord: Coordinate):
        self.rollables.add(coord)

    def rollables_by_line(self, reverse=False):
        return sorted(self.rollables, key=getter_by_line, reverse=reverse)

    def empty_rollables(self):
        self.rollables = set()

    @property
    def load(self):
        subtotal = 0
        for rock in self.rollables:
            distance_from_bottom = self.limits.max_line - rock.line
            subtotal += distance_from_bottom
        return subtotal

    def tilt_north(self):
        rollables_by_line = self.rollables_by_line()
        self.empty_rollables()
        for rollable in rollables_by_line:
            logging.log(hl.EXTRA_NOISY, 'Checking rollable starting from %r', rollable)
            found_blocker = False
            for line_index in range(rollable.line - 1, -1, -1):
                to_test = Coordinate(line_index, rollable.character)
                if to_test in self.blocks or to_test in self.rollables:
                    logger.log(hl.EXTRA_NOISY, 'blocker found at line %d', line_index)
                    new_coordinate = Coordinate(line_index + 1, rollable.character)
                    self.add_rollable(new_coordinate)
                    found_blocker = True
                    break
            if not found_blocker:
                new_coordinate = Coordinate(0, rollable.character)
                self.add_rollable(new_coordinate)

    def visualise(self) -> str:
        grid = np.full((self.limits.max_line, self.limits.max_character), blank_character)
        for block in self.blocks:
            grid[block.line][block.character] = block_character
        for rollable in self.rollables:
            grid[rollable.line][rollable.character] = rollable_character
        return '\n'.join(''.join(grid[line_index]) for line_index in range(self.limits.max_line))


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    depth = len(lines)
    width = len(lines[0])

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

    platform.tilt_north()
    if logger.isEnabledFor(hl.EXTRA_DETAIL):
        logger.log(hl.EXTRA_DETAIL, 'New grid: \n%s', platform.visualise())
    subtotal = platform.load

    print(subtotal)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
