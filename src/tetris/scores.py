"""Score handling and persistence integration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from .profiles import ProfileManager


@dataclass
class ScoreSnapshot:
    score: int
    lines: int


class ScoreManager:
    """Compute Tetris scores and persist results."""

    line_scores: Dict[int, int] = {1: 100, 2: 300, 3: 500, 4: 800}
    combo_bonus: int = 50
    soft_drop_bonus: int = 1
    hard_drop_bonus: int = 2

    def __init__(self, profile_manager: Optional[ProfileManager] = None) -> None:
        self.profile_manager = profile_manager or ProfileManager()
        self.reset()

    def reset(self) -> None:
        self.score = 0
        self.total_lines = 0
        self.combo_streak = 0
        self.active_profile: Optional[str] = None

    def attach_profile(self, name: str) -> None:
        self.active_profile = name

    def add_soft_drop(self, cells: int) -> None:
        if cells <= 0:
            return
        self.score += cells * self.soft_drop_bonus

    def add_hard_drop(self, cells: int) -> None:
        if cells <= 0:
            return
        self.score += cells * self.hard_drop_bonus

    def record_line_clear(self, lines: int) -> int:
        if lines <= 0:
            self.combo_streak = 0
            return 0
        self.combo_streak += 1
        self.total_lines += lines
        base = self.line_scores.get(lines, lines * 100)
        combo_points = (self.combo_streak - 1) * self.combo_bonus
        gained = base + combo_points
        self.score += gained
        return gained

    def finalize(self) -> ScoreSnapshot:
        if not self.active_profile:
            raise RuntimeError("Aucun profil actif pour enregistrer le score")
        snapshot = ScoreSnapshot(score=self.score, lines=self.total_lines)
        self.profile_manager.record_game(self.active_profile, snapshot.score, snapshot.lines)
        return snapshot
