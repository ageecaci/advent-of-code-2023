from lib.class_text_coordinate import TextCoordinate as Coordinate


'''
For defined functions: minimums are inclusive, maximums are exclusive
'''
class TextCoordinateLimits:
    def __init__(self, max_line: int, max_character: int, min_line: int = 0, min_character: int = 0):
        if min_line <= max_line:
            self.min_line = min_line
            self.max_line = max_line
        else:
            self.min_line = max_line
            self.max_line = min_line
        if min_character <= max_character:
            self.min_character = min_character
            self.max_character = max_character
        else:
            self.min_character = max_character
            self.max_character = min_character
        self.width = self.max_character - self.min_character
        self.depth = self.max_line - self.min_line

    def __contains__(self, value):
        if not isinstance(value, Coordinate):
            raise ValueError('Limits can only contain coordinates')
        return (value.line >= self.min_line and value.line < self.max_line
                and value.character >= self.min_character and value.character < self.max_character)

    def contains(self, coord: Coordinate) -> bool:
        return coord in self
