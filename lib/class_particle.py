from dataclasses import dataclass
from functools import cached_property

from lib.class_coordinate import Coordinate


@dataclass(frozen=True, order=True)
class Particle:
    position: Coordinate
    velocity: Coordinate
    label: str = ''
