"""Application service that orchestrates demo mode and live Groq mode."""

from __future__ import annotations

from typing import Any

from triage.decision import build_triage_result
from triage.demo import classify_demo
from triage.groq_client import DEFAULT_GROQ_MODEL, GroqAPIError, GroqClient


class ConfigurationError(RuntimeError):
    """Required configuration is missing or invalid."""


def run_triage(
    report: str,
    *,
    mode: str = "demo",
    api_key: str | None = None,
    model: str = DEFAULT_GROQ_MODEL,
    review_confidence_threshold: float = 0.72,
    evidence_confidence_threshold: float = 0.65,
) -> dict[str, Any]:
    cleaned_report = report.strip()
    if not cleaned_report:
        raise ValueError("Report text cannot be empty.")
    if mode == "demo":
        model_result = classify_demo(cleaned_report)
    elif mode == "groq":
        if not api_key or not api_key.strip():
            raise ConfigurationError(
                "Groq mode requires GROQ_API_KEY. Create a key in the Groq console and store it in your local .env file."
            )
        model_result = GroqClient(api_key=api_key, model=model).classify(cleaned_report)
    else:
        raise ValueError("Mode must be one of: demo, groq.")

    result = build_triage_result(
        model_result,
        mode=mode,
        review_confidence_threshold=review_confidence_threshold,
        evidence_confidence_threshold=evidence_confidence_threshold,
    )
    if mode == "demo":
        result["demo_note"] = model_result["demo_note"]
    if mode == "groq":
        result["category_reasoning"] = model_result.get("category_reasoning")
        result["evidence_reasoning"] = model_result.get("evidence_reasoning")
    return result
