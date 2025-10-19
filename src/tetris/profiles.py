"""Profile management and persistence helpers."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "profiles.json"


def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"


@dataclass
class Profile:
    name: str
    created_at: str
    last_played: Optional[str] = None
    games_played: int = 0
    best_score: int = 0

    def to_dict(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "created_at": self.created_at,
            "last_played": self.last_played,
            "games_played": self.games_played,
            "best_score": self.best_score,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "Profile":
        return cls(
            name=data["name"],
            created_at=data["created_at"],
            last_played=data.get("last_played"),
            games_played=int(data.get("games_played", 0)),
            best_score=int(data.get("best_score", 0)),
        )


class ProfileManager:
    """Handle creation, lookup and selection of profiles."""

    def __init__(self, data_file: Optional[Union[str, Path]] = None) -> None:
        if data_file is None:
            env_path = os.environ.get("TETRIS_DATA_FILE")
            data_file = Path(env_path) if env_path else DATA_FILE
        else:
            data_file = Path(data_file)
        self.data_file = data_file
        self._data = self._load()

    def _load(self) -> Dict[str, object]:
        if not self.data_file.exists():
            return {"active_profile": None, "profiles": {}, "scores": []}
        with self.data_file.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def save(self) -> None:
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        with self.data_file.open("w", encoding="utf-8") as fh:
            json.dump(self._data, fh, indent=2)

    def list_profiles(self) -> List[Profile]:
        return [Profile.from_dict(value) for value in self._data["profiles"].values()]

    def get_profile(self, name: str) -> Optional[Profile]:
        profile_data = self._data["profiles"].get(name)
        return Profile.from_dict(profile_data) if profile_data else None

    def create_profile(self, name: str) -> Profile:
        if name in self._data["profiles"]:
            raise ValueError(f"Le profil '{name}' existe déjà")
        profile = Profile(name=name, created_at=_now())
        self._data["profiles"][name] = profile.to_dict()
        self._data["active_profile"] = name
        self.save()
        return profile

    def set_active_profile(self, name: str) -> Profile:
        profile = self.get_profile(name)
        if not profile:
            raise ValueError(f"Profil inconnu: {name}")
        self._data["active_profile"] = name
        self.save()
        return profile

    def get_active_profile(self) -> Optional[Profile]:
        active_name = self._data.get("active_profile")
        if not active_name:
            return None
        return self.get_profile(active_name)

    def record_game(self, profile_name: str, score: int, lines: int) -> None:
        profile = self.get_profile(profile_name)
        if not profile:
            raise ValueError(f"Profil inconnu: {profile_name}")
        profile.games_played += 1
        profile.last_played = _now()
        if score > profile.best_score:
            profile.best_score = score
        self._data["profiles"][profile_name] = profile.to_dict()
        self._data.setdefault("scores", []).append(
            {
                "profile": profile_name,
                "score": score,
                "lines": lines,
                "played_at": profile.last_played,
            }
        )
        self.save()

    def top_scores(self, limit: int = 10) -> List[Dict[str, object]]:
        scores = list(self._data.get("scores", []))
        scores.sort(key=lambda item: item["score"], reverse=True)
        return scores[:limit]
