#!/usr/bin/env python3

from dataclasses import dataclass
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from functools import cached_property
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

    subtotal = 0
    for brick in settled:
        child_bricks = children[brick]
        if len(child_bricks) < 1:
            # nothing rests on this brick, so safe to disintegrate
            subtotal += 1
        else:
            has_child_with_no_other_supports = False
            for child in child_bricks:
                if len(parents[child]) == 1:
                    # at least one brick is only resting on this brick
                    # so *not* safe to disintegrate
                    has_child_with_no_other_supports = True
                    break
            if not has_child_with_no_other_supports:
                # all bricks resting on this brick
                # are also resting on at least one other brick
                # so safe to disintegrate
                subtotal += 1

    print(subtotal)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
