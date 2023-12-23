#!/usr/bin/env python3

from abc import ABC, abstractmethod
from dataclasses import dataclass
from collections import defaultdict, deque
from dataclasses import dataclass
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


@dataclass(frozen=True)
class Journey:
    end: Coordinate
    length: int
    already_visited: set[Coordinate]

    def __len__(self) -> int:
        return self.length


class MapSegment(ABC):
    @abstractmethod
    def get_ends(self) -> set[Coordinate]:
        return set()

    @abstractmethod
    def get_interior_locations(self) -> set[Coordinate]:
        return set()


@dataclass(frozen=True)
class Path(MapSegment):
    ends: tuple[Coordinate]
    interior_locations: tuple[Coordinate]
    length: int

    def __post_init__(self):
        assert len(self.ends) == 2

    def __len__(self) -> int:
        return self.length

    def get_ends(self) -> set[Coordinate]:
        return set(self.ends)

    def get_interior_locations(self) -> set[Coordinate]:
        return set(self.interior_locations)


@dataclass(frozen=True)
class Intersection(MapSegment):
    location: Coordinate
    ends: tuple[Coordinate]

    def __post_init__(self):
        assert len(self.ends) > 2

    def __len__(self) -> int:
        # two slopes / junctions and an interior
        return 3

    def get_ends(self) -> set[Coordinate]:
        return set(self.ends)

    def get_interior_locations(self) -> set[Coordinate]:
        return set((self.location,))


@cache
def walk_subpath(map: Map, start: Coordinate) -> tuple[MapSegment, set[Coordinate]]:
    ends: set[Coordinate] = set()
    interior_locations: set[Coordinate] = set()
    new_locations: set[Coordinate] = set()
    visited: set[Coordinate] = set()
    current_location = start
    while True:
        if at_path_start(map, current_location):
            ends.add(current_location)
            interior_locations.add(current_location)
            # path start is a special case, but can only be reached via 1 internal path
        if at_path_end(map, current_location):
            ends.add(current_location)
            break
        visited.add(current_location)
        possible_next_steps: set[Coordinate] = set()
        for direction in hd.DIRECTIONS:
            next_coord = hd.travel(direction).starting_at(current_location)
            if next_coord in visited:
                continue
            if next_coord not in map.limits:
                continue
            character = hc.lookup_in(next_coord, map.grid)
            if character == map_wall:
                continue
            elif character == map_path:
                possible_next_steps.add(next_coord)
            elif character in map_slope_directions:
                ends.add(next_coord)
                interior_locations.add(current_location)
                # if we keep going in the same direction we should reach a new map segment
                new_location = hd.travel(direction).starting_at(next_coord)
                assert hc.lookup_in(new_location, map.grid) == map_path
                new_locations.add(hd.travel(direction).starting_at(next_coord))
            else:
                raise Exception(f'Unexpected map character encountered: {character}')

        if len(possible_next_steps) == 0:
            break
        assert len(possible_next_steps) == 1
        # we expect to be on an internal path: so there should be no other ends yet
        assert len(ends) < 2
        # continue along the path
        current_location = list(possible_next_steps)[0]
    if len(ends) == 2:
        # was a path
        segment = Path(tuple(sorted(ends)), tuple(sorted(interior_locations)), len(visited))
    elif len(ends) > 2:
        # was an intersection
        assert len(visited) == 1
        assert len(interior_locations.difference(visited)) == 0
        interior_location = list(interior_locations)[0]
        segment = Intersection(interior_location, tuple(sorted(ends)))
    else:
        logger.error('discovered ends: %r', ends)
        logger.error('discovered interior locations: %r', interior_locations)
        logger.error('discovered new locations: %r', new_locations)
        logger.error('visited (%d) locations: %r', len(visited), visited)
        raise Exception('Unexpected state achieved walking subpath')
    return (segment, new_locations)


def at_path_start(map: Map, location: Coordinate) -> bool:
    return location.line == 0


def at_path_end(map: Map, location: Coordinate) -> bool:
    return location.line == map.limits.max_line - 1


def continue_with(journey: Journey, segment: MapSegment, end: Coordinate) -> Journey:
    return Journey(end, journey.length + len(segment),
                   journey.already_visited.union(segment.get_ends()))


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    map = Map(tuple(lines))
    start = Coordinate(line=0, character=1)
    assert hc.lookup_in(start, map.grid) == map_path

    junctions: dict[Coordinate, set[MapSegment]] = defaultdict(set)
    interior_locations: dict[Coordinate, MapSegment] = {}
    unexplored: deque[Coordinate] = deque((start,))
    while len(unexplored) > 0:
        next_start = unexplored.popleft()
        if next_start in interior_locations:
            continue
        next_map_segment, new_locations = walk_subpath(map, next_start)
        unexplored.extend(new_locations)
        for location in next_map_segment.get_ends():
            junctions[location].add(next_map_segment)
        for location in next_map_segment.get_interior_locations():
            interior_locations[location] = next_map_segment

    longest_journey = Journey(start, 0, set())
    count = 0
    initial_segment = interior_locations[start]
    first_junction_location = list(initial_segment.get_ends().difference((start,)))[0]
    longest_journey = continue_with(longest_journey, initial_segment, first_junction_location)
    journeys: deque[tuple[Journey, MapSegment]] = deque()
    journeys.append((longest_journey, initial_segment))
    while len(journeys) > 0:
        journey, last_segment = journeys.popleft()
        junction_segments = junctions[journey.end]
        next_segment = list(junction_segments.difference((last_segment,)))[0]
        for end in next_segment.get_ends():
            if end in journey.already_visited:
                continue
            new_journey = continue_with(journey, next_segment, end)
            if at_path_end(map, end):
                count += 1
                if len(new_journey) > len(longest_journey):
                    longest_journey = new_journey
                continue
            journeys.append((new_journey, next_segment))

    logger.debug('%d journeys found', count),
    logger.debug('Longest journey was %d : %r', len(longest_journey), longest_journey)

    print(len(longest_journey))


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
