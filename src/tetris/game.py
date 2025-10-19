"""Game loop logic orchestrating the board, pieces and scoring."""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Tuple

from .board import Board
from .scores import ScoreManager
from .tetromino import ALL_TETROMINOES, Tetromino, TetrominoState

Coordinate = Tuple[int, int]


@dataclass
class ActivePiece:
    state: TetrominoState
    origin: Coordinate

    def blocks(self) -> Sequence[Coordinate]:
        return [(self.origin[0] + dx, self.origin[1] + dy) for dx, dy in self.state.blocks]


class Game:
    """High level control of a single Tetris game."""

    def __init__(
        self,
        board: Optional[Board] = None,
        score_manager: Optional[ScoreManager] = None,
        piece_sequence: Optional[Iterable[Tetromino]] = None,
        rng: Optional[random.Random] = None,
    ) -> None:
        self.board = board or Board()
        self.score_manager = score_manager or ScoreManager()
        self._piece_sequence = list(piece_sequence) if piece_sequence else None
        self._rng = rng or random.Random()
        self._bag: List[Tetromino] = []
        self.active: Optional[ActivePiece] = None
        self.game_over = False

    def start(self, profile_name: Optional[str] = None) -> None:
        self.board.reset()
        self.score_manager.reset()
        if profile_name:
            self.score_manager.attach_profile(profile_name)
        self._bag.clear()
        self.game_over = False
        self._spawn_next_piece()

    # --- Piece management -------------------------------------------------

    def _draw_from_sequence(self) -> Tetromino:
        if self._piece_sequence is None:
            raise RuntimeError("No predefined sequence configured")
        if not self._piece_sequence:
            raise StopIteration
        return self._piece_sequence.pop(0)

    def _draw_from_bag(self) -> Tetromino:
        if not self._bag:
            self._bag = list(ALL_TETROMINOES)
            self._rng.shuffle(self._bag)
        return self._bag.pop(0)

    def _next_tetromino(self) -> Tetromino:
        return self._draw_from_sequence() if self._piece_sequence is not None else self._draw_from_bag()

    def _spawn_next_piece(self) -> None:
        try:
            tetromino = self._next_tetromino()
        except StopIteration:
            self.game_over = True
            self.active = None
            return
        state = tetromino.rotated(0)
        origin = (self.board.width // 2, 0)
        active = ActivePiece(state=state, origin=origin)
        if not self.board.can_place(active.blocks()):
            self.game_over = True
            self.active = None
            return
        self.active = active

    # --- Movement ---------------------------------------------------------

    def move(self, dx: int, dy: int) -> bool:
        if not self.active or self.game_over:
            return False
        new_origin = (self.active.origin[0] + dx, self.active.origin[1] + dy)
        new_blocks = [(new_origin[0] + dx, new_origin[1] + dy) for dx, dy in self.active.state.blocks]
        if not self.board.can_place(new_blocks):
            return False
        if dy > 0:
            self.score_manager.add_soft_drop(1)
        self.active = ActivePiece(self.active.state, new_origin)
        return True

    def move_left(self) -> bool:
        return self.move(-1, 0)

    def move_right(self) -> bool:
        return self.move(1, 0)

    def soft_drop(self) -> bool:
        return self.move(0, 1)

    def hard_drop(self) -> None:
        if not self.active or self.game_over:
            return
        distance = 0
        while self.move(0, 1):
            distance += 1
        self.score_manager.add_hard_drop(distance)
        self.lock_piece()

    def rotate(self, clockwise: bool = True) -> bool:
        if not self.active or self.game_over:
            return False
        delta = 1 if clockwise else -1
        new_state = self.active.state.tetromino.rotated(self.active.state.rotation_index + delta)
        new_blocks = [(self.active.origin[0] + dx, self.active.origin[1] + dy) for dx, dy in new_state.blocks]
        if not self.board.can_place(new_blocks):
            return False
        self.active = ActivePiece(new_state, self.active.origin)
        return True

    # --- Locking ----------------------------------------------------------

    def tick(self) -> None:
        if not self.active or self.game_over:
            return
        if not self.move(0, 1):
            self.lock_piece()

    def lock_piece(self) -> None:
        if not self.active:
            return
        blocks = self.active.blocks()
        self.board.lock_piece(blocks, self.active.state.tetromino.name)
        lines = self.board.clear_full_lines()
        self.score_manager.record_line_clear(lines)
        self.active = None
        self._spawn_next_piece()

    def finalize(self) -> None:
        if self.game_over or not self.active:
            try:
                self.score_manager.finalize()
            except RuntimeError:
                pass

    # --- Inspection -------------------------------------------------------

    def current_board(self) -> List[List[Optional[str]]]:
        grid = [[cell for cell in row] for row in self.board.grid]
        if not self.active:
            return grid
        for x, y in self.active.blocks():
            if 0 <= y < self.board.height and 0 <= x < self.board.width:
                grid[y][x] = self.active.state.tetromino.name
        return grid
