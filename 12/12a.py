#!/usr/bin/env python3

from dataclasses import dataclass
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


@cache
def fits(unknown: str, attempt: str):
    if len(attempt) > len(unknown):
        return False
    for index, character in enumerate(unknown[:len(attempt)]):
        if character != '?' and attempt[index] != character:
            return False
    return True


@dataclass(frozen=True)
class Partial:
    springs: str
    backups: tuple[int]


@cache
def count_permutations(partial: Partial) -> int:
    logger.log(hl.EXTRA_NOISY, 'Checking %r', partial)
    if len(partial.backups) < 1:
        count = 1 if '#' not in partial.springs else 0
        logger.log(hl.EXTRA_DETAIL, 'Returning count of %d for %r', count, partial)
        return count
    backup = partial.backups[0]
    if len(partial.springs) < backup:
        logger.log(hl.EXTRA_DETAIL, 'Returning count of 0 for %r', partial)
        return 0

    count = 0
    potential_match = backup * '#'
    if len(partial.springs) > backup:
        potential_match += '.'
    if fits(partial.springs, potential_match):
        # include count of sub-problems with this spring placed here
        springs_remainder = partial.springs[backup + 1:]
        sub_partial = Partial(springs_remainder, partial.backups[1:])
        sub_count = count_permutations(sub_partial)
        logger.log(hl.EXTRA_NOISY, 'Including sub-count of %d for %r from %r', sub_count, partial, sub_partial)
        count += sub_count

    if partial.springs[0] != '#':
        # include count of sub-problems with this spring not placed here
        springs_remainder = partial.springs[1:]
        sub_partial = Partial(springs_remainder, partial.backups)
        sub_count = count_permutations(sub_partial)
        logger.log(hl.EXTRA_NOISY, 'Including sub-count of %d for %r from %r', sub_count, partial, sub_partial)
        count += sub_count

    logger.log(hl.EXTRA_DETAIL, 'Returning count of %d for %r', count, partial)
    return count


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    count = 0
    for line in lines:
        logger.log(hl.EXTRA_DETAIL, '')
        logger.log(hl.EXTRA_DETAIL, 'Starting line %s', line[:-1])
        springs_label, backups_label = line.split()
        backup_labels = backups_label.split(',')
        backups = tuple(int(backup_label) for backup_label in backup_labels)

        start = Partial(springs_label, backups)
        sub_count = count_permutations(start)
        logger.debug('Returning count of %d for line %s', sub_count, line[:-1])
        count += sub_count

    print(count)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
