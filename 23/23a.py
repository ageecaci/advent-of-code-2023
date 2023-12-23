#!/usr/bin/env python3

from dataclasses import dataclass
from collections import deque
from dataclasses import dataclass, field
from functools import cache
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
class JourneyStep:
    location: Coordinate
    already_visited: set[Coordinate]

    def __lt__(self, other) -> bool:
        if not isinstance(other, JourneyStep):
            return NotImplemented
        return self.location < other.location

    def __len__(self) -> int:
        return len(self.already_visited)

    def continue_with(self, other) -> 'JourneyStep':
        if not isinstance(other, JourneyStep):
            return NotImplemented
        return JourneyStep(other.location, self.already_visited.union(other.already_visited))


@dataclass
class WalkResults:
    ends: list[JourneyStep] = field(default_factory=list)
    terminals: list[JourneyStep] = field(default_factory=list)

    def add_end(self, end: JourneyStep):
        self.ends.append(end)

    def add_terminus(self, end: JourneyStep):
        self.terminals.append(end)


@cache
def walk_subpath(map: Map, start: Coordinate) -> WalkResults:
    results = WalkResults()
    new_starting_subsegment = JourneyStep(start, set())
    possible_next_steps: deque[JourneyStep] = deque((new_starting_subsegment,))
    while len(possible_next_steps) > 0:
        current_step = possible_next_steps.popleft()
        character = hc.lookup_in(current_step.location, map.grid)
        if character == map_wall:
            continue
        else:
            if character == map_path:
                if at_path_end(map, current_step.location):
                    # will not include the end in the history,
                    # but this is fine as the length will include the start instead
                    results.add_terminus(current_step)
                    continue
                else:
                    new_visited = current_step.already_visited.union((current_step.location,))
                    for direction in hd.DIRECTIONS:
                        next_coord = hd.travel(direction).starting_at(current_step.location)
                        if next_coord in current_step.already_visited:
                            continue
                        if next_coord not in map.limits:
                            continue
                        possible_next_steps.append(JourneyStep(next_coord, new_visited))
                        continue
            elif character in map_slope_directions:
                slope_direction = map_slope_directions[character]
                subsequent_coord = hd.travel(slope_direction).starting_at(current_step.location)
                if subsequent_coord in current_step.already_visited:
                    continue
                if subsequent_coord not in map.limits:
                    continue
                assert hc.lookup_in(subsequent_coord, map.grid) == map_path
                # reached an end to that section
                new_visited = current_step.already_visited.union((current_step.location,))
                if at_path_end(map, subsequent_coord):
                    results.add_terminus(JourneyStep(subsequent_coord, new_visited))
                else:
                    results.add_end(JourneyStep(subsequent_coord, new_visited))
                continue
            else:
                raise Exception(f'Unexpected map character encountered: {character}')
    return results


def at_path_end(map: Map, location: Coordinate) -> bool:
    return location.line == map.limits.max_line - 1


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    map = Map(tuple(lines))
    start = Coordinate(line=0, character=1)
    assert hc.lookup_in(start, map.grid) == map_path

    paths: list[JourneyStep] = []
    subpaths: deque[JourneyStep] = deque((JourneyStep(start, set()),))
    while len(subpaths) > 0:
        subpath = subpaths.popleft()
        sub_walks = walk_subpath(map, subpath.location)
        for terminal in sub_walks.terminals:
            path = subpath.continue_with(terminal)
            paths.append(path)
        for sub_walk in sub_walks.ends:
            path = subpath.continue_with(sub_walk)
            subpaths.append(path)

    paths.sort(key=len, reverse=True)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug('%d paths found with respective lengths: %r', len(paths),
                     [len(path) for path in paths])
    longest_path = paths[0]

    print(len(longest_path))


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
