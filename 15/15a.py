#!/usr/bin/env python3

from collections.abc import Iterable
from functools import cache
import logging
import pathlib
import sys
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

import lib.helper_args as ha
import lib.helper_file as hf
import lib.helper_log as hl

logger = logging.getLogger(__file.stem)


def ascii_codes(input: str) -> Iterable[int]:
    codes = []
    for char in input:
        codes.append(ord(char))
    return codes


@cache
def wrap_subtotal(input: int) -> int:
    multiplied = input * 17
    logger.log(hl.EXTRA_NOISY, 'multiplying sequence sub-total %d -> %d', input, multiplied)
    return multiplied % 256


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    sequences = ''.join(lines).split(',')

    subtotal = 0
    for sequence in sequences:
        sequence = sequence.strip()
        logger.log(hl.EXTRA_DETAIL, 'starting sequence %s', sequence)
        sequence_ascii_codes = ascii_codes(sequence)
        sequence_subtotal = 0
        for code_index, code in enumerate(sequence_ascii_codes):
            new_sequence_subtotal = sequence_subtotal + code
            logger.log(hl.EXTRA_NOISY, 'adding %d (char %s) to sequence sub-total %d = %d',
                        code, sequence[code_index], sequence_subtotal, new_sequence_subtotal)
            sequence_subtotal = new_sequence_subtotal
            sequence_subtotal = wrap_subtotal(sequence_subtotal)
            logger.log(hl.EXTRA_NOISY, 'wrapping sequence sub-total %d -> %d',
                        new_sequence_subtotal, sequence_subtotal)
        logger.debug('sequence %s has hash %d', sequence, sequence_subtotal)
        subtotal += sequence_subtotal

    print(subtotal)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
