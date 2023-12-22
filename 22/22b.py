#!/usr/bin/env python3

from dataclasses import dataclass
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from functools import cached_property
import heapq
import logging
import operator
import pathlib
import sys
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

from lib.class_coordinate import Coordinate
from lib.class_coordinate_3d import Coordinate3D
import lib.helper_args as ha
import lib.helper_file as hf
import lib.helper_log as hl

logger = logging.getLogger(__file.stem)


@dataclass(frozen=True, order=True)
class Brick:
    ends: tuple[Coordinate3D]
    id: str = '?'

    def __post_init__(self):
        assert len(self.ends) == 2

    @cached_property
    def min_z(self) -> int:
        return min(coord.z for coord in self.ends)

    @cached_property
    def height(self) -> int:
        return max(coord.z for coord in self.ends) - self.min_z + 1

    @cached_property
    def xy_plane_projection(self) -> set[Coordinate]:
        end_1, end_2 = [end.xy_plane_projection for end in self.ends]
        return determine_area(end_1, end_2)

    def translate(self, translation: Coordinate3D) -> 'Brick':
        new_ends = tuple(coord + translation for coord in self.ends)
        return Brick(new_ends, self.id)


def determine_area(a: Coordinate, b: Coordinate) -> set[Coordinate]:
    min_x = min(a.x, b.x)
    max_x = max(a.x, b.x)
    min_y = min(a.y, b.y)
    max_y = max(a.y, b.y)
    assert (min_x == max_x) or (min_y == max_y)
    area: set[Coordinate] = set()
    for i in range(min_x, max_x + 1):
        for j in range (min_y, max_y + 1):
            area.add(Coordinate(i, j))
    return area


def settle(bricks: Iterable[Brick]) -> tuple[set[Brick], dict[Brick, set[Brick]]]:
    settled: set[Brick] = set()
    parents: dict[Brick, set[Brick]] = {}
    max_z: dict[Coordinate, int] = defaultdict(lambda: 1)
    max_z_owners: dict[Coordinate, Brick] = {}
    bricks = sorted(bricks, key=operator.attrgetter('min_z'))
    for brick in bricks:
        brick_parents: set[Brick] = set()
        if brick.min_z == 1:
            min_z = 1
            settled_brick = brick
        else:
            min_z = 1
            for cube in brick.xy_plane_projection:
                to_check = max_z[cube]
                if to_check > min_z:
                    min_z = to_check
                    brick_parents.clear()
                if to_check == min_z and cube in max_z_owners:
                    brick_parents.add(max_z_owners[cube])
            offset_z = brick.min_z - min_z
            settled_brick = brick.translate(Coordinate3D(0, 0, -offset_z))
        settled.add(settled_brick)
        parents[settled_brick] = brick_parents
        for cube in brick.xy_plane_projection:
            max_z[cube] = min_z + brick.height
            max_z_owners[cube] = settled_brick
    return (settled, parents)


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    bricks: list[Brick] = []
    for line_index, line in enumerate(lines):
        coord_labels = line.split('~')
        assert len(coord_labels) == 2
        coords: list[tuple[int]] = []
        for coord_label in coord_labels:
            x, y, z = coord_label.split(',')
            coords.append(Coordinate3D(int(x), int(y), int(z)))
        bricks.append(Brick(tuple(coords), str(line_index + 1)))

    settled, parents = settle(bricks)

    children: dict[Brick, set[Brick]] = defaultdict(set)
    for brick, brick_parents in parents.items():
        for parent in brick_parents:
            children[parent].add(brick)

    total = 0
    for brick in settled:
        # a brick falls if all its parents have moved
        removed = set([brick])
        checked = set([brick])
        remaining_children_to_process: list[tuple[int, Brick]] = []
        for child in children[brick]:
            heapq.heappush(remaining_children_to_process, (child.min_z, child))
        while len(remaining_children_to_process) > 0:
            _, current_child = heapq.heappop(remaining_children_to_process)
            if current_child in checked:
                continue
            checked.add(current_child)
            # falls cascade: if any children's parents have _all_ moved, they also move
            unremoved_parents = parents[current_child].difference(removed)
            if len(unremoved_parents) < 1:
                # no unmoved parents: this brick also moves
                removed.add(current_child)
                for child in children[current_child]:
                    heapq.heappush(remaining_children_to_process, (child.min_z, child))
        subtotal = len(removed) - 1
        logger.debug('Adding %d to subtotal from brick: %r', subtotal, brick)
        total += subtotal

    print(total)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
