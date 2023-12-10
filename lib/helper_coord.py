import argparse
from collections.abc import Iterable
import logging
import pathlib

from lib.class_text_coordinate_limits import TextCoordinateLimits as Limits
from lib.class_text_coordinate import TextCoordinate as Coordinate

logger = logging.getLogger(__name__)


def lookup_in(coord: Coordinate, grid: list[str]) -> str:
    return grid[coord.line][coord.character]


def valid_neighbours(
        coord: Coordinate,
        limits: Limits,
        diagonal: bool = True
        ) -> Iterable[Coordinate]:
    for neighbour in gen_neighbours(coord, diagonal=diagonal):
        if limits.contains(neighbour):
            yield neighbour


def gen_neighbours(coord: Coordinate, diagonal: bool = True) -> Iterable[Coordinate]:
    if diagonal:
        yield Coordinate(coord.line - 1, coord.character - 1)
    yield Coordinate(coord.line - 1, coord.character)
    if diagonal:
        yield Coordinate(coord.line - 1, coord.character + 1)
    yield Coordinate(coord.line, coord.character - 1)
    yield Coordinate(coord.line, coord.character + 1)
    if diagonal:
        yield Coordinate(coord.line + 1, coord.character - 1)
    yield Coordinate(coord.line + 1, coord.character)
    if diagonal:
        yield Coordinate(coord.line + 1, coord.character + 1)
