from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Coordinate:
    x: int
    y: int
