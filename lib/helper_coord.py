import argparse
from collections.abc import Iterable
import logging
import pathlib

from lib.class_text_coordinate_limits import TextCoordinateLimits as Limits
from lib.class_text_coordinate import TextCoordinate as Coordinate

logger = logging.getLogger(__name__)


def valid_neighbours(coord: Coordinate, limits: Limits) -> Iterable[Coordinate]:
    for neighbour in gen_neighbours(coord):
        if limits.contains(neighbour):
            yield neighbour


def gen_neighbours(coord: Coordinate) -> Iterable[Coordinate]:
    yield Coordinate(coord.line - 1, coord.character - 1)
    yield Coordinate(coord.line - 1, coord.character)
    yield Coordinate(coord.line - 1, coord.character + 1)
    yield Coordinate(coord.line, coord.character - 1)
    yield Coordinate(coord.line, coord.character + 1)
    yield Coordinate(coord.line + 1, coord.character - 1)
    yield Coordinate(coord.line + 1, coord.character)
    yield Coordinate(coord.line + 1, coord.character + 1)
