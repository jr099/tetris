"""Core board logic for the Tetris game."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Sequence, Tuple

from .tetromino import TetrominoState

Cell = Optional[str]
Coordinate = Tuple[int, int]


@dataclass
class Board:
    """A grid-based playing field for tetrominoes."""

    width: int = 10
    height: int = 20
    grid: List[List[Cell]] = field(init=False)

    def __post_init__(self) -> None:
        self.grid = [[None for _ in range(self.width)] for _ in range(self.height)]

    def reset(self) -> None:
        """Reset the board to an empty state."""
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = None

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def can_place(self, blocks: Sequence[Coordinate]) -> bool:
        """Check whether the given block coordinates can be placed."""
        for x, y in blocks:
            if x < 0 or x >= self.width:
                return False
            if y >= self.height:
                return False
            if y >= 0 and self.grid[y][x] is not None:
                return False
        return True

    def lock_piece(self, blocks: Sequence[Coordinate], value: str) -> None:
        """Lock the piece's blocks into the grid."""
        for x, y in blocks:
            if y < 0:
                continue
            self.grid[y][x] = value

    def clear_full_lines(self) -> int:
        """Remove filled lines from the board and return how many were cleared."""
        remaining = [row for row in self.grid if any(cell is None for cell in row)]
        cleared = self.height - len(remaining)
        if cleared:
            self.grid = [[None for _ in range(self.width)] for _ in range(cleared)] + remaining
        return cleared

    def iter_with_piece(self, state: TetrominoState, origin: Coordinate) -> Iterable[Tuple[int, int, Cell]]:
        """Yield cells with the provided piece temporarily overlaid."""
        piece_coords = {(origin[0] + dx, origin[1] + dy) for dx, dy in state.blocks}
        for y in range(self.height):
            for x in range(self.width):
                value = self.grid[y][x]
                if (x, y) in piece_coords:
                    yield x, y, state.tetromino.name
                else:
                    yield x, y, value

    def project_piece(self, state: TetrominoState, origin: Coordinate) -> Sequence[Coordinate]:
        """Return the absolute coordinates for a piece at a given origin."""
        return [(origin[0] + dx, origin[1] + dy) for dx, dy in state.blocks]
