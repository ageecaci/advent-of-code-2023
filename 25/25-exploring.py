#!/usr/bin/env python3

from collections import defaultdict
import logging
import pathlib
import sys
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

import lib.helper_args as ha
import lib.helper_graph as hg
import lib.helper_file as hf
import lib.helper_log as hl

logger = logging.getLogger(__file.stem)


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    nodes: set[str] = set()
    edges: dict[str, set[str]] = defaultdict(set)
    edge_set: set[tuple[str, str]] = set()
    for line in lines:
        source_label, destinations_label = line.split(': ')
        destination_labels = destinations_label.split()
        nodes.add(source_label)
        for destination_label in destination_labels:
            nodes.add(destination_label)
            edges[source_label].add(destination_label)
            edges[destination_label].add(source_label)
            edge_set.add(tuple(sorted((source_label, destination_label))))

    for node in nodes:
        print(f'Node "{node}" is connected to {len(edges[node])} other nodes: {", ".join(edges[node])}')
    print('')
    print('Mermaid graph:')
    hg.to_mermaid(edge_set)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
