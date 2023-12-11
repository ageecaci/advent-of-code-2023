#!/usr/bin/env python3

import itertools
import logging
# import operator
import os
import sys
sys.path.append(os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..')))

import numpy as np

from lib.class_text_coordinate import TextCoordinate as Coordinate
import lib.helper_args as ha
import lib.helper_file as hf
import lib.helper_log as hl


class Universe:
    def __init__(self, grid: list[str]):
        self.grid = grid
        self.depth = len(grid)
        self.width = len(grid[0])
        self.galaxies: set[Coordinate] = set()
        self.rows_without_galaxies = np.ones(self.depth, np.int8)
        self.columns_without_galaxies = np.ones(self.width, np.int8)

    def add(self, coord: Coordinate):
        self.galaxies.add(coord)
        self.rows_without_galaxies[coord.line] = 0
        self.columns_without_galaxies[coord.character] = 0

    def expand(self):
        expanded_galaxies: set[Coordinate] = set()
        for galaxy in self.galaxies:
            extra_rows = sum(self.rows_without_galaxies[:galaxy.line])
            extra_columns = sum(self.columns_without_galaxies[:galaxy.character])
            new_loc = Coordinate(galaxy.line + extra_rows, galaxy.character + extra_columns)
            logging.debug('Expanding: %r moved to %r', galaxy, new_loc)
            expanded_galaxies.add(new_loc)
        self.galaxies = expanded_galaxies


def calculate_distance(a: Coordinate, b: Coordinate) -> int:
    line_diff = abs(a.line - b.line)
    char_diff = abs(a.character - b.character)
    total_diff = line_diff + char_diff
    logging.debug('Distance of %d calculated between %r and %r', total_diff, a, b)
    return total_diff


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))
    universe = Universe(lines)

    # locate galaxies
    for line_index, line in enumerate(lines):
        for character_index, character in enumerate(line):
            if character == '#':
                coord = Coordinate(line_index, character_index)
                logging.debug('Galaxy found at %r', coord)
                universe.add(coord)

    universe.expand()

    pairs = itertools.combinations(universe.galaxies, 2)
    weights = [(calculate_distance(*pair), *pair) for pair in pairs]
    # unnecessary minimum spanning tree implementation
    # weights.sort(key=operator.itemgetter(0))

    # tree = set()
    # linked_galaxies = set()
    # for edge in weights:
    #     if edge[1] not in linked_galaxies or edge[2] not in linked_galaxies:
    #         tree.add(edge)
    #         linked_galaxies.add(edge[1])
    #         linked_galaxies.add(edge[2])
    #     if len(tree) == len(universe.galaxies) - 1:
    #         break

    # subtotal = 0
    # for edge in tree:
    #     subtotal += edge[0]

    subtotal = 0
    for edge in weights:
        subtotal += edge[0]

    print(subtotal)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
