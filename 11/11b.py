#!/usr/bin/env python3

import itertools
import logging
import pathlib
import sys
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

import numpy as np

from lib.class_text_coordinate import TextCoordinate as Coordinate
import lib.helper_args as ha
import lib.helper_file as hf
import lib.helper_log as hl

logger = logging.getLogger(__file.stem)

weight = 1000000


class Universe:
    def __init__(self, grid: list[str]):
        self.grid = grid
        self.depth = len(grid)
        self.width = len(grid[0])
        self.galaxies: set[Coordinate] = set()
        self.rows_without_galaxies = np.ones(self.depth, np.int8)
        self.columns_without_galaxies = np.ones(self.width, np.int8)
        self.pre_expansion_galaxies: set[Coordinate] = None

    def add(self, coord: Coordinate):
        self.galaxies.add(coord)
        self.rows_without_galaxies[coord.line] = 0
        self.columns_without_galaxies[coord.character] = 0

    def expand(self):
        if self.pre_expansion_galaxies:
            return
        self.pre_expansion_galaxies = self.galaxies
        expanded_galaxies: set[Coordinate] = set()
        for galaxy in self.galaxies:
            # expansion now replaces original rows: offset by 1
            extra_rows = (weight - 1) * sum(self.rows_without_galaxies[:galaxy.line])
            extra_columns = (weight - 1) * sum(self.columns_without_galaxies[:galaxy.character])
            new_loc = Coordinate(galaxy.line + extra_rows, galaxy.character + extra_columns)
            logger.debug('Expanding: %r moved to %r', galaxy, new_loc)
            expanded_galaxies.add(new_loc)
        self.galaxies = expanded_galaxies

    def visualise(self):
        new_grid = []
        for i in range(self.depth):
            new_line = []
            for j in range(self.width):
                if Coordinate(i, j) in self.pre_expansion_galaxies:
                    new_line.append('#')
                elif self.rows_without_galaxies[i] == 1 or self.columns_without_galaxies[j] == 1:
                    new_line.append('X')
                else:
                    new_line.append('.')
            new_grid.append(new_line)

        logger.debug('New galaxy:')
        for line in new_grid:
            logger.debug(''.join(line))



def calculate_distance(a: Coordinate, b: Coordinate) -> int:
    line_diff = abs(a.line - b.line)
    char_diff = abs(a.character - b.character)
    total_diff = line_diff + char_diff
    logger.debug('Distance of %d calculated between %r and %r', total_diff, a, b)
    return total_diff


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))
    grid = []
    for line in lines:
        grid.append(line.strip())
    universe = Universe(grid)

    for line_index, line in enumerate(lines):
        for character_index, character in enumerate(line):
            if character == '#':
                coord = Coordinate(line_index, character_index)
                logger.debug('Galaxy found at %r', coord)
                universe.add(coord)

    universe.expand()
    if props.debug:
        universe.visualise()

    pairs = itertools.combinations(universe.galaxies, 2)
    weights = [(calculate_distance(*pair), *pair) for pair in pairs]

    subtotal = 0
    for edge in weights:
        subtotal += edge[0]

    print(subtotal)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
