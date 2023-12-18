#!/usr/bin/env python3

from dataclasses import dataclass
import logging
import pathlib
import sys
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

from lib.class_text_coordinate import TextCoordinate as Coordinate
import lib.helper_args as ha
import lib.helper_direction as hd
import lib.helper_file as hf
import lib.helper_log as hl

logger = logging.getLogger(__file.stem)

character_dug = '#'
character_undug = '.'
corner_top_left = 'F'
corner_top_right = '7'
corner_bottom_left = 'L'
corner_bottom_right = 'J'
corners_with_stems_down = 'F7'
corners_with_stems_up = 'LJ'
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
        self.discrete_edges: set[Coordinate] = set((origin,))

        self.limits: MutableLimits = MutableLimits()

        self._filled = False
        self.diggings: list[str] = []
        self.edged: list[str] = []
        self._size = 0

    @property
    def last_visited(self) -> Coordinate:
        return self.vertices[-1]

    def reset_diggings(self):
        self._filled = False
        self.diggings = []
        self.edged = []
        self._size = 0

    def travel(self, direction: hd.Direction, multiplicity: int):
        self.reset_diggings()
        previous_location = self.last_visited
        next_location = previous_location
        for _ in range(multiplicity):
            next_location = hd.travel(direction).starting_at(next_location)
            self.discrete_edges.add(next_location)
        logger.log(hl.EXTRA_NOISY, 'travelled %s %d times from %r to %r',
                   direction, multiplicity, previous_location, next_location)
        self.vertices.append(next_location)
        self.limits.include(next_location)

    def fill(self):
        if self._filled:
            return
        diggings = []
        edged = []
        for line in range(self.limits.min_line, self.limits.max_line + 1):
            diggings_line = []
            edged_line = []
            inside = False
            last_corner = None
            for character in range(self.limits.min_character, self.limits.max_character + 1):
                location = Coordinate(line, character)
                if location in self.discrete_edges:
                    # all edges have already been dug
                    diggings_line.append(character_dug)
                    edged_line.append(character_dug)
                    self._size += 1
                    above_is_edge = location.up() in self.discrete_edges
                    below_is_edge = location.down() in self.discrete_edges
                    if above_is_edge and below_is_edge:
                        # verify the shape does not have any T junctions
                        # we would need to do loop detection if so
                        left_is_edge = location.left() in self.discrete_edges
                        right_is_edge = location.right() in self.discrete_edges
                        assert not left_is_edge
                        assert not right_is_edge
                        # vertical edge must be a crossing
                        inside = not inside
                    # corners are only crossings if the pair has one stem leading up and one leading down
                    elif above_is_edge and not below_is_edge:
                        if last_corner is None:
                            last_corner = corner_bottom_left
                        else:
                            if last_corner in corners_with_stems_down:
                                inside = not inside
                            last_corner = None
                    elif not above_is_edge and below_is_edge:
                        if last_corner is None:
                            last_corner = corner_top_left
                        else:
                            if last_corner in corners_with_stems_up:
                                inside = not inside
                            last_corner = None
                else:
                    edged_line.append(character_undug)
                    if inside:
                        diggings_line.append(character_dug)
                        self._size += 1
                    else:
                        diggings_line.append(character_undug)
            diggings.append(''.join(diggings_line))
            edged.append(''.join(edged_line))
        self.diggings = diggings
        self.edged = edged
        self._filled = True

    @property
    def size(self) -> int:
        if not self._filled:
            self.fill()
        return self._size

    def visualise_edges(self) -> str:
        if not self._filled:
            self.fill()
        return '\n'.join(self.edged)

    def visualise_digging(self) -> str:
        if not self._filled:
            self.fill()
        return '\n'.join(self.painted)


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    pit = Pit()
    previous_direction = None
    for line in lines:
        abbreviated_direction, multiplicity_label, _ = line.split()
        direction = hd.Direction.from_initial(abbreviated_direction)
        assert direction != previous_direction
        multiplicity = int(multiplicity_label)
        pit.travel(direction, multiplicity)
        previous_direction = direction

    pit.fill()
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug('Pit state after edging:\n%s', pit.visualise_edges())
        logger.debug('Pit state after digging:\n%s', pit.visualise_digging())

    print(pit.size)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
