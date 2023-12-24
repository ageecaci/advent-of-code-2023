#!/usr/bin/env python3

import bisect
from dataclasses import dataclass
from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass
from functools import cache
import heapq
import itertools
import logging
import math
import operator
import pathlib
import random
import sys
from typing import Optional
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

from bidict import bidict
import numpy as np
import sympy as sp

from lib.class_coordinate import Coordinate
from lib.class_coordinate_3d import Coordinate3D
from lib.class_edge import Edge
from lib.class_limits import Limits
from lib.class_particle import Particle
from lib.class_particle_3d import Particle3D
import lib.helper_args as ha
import lib.helper_coord as hc
import lib.helper_direction as hd
import lib.helper_file as hf
import lib.helper_log as hl

logger = logging.getLogger(__file.stem)


def parse(props) -> set[Particle3D]:
    lines = hf.load_lines(hf.find_input_file(props))

    particles: set[Particle3D] = set()
    for line_index, line in enumerate(lines):
        position_label, velocity_label = line.split(' @ ')
        x_label, y_label, z_label = position_label.split(', ')
        vx_label, vy_label, vz_label = velocity_label.split(', ')
        position = Coordinate3D(int(x_label), int(y_label), int(z_label))
        velocity = Coordinate3D(int(vx_label), int(vy_label), int(vz_label))
        particles.add(Particle3D(position, velocity, str(line_index + 1)))
    return particles


def main(props):
    particles = parse(props)

    # More linear algebra: setup for SymPy solution
    symbols = sp.symbols('px py pz vx vy vz t0 t1 t2', real=True)
    px, py, pz, vx, vy, vz, t0, t1, t2 = symbols

    # Setup three sets of equalities for three crossings with random hailstones.
    # Notably, the times must be unique, but the coordinates at each crossing will be equal.
    # If there is a solution, it should naturally extend to all other hailstones.
    sample = random.sample(list(particles), 3)
    equations = [
        sp.Eq(px + vx * t0, sample[0].position.x + sample[0].velocity.x * t0),
        sp.Eq(py + vy * t0, sample[0].position.y + sample[0].velocity.y * t0),
        sp.Eq(pz + vz * t0, sample[0].position.z + sample[0].velocity.z * t0),

        sp.Eq(px + vx * t1, sample[1].position.x + sample[1].velocity.x * t1),
        sp.Eq(py + vy * t1, sample[1].position.y + sample[1].velocity.y * t1),
        sp.Eq(pz + vz * t1, sample[1].position.z + sample[1].velocity.z * t1),

        sp.Eq(px + vx * t2, sample[2].position.x + sample[2].velocity.x * t2),
        sp.Eq(py + vy * t2, sample[2].position.y + sample[2].velocity.y * t2),
        sp.Eq(pz + vz * t2, sample[2].position.z + sample[2].velocity.z * t2),
    ]
    solution = sp.solve(equations, symbols)
    # `solution` will be an array with a tuple of the symbol values.
    # Hence to sum the position coordinates, we sum the first three values.
    logger.debug('Lin alg solution: %r', solution)
    total = solution[0][0] + solution[0][1] + solution[0][2]

    print(total)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
