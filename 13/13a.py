#!/usr/bin/env python3

from dataclasses import dataclass
import logging
import operator
import os
import sys
sys.path.append(os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..')))

import lib.helper_args as ha
import lib.helper_file as hf
import lib.helper_log as hl


def find_horizontal_reflection_point(grid: list[str]) -> int:
    width = len(grid[0])
    for column_to_check in range(1, width):
        logging.log(hl.EXTRA_NOISY, 'Checking column %s', column_to_check)
        if is_horizontal_reflection_point(column_to_check, grid):
            return column_to_check
    return -1


def find_vertical_reflection_point(grid: list[str]) -> int:
    depth = len(grid)
    for row_to_check in range(1, depth):
        logging.log(hl.EXTRA_NOISY, 'Checking row %s', row_to_check)
        if is_vertical_reflection_point(row_to_check, grid):
            return row_to_check
    return -1


def is_horizontal_reflection_point(column: int, grid: list[str]) -> bool:
    width = len(grid[0])
    current_left_column = column - 1
    current_right_column = column
    still_potential_reflection_point = True
    while still_potential_reflection_point:
        if current_left_column < 0 or current_right_column >= width:
            return True
        for line_index, line in enumerate(grid):
            if line[current_left_column] != line[current_right_column]:
                logging.log(hl.EXTRA_DETAIL, 'Detected difference for line %d between columns %d and %d: %s does not match %s', line_index, current_left_column, current_right_column, line[current_left_column], line[current_right_column])
                still_potential_reflection_point = False
                break
        current_left_column -= 1
        current_right_column += 1
    return False


def is_vertical_reflection_point(row: int, grid: list[str]) -> bool:
    width = len(grid[0])
    depth = len(grid)
    current_top_row = row - 1
    current_bottom_row = row
    still_potential_reflection_point = True
    while still_potential_reflection_point:
        if current_top_row < 0 or current_bottom_row >= depth:
            return True
        for column in range(width):
            if grid[current_top_row][column] != grid[current_bottom_row][column]:
                logging.log(hl.EXTRA_DETAIL, 'Detected difference for column %d between lines %d and %d: %s does not match %s', column, current_top_row, current_bottom_row, grid[current_top_row][column], grid[current_bottom_row][column])
                still_potential_reflection_point = False
                break
        current_top_row -= 1
        current_bottom_row += 1
    return False


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    patterns = []
    pattern = []
    for line in lines:
        stripped_line = line.strip()
        if len(stripped_line) < 1:
            if len(pattern) > 1:
                patterns.append(pattern)
                pattern = []
        else:
            pattern.append(stripped_line)
    if len(pattern) > 1:
        patterns.append(pattern)

    subtotal = 0
    for pattern_index, pattern in enumerate(patterns):
        logging.log(hl.EXTRA_DETAIL, '')
        logging.log(hl.EXTRA_DETAIL, 'Starting searches for pattern %d (starting "%s")', pattern_index, pattern[0])
        horizontal = find_horizontal_reflection_point(pattern)
        if horizontal > 0:
            logging.debug('found a horizontal reflection point for pattern %d at %d', pattern_index, horizontal)
            subtotal += horizontal
            continue
        vertical = find_vertical_reflection_point(pattern)
        if vertical > 0:
            logging.debug('found a vertical reflection point for pattern %d at %d', pattern_index, vertical)
            subtotal += 100 * vertical
            continue
        raise Exception(f'No reflection point found for pattern {pattern_index} (starting "{pattern[0]}")')

    print(subtotal)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
