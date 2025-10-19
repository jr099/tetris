"""Tetromino definitions and rotation logic for the Tetris game."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

Coordinate = Tuple[int, int]


@dataclass(frozen=True)
class Tetromino:
    """Representation of a tetromino shape with its rotation states."""

    name: str
    rotations: Tuple[Tuple[Coordinate, ...], ...]
    color: str = ""

    def rotated(self, rotation_index: int) -> "TetrominoState":
        """Return a TetrominoState for the rotation index modulo rotation count."""
        index = rotation_index % len(self.rotations)
        return TetrominoState(self, index)


@dataclass(frozen=True)
class TetrominoState:
    """A specific rotation state of a tetromino."""

    tetromino: Tetromino
    rotation_index: int

    @property
    def blocks(self) -> Tuple[Coordinate, ...]:
        return self.tetromino.rotations[self.rotation_index]


# fmt: off
I = Tetromino(
    name="I",
    rotations=(
        ((-2, 0), (-1, 0), (0, 0), (1, 0)),
        ((0, -1), (0, 0), (0, 1), (0, 2)),
    ),
    color="cyan",
)

O = Tetromino(
    name="O",
    rotations=(
        ((0, 0), (1, 0), (0, 1), (1, 1)),
    ),
    color="yellow",
)

T = Tetromino(
    name="T",
    rotations=(
        ((-1, 0), (0, 0), (1, 0), (0, 1)),
        ((0, -1), (0, 0), (1, 0), (0, 1)),
        ((0, -1), (-1, 0), (0, 0), (1, 0)),
        ((0, -1), (-1, 0), (0, 0), (0, 1)),
    ),
    color="purple",
)

S = Tetromino(
    name="S",
    rotations=(
        ((0, 0), (1, 0), (-1, 1), (0, 1)),
        ((0, -1), (0, 0), (1, 0), (1, 1)),
    ),
    color="green",
)

Z = Tetromino(
    name="Z",
    rotations=(
        ((-1, 0), (0, 0), (0, 1), (1, 1)),
        ((1, -1), (0, 0), (1, 0), (0, 1)),
    ),
    color="red",
)

J = Tetromino(
    name="J",
    rotations=(
        ((-1, 0), (0, 0), (1, 0), (-1, 1)),
        ((0, -1), (0, 0), (0, 1), (1, -1)),
        ((1, -1), (-1, 0), (0, 0), (1, 0)),
        ((-1, 1), (0, -1), (0, 0), (0, 1)),
    ),
    color="blue",
)

L = Tetromino(
    name="L",
    rotations=(
        ((-1, 0), (0, 0), (1, 0), (1, 1)),
        ((0, -1), (0, 0), (0, 1), (1, 1)),
        ((-1, -1), (-1, 0), (0, 0), (1, 0)),
        ((-1, -1), (0, -1), (0, 0), (0, 1)),
    ),
    color="orange",
)
# fmt: on

ALL_TETROMINOES: Tuple[Tetromino, ...] = (I, O, T, S, Z, J, L)
