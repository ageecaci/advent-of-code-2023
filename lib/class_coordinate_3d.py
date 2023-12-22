from dataclasses import dataclass
from functools import cached_property

from lib.class_coordinate import Coordinate


@dataclass(frozen=True, order=True)
class Coordinate3D:
    x: int
    y: int
    z: int

    @cached_property
    def xy_plane_projection(self) -> Coordinate:
        return Coordinate(self.x, self.y)

    def __add__(self, other) -> 'Coordinate3D':
        if not isinstance(other, Coordinate3D):
            return NotImplemented
        return Coordinate3D(self.x + other.x, self.y + other.y, self.z + other.z)
