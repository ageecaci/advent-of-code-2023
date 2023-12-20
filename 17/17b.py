#!/usr/bin/env python3

from dataclasses import dataclass
from functools import cache
import heapq
import logging
import pathlib
import sys
from typing import Optional
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

from lib.class_text_coordinate_limits import TextCoordinateLimits as Limits
from lib.class_text_coordinate import TextCoordinate as Coordinate
import lib.helper_args as ha
import lib.helper_coord as hc
import lib.helper_file as hf
import lib.helper_log as hl

logger = logging.getLogger(__file.stem)

up = 'up'
down = 'down'
left = 'left'
right = 'right'
directions = [up, down, left, right]
visual_directions = {
    up: '^',
    down: 'v',
    left: '<',
    right: '>',
}


@dataclass(frozen=True)
class Visit:
    location: Coordinate
    last_direction: Optional[str]
    last_direction_multiplicity: int

    @property
    def triple_direction(self) -> Optional[str]:
        if self.last_direction_multiplicity >= 3:
            return self.last_direction
        return None

    def next_visit(self, neighbour: Coordinate, direction: str) -> 'Visit':
        next_multiplicity = 1
        if self.last_direction == direction:
            next_multiplicity = self.last_direction_multiplicity + 1
        return Visit(neighbour, direction, next_multiplicity)


@dataclass(frozen=True)
class Journey:
    heat_loss: int
    steps_taken: tuple[Visit]

    @property
    def last_step(self) -> Visit:
        return self.steps_taken[-1]

    def __lt__(self, other):
        if isinstance(other, Journey):
            return self.heat_loss < other.heat_loss
        return NotImplemented


class City:
    def __init__(self, weights: tuple[str], destination: Coordinate = None):
        self.weights = weights
        self.limits = Limits(len(weights), len(weights[0]))
        if destination is not None:
            self.destination = destination
        else:
            self.destination = Coordinate(self.limits.max_line - 1, self.limits.max_character - 1)

        self.initial_location: Optional[Coordinate] = None
        self.partial_journeys: list[Journey] = []
        self.previous_visits: set[Visit] = set()
        self.minimal_heat_loss_from: dict[Visit, int] = {}
        self.minimal_journey: Optional[Journey] = None


    def find_minimal_journey(self, initial_location: Coordinate) -> Journey:
        if self.initial_location is not None:
            if self.initial_location == initial_location:
                return self.minimal_journey
            raise Exception('A journey has already taken place through this city')
        self.initial_location = initial_location
        initial_visit = Visit(initial_location, None, 0)
        initial_journey = Journey(0, (initial_visit,))
        heapq.heappush(self.partial_journeys, initial_journey)
        while len(self.partial_journeys) > 0:
            # heapq guarantees we are always working with partial journey with minimal heat loss
            journey = heapq.heappop(self.partial_journeys)
            if journey.last_step.location == self.destination:
                self.minimal_journey = journey
                return journey
            if journey.last_step in self.previous_visits:
                continue
            self.previous_visits.add(journey.last_step)
            self.explore_from(journey)
        return -1


    def explore_from(self, journey: Journey):
        visit = journey.last_step
        logger.log(hl.EXTRA_NOISY, 'Exploring %r', visit)
        valid_directions = get_valid_directions(visit.last_direction, visit.last_direction_multiplicity)
        for direction_travelled in valid_directions:
            neighbour = from_direction(visit.location, direction_travelled)
            if not self.limits.contains(neighbour):
                continue
            new_visit = visit.next_visit(neighbour, direction_travelled)
            new_heat_loss = journey.heat_loss + int(hc.lookup_in(neighbour, self.weights))
            prior_minimal_heat_loss = self.minimal_heat_loss_from.get(new_visit, None)
            if prior_minimal_heat_loss is None or new_heat_loss < prior_minimal_heat_loss:
                self.minimal_heat_loss_from[new_visit] = new_heat_loss
                new_steps = (*journey.steps_taken, new_visit)
                heapq.heappush(self.partial_journeys, Journey(new_heat_loss, new_steps))


    def visualise(self, journey: Journey) -> str:
        overrides: dict[Coordinate, list[str]] = {}
        for step in journey.steps_taken:
            if step.last_direction is None:
                continue
            if step.location not in overrides:
                overrides[step.location] = [step.last_direction]
            else:
                overrides[step.location].append(step.last_direction)
        new_start_line = '.' * self.limits.max_character
        new_grid = [new_start_line] * self.limits.max_line
        for location, visits in overrides.items():
            line = new_grid[location.line]
            output = str(len(visits)) if len(visits) > 1 else visual_directions[visits[0]]
            new_line = (
                line[:location.character]
                + output
                + line[location.character+1:])
            new_grid[location.line] = new_line
        return '\n'.join(new_grid)


@cache
def from_direction(origin: Coordinate, direction: str) -> Coordinate:
    if direction == up:
        return origin.up()
    if direction == down:
        return origin.down()
    if direction == left:
        return origin.left()
    if direction == right:
        return origin.right()
    raise Exception(f'Invalid direction {direction}')


@cache
def get_valid_directions(inbound_direction: Optional[str], direction_multiplicity: int) -> set[str]:
    if inbound_direction is None or direction_multiplicity == 0:
        return set(directions)
    if direction_multiplicity < 4:
        # must keep going
        return set((inbound_direction,))
    valid_directions = set(directions)
    # we can never go backwards
    if inbound_direction == up:
        valid_directions.discard(down)
    elif inbound_direction == down:
        valid_directions.discard(up)
    elif inbound_direction == left:
        valid_directions.discard(right)
    elif inbound_direction == right:
        valid_directions.discard(left)
    if direction_multiplicity >= 10:
        # we cannot keep going forward
        valid_directions.discard(inbound_direction)
    return valid_directions


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))
    weights = tuple(line for line in lines)
    city = City(weights)
    initial_location = Coordinate(0, 0)
    journey = city.find_minimal_journey(initial_location)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug('Minimal heat-loss journey: %s', journey)
        logger.debug('Minimal heat-loss path:\n%s', city.visualise(journey))

    print(journey.heat_loss)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
