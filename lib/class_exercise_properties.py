from dataclasses import dataclass
import pathlib


@dataclass
class ExerciseProperties:
    day: int
    exercise: str
    parent_directory: pathlib.Path
    use_examples: bool = False
    debug: bool = False
