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


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    subtotal = 0
    for line in lines:
        if len(line) < 1:
            continue
        max_counts = {}
        game_label, cube_sets_label = line.split(':', 1)
        cube_sets = cube_sets_label.split(';')
        for cube_set in cube_sets:
            cube_counts = cube_set.split(',')
            for count_label in cube_counts:
                count_label = count_label.strip()
                count, colour = count_label.split(' ')
                count = int(count)
                if colour not in max_counts or count > max_counts[colour]:
                    max_counts[colour] = count
        game_power = 1
        for colour, max_count in max_counts.items():
            game_power *= max_count
        logger.debug('%s has power %d', game_label, game_power)
        subtotal += game_power

    print(subtotal)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
