from lib.class_text_coordinate import TextCoordinate as Coordinate


class Edge:
    def __init__(self, start: Coordinate, end: Coordinate):
        self._horizontal = False
        self._vertical = False
        if start.line == end.line:
            self._horizontal = True
        if start.character == end.character:
            self._vertical = True
        # only support horizontal or vertical lines
        assert (self._horizontal or self._vertical) and not (self._horizontal and self._vertical)
        ordered_vertices = sorted((start, end))
        self.start = ordered_vertices[0]
        self.end = ordered_vertices[1]

    @property
    def horizontal(self):
        return self._horizontal

    @property
    def vertical(self):
        return self._vertical

    @property
    def is_point(self):
        return self.start == self.end

    @property
    def length(self) -> int:
        if self.horizontal:
            return self.end.character - self.start.character
        elif self.vertical:
            return self.end.line - self.start.line
        raise Exception('Invalid edge to determine length for')

    def crosses_point(self, coord: Coordinate) -> bool:
        if self._horizontal and self.start.line == coord.line:
            return self.start.character < coord.character and coord.character < self.end.character
        if self._vertical and self.start.character == coord.character:
            return self.start.line < coord.line and coord.line < self.end.line
        return False

    def __repr__(self):
        return f'Edge({self.start}, {self.end})'
