"""Convert model output into a cautious, explainable review recommendation."""

from __future__ import annotations

from typing import Any

from triage.categories import CATEGORY_DESCRIPTIONS, RECOMMENDATIONS


def build_triage_result(
    model_result: dict[str, Any],
    *,
    mode: str,
    review_confidence_threshold: float = 0.72,
    evidence_confidence_threshold: float = 0.65,
) -> dict[str, Any]:
    category = model_result["category"]
    evidence_quality = model_result["evidence_quality"]
    category_confidence = model_result.get("category_confidence")
    evidence_confidence = model_result.get("evidence_confidence")

    reasons: list[str] = []
    if category == "insufficient_evidence":
        reasons.append("The report was classified as lacking sufficient evidence.")
    if evidence_quality == "insufficient":
        reasons.append("The evidence-quality assessment is insufficient.")
    if evidence_quality == "partial":
        reasons.append("Some technical evidence is missing; confirm details manually.")
    if category_confidence is None or category_confidence < review_confidence_threshold:
        reasons.append(
            f"Category confidence is below the configured threshold ({review_confidence_threshold:.2f})."
        )
    if evidence_confidence is None or evidence_confidence < evidence_confidence_threshold:
        reasons.append(
            f"Evidence-quality confidence is below the configured threshold ({evidence_confidence_threshold:.2f})."
        )
    if mode == "demo":
        reasons.append("Demo mode uses local keyword heuristics, not a hosted AI model.")
    if mode == "groq":
        reasons.append("Groq confidence is not calibrated or reported; human review is required.")

    manual_review_required = bool(reasons)
    return {
        "mode": mode,
        "model": model_result["model"],
        "category": category,
        "category_label": CATEGORY_DESCRIPTIONS[category],
        "category_confidence": category_confidence,
        "category_probabilities": model_result.get("category_probabilities", {}),
        "evidence_quality": evidence_quality,
        "evidence_quality_label": evidence_quality.replace("_", " ").title(),
        "evidence_confidence": evidence_confidence,
        "decision": "manual_review_required" if manual_review_required else "triage_candidate",
        "manual_review_required": manual_review_required,
        "review_reasons": reasons,
        "recommendation": RECOMMENDATIONS[category],
        "usage": model_result.get("usage", {"input_tokens": 0, "output_tokens": 0}),
        "notice": (
            "This is a triage aid, not proof that a vulnerability exists or is exploitable. "
            "Do not auto-close reports or execute tests based only on this output."
        ),
        "category_reasoning": model_result.get("category_reasoning"),
        "evidence_reasoning": model_result.get("evidence_reasoning"),
        "thresholds": {
            "category_confidence": review_confidence_threshold,
            "evidence_confidence": evidence_confidence_threshold,
        },
    }
