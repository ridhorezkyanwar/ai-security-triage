"""ASGI entry point: run with `uvicorn app:app --reload`."""

from triage.web import app

__all__ = ["app"]
