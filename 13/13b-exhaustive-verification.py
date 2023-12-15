#!/usr/bin/env python3

import logging
import pathlib
import sys
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

import lib.helper_args as ha
import lib.helper_file as hf
import lib.helper_log as hl

logger = logging.getLogger(__file.stem)


def find_horizontal_reflection_point(grid: list[str]) -> int:
    width = len(grid[0])
    potential_matches = []
    for column_to_check in range(1, width):
        logger.log(hl.EXTRA_NOISY, 'Checking column %s', column_to_check)
        if is_horizontal_reflection_point(column_to_check, grid):
            potential_matches.append(column_to_check)
    if len(potential_matches) == 1:
        return potential_matches[0]
    if len(potential_matches) > 1:
        raise Exception(f'Multiple horizontal reflection points found: {potential_matches}')
    return -1


def find_vertical_reflection_point(grid: list[str]) -> int:
    depth = len(grid)
    potential_matches = []
    for row_to_check in range(1, depth):
        logger.log(hl.EXTRA_NOISY, 'Checking row %s', row_to_check)
        if is_vertical_reflection_point(row_to_check, grid):
            potential_matches.append(row_to_check)
    if len(potential_matches) == 1:
        return potential_matches[0]
    if len(potential_matches) > 1:
        raise Exception(f'Multiple vertical reflection points found: {potential_matches}')
    return -1


def is_horizontal_reflection_point(column: int, grid: list[str]) -> bool:
    width = len(grid[0])
    current_left_column = column - 1
    current_right_column = column
    error_count = 0
    while error_count < 2:
        if current_left_column < 0 or current_right_column >= width:
            break
        for line_index, line in enumerate(grid):
            if line[current_left_column] != line[current_right_column]:
                logger.log(hl.EXTRA_DETAIL, 'Detected difference for line %d between columns %d and %d: %s does not match %s', line_index, current_left_column, current_right_column, line[current_left_column], line[current_right_column])
                error_count += 1
        current_left_column -= 1
        current_right_column += 1
    return error_count == 1


def is_vertical_reflection_point(row: int, grid: list[str]) -> bool:
    width = len(grid[0])
    depth = len(grid)
    current_top_row = row - 1
    current_bottom_row = row
    error_count = 0
    while error_count < 2:
        if current_top_row < 0 or current_bottom_row >= depth:
            break
        for column in range(width):
            if grid[current_top_row][column] != grid[current_bottom_row][column]:
                logger.log(hl.EXTRA_DETAIL, 'Detected difference for column %d between lines %d and %d: %s does not match %s', column, current_top_row, current_bottom_row, grid[current_top_row][column], grid[current_bottom_row][column])
                error_count += 1
        current_top_row -= 1
        current_bottom_row += 1
    return error_count == 1


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
        logger.log(hl.EXTRA_DETAIL, '')
        logger.log(hl.EXTRA_DETAIL, 'Starting searches for pattern %d (starting "%s")', pattern_index, pattern[0])
        horizontal = find_horizontal_reflection_point(pattern)
        if horizontal > 0:
            logger.debug('found a horizontal reflection point for pattern %d at %d', pattern_index, horizontal)
            subtotal += horizontal
        vertical = find_vertical_reflection_point(pattern)
        if vertical > 0:
            logger.debug('found a vertical reflection point for pattern %d at %d', pattern_index, vertical)
            subtotal += 100 * vertical
        if horizontal > 0 and vertical > 0:
            raise Exception(f'Multiple reflection points (v{vertical}, h{horizontal}) found for pattern {pattern_index} (starting "{pattern[0]}")')
        if horizontal < 0 and vertical < 0:
            raise Exception(f'No reflection point found for pattern {pattern_index} (starting "{pattern[0]}")')

    print(subtotal)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
