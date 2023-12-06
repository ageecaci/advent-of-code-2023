#!/usr/bin/env python3

import logging
import math
import os
import sys
sys.path.append(os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..')))

import lib.helper_args as ha
import lib.helper_file as hf
import lib.helper_log as hl


def min_if_not_unset(new_value: int, existing_value: int, label: str) -> int:
    if existing_value < 0:
        logging.debug('New min for %s: %d (was %d)', label, new_value, existing_value)
        return new_value
    new_minimum = min(new_value, existing_value)
    if new_minimum != existing_value:
        logging.debug('New min for %s: %d (was %d)', label, new_value, existing_value)
    return new_minimum


def max_if_not_unset(new_value: int, existing_value: int, label: str) -> int:
    if existing_value < 0:
        logging.debug('New max for %s: %d (was %d)', label, new_value, existing_value)
        return new_value
    new_maximum = max(new_value, existing_value)
    if new_maximum != existing_value:
        logging.debug('New max for %s: %d (was %d)', label, new_value, existing_value)
    return new_maximum


def midpoint(minimum: int, maximum: int) -> int:
    return math.floor((maximum - minimum)/2) + minimum



def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    _, times_label = lines[0].split(':', 1)
    _, distances_label = lines[1].split(':', 1)
    time_labels = times_label.split()
    distance_labels = distances_label.split()
    assert len(time_labels) == len(distance_labels)
    number_of_games = len(time_labels)

    subtotal = 1
    for game in range(number_of_games):
        time_limit = int(time_labels[game])
        distance_target = int(distance_labels[game])

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