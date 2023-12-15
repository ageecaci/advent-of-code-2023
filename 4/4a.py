#!/usr/bin/env python3

import logging
import pathlib
import sys
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

import lib.helper_args as ha
import lib.helper_file as hf
import lib.helper_log as hl



def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    subtotal = 0
    for line in lines:
        if len(line) < 1:
            continue
        game_subtotal = 0
        righters = set()
        game_label, number_sets_label = line.split(':', 1)
        lefter_labels, righter_labels = number_sets_label.split('|', 1)
        for righter_label in righter_labels.split():
            righters.add(int(righter_label))
        for lefter_label in lefter_labels.split():
            lefter = int(lefter_label)
            if lefter in righters:
                if game_subtotal == 0:
                    game_subtotal = 1
                else:
                    game_subtotal *= 2
        logging.debug('%s is worth %d points', game_label, game_subtotal)
        subtotal += game_subtotal

    print(subtotal)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
