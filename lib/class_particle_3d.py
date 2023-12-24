from dataclasses import dataclass
from functools import cached_property

from lib.class_coordinate_3d import Coordinate3D
from lib.class_particle import Particle


@dataclass(frozen=True, order=True)
class Particle3D:
    position: Coordinate3D
    velocity: Coordinate3D
    label: str = ''

    @cached_property
    def xy_plane_projection(self) -> Particle:
        return Particle(self.position.xy_plane_projection, self.velocity.xy_plane_projection, self.label)
