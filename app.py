"""WSGI-compatible web interface for the Tetris project."""
from __future__ import annotations

import json
from http import HTTPStatus
from io import BytesIO
from pathlib import Path
from textwrap import dedent
from typing import Callable, Iterable, List, Optional, Tuple, Union

from src.tetris.profiles import ProfileManager

Headers = List[Tuple[str, str]]
Body = bytes


class HTTPError(Exception):
    """Internal exception to propagate HTTP errors through the router."""

    def __init__(self, status: HTTPStatus, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message

    @property
    def body(self) -> bytes:
        payload = {"error": self.message, "status": self.status.value}
        return json.dumps(payload).encode("utf-8")

    @property
    def headers(self) -> Headers:
        return [("Content-Type", "application/json; charset=utf-8")]


class Response:
    """Simple response object used by the test client."""

    def __init__(self, status: int, headers: Headers, body: Body) -> None:
        self.status_code = status
        self.headers = {key.lower(): value for key, value in headers}
        self.data = body

    def get_data(self, as_text: bool = False) -> Union[str, bytes]:
        return self.data.decode("utf-8") if as_text else self.data

    def get_json(self) -> object:
        return json.loads(self.data.decode("utf-8"))


class TestClient:
    """WSGI test client with a Flask-like API for unit tests."""

    def __init__(self, app: "TetrisWSGIApp") -> None:
        self.app = app

    def open(self, path: str, method: str = "GET", json_payload: Optional[dict] = None) -> Response:
        body = b""
        headers: Headers = []
        if json_payload is not None:
            body = json.dumps(json_payload).encode("utf-8")
            headers.append(("Content-Type", "application/json"))

        environ = {
            "REQUEST_METHOD": method,
            "PATH_INFO": path,
            "SERVER_NAME": "localhost",
            "SERVER_PORT": "80",
            "SERVER_PROTOCOL": "HTTP/1.1",
            "wsgi.version": (1, 0),
            "wsgi.url_scheme": "http",
            "wsgi.input": BytesIO(body),
            "wsgi.errors": BytesIO(),
            "wsgi.multiprocess": False,
            "wsgi.multithread": False,
            "wsgi.run_once": False,
            "CONTENT_LENGTH": str(len(body)),
        }
        for key, value in headers:
            environ[f"HTTP_{key.upper().replace('-', '_')}"] = value
            if key.lower() == "content-type":
                environ["CONTENT_TYPE"] = value

        status: str = ""
        response_headers: Headers = []

        def start_response(status_line: str, resp_headers: Headers) -> None:
            nonlocal status, response_headers
            status = status_line
            response_headers = resp_headers

        result = b"".join(self.app(environ, start_response))
        status_code = int(status.split(" ")[0]) if status else 500
        return Response(status_code, response_headers, result)

    def get(self, path: str) -> Response:
        return self.open(path, "GET")

    def post(self, path: str, json: Optional[dict] = None) -> Response:
        return self.open(path, "POST", json_payload=json)


class TetrisWSGIApp:
    """Minimal WSGI application serving the Tetris dashboard and API."""

    def __init__(self, data_file: Optional[Union[str, Path]] = None) -> None:
        self.data_file = data_file

    # -- Helper utilities -------------------------------------------------
    def _manager(self) -> ProfileManager:
        return ProfileManager(data_file=self.data_file)

    def _json_body(self, environ: dict) -> dict:
        try:
            length = int(environ.get("CONTENT_LENGTH") or 0)
        except ValueError:
            length = 0
        raw = environ.get("wsgi.input")
        body = raw.read(length) if length and raw else b""
        if not body:
            return {}
        try:
            return json.loads(body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise HTTPError(HTTPStatus.BAD_REQUEST, f"JSON invalide: {exc}") from exc

    # -- Response builders ------------------------------------------------
    @staticmethod
    def _response(body: str | bytes, status: HTTPStatus, headers: Optional[Headers] = None) -> Tuple[HTTPStatus, Headers, Body]:
        payload = body.encode("utf-8") if isinstance(body, str) else body
        base_headers: Headers = [("Content-Length", str(len(payload)))]
        if headers:
            base_headers.extend(headers)
        return status, base_headers, payload

    def _json_response(self, payload: object, status: HTTPStatus = HTTPStatus.OK) -> Tuple[HTTPStatus, Headers, Body]:
        body = json.dumps(payload)
        headers = [("Content-Type", "application/json; charset=utf-8"), ("Cache-Control", "no-store")]
        return self._response(body, status, headers)

    def _html_response(self, body: str, status: HTTPStatus = HTTPStatus.OK) -> Tuple[HTTPStatus, Headers, Body]:
        headers = [("Content-Type", "text/html; charset=utf-8")]
        return self._response(body, status, headers)

    def _text_response(self, body: str, status: HTTPStatus = HTTPStatus.OK) -> Tuple[HTTPStatus, Headers, Body]:
        headers = [("Content-Type", "text/plain; charset=utf-8")]
        return self._response(body, status, headers)

    # -- Route handlers ---------------------------------------------------
    def healthcheck(self) -> Tuple[HTTPStatus, Headers, Body]:
        return self._text_response("ok", HTTPStatus.OK)

    def index(self) -> Tuple[HTTPStatus, Headers, Body]:
        manager = self._manager()
        profiles = manager.list_profiles()
        scores = manager.top_scores(limit=20)

        def render_scores() -> str:
            if not scores:
                return "<p class=\"empty\">Aucun score enregistré pour le moment.</p>"
            rows = []
            for idx, entry in enumerate(scores, start=1):
                rows.append(
                    "<tr>"
                    f"<td>{idx}</td>"
                    f"<td>{entry.get('profile', '?')}</td>"
                    f"<td>{entry.get('score', 0)}</td>"
                    f"<td>{entry.get('lines', 0)}</td>"
                    f"<td>{entry.get('played_at', '-') or '-'}</td>"
                    "</tr>"
                )
            rows_html = "\n".join(rows)
            return dedent(
                f"""
                <table>
                  <thead>
                    <tr><th>#</th><th>Profil</th><th>Score</th><th>Lignes</th><th>Joué le</th></tr>
                  </thead>
                  <tbody>
                    {rows_html}
                  </tbody>
                </table>
                """
            )

        def render_profiles() -> str:
            if not profiles:
                return "<p class=\"empty\">Aucun profil créé pour le moment.</p>"
            rows = []
            for profile in profiles:
                rows.append(
                    "<tr>"
                    f"<td>{profile.name}</td>"
                    f"<td>{profile.best_score}</td>"
                    f"<td>{profile.games_played}</td>"
                    f"<td>{profile.last_played or '-'}</td>"
                    "</tr>"
                )
            rows_html = "\n".join(rows)
            return dedent(
                f"""
                <table>
                  <thead>
                    <tr><th>Nom</th><th>Meilleur score</th><th>Parties</th><th>Dernière partie</th></tr>
                  </thead>
                  <tbody>
                    {rows_html}
                  </tbody>
                </table>
                """
            )

        html = dedent(
            f"""
            <!doctype html>
            <html lang=\"fr\">
              <head>
                <meta charset=\"utf-8\" />
                <title>Tetris - Tableau de bord</title>
                <style>
                  body {{ font-family: Arial, sans-serif; margin: 2rem; }}
                  h1, h2 {{ color: #1b1464; }}
                  table {{ border-collapse: collapse; width: 100%; max-width: 600px; }}
                  th, td {{ border: 1px solid #ddd; padding: 0.5rem; text-align: left; }}
                  th {{ background: #f2f2f2; }}
                  .empty {{ font-style: italic; color: #666; }}
                  .container {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem; }}
                  footer {{ margin-top: 3rem; font-size: 0.8rem; color: #666; }}
                </style>
              </head>
              <body>
                <h1>Tetris - Tableau de bord</h1>
                <p>Interface web prête pour Hostinger. Utilisez les API pour créer des profils et publier des scores.</p>
                <div class=\"container\">
                  <section>
                    <h2>Meilleurs scores</h2>
                    {render_scores()}
                  </section>
                  <section>
                    <h2>Profils</h2>
                    {render_profiles()}
                  </section>
                </div>
                <footer>
                  <p>Endpoints disponibles : <code>GET /api/profiles</code>, <code>POST /api/profiles</code>, <code>GET /api/scores</code>, <code>POST /api/scores</code>, <code>GET /healthz</code>.</p>
                </footer>
              </body>
            </html>
            """
        ).strip()
        return self._html_response(html, HTTPStatus.OK)

    def list_profiles(self) -> Tuple[HTTPStatus, Headers, Body]:
        manager = self._manager()
        payload = [profile.to_dict() for profile in manager.list_profiles()]
        return self._json_response(payload)

    def create_profile(self, environ: dict) -> Tuple[HTTPStatus, Headers, Body]:
        payload = self._json_body(environ)
        name = payload.get("name")
        if not isinstance(name, str) or not name.strip():
            raise HTTPError(HTTPStatus.BAD_REQUEST, "Le champ 'name' est requis.")
        manager = self._manager()
        try:
            profile = manager.create_profile(name.strip())
        except ValueError as exc:
            raise HTTPError(HTTPStatus.CONFLICT, str(exc)) from exc
        return self._json_response(profile.to_dict(), HTTPStatus.CREATED)

    def list_scores(self) -> Tuple[HTTPStatus, Headers, Body]:
        manager = self._manager()
        payload = manager.top_scores(limit=50)
        return self._json_response(payload)

    def create_score(self, environ: dict) -> Tuple[HTTPStatus, Headers, Body]:
        payload = self._json_body(environ)
        profile = payload.get("profile")
        score = payload.get("score")
        lines = payload.get("lines", 0)
        if not isinstance(profile, str) or not profile.strip():
            raise HTTPError(HTTPStatus.BAD_REQUEST, "Le champ 'profile' est requis.")
        try:
            score_value = int(score)
            lines_value = int(lines)
        except (TypeError, ValueError) as exc:
            raise HTTPError(HTTPStatus.BAD_REQUEST, "Les champs 'score' et 'lines' doivent être numériques.") from exc
        manager = self._manager()
        try:
            manager.record_game(profile.strip(), score_value, lines_value)
        except ValueError as exc:
            raise HTTPError(HTTPStatus.NOT_FOUND, str(exc)) from exc
        payload = {"profile": profile.strip(), "score": score_value, "lines": lines_value}
        return self._json_response(payload, HTTPStatus.CREATED)

    # -- WSGI interface ---------------------------------------------------
    def __call__(self, environ: dict, start_response: Callable) -> Iterable[bytes]:
        method = environ.get("REQUEST_METHOD", "GET").upper()
        path = environ.get("PATH_INFO", "") or "/"

        try:
            if method == "GET" and path == "/healthz":
                status, headers, body = self.healthcheck()
            elif method == "GET" and path == "/":
                status, headers, body = self.index()
            elif method == "GET" and path == "/api/profiles":
                status, headers, body = self.list_profiles()
            elif method == "POST" and path == "/api/profiles":
                status, headers, body = self.create_profile(environ)
            elif method == "GET" and path == "/api/scores":
                status, headers, body = self.list_scores()
            elif method == "POST" and path == "/api/scores":
                status, headers, body = self.create_score(environ)
            else:
                raise HTTPError(HTTPStatus.NOT_FOUND, "Ressource introuvable")
        except HTTPError as exc:
            status, headers, body = self._response(
                exc.body, exc.status, list(exc.headers)
            )

        status_line = f"{status.value} {status.phrase}"
        start_response(status_line, headers)
        return [body]

    def test_client(self) -> TestClient:
        return TestClient(self)


def create_app(data_file: Optional[Union[str, Path]] = None) -> TetrisWSGIApp:
    """Factory returning the WSGI application used both in production and tests."""

    return TetrisWSGIApp(data_file=data_file)


# Default application for WSGI servers such as Passenger on Hostinger.
app = create_app()


__all__ = ["create_app", "app", "TetrisWSGIApp", "TestClient", "Response"]
