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
import sys
from typing import Optional
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

from bidict import bidict
import numpy as np

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
    projected_particles = set(particle.xy_plane_projection for particle in particles)

    # Given input equations of `x = px + vx * t` and `y = py + vy * t`
    # For each pair of equations, need to discover if there are values `t1` and `t2`
    # for which `x1 == x2` and `y1 == y2`,
    # and if so, whether it lies in pre-defined bounds.
    # Rearrange equations:
    #   `x1 == x2 => px1 + vx1 * t1 == px2 + vx2 * t2`
    #            `=> vx1 * t1 - vx2 * t2 = px2 - px1`
    #   `y1 == y2 => vy1 * t1 - vy2 * t2 = py2 - py1`

    if props.use_examples:
        limit_max = 27
        limit_min = 7
    else:
        limit_max = 400000000000000
        limit_min = 200000000000000

    count = 0
    pairs = itertools.combinations(projected_particles, 2)
    for particle_1, particle_2 in pairs:
        a = np.array([[particle_1.velocity.x, - particle_2.velocity.x], [particle_1.velocity.y, - particle_2.velocity.y]])
        b = np.array([particle_2.position.x - particle_1.position.x, particle_2.position.y - particle_1.position.y])
        try:
            x = np.linalg.solve(a, b)
            # t1 = x[0], t2 = x[1]
        except:
            logger.log(hl.EXTRA_DETAIL, 'Particles %s and %s do not cross (%r; %r)',
                       particle_1.label, particle_2.label, particle_1, particle_2)
            continue
        crossing_x = x[0] * particle_1.velocity.x + particle_1.position.x
        crossing_y = x[0] * particle_1.velocity.y + particle_1.position.y
        logger.log(hl.EXTRA_NOISY, 'Particles %s and %s cross at (%F, %F) with linalg solution %r',
                    particle_1.label, particle_2.label, crossing_x, crossing_y, x)
        if x[0] < 0 or x[1] < 0:
            logger.log(hl.EXTRA_DETAIL, 'Excluding crossing (%F, %F) between %s and %s as it occurred in the past.',
                       crossing_x, crossing_y, particle_1.label, particle_2.label)
            continue
        if crossing_x <= limit_min or limit_max <= crossing_x:
            logger.log(hl.EXTRA_DETAIL, 'Excluding crossing (%F, %F) between %s and %s as x outside limits.',
                       crossing_x, crossing_y, particle_1.label, particle_2.label)
            continue
        if crossing_y <= limit_min or limit_max <= crossing_y:
            logger.log(hl.EXTRA_DETAIL, 'Excluding crossing (%F, %F) between %s and %s as y outside limits.',
                       crossing_x, crossing_y, particle_1.label, particle_2.label)
            continue
        count += 1

    print(count)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
