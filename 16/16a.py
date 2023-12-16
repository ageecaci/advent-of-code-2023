#!/usr/bin/env python3

from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass
from functools import cache
import logging
import pathlib
import sys
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

from lib.class_text_coordinate_limits import TextCoordinateLimits as Limits
from lib.class_text_coordinate import TextCoordinate as Coordinate
import lib.helper_args as ha
import lib.helper_coord as hc
import lib.helper_file as hf
import lib.helper_log as hl

logger = logging.getLogger(__file.stem)

up = 'up'
down = 'down'
left = 'left'
right = 'right'
directions = [up, down, left, right]

blank_character = '.'
splitter_vertical = '|'
splitter_horizontal = '-'
mirror_backslash = '\\'
mirror_forward_slash = '/'


@cache
def new_directions(character: str, direction_of_travel: str) -> Iterable[str]:
    if character == blank_character and direction_of_travel in directions:
        return [direction_of_travel]
    if character == splitter_vertical:
        if direction_of_travel == up or direction_of_travel == down:
            return [direction_of_travel]
        if direction_of_travel == left or direction_of_travel == right:
            return [up, down]
    if character == splitter_horizontal:
        if direction_of_travel == left or direction_of_travel == right:
            return [direction_of_travel]
        if direction_of_travel == up or direction_of_travel == down:
            return [left, right]
    if character == mirror_backslash: #\
        if direction_of_travel == up:
            return [left]
        if direction_of_travel == down:
            return [right]
        if direction_of_travel == left:
            return [up]
        if direction_of_travel == right:
            return [down]
    if character == mirror_forward_slash: #/
        if direction_of_travel == up:
            return [right]
        if direction_of_travel == down:
            return [left]
        if direction_of_travel == left:
            return [down]
        if direction_of_travel == right:
            return [up]
    raise Exception(f'Invalid character ({character}) or direction ({inbound_direction})')


@dataclass(frozen=True)
class Visit(Coordinate):
    direction: str

    def where_next(self) -> Coordinate:
        if self.direction == up:
            return self.up()
        if self.direction == down:
            return self.down()
        if self.direction == left:
            return self.left()
        if self.direction == right:
            return self.right()


class Contraption:
    def __init__(self, grid: list[str]):
        self.grid = grid
        self.limits = Limits(len(grid), len(grid[0]))
        self.visited: dict[Coordinate, set[str]] = {}
        self.walked = False

    def walk(self):
        to_visit: deque[Visit] = deque()
        to_visit.append(Visit(0, -1, right))
        while len(to_visit) > 0:
            current = to_visit.popleft()
            next = current.where_next()
            logger.log(hl.EXTRA_NOISY, 'Visiting %r from %r', next, current)
            if not self.limits.contains(next):
                continue
            next_directions = new_directions(hc.lookup_in(next, self.grid), current.direction)
            logger.log(hl.EXTRA_NOISY, 'New directions for %r travelling %s: %r', next, current.direction, next_directions)
            unvisited_next_directions = []
            if next not in self.visited:
                self.visited[next] = set()
                unvisited_next_directions = next_directions
            else:
                previous_directions = self.visited[next]
                for next_direction in next_directions:
                    if next_direction not in previous_directions:
                        unvisited_next_directions.append(next_direction)
            for next_direction in unvisited_next_directions:
                self.visited[next].add(next_direction)
                next_visit = Visit(next.line, next.character, next_direction)
                to_visit.append(next_visit)
        self.walked = True

    def count_empowered(self):
        if not self.walked:
            self.walk()
        return len(self.visited)

    def visualise(self):
        if not self.walked:
            self.walk()
        new_grid = [line for line in self.grid]
        for visit, directions in self.visited.items():
            existing_character = hc.lookup_in(visit, self.grid)
            if existing_character == blank_character:
                if len(directions) > 1:
                    new_character = str(len(directions))
                else:
                    for direction in directions:
                        if direction == up:
                            new_character = '^'
                        elif direction == down:
                            new_character = 'v'
                        elif direction == left:
                            new_character = '<'
                        elif direction == right:
                            new_character = '>'
                line = new_grid[visit.line]
                new_grid[visit.line] = (
                    line[:visit.character]
                    + new_character
                    + line[visit.character+1:])
        return '\n'.join(new_grid)


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))
    grid = [line.strip() for line in lines]
    contraption = Contraption(grid)
    subtotal = contraption.walk()
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug('View of light beams: \n%s', contraption.visualise())
    subtotal = contraption.count_empowered()
    print(subtotal)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
