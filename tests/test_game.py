from pathlib import Path

import pytest

from tetris import tetromino
from tetris.game import Game
from tetris.profiles import ProfileManager
from tetris.scores import ScoreManager


@pytest.fixture
def temp_manager(tmp_path: Path) -> ProfileManager:
    data_file = tmp_path / "profiles.json"
    manager = ProfileManager(data_file)
    manager.create_profile("test")
    return manager


def test_piece_rotation_and_line_clear(temp_manager: ProfileManager) -> None:
    score_manager = ScoreManager(temp_manager)
    pieces = [tetromino.I, tetromino.O]
    game = Game(score_manager=score_manager, piece_sequence=pieces)
    game.start("test")

    # Rotate the I piece vertically and back to horizontal
    assert game.active is not None
    assert game.active.state.tetromino.name == "I"
    assert game.rotate()
    assert game.active.state.rotation_index == 1
    assert game.rotate(clockwise=False)
    assert game.active.state.rotation_index == 0

    # Prepare the board to clear a line when the I piece locks.
    bottom = game.board.grid[-1]
    for x in range(game.board.width):
        bottom[x] = "X"
    for x in range(3, 7):
        bottom[x] = None

    # Soft drop the piece until it rests on the filled row then lock it.
    while game.soft_drop():
        pass
    game.tick()

    assert game.board.grid[-1] == [None] * game.board.width
    assert game.score_manager.score == 119
    assert game.score_manager.total_lines == 1


def test_combo_scoring(temp_manager: ProfileManager) -> None:
    scores = ScoreManager(temp_manager)
    scores.attach_profile("test")

    gained1 = scores.record_line_clear(1)
    gained2 = scores.record_line_clear(2)
    gained3 = scores.record_line_clear(0)

    assert gained1 == 100
    assert gained2 == 350
    assert gained3 == 0
    assert scores.score == 450
    assert scores.combo_streak == 0
