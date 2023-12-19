from dataclasses import dataclass
from functools import cached_property

@dataclass(frozen=True, order=True)
class Limits:
    min: int = 0 # inclusive
    max: int = 0 # exclusive

    def __post_init__(self):
        assert self.min <= self.max

    @cached_property
    def length(self) -> int:
        return self.max - self.min

    def __contains__(self, value):
        if not isinstance(value, int):
            raise ValueError(f'Limits can only contain integers')
        return self.min <= value and value < self.max

    def split_at(self, value: int) -> tuple['Limits']:
        '''Input value becomes new minimum for upper range'''
        if value not in self:
            return (self,)
        if self.min == value:
            # avoid creating a limit with length 0
            return (self,)
        left = Limits(self.min, value)
        right = Limits(value, self.max)
        return (left, right)
