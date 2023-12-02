#!/usr/bin/env python3

import logging
import os
import sys
sys.path.append(os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..')))

import lib.helper_args as ha
import lib.helper_file as hf
import lib.helper_log as hl


limits = {
    'red': 12,
    'green': 13,
    'blue': 14
}


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    subtotal = 0
    for line in lines:
        if len(line) < 1:
            continue
        game_valid = True
        game_label, cube_sets_label = line.split(':', 1)
        cube_sets = cube_sets_label.split(';')
        for cube_set in cube_sets:
            if not game_valid:
                break
            cube_counts = cube_set.split(',')
            for count_label in cube_counts:
                count_label = count_label.strip()
                count, colour = count_label.split(' ')
                count = int(count)
                if colour not in limits or count > limits[colour]:
                    logging.debug('%s failed with %s', game_label, count_label)
                    game_valid = False
                    break
        if game_valid:
            logging.debug('%s succeeded', game_label)
            subtotal += int(game_label[5:])

    print(subtotal)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
