from dataclasses import dataclass


@dataclass
class TextCoordinate:
    line: int
    character: int
