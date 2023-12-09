#!/usr/bin/env python3

import collections
import logging
import os
import sys
sys.path.append(os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..')))

import lib.helper_args as ha
import lib.helper_file as hf
import lib.helper_log as hl


def all_zeros(sequence: list[int]) -> bool:
    for item in sequence:
        if item != 0:
            return False
    return True


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    next_predictions = []
    for line in lines:
        seq = list(map(int, line.split()))
        diffs = [seq]
        found_seq_end = False
        for i in range(1, len(seq)):
            last_diff = diffs[i-1]
            diff = [ last_diff[j] - last_diff[j-1] for j in range(1, len(last_diff)) ]
            diffs.append(diff)
            if all_zeros(diff):
                found_seq_end = True
                break
        if not found_seq_end:
            logging.error('%r', diffs)
            raise Exception('Ran out of differences for sequence')
        for i in range(len(diffs) - 1, 0, -1):
            diff = diffs[i - 1]
            diff_diff = diffs[i]
            diff.append(diff[0] - diff_diff[-1])
        logging.debug('New sequence (last elements should be at start): %r', diffs)
        next_predictions.append(diffs[0][-1])

    logging.debug('Predictions: %r', next_predictions)
    print(sum(next_predictions))


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
