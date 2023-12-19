#!/usr/bin/env python3

from dataclasses import dataclass
from collections import deque
from dataclasses import dataclass
from functools import cached_property
import logging
import operator
import pathlib
import sys
from typing import Callable, Optional
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

from lib.class_limits import Limits
import lib.helper_args as ha
import lib.helper_file as hf
import lib.helper_log as hl

logger = logging.getLogger(__file.stem)

less_than = '<'
greater_than = '>'
operators = set((less_than, greater_than))
rule_accept = 'A'
rule_reject = 'R'
workflow_start = 'in'

lookups = {
    'x': operator.attrgetter('x'),
    'm': operator.attrgetter('m'),
    'a': operator.attrgetter('a'),
    's': operator.attrgetter('s'),
}


@dataclass(frozen=True)
class PartSetPartition:
    x: Limits
    m: Limits
    a: Limits
    s: Limits

    @cached_property
    def size(self) -> int:
        return self.x.length * self.m.length * self.a.length * self.s.length

    def new_with_override(
            self, x: Optional[Limits] = None,
            m: Optional[Limits] = None,
            a: Optional[Limits] = None,
            s: Optional[Limits] = None):
        limits = {
            'x': self.x,
            'm': self.m,
            'a': self.a,
            's': self.s,
        }
        if x is not None:
            limits['x'] = x
        if m is not None:
            limits['m'] = m
        if a is not None:
            limits['a'] = a
        if s is not None:
            limits['s'] = s
        return PartSetPartition(**limits)


Rule = Callable[[PartSetPartition], list[tuple[PartSetPartition, str]]]


def build_rule_from(attribute_name: str, operator: str, threshold: int, target: str) -> Rule:
    if operator not in operators:
        raise Exception(f'Unexpected operator ({operator}) specified')
    attribute_lookup = lookups[attribute_name]
    if operator == less_than:
        def new_rule(partition: PartSetPartition) -> Optional[str]:
            output: list[tuple[PartSetPartition, str]] = []
            attribute_limits: Limits = attribute_lookup(partition)
            # [min, max) -> [min, threshold), [threshold, max)
            new_limits = attribute_limits.split_at(threshold)
            for limit in new_limits:
                override = {attribute_name: limit}
                if threshold in limit:
                    # in the upper limit, which does not get redirected
                    output.append((partition.new_with_override(**override), None))
                else:
                    # in the lower limit, which gets redirected
                    output.append((partition.new_with_override(**override), target))
            return output
    else: # operator == greater_than
        def new_rule(partition: PartSetPartition) -> Optional[str]:
            output: list[tuple[PartSetPartition, str]] = []
            attribute_limits: Limits = attribute_lookup(partition)
            # [min, max) -> [min, threshold+1), [threshold+1, max)
            new_limits = attribute_limits.split_at(threshold + 1)
            for limit in new_limits:
                override = {attribute_name: limit}
                if threshold in limit:
                    # in the lower limit, which does not get redirected
                    output.append((partition.new_with_override(**override), None))
                else:
                    # in the upper limit, which gets redirected
                    output.append((partition.new_with_override(**override), target))
            return output
    return new_rule


@dataclass
class Workflow:
    key: str
    rules: tuple[Rule]

    def apply(self, partition: PartSetPartition) -> list[tuple[PartSetPartition, str]]:
        output = []
        remaining_partition = partition
        for rule in self.rules:
            results = rule(remaining_partition)
            none_count = 0
            for result in results:
                partition, target = result
                if target is None:
                    none_count += 1
                    remaining_partition = partition
                else:
                    output.append(result)
            if none_count == 0:
                break
            elif none_count > 1:
                raise Exception(f'More than one partition without a target workflow during processing of workflow "{self.key}"')
        if none_count > 0:
            raise Exception(f'At least one partition without a target workflow after processing workflow "{self.key}"')
        return output


def parse_workflow(input: str) -> Workflow:
    key, ruleset_label = input.strip().split('{', 1)
    rule_labels = ruleset_label[:-1].split(',')
    rules: list[Rule] = []
    for rule_label in rule_labels[:-1]:
        condition_label, target = rule_label.split(':', 1)
        if less_than in condition_label:
            operator = less_than
        elif greater_than in condition_label:
            operator = greater_than
        else:
            raise Exception(f'Neither "<" nor ">" found in rule: {rule_label}')
        attribute, threshold = condition_label.split(operator, 1)
        rule = build_rule_from(attribute, operator, int(threshold), target)
        rules.append(rule)
    rules.append(lambda x: [(x, rule_labels[-1])])
    workflow = Workflow(key, tuple(rules))
    return workflow


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    workflows: dict[str, Workflow] = {}
    for line in lines:
        line = line.strip()
        if len(line) < 1:
            break
        workflow = parse_workflow(line)
        workflows[workflow.key] = workflow

    initial_limits = Limits(1, 4001)
    initial_partition = PartSetPartition(
        initial_limits, initial_limits,
        initial_limits, initial_limits)

    q: deque[tuple[PartSetPartition, str]] = deque([(initial_partition, workflow_start)])

    subtotal = 0
    while len(q) > 0:
        partition, workflow_key = q.popleft()
        logger.log(hl.EXTRA_DETAIL, 'Processing workflow %s for partition: %r', workflow_key, partition)
        workflow = workflows[workflow_key]
        results = workflow.apply(partition)
        for result in results:
            partition, workflow_key = result
            if workflow_key == rule_accept:
                logger.debug('Adding %d to subtotal from accepted partition: %r', partition.size, partition)
                subtotal += partition.size
            elif workflow_key == rule_reject:
                logger.log(hl.EXTRA_DETAIL, 'Rejecting partition: %r', partition)
            else:
                logger.log(hl.EXTRA_NOISY, 'mapping to workflow %s for partition: %r', workflow_key, partition)
                q.append(result)

    print(subtotal)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
