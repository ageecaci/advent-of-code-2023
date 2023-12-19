#!/usr/bin/env python3

from dataclasses import dataclass
from dataclasses import dataclass
import logging
import operator
import pathlib
import sys
from typing import Callable, Optional
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

import lib.helper_args as ha
import lib.helper_file as hf
import lib.helper_log as hl

logger = logging.getLogger(__file.stem)

less_than = '<'
greater_than = '>'
rule_accept = 'A'
rule_reject = 'R'
terminals = set((rule_accept, rule_reject))
workflow_start = 'in'

lookups = {
    'x': operator.attrgetter('x'),
    'm': operator.attrgetter('m'),
    'a': operator.attrgetter('a'),
    's': operator.attrgetter('s'),
}


@dataclass
class Part:
    x: int
    m: int
    a: int
    s: int

    def __post_init__(self):
        self._total = None

    @property
    def total(self):
        if self._total == None:
            self._total = self.x + self.m + self.a + self.s
        return self._total


Rule = Callable[[Part], Optional[str]]


def build_rule_from(attribute_name: str, operator: str, threshold: int, target: str) -> Rule:
    attribute_lookup = lookups[attribute_name]
    if operator == less_than:
        def new_condition(part: Part) -> Optional[str]:
            attribute_value = attribute_lookup(part)
            if attribute_value < threshold:
                return target
            return None
    elif operator == greater_than:
        def new_condition(part: Part) -> Optional[str]:
            attribute_value = attribute_lookup(part)
            if attribute_value > threshold:
                return target
            return None
    else:
        raise Exception(f'Unexpected operator ({operator}) specified')
    return new_condition


@dataclass
class Workflow:
    key: str
    rules: tuple[Rule]

    def apply(self, part: Part) -> str:
        for rule in self.rules:
            result = rule(part)
            if result is not None:
                return result
        raise Exception(f'Reached end of workflow {self.key} without reaching a terminus')


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
    rules.append(lambda _: rule_labels[-1])
    workflow = Workflow(key, tuple(rules))
    return workflow


def parse_part(input: str) -> Part:
    attribute_labels = input.strip()[1:-1].split(',')
    attributes: dict[str, int] = {}
    for attribute_label in attribute_labels:
        attribute_name, value = attribute_label.split('=', 1)
        attributes[attribute_name] = int(value)
    return Part(**attributes)


def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    workflows: dict[str, Workflow] = {}
    parts: list[Part] = []
    processing_workflows = True
    for line in lines:
        line = line.strip()
        if processing_workflows and len(line) < 1:
            processing_workflows = False
            continue
        if processing_workflows:
            workflow = parse_workflow(line)
            workflows[workflow.key] = workflow
        else:
            part = parse_part(line)
            parts.append(part)

    subtotal = 0
    for part in parts:
        logger.log(hl.EXTRA_DETAIL, 'Processing part: %r', part)
        next_workflow_key = workflow_start
        while next_workflow_key not in terminals:
            next_workflow = workflows[next_workflow_key]
            next_workflow_key = next_workflow.apply(part)
            logger.log(hl.EXTRA_DETAIL, 'mapping to workflow %s', next_workflow_key)
        if next_workflow_key == rule_accept:
            logger.debug('Adding %d to subtotal from accepting part: %r', part.total, part)
            subtotal += part.total
        elif next_workflow_key == rule_reject:
            logger.debug('Rejecting part: %r', part)
        else:
            raise Exception(f'Unexpected terminus ({next_workflow_key}) reached for part: {part}')

    print(subtotal)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
