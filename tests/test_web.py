import pytest
from pathlib import Path

from fastapi.testclient import TestClient

from triage.web import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def default_local_test_environment(monkeypatch):
    # Tests opt into local mode unless a specific test checks the hosted secure default.
    monkeypatch.setenv("REQUIRE_AUTH", "false")
    monkeypatch.delenv("VERCEL", raising=False)


def test_health_does_not_expose_api_key(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-secret-do-not-return")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["groq_key_configured"] is True
    assert response.json()["template_ready"] is True
    assert "test-secret-do-not-return" not in response.text


def test_vercel_config_includes_templates_in_function_bundle():
    import json

    config = Path(__file__).resolve().parents[1] / "vercel.json"
    data = json.loads(config.read_text(encoding="utf-8"))
    assert data["functions"]["app.py"]["includeFiles"] == "templates/**"


def test_public_stylesheet_is_packaged_for_vercel_cdn():
    css = Path(__file__).resolve().parents[1] / "public" / "static" / "styles.css"
    assert css.is_file()
    assert ".topbar" in css.read_text(encoding="utf-8")


def test_local_static_route_serves_stylesheet():
    response = client.get("/static/styles.css")
    assert response.status_code == 200
    assert ".topbar" in response.text


def test_homepage_renders_groq_mode():
    response = client.get("/")
    assert response.status_code == 200
    assert "AI Security Triage Agent" in response.text
    assert "Groq cloud AI" in response.text
    assert "Ollama local AI" not in response.text
    assert "Jev API" not in response.text


def test_demo_api_works_without_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    response = client.post("/api/triage", json={
        "mode": "demo",
        "report": "Synthetic cross-site scripting report. Endpoint: /search. No confirmed proof yet.",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "demo"
    assert data["category"] == "xss"
    assert data["manual_review_required"] is True


def test_groq_mode_fails_clearly_without_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    response = client.post("/api/triage", json={
        "mode": "groq",
        "report": "Synthetic report text that is long enough for input validation.",
    })
    assert response.status_code == 400
    assert "GROQ_API_KEY" in response.json()["detail"]


def test_groq_api_error_is_returned_as_safe_502(monkeypatch):
    from triage.groq_client import GroqAPIError

    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    def fail_classify(self, report):
        raise GroqAPIError("Groq rate limit or quota reached (HTTP 429).")

    monkeypatch.setattr("triage.groq_client.GroqClient.classify", fail_classify)
    response = client.post("/api/triage", json={
        "mode": "groq",
        "report": "Synthetic report text that is long enough for input validation.",
    })
    assert response.status_code == 502
    assert "429" in response.json()["detail"]


def test_too_short_report_is_rejected():
    response = client.post("/api/triage", json={"mode": "demo", "report": "tiny"})
    assert response.status_code == 422


def test_auth_defaults_to_required_if_environment_is_missing(monkeypatch):
    monkeypatch.delenv("REQUIRE_AUTH", raising=False)
    monkeypatch.delenv("APP_ACCESS_PASSWORD", raising=False)
    response = client.get("/")
    assert response.status_code == 503
    assert "locked" in response.text.lower()


def test_required_auth_fails_closed_if_password_missing(monkeypatch):
    monkeypatch.setenv("REQUIRE_AUTH", "true")
    monkeypatch.delenv("APP_ACCESS_PASSWORD", raising=False)

    # Health checks remain reachable for hosting platforms, but app/API routes stay locked.
    assert client.get("/health").status_code == 200
    assert client.get("/").status_code == 503
    response = client.post("/api/triage", json={
        "mode": "demo",
        "report": "Synthetic report content long enough to pass request validation.",
    })
    assert response.status_code == 503


def test_optional_basic_auth_protects_ui_when_configured(monkeypatch):
    monkeypatch.setenv("APP_ACCESS_USERNAME", "analyst")
    monkeypatch.setenv("APP_ACCESS_PASSWORD", "test-password")
    assert client.get("/").status_code == 401
    response = client.get("/", auth=("analyst", "test-password"))
    assert response.status_code == 200
    assert client.get("/health").status_code == 200
    monkeypatch.delenv("APP_ACCESS_PASSWORD", raising=False)
    monkeypatch.delenv("APP_ACCESS_USERNAME", raising=False)
