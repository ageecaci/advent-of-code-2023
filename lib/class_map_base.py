from dataclasses import dataclass
from functools import cached_property

from lib.class_text_coordinate_limits import TextCoordinateLimits as Limits


@dataclass(frozen=True)
class Map:
    grid: tuple[str]

    @cached_property
    def limits(self) -> Limits:
        return Limits(len(self.grid), len(self.grid[0]))
