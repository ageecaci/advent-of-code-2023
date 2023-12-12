from dataclasses import dataclass


@dataclass(frozen=True)
class Coordinate:
    x: int
    y: int
