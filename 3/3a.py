#!/usr/bin/env python3

import json
import logging
import os
import sys
sys.path.append(os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..')))

import numpy as np

from lib.class_coordinate import Coordinate as cco
import lib.helper_args as ha
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


def does_character_match(grid: list[str], coord: cco, matching_characters: str):
    return grid[coord.x][coord.y] in matching_characters


'''
minimums are inclusive, maximums are exclusive
gen_neighbours(cco(1,1), max_x=3, max_y=3) -> cco(0,0)..cco(2,2)
'''
def valid_neighbours(coord: cco, *args, min_x=0, max_x, min_y=0, max_y):
    if min_x >= max_x:
        return
    if min_y >= max_y:
        return
    for neighbour in gen_neighbours(coord):
        if neighbour.x >= min_x and neighbour.x < max_x:
            if neighbour.y >= min_y and neighbour.y < max_y:
                yield neighbour


def gen_neighbours(coord: cco):
    yield cco(coord.x - 1, coord.y - 1)
    yield cco(coord.x - 1, coord.y)
    yield cco(coord.x - 1, coord.y + 1)
    yield cco(coord.x, coord.y - 1)
    yield cco(coord.x, coord.y + 1)
    yield cco(coord.x + 1, coord.y - 1)
    yield cco(coord.x + 1, coord.y)
    yield cco(coord.x + 1, coord.y + 1)


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    # as we iterate over lines first, max "x" is actually depth
    depth = len(lines)
    width = len(lines[0])

    # find all symbols
    symbol_coords = []
    for i in range(len(lines)):
        line = lines[i]
        for j in range(len(line)):
            character = line[j]
            if character in symbols:
                symbol_coords.append(cco(i, j))
    logging.debug('Discovered %d symbol coordinates: %r', len(symbol_coords), symbol_coords)

    # mark adjacent digits
    adjacent = np.full((depth, width), False, np.bool_)
    for symbol in symbol_coords:
        for neighbour in valid_neighbours(symbol, max_x=depth, max_y=width):
            neighbour_character = lines[neighbour.x][neighbour.y]
            if neighbour_character in digits:
                adjacent[neighbour.x, neighbour.y] = True

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
