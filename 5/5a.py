#!/usr/bin/env python3

import bisect
import logging
import operator
import pathlib
import sys
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

from bidict import bidict

import lib.helper_args as ha
import lib.helper_file as hf
import lib.helper_log as hl

logger = logging.getLogger(__file.stem)


class Instruction:
    def __init__(self, destination_start, source_start, range_length):
        self.destination_start = destination_start
        self.source_start = source_start
        self.destination_end = destination_start + range_length - 1
        self.source_end = source_start + range_length - 1
        self.destination_range = (destination_start, self.destination_end)
        self.source_range = (source_start, self.source_end)
        self.range_length = range_length

    def map(self, input: int) -> int:
        if input < self.source_start or input > self.source_range[1]:
            raise Exception(f'Input {input} not in source range {self.source_range}')
        input_offset = input - self.source_start
        return self.destination_start + input_offset


class RangeMap:
    def __init__(self):
        # self._minimums = []
        # self._maximums = []
        self._ranges = []

    def insert(self, range: Instruction) -> None:
        # https://stackoverflow.com/a/5528318
        bisect.insort(self._ranges, range, key=operator.attrgetter('source_range'))

    def find(self, input: int) -> Instruction:
        # want the range with minimum less than input and maximum greater than input
        # bisect_right returns the index of the element _after_ an appropriate minimum, if any
        matching_minimum = bisect.bisect_right(self._ranges, input, key=operator.attrgetter('source_start')) - 1
        # bisect_left returns the index of an appropriate maximum, if any
        matching_maximum = bisect.bisect_left(self._ranges, input, key=operator.attrgetter('source_end'))
        if matching_minimum == matching_maximum and matching_minimum < len(self._ranges):
            return self._ranges[matching_minimum]
        return None


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    target_seeds = lines[0]
    dependency_mappings = bidict()
    dependency_instructions = {}
    seed_locations = {}

    dependencies = {}
    i = 2
    current_map_label = ''
    current_map = []
    while i < len(lines):
        line = lines[i].strip()
        if len(line) < 1:
            if len(current_map_label) < 1:
                logger.debug('Empty map label encountered during break: skipping')
            elif len(current_map) < 1:
                logger.warn('Empty mapping encountered for %s', current_map_label)
                current_map_label = ''
            else:
                dependencies[current_map_label] = current_map
                current_map_label = ''
                current_map = []
        elif len(current_map_label) < 1:
            current_map_label = line
        else:
            current_map.append(line)
        i += 1
    dependencies[current_map_label] = current_map
    if len(current_map) < 1:
        logger.warn('Empty mapping encountered for %s', current_map_label)
    else:
        dependencies[current_map_label] = current_map
    logger.debug('Extracted %d dependencies from almanac', len(dependencies))

    for map_label, map_instructions in dependencies.items():
        trimmed_map_label, _ = map_label.split(None, 1)
        source, destination = trimmed_map_label.split('-to-', 1)
        dependency_mappings[source] = destination
        logger.debug('Adding mapping from %s to %s', source, destination)
        instructions = RangeMap()
        for map_instruction in map_instructions:
            instruction_labels = map_instruction.split()
            if len(instruction_labels) > 3:
                logger.warn('More than 3 instructions found in almanac: %s (%s)', map_label, map_instruction)
            destination_start = int(instruction_labels[0])
            source_start = int(instruction_labels[1])
            range_length = int(instruction_labels[2])
            instruction = Instruction(destination_start, source_start, range_length)
            instructions.insert(instruction)
        dependency_instructions[source] = instructions

    # assert there is a route from seed to location
    checker = 'location'
    while checker != 'seed':
        if checker not in dependency_mappings.inverse:
            raise Exception(f'No inverse mapping found for {checker}')
        checker = dependency_mappings.inverse[checker]
    logger.debug('Found valid mapping path from seed to location')

    _, seeds_label = target_seeds.split(':', 1)
    seed_labels = seeds_label.split()

    for seed_label in seed_labels:
        seed = int(seed_label.strip())
        target_index = seed
        target_property = 'seed'
        while True:
            ranges = dependency_instructions[target_property]
            range = ranges.find(target_index)
            if range != None:
                next_index = range.map(target_index)
            else:
                next_index = target_index
            next_property = dependency_mappings[target_property]
            logger.debug('mapping %s %d to %s %d', target_property, target_index, next_property, next_index)
            target_index = next_index
            target_property = next_property
            if target_property == 'location':
                break
        seed_locations[seed] = target_index

    closest_location = min(seed_locations.values())
    print(closest_location)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
