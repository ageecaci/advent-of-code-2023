from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class TextCoordinate:
    line: int
    character: int

    def above(self, other) -> bool:
        if isinstance(other, TextCoordinate):
            return self.line == other.line - 1 and self.character == other.character
        return NotImplemented

    def below(self, other) -> bool:
        if isinstance(other, TextCoordinate):
            return self.line == other.line + 1 and self.character == other.character
        return NotImplemented

    def left_of(self, other) -> bool:
        if isinstance(other, TextCoordinate):
            return self.line == other.line and self.character == other.character - 1
        return NotImplemented

    def right_of(self, other) -> bool:
        if isinstance(other, TextCoordinate):
            return self.line == other.line and self.character == other.character + 1
        return NotImplemented

    def up(self, distance: int = 1) -> 'TextCoordinate':
        return TextCoordinate(self.line - distance, self.character)

    def down(self, distance: int = 1) -> 'TextCoordinate':
        return TextCoordinate(self.line + distance, self.character)

    def left(self, distance: int = 1) -> 'TextCoordinate':
        return TextCoordinate(self.line, self.character - distance)

    def right(self, distance: int = 1) -> 'TextCoordinate':
        return TextCoordinate(self.line, self.character + distance)
