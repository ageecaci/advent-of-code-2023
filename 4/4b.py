#!/usr/bin/env python3

import logging
import pathlib
import sys
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

import numpy as np

import lib.helper_args as ha
import lib.helper_file as hf
import lib.helper_log as hl



def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    matching_numbers = np.zeros(len(lines), np.int8)
    for line in lines:
        if len(line) < 1:
            continue
        matching_game_numbers = 0
        righters = set()
        game_label, number_sets_label = line.split(':', 1)
        game_number = int(game_label.split()[1])
        lefter_labels, righter_labels = number_sets_label.split('|', 1)
        for righter_label in righter_labels.split():
            righters.add(int(righter_label))
        for lefter_label in lefter_labels.split():
            lefter = int(lefter_label)
            if lefter in righters:
                matching_game_numbers += 1
        logging.debug('%s has %d matching numbers', game_label, matching_game_numbers)
        matching_numbers[game_number - 1] = matching_game_numbers

    copy_count = np.ones(len(lines), np.longlong)
    for game_number in range(len(matching_numbers)):
        matches = matching_numbers[game_number]
        for i in range(matches):
            copy_count[game_number + i + 1] += copy_count[game_number]
    logging.debug('Copy counts: %r', copy_count)

    subtotal = 0
    for count in copy_count:
        subtotal += count

    print(subtotal)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
