#!/usr/bin/env python3

from collections import deque
import logging
import pathlib
import sys
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

import lib.helper_args as ha
import lib.helper_file as hf
import lib.helper_log as hl

logger = logging.getLogger(__file.stem)

pulse_high = 'high'
pulse_low = 'low'
type_broadcaster = 'broadcaster'
type_button = 'button'
type_conjunction = '&'
type_flip_flop = '%'
type_unknown = '-'


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    source_map_to_type: dict[str, str] = {}
    source_map_to_destination: dict[str, list[str]] = {}
    destination_map_to_source: dict[str, list[str]] = {}
    for line in lines:
        source_label, destinations_label = line.split(' -> ')
        destination_labels = destinations_label.split(', ')
        if source_label == type_broadcaster:
            source_key = type_broadcaster
            source_type = type_broadcaster
        else:
            source_type = source_label[0]
            source_key = source_label[1:]
        source_map_to_type[source_key] = source_type
        source_map_to_destination[source_key] = destination_labels
        for destination_key in destination_labels:
            if destination_key not in destination_map_to_source:
                destination_map_to_source[destination_key] = []
            destination_map_to_source[destination_key].append(source_key)
    destination_map_to_source[type_broadcaster] = [type_button]

    visited_modules = set()
    modules = deque()
    modules.append(type_broadcaster)
    print('graph TD;')
    while len(modules) > 0:
        next = modules.popleft()
        if next in visited_modules:
            continue
        visited_modules.add(next)
        for dest in source_map_to_destination.get(next, []):
            print(f'{next} --> {dest};')
            modules.append(dest)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
