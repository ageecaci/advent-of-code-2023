#!/usr/bin/env python3

import json
import logging
import os
import sys
sys.path.append(os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..')))

import numpy as np

from lib.class_text_coordinate_limits import TextCoordinateLimits as Limits
from lib.class_text_coordinate import TextCoordinate as Coordinate
import lib.helper_args as ha
import lib.helper_coord as hc
import lib.helper_file as hf
import lib.helper_log as hl

# characters = '#$%&*+-./0123456789=@' + '\n'
symbols = '*'
digits = '0123456789'


def find_characters(lines):
    characters = set()
    for i in range(len(lines)):
        line = lines[i]
        for j in range(len(line)):
            characters.add(line[j])
    print(json.dumps(sorted(list(characters))))


def find_contiguous_matches_to_left(string: str, start_index: int, matching_characters: str):
    matching_substr = ''
    i = start_index - 1
    while i >= 0:
        if string[i] in matching_characters:
            matching_substr = string[i] + matching_substr
        else:
            break
        i -= 1
    return matching_substr


def find_contiguous_matches_to_right(string: str, start_index: int, matching_characters: str):
    matching_substr = ''
    i = start_index + 1
    while i < len(string):
        if string[i] in matching_characters:
            matching_substr += string[i]
        else:
            break
        i += 1
    return matching_substr


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    # as we iterate over lines first, max "x" is actually depth
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

    subtotal = 0
    for symbol in symbol_coords:
        # filter out gears without exactly two adjacent numbers
        gear_adjacent = np.full((3, 3), False, np.bool_)
        for neighbour in hc.valid_neighbours(symbol, limits):
            neighbour_character = lines[neighbour.line][neighbour.character]
            if neighbour_character in digits:
                gear_adjacent[neighbour.line - symbol.line + 1, neighbour.character - symbol.character + 1] = True
        count = 0
        # horizontal matches can never overlap with other matches
        if gear_adjacent[1, 0]:
            count += 1
        if gear_adjacent[1, 2]:
            count += 1
        # if above/below matched, then at most 1 number can be present
        # otherwise count corners
        if gear_adjacent[0, 1]:
            count += 1
        else:
            if gear_adjacent[0, 0]:
                count += 1
            if gear_adjacent[0, 2]:
                count += 1
        if gear_adjacent[2, 1]:
            count += 1
        else:
            if gear_adjacent[2, 0]:
                count += 1
            if gear_adjacent[2, 2]:
                count += 1
        if count != 2:
            continue
        logging.debug('Found valid gear: %s', symbol)

        # find adjacent numbers from the adjacent digits
        gear_power = 1
        if gear_adjacent[1, 0]: # left
            number = (find_contiguous_matches_to_left(lines[symbol.line], symbol.character - 1, digits)
                      + lines[symbol.line][symbol.character - 1])
            logging.debug('  Gear number: %s', number)
            gear_power *= int(number)
        if gear_adjacent[1, 2]: # right
            number = (lines[symbol.line][symbol.character + 1]
                      + find_contiguous_matches_to_right(lines[symbol.line], symbol.character + 1, digits))
            logging.debug('  Gear number: %s', number)
            gear_power *= int(number)
        if gear_adjacent[0, 1]: # up
            number = (find_contiguous_matches_to_left(lines[symbol.line - 1], symbol.character, digits)
                      + lines[symbol.line - 1][symbol.character]
                      + find_contiguous_matches_to_right(lines[symbol.line - 1], symbol.character, digits))
            logging.debug('  Gear number: %s', number)
            gear_power *= int(number)
        else:
            if gear_adjacent[0, 0]: # up left
                number = (find_contiguous_matches_to_left(lines[symbol.line - 1], symbol.character - 1, digits)
                          + lines[symbol.line - 1][symbol.character - 1])
                logging.debug('  Gear number: %s', number)
                gear_power *= int(number)
            if gear_adjacent[0, 2]: # up right
                number = (lines[symbol.line - 1][symbol.character + 1]
                          + find_contiguous_matches_to_right(lines[symbol.line - 1], symbol.character + 1, digits))
                logging.debug('  Gear number: %s', number)
                gear_power *= int(number)
        if gear_adjacent[2, 1]: # down
            number = (find_contiguous_matches_to_left(lines[symbol.line + 1], symbol.character, digits)
                      + lines[symbol.line + 1][symbol.character]
                      + find_contiguous_matches_to_right(lines[symbol.line + 1], symbol.character, digits))
            logging.debug('  Gear number: %s', number)
            gear_power *= int(number)
        else:
            if gear_adjacent[2, 0]: # down left
                number = (find_contiguous_matches_to_left(lines[symbol.line + 1], symbol.character - 1, digits)
                          + lines[symbol.line + 1][symbol.character - 1])
                logging.debug('  Gear number: %s', number)
                gear_power *= int(number)
            if gear_adjacent[2, 2]: # down right
                number = (lines[symbol.line + 1][symbol.character + 1]
                          + find_contiguous_matches_to_right(lines[symbol.line + 1], symbol.character + 1, digits))
                logging.debug('  Gear number: %s', number)
                gear_power *= int(number)
        logging.debug('  Gear power: %s', gear_power)
        subtotal += gear_power

    print(subtotal)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
