#!/usr/bin/env python3

import bisect
from dataclasses import dataclass
import itertools
import logging
import pathlib
import sys
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

from lib.class_edge import Edge
from lib.class_text_coordinate import TextCoordinate as Coordinate
import lib.helper_args as ha
import lib.helper_direction as hd
import lib.helper_file as hf
import lib.helper_log as hl

logger = logging.getLogger(__file.stem)

origin = Coordinate(0, 0)


@dataclass
class MutableLimits:
    min_line: int = 0
    max_line: int = 0
    min_character: int = 0
    max_character: int = 0

    @property
    def depth(self):
        return self.limits.max_line - self.limits.min_line + 1

    @property
    def width(self):
        return self.limits.max_character - self.limits.min_character + 1

    def include(self, coord: Coordinate):
        if coord.line < self.min_line:
            self.min_line = coord.line
        elif coord.line > self.max_line:
            self.max_line = coord.line
        if coord.character < self.min_character:
            self.min_character = coord.character
        elif coord.character > self.max_character:
            self.max_character = coord.character


class Pit:
    def __init__(self):
        self.vertices: list[Coordinate] = [origin]
        self.edges: list[Edge] = []
        self.lines_with_edges: set[int] = set()
        self.columns_with_edges: set[int] = set()

        self.limits: MutableLimits = MutableLimits()

        self._filled = False
        self._size = 0

    @property
    def last_visited(self) -> Coordinate:
        return self.vertices[-1]

    def reset_diggings(self):
        self._filled = False
        self._size = 0

    def travel(self, direction: hd.Direction, distance: int):
        if self._filled:
            self.reset_diggings()
        previous_location = self.last_visited
        next_location = hd.travel(direction).starting_at(previous_location, distance)
        logger.log(hl.EXTRA_NOISY, 'travelled %s from %r to %r',
                   direction, previous_location, next_location)
        self.vertices.append(next_location)
        edge = Edge(previous_location, next_location)
        self.edges.append(edge)
        if direction.axis == hd.Axis.HORIZONTAL:
            self.lines_with_edges.add(edge.start.line)
        elif direction.axis == hd.Axis.VERTICAL:
            self.columns_with_edges.add(edge.start.character)
        self.limits.include(next_location)

    def fill(self):
        if self._filled:
            return
        ordered_columns_with_edges = sorted(self.columns_with_edges)
        ordered_lines_with_edges = sorted(self.lines_with_edges)

        # initialise data structures
        # for each segmented column (start character -> end character) track line indices
        # for each segmented row (start line -> end line) track character indices
        # for each resulting "block" (column limits combined with row limits) track whether block is interior
        _segmented_columns: dict[tuple[int], list[int]] = {}
        _segmented_rows: dict[tuple[int], list[int]] = {}
        _blocks: dict[tuple[int], dict[tuple[int], bool]] = {}
        for index in range(len(ordered_columns_with_edges) - 1):
            column_limits = (ordered_columns_with_edges[index], ordered_columns_with_edges[index+1])
            _segmented_columns[column_limits] = []
            _blocks[column_limits] = {}
        for index in range(len(ordered_lines_with_edges) - 1):
            row_limits = (ordered_lines_with_edges[index], ordered_lines_with_edges[index+1])
            _segmented_rows[row_limits] = []
        if logger.isEnabledFor(hl.EXTRA_DETAIL):
            logger.log(hl.EXTRA_DETAIL, 'Segmented columns: %r', list(_segmented_columns.keys()))
            logger.log(hl.EXTRA_DETAIL, 'Segmented rows: %r', list(_segmented_rows.keys()))

        # split each line into segments and group
        for edge in self.edges:
            if edge.horizontal:
                segments = split_horizontal_at(edge, ordered_columns_with_edges)
                for segment in segments:
                    limits = (segment.start.character, segment.end.character)
                    _segmented_columns[limits].append(segment.start.line)
            elif edge.vertical:
                segments = split_vertical_at(edge, ordered_lines_with_edges)
                for segment in segments:
                    limits = (segment.start.line, segment.end.line)
                    _segmented_rows[limits].append(segment.start.character)
            else:
                raise Exception('Invalid edge discovered')

        # determine whether each "block" (in cross-section of segment by segment) is interior or not
        size = 0
        for column_limits, lines_with_boundaries in _segmented_columns.items():
            logger.log(hl.EXTRA_NOISY, 'Scanning column: %r', column_limits)
            lines_with_boundaries.sort()
            for row_limits, columns_with_boundaries in _segmented_rows.items():
                logger.log(hl.EXTRA_NOISY, 'Scanning row: %r', row_limits)
                columns_with_boundaries.sort()
                edges_above = bisect.bisect(lines_with_boundaries, midpoint(row_limits))
                column_is_interior = edges_above % 2 == 1
                edges_to_left = bisect.bisect(columns_with_boundaries, midpoint(column_limits))
                row_is_interior = edges_to_left % 2 == 1
                if column_is_interior and row_is_interior:
                    # do not count edges here: interior block count only
                    block_width = length(column_limits) - 1
                    block_height = length(row_limits) - 1
                    block_size = block_width * block_height
                    logger.log(hl.EXTRA_DETAIL, 'Including block of size: %d (%r, %r)', block_size, column_limits, row_limits)
                    size += block_size
                    _blocks[column_limits][row_limits] = True
                else:
                    logger.log(hl.EXTRA_NOISY, 'Discounting block (%r, %r)', column_limits, row_limits)
                    _blocks[column_limits][row_limits] = False
        logger.debug('Size includes subtotal from block interiors: %d', size)

        logger.log(hl.EXTRA_NOISY, 'block inclusion results: %r', _blocks)

        # add the edge lengths: we excluded edges above, so include outer edges _and_ inner edges
        # do not include vertices, else we double-count some interior vertices
        edge_subtotal = 0
        # columns first
        for column_limits in _segmented_columns:
            count = 0
            previously_interior = False
            for row_limits in _segmented_rows:
                block_is_interior = _blocks[column_limits][row_limits]
                if block_is_interior:
                    count += 1
                    if not previously_interior:
                        count += 1
                previously_interior = block_is_interior
            column_subtotal = count * (length(column_limits) - 1)
            logger.log(hl.EXTRA_DETAIL, 'Including %d in edge count: %d edge segments for column %r', column_subtotal, count, column_limits)
            edge_subtotal += column_subtotal
        # now rows
        for row_limits in _segmented_rows:
            count = 0
            previously_interior = False
            for column_limits in _segmented_columns:
                block_is_interior = _blocks[column_limits][row_limits]
                if block_is_interior:
                    count += 1
                    if not previously_interior:
                        count += 1
                previously_interior = block_is_interior
            row_subtotal = count * (length(row_limits) - 1)
            logger.log(hl.EXTRA_DETAIL, 'Including %d in edge count: %d edge segments for row %r', row_subtotal, count, row_limits)
            edge_subtotal += row_subtotal
        logger.debug('Size includes subtotal from edges: %d', edge_subtotal)
        size += edge_subtotal

        # add the vertex count:
        vertex_count = 0
        buffered_columns = [None] + list(_segmented_columns.keys()) + [None]
        buffered_rows = [None] + list(_segmented_rows.keys()) + [None]
        adjacent_column_pairs = list(itertools.pairwise(buffered_columns))
        adjacent_row_pairs = list(itertools.pairwise(buffered_rows))
        if logger.isEnabledFor(hl.EXTRA_NOISY):
            logger.log(hl.EXTRA_NOISY, 'adjacent column pairs: %r', adjacent_column_pairs)
            logger.log(hl.EXTRA_NOISY, 'adjacent row pairs: %r', adjacent_row_pairs)
        for column_pair in adjacent_column_pairs:
            for row_pair in adjacent_row_pairs:
                top_left_is_interior = column_pair[0] is not None and row_pair[0] is not None and _blocks[column_pair[0]][row_pair[0]]
                top_right_is_interior = column_pair[1] is not None and row_pair[0] is not None and _blocks[column_pair[1]][row_pair[0]]
                bottom_left_is_interior = column_pair[0] is not None and row_pair[1] is not None and _blocks[column_pair[0]][row_pair[1]]
                bottom_right_is_interior = column_pair[1] is not None and row_pair[1] is not None and _blocks[column_pair[1]][row_pair[1]]
                vertex_is_interior = any((top_left_is_interior, top_right_is_interior,
                                         bottom_left_is_interior, bottom_right_is_interior))
                if vertex_is_interior:
                    vertex_count += 1
        logger.debug('Size includes vertex count: %d', vertex_count)
        size += vertex_count

        self._size = size
        self._filled = True

    @property
    def size(self) -> int:
        if not self._filled:
            return -1
        return self._size


def split_horizontal_at(edge: Edge, character_indices_with_edges: list[int]) -> list[Edge]:
    assert edge.horizontal
    line_index = edge.start.line
    edges = []
    remainder = edge
    for boundary in character_indices_with_edges:
        point_to_check = Coordinate(line_index, boundary)
        if remainder.crosses_point(point_to_check):
            split = Edge(remainder.start, point_to_check)
            remainder = Edge(point_to_check, remainder.end)
            if not split.is_point:
                edges.append(split)
    if not remainder.is_point:
        edges.append(remainder)
    return edges


def split_vertical_at(edge: Edge, line_indices_with_edges: list[int]) -> list[Edge]:
    assert edge.vertical
    character_index = edge.start.character
    edges = []
    remainder = edge
    for boundary in line_indices_with_edges:
        point_to_check = Coordinate(boundary, character_index)
        if remainder.crosses_point(point_to_check):
            split = Edge(remainder.start, point_to_check)
            remainder = Edge(point_to_check, remainder.end)
            if not split.is_point:
                edges.append(split)
    if not remainder.is_point:
        edges.append(remainder)
    return edges


def midpoint(limits: tuple[int]) -> float:
    difference = limits[1] - limits[0]
    return limits[0] + difference/2


def length(limits: tuple[int]) -> int:
    return limits[1] - limits[0]


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    directions = 'RDLU'
    pit = Pit()
    previous_direction = None
    for line in lines:
        _, _, colour_label = line.split()
        direction_index = int(colour_label[7])
        direction = hd.Direction.from_initial(directions[direction_index])
        assert direction != previous_direction
        distance_hex_label = colour_label[2:7]
        distance = int(distance_hex_label, 16)
        logger.log(hl.EXTRA_NOISY, 'Converted color %s to %s %d', colour_label, direction, distance)
        pit.travel(direction, distance)
        previous_direction = direction

    pit.fill()
    print(pit.size)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
