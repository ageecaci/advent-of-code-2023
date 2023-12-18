from enum import Enum
from functools import cached_property

from lib.class_text_coordinate import TextCoordinate

_up = 'up'
_down = 'down'
_left = 'left'
_right = 'right'
directions = [_up, _down, _left, _right]
visual_directions = {
    _up: '^',
    _down: 'v',
    _left: '<',
    _right: '>',
}
_horizontal = 'horizontal'
_vertical = 'vertical'

class Axis(Enum):
    HORIZONTAL = _horizontal
    VERTICAL = _vertical

class Direction(Enum):
    UP = _up
    DOWN = _down
    LEFT = _left
    RIGHT = _right

    def visualise(self):
        return visual_directions[self.value]

    @cached_property
    def axis(self):
        if self.value == _up or self.value == _down:
            return Axis.VERTICAL
        if self.value == _left or self.value == _right:
            return Axis.HORIZONTAL

    def starting_at(self, coord: TextCoordinate, distance: int = 1) -> TextCoordinate:
        if self.value == _up:
            return coord.up(distance)
        if self.value == _down:
            return coord.down(distance)
        if self.value == _left:
            return coord.left(distance)
        if self.value == _right:
            return coord.right(distance)

    @classmethod
    def from_initial(cls, direction: str) -> 'Direction':
        assert len(direction) == 1
        if direction in 'uU':
            return cls.UP
        if direction in 'dD':
            return cls.DOWN
        if direction in 'lL':
            return cls.LEFT
        if direction in 'rR':
            return cls.RIGHT
        raise Exception(f'Unexpected direction initial "{direction}"')


def travel(direction: Direction) -> Direction:
    return direction

UP = Direction.UP
DOWN = Direction.DOWN
LEFT = Direction.LEFT
RIGHT = Direction.RIGHT
DIRECTIONS = [UP, DOWN, LEFT, RIGHT]
