from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app


def create_test_client(tmp_path: Path):
    data_file = tmp_path / "profiles.json"
    app = create_app(data_file=data_file)
    return app.test_client()


def test_healthcheck(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.data == b"ok"


def test_profile_and_score_api(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)

    response = client.get("/api/profiles")
    assert response.status_code == 200
    assert response.get_json() == []

    response = client.post("/api/profiles", json={"name": "Alice"})
    assert response.status_code == 201
    assert response.get_json()["name"] == "Alice"

    duplicate = client.post("/api/profiles", json={"name": "Alice"})
    assert duplicate.status_code == 409

    missing_profile = client.post(
        "/api/scores",
        json={"profile": "Bob", "score": 10, "lines": 1},
    )
    assert missing_profile.status_code == 404

    response = client.post(
        "/api/scores",
        json={"profile": "Alice", "score": 1234, "lines": 4},
    )
    assert response.status_code == 201

    scores = client.get("/api/scores")
    assert scores.status_code == 200
    payload = scores.get_json()
    assert payload[0]["profile"] == "Alice"
    assert payload[0]["score"] == 1234

    html = client.get("/")
    assert html.status_code == 200
    assert "Alice" in html.get_data(as_text=True)
    assert "1234" in html.get_data(as_text=True)
