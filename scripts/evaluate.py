"""Evaluate Groq classifications on synthetic examples; live calls require --live.

Start with: python scripts/evaluate.py --live --limit 5
This sends synthetic report text to Groq and consumes the account's API quota.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from triage.groq_client import DEFAULT_GROQ_MODEL, GroqAPIError, GroqClient  # noqa: E402

CASES_PATH = ROOT / "tests" / "fixtures" / "triage_cases.json"
REPORTS_DIR = ROOT / "reports"


def score_dimension(rows: list[dict[str, Any]], expected_key: str, predicted_key: str) -> dict[str, Any]:
    labels = sorted({str(row[expected_key]) for row in rows} | {str(row[predicted_key]) for row in rows})
    confusion: dict[str, dict[str, int]] = {label: {col: 0 for col in labels} for label in labels}
    for row in rows:
        expected = str(row[expected_key])
        predicted = str(row[predicted_key])
        confusion.setdefault(expected, {col: 0 for col in labels})
        confusion[expected][predicted] = confusion[expected].get(predicted, 0) + 1

    per_class = {}
    for label in labels:
        tp = confusion.get(label, {}).get(label, 0)
        fp = sum(confusion.get(other, {}).get(label, 0) for other in labels if other != label)
        fn = sum(confusion.get(label, {}).get(other, 0) for other in labels if other != label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        support = sum(confusion.get(label, {}).values())
        per_class[label] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "support": support,
        }

    correct = sum(str(row[expected_key]) == str(row[predicted_key]) for row in rows)
    return {
        "accuracy": round(correct / len(rows), 4) if rows else None,
        "correct": correct,
        "total": len(rows),
        "per_class": per_class,
        "confusion_matrix": confusion,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate Groq classifications against synthetic labels.")
    parser.add_argument("--live", action="store_true", help="Confirm live Groq API requests may be sent.")
    parser.add_argument("--limit", type=int, default=0, help="Only evaluate first N cases (0 = all 36).")
    parser.add_argument("--delay", type=float, default=1.0, help="Seconds between calls, default 1.0 to reduce bursts.")
    args = parser.parse_args()

    if not args.live:
        parser.error("No API calls were made. Add --live to explicitly enable live Groq requests.")
    if args.limit < 0 or args.delay < 0:
        parser.error("--limit and --delay must be non-negative.")

    load_dotenv(ROOT / ".env")
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        print("ERROR: GROQ_API_KEY is missing. Add it to .env first.", file=sys.stderr)
        return 2

    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    if args.limit:
        cases = cases[:args.limit]
    if not cases:
        print("ERROR: no cases selected", file=sys.stderr)
        return 2

    model = os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL).strip() or DEFAULT_GROQ_MODEL
    client = GroqClient(api_key, model=model)
    rows = []
    for index, case in enumerate(cases, 1):
        print(f"[{index}/{len(cases)}] {case['id']} ...", flush=True)
        try:
            result = client.classify(case["report"])
            rows.append({
                "id": case["id"],
                "expected_category": case["expected_category"],
                "predicted_category": result["category"],
                "expected_evidence_quality": case["expected_evidence_quality"],
                "predicted_evidence_quality": result["evidence_quality"],
                "category_confidence": "",
                "evidence_confidence": "",
                "model": result["model"],
                "input_tokens": result["usage"]["input_tokens"],
                "output_tokens": result["usage"]["output_tokens"],
            })
        except GroqAPIError as exc:
            print(f"ERROR: {case['id']}: {exc}", file=sys.stderr)
            return 1
        if args.delay and index < len(cases):
            time.sleep(args.delay)

    category_metrics = score_dimension(rows, "expected_category", "predicted_category")
    evidence_metrics = score_dimension(rows, "expected_evidence_quality", "predicted_evidence_quality")
    total_input = sum(row["input_tokens"] for row in rows)
    total_output = sum(row["output_tokens"] for row in rows)
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "note": (
            "Synthetic starter benchmark, not a representative external benchmark or a guarantee of real-world performance. "
            "Groq usage limits apply; model confidence is not reported or inferred."
        ),
        "model": rows[0]["model"] if rows else None,
        "case_count": len(rows),
        "category": category_metrics,
        "evidence_quality": evidence_metrics,
        "usage": {"input_tokens": total_input, "output_tokens": total_output},
        "cases": rows,
    }

    REPORTS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = REPORTS_DIR / f"benchmark-{stamp}.json"
    csv_path = REPORTS_DIR / f"benchmark-{stamp}.csv"
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print("\nRESULTS (synthetic dataset; not a generalization guarantee)")
    print(f"Cases: {len(rows)}")
    print(f"Category accuracy: {category_metrics['accuracy']}")
    print(f"Evidence-quality accuracy: {evidence_metrics['accuracy']}")
    print(f"Token usage: {total_input} input, {total_output} output")
    print(f"Saved JSON: {json_path.relative_to(ROOT)}")
    print(f"Saved CSV:  {csv_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
