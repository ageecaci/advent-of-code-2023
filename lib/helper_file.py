import argparse
import logging
import pathlib

from lib.class_exercise_properties import ExerciseProperties as cep

logger = logging.getLogger(__name__)


def load_lines(file_path: str) -> list[str]:
    with open(file_path) as f:
        return list(f.readlines())


def find_input_file(properties: cep) -> pathlib.Path:
    for include_exercise in [True, False]:
        path = properties.parent_directory / determine_name(properties, include_exercise)
        if path.is_file():
            logger.debug('Using input file: %s', path)
            return path
    raise Exception(
        f'No valid input file found for {properties.day}{properties.exercise} (use examples: {properties.use_examples})')


def determine_name(properties: cep, include_exercise=True) -> str:
    if properties.use_examples:
        if include_exercise:
            return f'{properties.day}{properties.exercise}-examples.txt'
        return f'{properties.day}-examples.txt'
    return f'{properties.day}-input.txt'


def parse_name(file_path_str: str, args: argparse.Namespace) -> cep:
    file_path = pathlib.Path(file_path_str).resolve()
    file_name = file_path.stem
    if args is not None:
        return cep(int(file_name[0]), file_name[1], file_path.parent, args.examples, args.verbose)
    return cep(int(file_name[0]), file_name[1], file_path.parent)
