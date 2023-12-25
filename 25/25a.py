#!/usr/bin/env python3

import logging
import pathlib
import sys
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

import networkx as nx

import lib.helper_args as ha
import lib.helper_file as hf
import lib.helper_log as hl

logger = logging.getLogger(__file.stem)


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))
    g = nx.parse_adjlist(
        line.replace(':', '') for line in lines)
    edge_cut = nx.minimum_edge_cut(g)
    assert len(edge_cut) == 3

    for edge in edge_cut:
        g.remove_edge(*edge)
    count = 0
    subtotal = 1
    for component in nx.connected_components(g):
        subtotal *= len(component)
        count += 1
    assert count == 2
    print(subtotal)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
