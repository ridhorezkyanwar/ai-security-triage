"""FastAPI web interface. Groq API credentials stay on the server, never in the browser."""

from __future__ import annotations

import base64
import hmac
import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from starlette.requests import Request

from triage.groq_client import DEFAULT_GROQ_MODEL, GroqAPIError, GroqClient
from triage.service import ConfigurationError, run_triage

load_dotenv()
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = PROJECT_ROOT / "templates"
STATIC_DIR = PROJECT_ROOT / "static"


class TriageRequest(BaseModel):
    report: str = Field(min_length=20, max_length=20_000)
    mode: Literal["demo", "groq"] = "demo"


class TriageResponse(BaseModel):
    mode: str
    model: str
    category: str
    category_label: str
    category_confidence: float | None
    category_probabilities: dict[str, float]
    evidence_quality: str
    evidence_quality_label: str
    evidence_confidence: float | None
    decision: str
    manual_review_required: bool
    review_reasons: list[str]
    recommendation: str
    usage: dict[str, int]
    notice: str
    thresholds: dict[str, float]
    demo_note: str | None = None
    category_reasoning: str | None = None
    evidence_reasoning: str | None = None


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Security Triage Agent",
        version="1.1.0",
        description=(
            "A cautious vulnerability-report triage prototype with offline demo mode "
            "and optional Groq-hosted model inference."
        ),
    )
    templates = Jinja2Templates(directory=str(TEMPLATE_DIR))
    # Vercel serves files in public/ via its CDN. Keep the Starlette mount for
    # local development; avoid relying on dynamic StaticFiles discovery at build time.
    if STATIC_DIR.exists() and not os.getenv("VERCEL"):
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.middleware("http")
    async def optional_basic_auth(request: Request, call_next):
        """A lightweight shared-password gate; not a full multi-user account system."""
        if request.url.path == "/health":
            return await call_next(request)

        # Secure by default on hosted platforms. Local development explicitly opts out via .env.example.
        require_auth = os.getenv("REQUIRE_AUTH", "true").strip().lower() in {"1", "true", "yes", "on"}
        configured_password = os.getenv("APP_ACCESS_PASSWORD", "").strip()
        if not configured_password:
            if require_auth:
                return PlainTextResponse(
                    "Application access is locked because APP_ACCESS_PASSWORD is not configured.",
                    status_code=503,
                )
            return await call_next(request)

        username = os.getenv("APP_ACCESS_USERNAME", "analyst")
        authorization = request.headers.get("authorization", "")
        try:
            scheme, encoded = authorization.split(" ", 1)
            if scheme.lower() != "basic":
                raise ValueError
            decoded = base64.b64decode(encoded, validate=True).decode("utf-8")
            supplied_username, supplied_password = decoded.split(":", 1)
        except (ValueError, UnicodeDecodeError):
            supplied_username, supplied_password = "", ""

        valid_user = hmac.compare_digest(supplied_username.encode("utf-8"), username.encode("utf-8"))
        valid_password = hmac.compare_digest(supplied_password.encode("utf-8"), configured_password.encode("utf-8"))
        if not (valid_user and valid_password):
            return PlainTextResponse(
                "Authentication required. Configure valid app access credentials.",
                status_code=401,
                headers={"WWW-Authenticate": 'Basic realm="AI Security Triage", charset="UTF-8"'},
            )
        return await call_next(request)

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def home(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "default_model": os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL),
                "max_report_chars": 20_000,
            },
        )

    @app.get("/health")
    async def health() -> dict[str, str | bool]:
        return {
            "status": "ok",
            "service": "ai-security-triage",
            "groq_key_configured": bool(os.getenv("GROQ_API_KEY", "").strip()),
        }

    @app.get("/api/models")
    async def models() -> dict[str, object]:
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            raise HTTPException(
                status_code=400,
                detail="Add GROQ_API_KEY to your .env file, then restart the app.",
            )
        try:
            result = GroqClient(
                api_key=api_key,
                model=os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL),
            ).list_models()
            return {"models": result}
        except GroqAPIError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    @app.post("/api/triage", response_model=TriageResponse)
    async def triage(request: TriageRequest) -> dict[str, object]:
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        model = os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL).strip() or DEFAULT_GROQ_MODEL
        try:
            return run_triage(
                request.report,
                mode=request.mode,
                api_key=api_key,
                model=model,
                review_confidence_threshold=_read_threshold("REVIEW_CONFIDENCE_THRESHOLD", 0.72),
                evidence_confidence_threshold=_read_threshold("EVIDENCE_CONFIDENCE_THRESHOLD", 0.65),
            )
        except ConfigurationError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except GroqAPIError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    return app


def _read_threshold(name: str, default: float) -> float:
    raw = os.getenv(name, str(default))
    try:
        value = float(raw)
    except ValueError:
        return default
    if not 0.0 <= value <= 1.0:
        return default
    return value


app = create_app()
