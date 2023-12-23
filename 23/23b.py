#!/usr/bin/env python3

from abc import ABC, abstractmethod
from dataclasses import dataclass
from collections import defaultdict, deque
from collections.abc import Iterable
from dataclasses import dataclass
from functools import cache
import logging
import pathlib
import sys
from typing import TypeVar
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

from lib.class_edge_weighted import WeightedEdge
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
T = TypeVar('T')


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
        # path start / end are special cases,
        # as they can only be reached from 1 other segment
        if at_path_start(map, current_location):
            ends.add(current_location)
            interior_locations.add(current_location)
        if at_path_end(map, current_location):
            ends.add(current_location)
            interior_locations.add(current_location)
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


def get_other(input: Iterable[T], to_exclude: T) -> T:
    for thing in input:
        if thing != to_exclude:
            return thing


def longest_path(
        edges: Iterable[WeightedEdge],
        graph_start: Coordinate,
        graph_end: Coordinate) -> int:
    '''
    Based on code from StackOverflow answer:
    https://stackoverflow.com/a/29321323
    question author: https://stackoverflow.com/users/3685422/learningninja
    answer author: https://stackoverflow.com/users/736937/jedwards
    '''
    graph: dict[Coordinate, set[WeightedEdge]] = defaultdict(set)
    for edge in edges:
        graph[edge.start].add(edge)
        graph[edge.end].add(edge)

    logger.debug('Starting depth-first search for paths from %r to %r', graph_start, graph_end)
    all_paths = depth_first_search(graph, graph_start, graph_end)

    longest = 0
    for _, weight in all_paths:
        if weight > longest:
            longest = weight
    return longest


def depth_first_search(
        graph: dict[Coordinate, set[WeightedEdge]],
        start: Coordinate,
        target: Coordinate,
        seen: set[Coordinate] = None,
        path: tuple[Coordinate, ...] = None,
        weight: int = 0
        ) -> list[tuple[tuple[Coordinate, ...], int]]:
    '''
    Based on code from StackOverflow answer:
    https://stackoverflow.com/a/29321323
    question author: https://stackoverflow.com/users/3685422/learningninja
    answer author: https://stackoverflow.com/users/736937/jedwards
    '''
    if seen is None:
        seen = set()
    if path is None:
        path = (start,)
    seen.add(start)
    paths: list[tuple[tuple[Coordinate, ...], int]] = []
    for edge in graph[start]:
        destination = get_other((edge.start, edge.end), start)
        if destination in seen:
            continue
        subpath = path + (destination,)
        new_weight = weight + edge.weight
        if destination == target:
            paths.append((subpath, new_weight))
        else:
            paths.extend(depth_first_search(
                graph, destination, target, seen.copy(), subpath, new_weight))
    return paths


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    map = Map(tuple(lines))
    start = Coordinate(line=0, character=1)
    assert hc.lookup_in(start, map.grid) == map_path
    end_index = lines[-1].index(map_path)
    end = Coordinate(line=len(lines)-1, character=end_index)

    segments: set[MapSegment] = set()
    slopes: dict[Coordinate, set[MapSegment]] = defaultdict(set)
    interior_locations: set[Coordinate] = set()
    unexplored: deque[Coordinate] = deque((start,))
    while len(unexplored) > 0:
        next_start = unexplored.popleft()
        if next_start in interior_locations:
            continue
        next_map_segment, new_locations = walk_subpath(map, next_start)
        segments.add(next_map_segment)
        for location in next_map_segment.get_ends():
            slopes[location].add(next_map_segment)
        interior_locations.update(next_map_segment.get_interior_locations())
        unexplored.extend(new_locations)

    start_segment = None
    graph_start = None
    end_segment = None
    graph_end = None
    nodes = []
    edges = []
    for segment in segments:
        if start in segment.get_interior_locations():
            start_segment = segment
            other_end = get_other(segment.get_ends(), start)
            next_segment = get_other(slopes[other_end], start_segment)
            assert isinstance(next_segment, Intersection)
            graph_start = next_segment.location
            continue
        elif end in segment.get_interior_locations():
            end_segment = segment
            other_end = get_other(segment.get_ends(), end)
            previous_segment = get_other(slopes[other_end], end_segment)
            assert isinstance(previous_segment, Intersection)
            graph_end = previous_segment.location
            continue
        elif isinstance(segment, Intersection):
            nodes.append(segment.location)
        elif isinstance(segment, Path):
            connected_nodes = []
            for segment_end in segment.ends:
                connected_segment = get_other(
                    slopes[segment_end], segment)
                assert isinstance(connected_segment, Intersection)
                connected_nodes.append(connected_segment.location)
            edges.append(WeightedEdge(
                segment.length + 3, *sorted(connected_nodes)))
        else:
            raise Exception('Unexpected segment encountered')

    longest_path_length = longest_path(edges, graph_start, graph_end)
    longest_path_length += len(start_segment) + 3 + len(end_segment)

    print(longest_path_length)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
