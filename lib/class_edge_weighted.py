from dataclasses import dataclass

from lib.class_text_coordinate import TextCoordinate as Coordinate


@dataclass(frozen=True, order=True)
class WeightedEdge:
    weight: int
    start: Coordinate
    end: Coordinate

    def __repr__(self):
        return f'WeightedEdge({self.start}, {self.end}: {self.weight})'
