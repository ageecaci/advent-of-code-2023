from dataclasses import dataclass
import pathlib
from typing import Optional


@dataclass(frozen=True)
class ExerciseProperties:
    day: int
    exercise: str
    parent_directory: pathlib.Path
    use_examples: bool = False
    file_suffix: Optional[str] = None
    debug: bool = False
