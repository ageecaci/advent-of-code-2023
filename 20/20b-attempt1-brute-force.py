#!/usr/bin/env python3

from dataclasses import dataclass, field
from collections import deque
from dataclasses import dataclass
import logging
import pathlib
import sys
from typing import Hashable, Optional
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

    def __add__(self, other) -> 'PulseCount':
        if not isinstance(other, PulseCount):
            return NotImplemented
        return PulseCount(
            self.low + other.low,
            self.high + other.high)

    def __sub__(self, other) -> 'PulseCount':
        if not isinstance(other, PulseCount):
            return NotImplemented
        return PulseCount(
            self.low - other.low,
            self.high - other.high)

    def __mul__(self, other) -> 'PulseCount':
        if not isinstance(other, int):
            return NotImplemented
        return PulseCount(
            self.low * other,
            self.high * other)


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

    def get_state(self) -> Optional[Hashable]:
        return None


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

    def get_state(self) -> Optional[Hashable]:
        return (self.key, self.is_on)


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

    def get_state(self) -> Optional[Hashable]:
        states = []
        for source_key, last_seen_type in self.last_seen.items():
            states.append((source_key, last_seen_type))
        return tuple(states)


@dataclass(frozen=True)
class ModuleMap:
    modules: dict[str, Module]

    def send_pulse(self, module_of_interest: str) -> PulseCount:
        counts = {
            pulse_high: 0,
            pulse_low: 0,
        }
        unprocessed_pulses: deque[Pulse] = deque()
        unprocessed_pulses.append(Pulse(pulse_low, type_button, type_broadcaster))
        while len(unprocessed_pulses) > 0:
            next_pulse = unprocessed_pulses.popleft()
            if next_pulse.destination == module_of_interest:
                counts[next_pulse.type] += 1
            logger.log(hl.EXTRA_DETAIL, '%s -%s-> %s', next_pulse.source, next_pulse.type, next_pulse.destination)
            target = self.modules.get(next_pulse.destination, None)
            if target is None:
                # no module definition provided: pulse is swallowed
                continue
            produced_pulses = target.get_pulse(next_pulse)
            unprocessed_pulses.extend(produced_pulses)
        return PulseCount(counts[pulse_low], counts[pulse_high])

    def get_state(self) -> Hashable:
        module_states = []
        for _, module in self.modules.items():
            module_state = module.get_state()
            if module_state is not None:
                module_states.append(module_state)
        return tuple(module_states)


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
    index = 0
    state_indices: dict[Hashable, int] = {}
    current_state = module_map.get_state()
    state_indices[current_state] = 0
    while True:
        index += 1
        pulses_sent = module_map.send_pulse(module_of_interest)
        logger.debug('Button press %d resulted in module %s receiving pulses: %r', index, module_of_interest, pulses_sent)
        if pulses_sent.low == 1:
            break
        current_state = module_map.get_state()
        if current_state in state_indices:
            start_of_loop_index = state_indices[current_state]
            end_of_loop_index = index
            logger.debug('Loop detected from pulse %d to pulse %d', start_of_loop_index, end_of_loop_index)
            index = -1
            break
        else:
            state_indices[current_state] = index

    print(index)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
