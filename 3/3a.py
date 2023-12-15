#!/usr/bin/env python3

import json
import logging
import pathlib
import sys
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

import numpy as np

from lib.class_text_coordinate_limits import TextCoordinateLimits as Limits
from lib.class_text_coordinate import TextCoordinate as Coordinate
import lib.helper_args as ha
import lib.helper_coord as hc
import lib.helper_file as hf
import lib.helper_log as hl

# characters = '#$%&*+-./0123456789=@' + '\n'
symbols = '#$%&*+-/=@'
digits = '0123456789'


def find_characters(lines):
    characters = set()
    for i in range(len(lines)):
        line = lines[i]
        for j in range(len(line)):
            characters.add(line[j])
    print(json.dumps(sorted(list(characters))))


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    depth = len(lines)
    width = len(lines[0])
    limits = Limits(depth, width)

    # find all symbols
    symbol_coords = []
    for i in range(len(lines)):
        line = lines[i]
        for j in range(len(line)):
            character = line[j]
            if character in symbols:
                symbol_coords.append(Coordinate(i, j))
    logging.debug('Discovered %d symbol coordinates: %r', len(symbol_coords), symbol_coords)

    # mark adjacent digits
    adjacent = np.full((depth, width), False, np.bool_)
    for symbol in symbol_coords:
        for neighbour in hc.valid_neighbours(symbol, limits):
            neighbour_character = lines[neighbour.line][neighbour.character]
            if neighbour_character in digits:
                adjacent[neighbour.line, neighbour.character] = True

    # for each "adjacent digit" find the "adjacent number"
    for i in range(depth):
        for j in range(width):
            if adjacent[i, j]:
                k = j - 1
                while k >= 0:
                    if adjacent[i, k]:
                        break
                    elif lines[i][k] in digits:
                        adjacent[i, k] = True
                    else:
                        break
                    k -= 1
                k = j + 1
                while k < width:
                    if adjacent[i, k]:
                        break
                    elif lines[i][k] in digits:
                        adjacent[i, k] = True
                    else:
                        break
                    k += 1

    subtotal = 0
    for i in range(depth):
        number = ''
        j = 0
        while j < width:
            if adjacent[i, j]:
                number += lines[i][j]
            elif len(number) > 0:
                logging.debug('Discovered adjacent number: %s', number)
                subtotal += int(number)
                number = ''
            j += 1
        if len(number) > 0:
            logging.debug('Discovered adjacent number: %s', number)
            subtotal += int(number)
            number = ''

    print(subtotal)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
