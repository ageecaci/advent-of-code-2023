#!/usr/bin/env python3

import logging
import pathlib
import sys
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

import lib.helper_args as ha
import lib.helper_file as hf
import lib.helper_log as hl

NUMBERS = {
    '0': 0,
    '1': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9,
}

NUMBERS_REVERSED = {
    '0': 0,
    '1': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    'eno': 1,
    'owt': 2,
    'eerht': 3,
    'ruof': 4,
    'evif': 5,
    'xis': 6,
    'neves': 7,
    'thgie': 8,
    'enin': 9,
}


def get_substring_match(to_test, matches=NUMBERS):
    for k in matches:
        if len(k) <= len(to_test) and k == to_test[0:len(k)]:
            return matches[k]
    return -1


def find_first_number(line):
    for i in range(len(line)):
        potential_match = get_substring_match(line[i:])
        if potential_match >= 0:
            return potential_match
    raise Exception('No number found')


def find_last_number(line):
    target = line[::-1]
    for i in range(len(target)):
        potential_match = get_substring_match(target[i:], NUMBERS_REVERSED)
        if potential_match >= 0:
            return potential_match
    raise Exception('No number found')


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    subtotal = 0
    for line in lines:
        first = find_first_number(line)
        last = find_last_number(line)
        result = f'{first}{last}'
        logging.debug(result)
        subtotal += int(result)

    print(subtotal)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
