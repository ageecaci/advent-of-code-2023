from dataclasses import dataclass


@dataclass(frozen=True)
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

    def up(self) -> 'TextCoordinate':
        return TextCoordinate(self.line - 1, self.character)

    def down(self) -> 'TextCoordinate':
        return TextCoordinate(self.line + 1, self.character)

    def left(self) -> 'TextCoordinate':
        return TextCoordinate(self.line, self.character - 1)

    def right(self) -> 'TextCoordinate':
        return TextCoordinate(self.line, self.character + 1)
