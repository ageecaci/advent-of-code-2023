#!/usr/bin/env python3

import logging
import math
import pathlib
import sys
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

import lib.helper_args as ha
import lib.helper_file as hf
import lib.helper_log as hl


def midpoint(minimum: int, maximum: int) -> int:
    return math.floor((maximum - minimum)/2) + minimum



def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    _, times_label = lines[0].split(':', 1)
    _, distances_label = lines[1].split(':', 1)
    time_label = times_label.replace(" ", "")
    distance_label = distances_label.replace(" ", "")
    number_of_games = 1

    subtotal = 1
    for game in range(number_of_games):
        time_limit = int(time_label)
        distance_target = int(distance_label)

        starting_midpoint = midpoint(1, time_limit)
        lower_bound_range = (1, starting_midpoint)
        upper_bound_range = (starting_midpoint, time_limit)

        while lower_bound_range[1] - lower_bound_range[0] > 0:
            time_test = midpoint(lower_bound_range[0], lower_bound_range[1])
            remaining_time = time_limit - time_test
            distance_travelled = remaining_time * time_test
            if distance_travelled > distance_target:
                lower_bound_range = (lower_bound_range[0], time_test)
            else:
                lower_bound_range = (time_test + 1, lower_bound_range[1])

        while upper_bound_range[1] - upper_bound_range[0] > 0:
            time_test = midpoint(upper_bound_range[0], upper_bound_range[1])
            if time_test == upper_bound_range[0]:
                assert upper_bound_range[1] - upper_bound_range[0] == 1
                # Force the final iteration step to split the range
                time_test = upper_bound_range[1]
            remaining_time = time_limit - time_test
            distance_travelled = remaining_time * time_test
            if distance_travelled > distance_target:
                upper_bound_range = (time_test, upper_bound_range[1])
            else:
                upper_bound_range = (upper_bound_range[0], time_test - 1)

        winning_strategy_count = upper_bound_range[0] - lower_bound_range[0] + 1
        logging.debug(
            'Game %d has %s winning strategies (%d to %d)',
            game, winning_strategy_count, lower_bound_range[0], upper_bound_range[0])
        subtotal *= winning_strategy_count

    print(subtotal)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
