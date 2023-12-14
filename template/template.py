#!/usr/bin/env python3

from collections.abc import Iterable
from dataclasses import dataclass
from functools import cache
import logging
import math
import operator
import os
import sys
from typing import Optional
sys.path.append(os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..')))

from bidict import bidict
import numpy as np

from lib.class_text_coordinate_limits import TextCoordinateLimits as Limits
from lib.class_text_coordinate import TextCoordinate as Coordinate
import lib.helper_args as ha
import lib.helper_file as hf
import lib.helper_log as hl


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    subtotal = 0
    print(subtotal)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
