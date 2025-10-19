from pathlib import Path

import pytest

from tetris.profiles import ProfileManager


def test_profile_creation_and_persistence(tmp_path: Path) -> None:
    data_file = tmp_path / "profiles.json"
    manager = ProfileManager(data_file)

    profile = manager.create_profile("Alice")
    assert profile.name == "Alice"
    assert manager.get_active_profile().name == "Alice"

    manager.record_game("Alice", score=1200, lines=10)

    other = ProfileManager(data_file)
    loaded = other.get_profile("Alice")
    assert loaded is not None
    assert loaded.games_played == 1
    assert loaded.best_score == 1200

    top = other.top_scores()
    assert top and top[0]["score"] == 1200


def test_duplicate_profile_raises(tmp_path: Path) -> None:
    data_file = tmp_path / "profiles.json"
    manager = ProfileManager(data_file)
    manager.create_profile("Bob")

    with pytest.raises(ValueError):
        manager.create_profile("Bob")
