#!/usr/bin/env python3

from dataclasses import dataclass
from collections import deque
from dataclasses import dataclass, field
import logging
import pathlib
import sys
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

from lib.class_map_base import Map
from lib.class_text_coordinate import TextCoordinate as Coordinate
import lib.helper_args as ha
import lib.helper_coord as hc
import lib.helper_direction as hd
import lib.helper_file as hf
import lib.helper_log as hl

logger = logging.getLogger(__file.stem)

map_path = '.'
map_wall = '#'
map_slope_up = '^'
map_slope_down = 'v'
map_slope_left = '<'
map_slope_right = '>'
map_slope_directions = {
    map_slope_up: hd.UP,
    map_slope_down: hd.DOWN,
    map_slope_left: hd.LEFT,
    map_slope_right: hd.RIGHT,
}


@dataclass
class ExplorationResults:
    ends: set[Coordinate] = field(default_factory=set)
    terminals: set[Coordinate] = field(default_factory=set)
    internals: set[Coordinate] = field(default_factory=set)
    new_locations: set[Coordinate] = field(default_factory=set)


def explore(map: Map, start: Coordinate) -> ExplorationResults:
    results = ExplorationResults()
    unvisited: deque[Coordinate] = deque((start,))
    while len(unvisited) > 0:
        current_location = unvisited.popleft()
        character = hc.lookup_in(current_location, map.grid)
        if character == map_wall:
            continue
        elif character == map_path:
            if at_path_start(map, current_location):
                results.ends.add(current_location)
            if at_path_end(map, current_location):
                results.terminals.add(current_location)
                continue
            else:
                results.internals.add(current_location)
                for direction in hd.DIRECTIONS:
                    next_coord = hd.travel(direction).starting_at(current_location)
                    if next_coord in results.internals:
                        continue
                    if next_coord not in map.limits:
                        continue
                    unvisited.append(next_coord)
                    continue
        elif character in map_slope_directions:
            results.ends.add(current_location)
            for direction in hd.DIRECTIONS:
                next_coord = hd.travel(direction).starting_at(current_location)
                if next_coord in results.internals:
                    continue
                if next_coord not in map.limits:
                    continue
                character = hc.lookup_in(next_coord, map.grid)
                if character == map_wall:
                    continue
                assert character == map_path
                results.new_locations.add(next_coord)
            continue
        else:
            raise Exception(f'Unexpected map character encountered: {character}')
    return results


def at_path_start(map: Map, location: Coordinate) -> bool:
    return location.line == 0

def at_path_end(map: Map, location: Coordinate) -> bool:
    return location.line == map.limits.max_line - 1


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    map = Map(tuple(lines))
    start = Coordinate(line=0, character=1)
    assert hc.lookup_in(start, map.grid) == map_path

    ends = sum(1 for char in lines[-1] if char == map_path)
    assert ends == 1

    visited: set[Coordinate] = set()
    unvisited: deque[Coordinate] = deque((start,))
    while len(unvisited) > 0:
        next_start = unvisited.popleft()
        if next_start in visited:
            continue
        results = explore(map, next_start)
        assert (len(results.ends) + len(results.terminals) == 2
                or len(results.internals) == 1)
        visited.update(results.ends)
        visited.update(results.terminals)
        visited.update(results.internals)
        unvisited.extend(results.new_locations)

    print('All assertions verified')
    print('Input consists only of paths (with 2 ends) and intersections (with only one step)')
    print('Input only has one exit')


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
