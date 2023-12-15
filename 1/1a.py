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

NUMBERS = '0123456789'


def find_first_number(line):
    for c in line:
        if c in NUMBERS:
            return int(c)
    raise Exception('No number found')


def find_last_number(line):
    for c in reversed(line):
        if c in NUMBERS:
            return int(c)
    raise Exception('No number found')


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    subtotal = 0
    for line in lines:
        first = find_first_number(line)
        last = find_last_number(line)
        result = f'{first}{last}'
        logger.debug(result)
        subtotal += int(result)

    print(subtotal)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
