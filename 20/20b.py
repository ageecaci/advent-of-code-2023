#!/usr/bin/env python3

from dataclasses import dataclass, field
from collections import deque
from dataclasses import dataclass
import logging
import math
import pathlib
import sys
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

import lib.helper_args as ha
import lib.helper_file as hf
import lib.helper_log as hl

logger = logging.getLogger(__file.stem)

pulse_high = 'high'
pulse_low = 'low'
type_broadcaster = 'broadcaster'
type_button = 'button'
type_conjunction = '&'
type_flip_flop = '%'


@dataclass(frozen=True)
class Pulse:
    type: str
    source: str
    destination: str


@dataclass
class PulseCount:
    low: int = 0
    high: int = 0


@dataclass
class Module:
    key: str
    destinations: tuple[str]
    sources: tuple[str]

    def get_pulse(self, input: Pulse) -> list[Pulse]:
        logger.log(hl.EXTRA_NOISY, 'Broadcast module forwarding %s pulse from %s', input.type, input.source)
        return self.send_pulse(input.type)

    def send_pulse(self, type: str) -> list[Pulse]:
        output = []
        for destination_key in self.destinations:
            output.append(Pulse(type, self.key, destination_key))
        return output


@dataclass
class ModuleFlipFlop(Module):
    is_on: bool = False

    def get_pulse(self, input: Pulse) -> list[Pulse]:
        if input.type == pulse_high:
            logger.log(hl.EXTRA_NOISY, 'FlipFlop module %s ignoring %s pulse from %s', self.key, input.type, input.source)
            return []
        self.is_on = not self.is_on
        if self.is_on:
            logger.log(hl.EXTRA_NOISY, 'FlipFlop module %s sending %s pulse', self.key, pulse_high)
            return self.send_pulse(pulse_high)
        else:
            logger.log(hl.EXTRA_NOISY, 'FlipFlop module %s sending %s pulse', self.key, pulse_low)
            return self.send_pulse(pulse_low)


@dataclass
class ModuleConjunction(Module):
    last_seen: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        for source_key in self.sources:
            self.last_seen[source_key] = pulse_low

    def get_pulse(self, input: Pulse) -> list[Pulse]:
        self.last_seen[input.source] = input.type
        if self.last_seen_all_high():
            logger.log(hl.EXTRA_NOISY, 'Conjunction module %s sending %s pulse', self.key, pulse_low)
            return self.send_pulse(pulse_low)
        else:
            logger.log(hl.EXTRA_NOISY, 'Conjunction module %s sending %s pulse', self.key, pulse_high)
            return self.send_pulse(pulse_high)

    def last_seen_all_high(self):
        for _, last_seen_type in self.last_seen.items():
            if last_seen_type != pulse_high:
                return False
        return True


@dataclass(frozen=True)
class ModuleMap:
    modules: dict[str, Module]

    def send_pulse(self, modules_of_interest: set[str]) -> dict[str, PulseCount]:
        counts: dict[str, dict[str, int]] = {}
        for module_key in modules_of_interest:
            counts[module_key] = {
                pulse_high: 0,
                pulse_low: 0,
            }
        unprocessed_pulses: deque[Pulse] = deque()
        unprocessed_pulses.append(Pulse(pulse_low, type_button, type_broadcaster))
        while len(unprocessed_pulses) > 0:
            next_pulse = unprocessed_pulses.popleft()
            if next_pulse.source in modules_of_interest:
                counts[next_pulse.source][next_pulse.type] += 1
            logger.log(hl.EXTRA_DETAIL, '%s -%s-> %s', next_pulse.source, next_pulse.type, next_pulse.destination)
            target = self.modules.get(next_pulse.destination, None)
            if target is None:
                # no module definition provided: pulse is swallowed
                continue
            produced_pulses = target.get_pulse(next_pulse)
            unprocessed_pulses.extend(produced_pulses)
        return {key: PulseCount(value[pulse_low], value[pulse_high]) for key, value in counts.items()}


def construct_module(key: str, type: str, destinations: list[str], sources: list[str]) -> Module:
    sources.sort()
    if type == type_broadcaster:
        return Module(key, tuple(destinations), tuple(sources))
    elif type == type_conjunction:
        return ModuleConjunction(key, tuple(destinations), tuple(sources))
    elif type == type_flip_flop:
        return ModuleFlipFlop(key, tuple(destinations), tuple(sources))


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    source_map_to_type: dict[str, str] = {}
    source_map_to_destination: dict[str, list[str]] = {}
    destination_map_to_source: dict[str, list[str]] = {}
    for line in lines:
        source_label, destinations_label = line.split(' -> ')
        destination_labels = destinations_label.split(', ')
        if source_label == type_broadcaster:
            source_key = type_broadcaster
            source_type = type_broadcaster
        else:
            source_type = source_label[0]
            source_key = source_label[1:]
        source_map_to_type[source_key] = source_type
        source_map_to_destination[source_key] = destination_labels
        for destination_key in destination_labels:
            if destination_key not in destination_map_to_source:
                destination_map_to_source[destination_key] = []
            destination_map_to_source[destination_key].append(source_key)
    destination_map_to_source[type_broadcaster] = [type_button]

    modules: dict[str, Module] = {}
    keys = sorted(source_map_to_destination.keys())
    for module_key in keys:
        modules[module_key] = construct_module(
            module_key,
            source_map_to_type[module_key],
            source_map_to_destination[module_key],
            destination_map_to_source[module_key])
    module_map = ModuleMap(modules)

    module_of_interest = 'rx'
    targets_module_of_interest = destination_map_to_source[module_of_interest]
    assert len(targets_module_of_interest) == 1
    sources_of_interest = destination_map_to_source[targets_module_of_interest[0]]
    first_highs: dict[str, int] = {}
    index = 0
    while True:
        index += 1
        pulses_sent = module_map.send_pulse(sources_of_interest)
        for module_key, pulse_count in pulses_sent.items():
            if module_key not in first_highs and pulse_count.high > 0:
                logger.debug('Button press %d resulted in module %s receiving its first high pulse', index, module_key)
                first_highs[module_key] = index
        if len(first_highs) == len(sources_of_interest):
            break

    logger.warning('This is the solution to the AoC problem, not the generalised problem statement.')
    print(math.lcm(*list(first_highs.values())))


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
