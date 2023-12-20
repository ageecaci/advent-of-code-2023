import argparse
import logging
import pathlib

from lib.class_exercise_properties import ExerciseProperties as cep

logger = logging.getLogger(__name__)


def load_lines(file_path: str) -> list[str]:
    with open(file_path) as f:
        return [line.strip() for line in f.readlines()]


def find_input_file(properties: cep) -> pathlib.Path:
    for include_exercise in [True, False]:
        path = properties.parent_directory / determine_name(properties, include_exercise)
        if path.is_file():
            logger.debug('Using input file: %s', path)
            return path
    raise Exception(
        f'No input files found at expected paths for {properties.day}{properties.exercise}')


def determine_name(properties: cep, include_exercise=True) -> str:
    parts = [str(properties.day)]
    if include_exercise:
        parts.append(str(properties.exercise))
    if properties.use_examples:
        parts.append(str('-examples'))
    else:
        parts.append(str('-input'))
    if properties.file_suffix:
        parts.append(properties.file_suffix)
    parts.append('.txt')
    file_name = ''.join(parts)
    logger.debug('About to check file "%s"', file_name)
    return file_name


def parse_name(file_path_str: str, args: argparse.Namespace) -> cep:
    file_path = pathlib.Path(file_path_str).resolve()
    file_name = file_path.stem.split('-', 1)[0]
    if args is not None:
        return cep(int(file_name[:-1]), file_name[-1], file_path.parent, args.examples, args.file_suffix, args.verbose)
    return cep(int(file_name[:-1]), file_name[-1], file_path.parent)
