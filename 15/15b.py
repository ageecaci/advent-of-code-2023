#!/usr/bin/env python3

from collections.abc import Iterable
from dataclasses import dataclass, field
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

operator_remove = '-'
operator_add = '='


def convert_to_ascii_codes(input: str) -> Iterable[int]:
    codes = []
    for char in input:
        codes.append(ord(char))
    return codes


@cache
def wrap_subtotal(input: int) -> int:
    multiplied = input * 17
    logger.log(hl.EXTRA_NOISY, 'multiplying sequence sub-total %d -> %d', input, multiplied)
    return multiplied % 256


@cache
def aoc_hash(input: str) -> int:
    logger.log(hl.EXTRA_DETAIL, 'hashing input "%s"', input)
    ascii_codes = convert_to_ascii_codes(input)
    subtotal = 0
    for code_index, code in enumerate(ascii_codes):
        new_subtotal = subtotal + code
        logger.log(hl.EXTRA_NOISY, 'adding %d (char %s) to hash sub-total %d = %d',
                    code, input[code_index], subtotal, new_subtotal)
        subtotal = new_subtotal
        subtotal = wrap_subtotal(subtotal)
        logger.log(hl.EXTRA_NOISY, 'wrapping sequence sub-total %d -> %d',
                    new_subtotal, subtotal)
    return subtotal


@dataclass
class Station:
    boxes: list[dict[str, int]] = field(default_factory=lambda: [None] * 256)

    def add_to_box(self, label: str, focal_length: int):
        label_hash = aoc_hash(label)
        if self.boxes[label_hash] is None:
            self.boxes[label_hash] = {}
        box = self.boxes[label_hash]
        # dicts already preserve order of key insertion
        box[label] = focal_length

    def remove_from_box(self, label: str):
        label_hash = aoc_hash(label)
        box = self.boxes[label_hash]
        if box is None:
            return
        # dicts already preserve order of key insertion even after deletion
        if label in box:
            del box[label]
        if len(box) == 0:
            self.boxes[label_hash] = None

    def determine_focusing_powers(self) -> dict[str, int]:
        lenses = {}
        for box_index, box in enumerate(self.boxes):
            if box is None:
                continue
            for position, (label, focal_length) in enumerate(box.items()):
                power = (box_index + 1) * (position + 1) * focal_length
                logger.log(hl.EXTRA_NOISY, 'lens %s: box %d; slot %d; f-length %d = power %d',
                           label, box_index + 1, position + 1, focal_length, power)
                lenses[label] = power
        return lenses

    def visualise(self) -> str:
        string_forms = []
        for box_index, box in enumerate(self.boxes):
            if box is None:
                continue
            box_contents = []
            for label, focal_length in box.items():
                box_contents.append(f'[{label} {focal_length}]')
            string_forms.append(f'Box {box_index}: {"".join(box_contents)}')
        return '\n'.join(string_forms)


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))
    sequences = ''.join(lines).split(',')

    # hash label -> box number
    # if -: remove lens with label & reposition
    # if =:
    #       if label already in box, replace existing with new
    #       if label not in box, add lens to box behind others

    subtotal = 0
    station = Station()
    for sequence in sequences:
        sequence = sequence.strip()
        if operator_remove in sequence:
            label, _ = sequence.split(operator_remove, 1)
            station.remove_from_box(label)
        elif operator_add in sequence:
            label, focal_length_label = sequence.split(operator_add, 1)
            focal_length = int(focal_length_label)
            station.add_to_box(label, focal_length)
        logger.log(hl.EXTRA_DETAIL, 'After "%s"\n%s\n', sequence, station.visualise())

    lens_powers = station.determine_focusing_powers()
    if logger.isEnabledFor(hl.EXTRA_DETAIL) and not logger.isEnabledFor(hl.EXTRA_NOISY):
        for label, power in lens_powers.items():
            logger.log(hl.EXTRA_DETAIL, 'lens "%s" has power %d', label, power)
    subtotal = sum(lens_powers.values())
    print(subtotal)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
