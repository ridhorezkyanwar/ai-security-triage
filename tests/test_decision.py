from triage.decision import build_triage_result


def test_low_confidence_routes_to_manual_review():
    result = build_triage_result({
        "model": "test-model",
        "category": "xss",
        "category_confidence": 0.40,
        "category_probabilities": {"xss": 0.40, "other": 0.35, "insufficient_evidence": 0.25},
        "evidence_quality": "actionable",
        "evidence_confidence": 0.90,
        "usage": {"input_tokens": 10, "output_tokens": 5},
    }, mode="test-model")
    assert result["manual_review_required"] is True
    assert result["decision"] == "manual_review_required"
    assert any("below the configured threshold" in reason for reason in result["review_reasons"])


def test_high_confidence_still_does_not_claim_vulnerability_is_proven():
    result = build_triage_result({
        "model": "test-model",
        "category": "xss",
        "category_confidence": 0.95,
        "category_probabilities": {"xss": 0.95, "other": 0.05},
        "evidence_quality": "actionable",
        "evidence_confidence": 0.95,
        "usage": {"input_tokens": 10, "output_tokens": 5},
    }, mode="test-model")
    assert result["manual_review_required"] is False
    assert "not proof" in result["notice"]
    assert "proof" not in result["decision"]


def test_missing_confidence_is_not_misreported_as_below_threshold():
    result = build_triage_result({
        "model": "openai/gpt-oss-120b",
        "category": "insufficient_evidence",
        "category_confidence": None,
        "category_probabilities": {},
        "evidence_quality": "insufficient",
        "evidence_confidence": None,
        "usage": {"input_tokens": 824, "output_tokens": 343},
    }, mode="groq")

    assert result["manual_review_required"] is True
    assert result["decision"] == "manual_review_required"
    assert result["category_confidence"] is None
    assert result["evidence_confidence"] is None
    assert any("Category confidence was not provided" in reason for reason in result["review_reasons"])
    assert any("Evidence-quality confidence was not provided" in reason for reason in result["review_reasons"])
    assert not any("is below the configured threshold" in reason for reason in result["review_reasons"])
