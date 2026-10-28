# AI Security Triage Agent

A small, review-first prototype that classifies sanitized vulnerability reports into a controlled taxonomy, assesses whether their evidence is actionable, and recommends the next human-review step.

**Primary AI provider: Groq API.** The live AI mode uses Groq only. An offline rule-based demo remains available without any API key. Groq hosts inference remotely, so the model does not need to fit in your computer's RAM; report text is sent to Groq when you choose Groq mode.

> This is a triage aid, not a scanner, vulnerability verifier, bounty finder, or replacement for expert review. Outputs must not automatically close reports, run exploits, or authorize security actions.

## Features

- FastAPI backend and responsive browser UI.
- Groq chat-completions integration using structured JSON output.
- Default model `openai/gpt-oss-20b`, configurable through `GROQ_MODEL`.
- Server-side API key handling; the browser never receives `GROQ_API_KEY`.
- Offline, keyword-based demo that does not send data to a third party.
- Fixed category and evidence-quality taxonomies, response validation, safe provider errors, and manual-review routing.
- Synthetic test dataset and optional opt-in benchmark script.
- Docker and Render configuration, plus GitHub Actions tests.

## 1. Prerequisites

- Python 3.11 or later.
- A Groq account and an API key from the [Groq Console](https://console.groq.com/keys) for live AI mode.
- Internet access for Groq mode.

Groq documents a Free Plan with limits, and API quotas/rate limits vary by plan, model, and organization. The app does not assume unlimited usage or automatically buy credits/retry requests. Check your console and the current [rate-limit documentation](https://console.groq.com/docs/rate-limits) before using it. If a screen asks you to add payment details and you only want zero-cost usage, stop and use Demo mode until you confirm the terms. Free tier limits can return HTTP 429 instead of processing additional requests.

## 2. Install and run

### Windows

1. Extract the project ZIP.
2. Install Python 3.11+ if required.
3. Double-click `run-windows.bat`.
4. On first run, the script creates `.venv`, installs dependencies, and copies `.env.example` to `.env`.
5. Open `http://127.0.0.1:8000`.

### Linux, macOS, or Termux

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app:app --reload
```

Open `http://127.0.0.1:8000` in a browser.

## 3. Use offline demo mode

Choose **Rule-based demo — offline, not AI**, click **Load sample**, then **Analyze report**. The demo uses keyword heuristics to exercise the interface; it is not an AI prediction or a real vulnerability detector. This mode does not need an API key and sends no report to any external provider.

## 4. Configure Groq

1. Open the [Groq Console API Keys page](https://console.groq.com/keys) and create a key if your account allows it under your selected plan.
2. Open the project's `.env` file, then set:

   ```dotenv
   GROQ_API_KEY=put_your_own_key_here
   GROQ_MODEL=openai/gpt-oss-20b
   ```

3. Save `.env`, then restart the server. For Windows, stop the command window with `Ctrl+C` and run `run-windows.bat` again.
4. In the UI choose **Groq cloud AI**, load the synthetic sample, and click **Analyze report**.
5. If the key/model doesn't work, use `/api/models` after starting the app to list the models visible to the configured key. You can also check [Groq supported models](https://console.groq.com/docs/models).

The project uses `POST https://api.groq.com/openai/v1/chat/completions` and the documented strict structured-output format for `openai/gpt-oss-20b`. See the official [Groq API reference](https://console.groq.com/docs/api-reference) and [structured-output guide](https://console.groq.com/docs/structured-outputs). Models and endpoints can change; verify the current model list if requests stop working.

### API key safety

- Keep the key in `.env` or your hosting provider's server-side secret settings only.
- Never put `GROQ_API_KEY` in frontend JavaScript, screenshots, README examples, GitHub commits, or chats.
- `.env` is ignored by Git, but verify `git status` before committing.
- Do not paste real reports that include authentication tokens, cookies, private source code, personal data, confidential program details, or customer information. Groq mode sends report text to the provider.
- Free-tier use is limited, not infinite. Rate limiting is handled as a clear error; no automatic paid upgrade or retry is attempted.

## 5. Result interpretation

Groq returns a category, evidence-quality label, and brief explanation. It does **not** provide calibrated probabilities in this project. The UI intentionally shows no numeric confidence instead of inventing one. As a result, Groq classifications are routed for human review. A structured response guarantees response shape for supported models, not factual correctness.

## 6. Tests

Run all tests offline:

```bash
python -m pytest
```

Tests use fake HTTP responses and do not require a Groq key, send reports to Groq, or consume API usage. GitHub Actions runs the same suite on pushes and pull requests.

## 7. Optional synthetic benchmark (uses Groq API quota)

`tests/fixtures/triage_cases.json` contains 36 synthetic cases. Begin with a small batch and review your account's limits before evaluating more:

```bash
python scripts/evaluate.py --live --limit 5
```

To evaluate all bundled cases, run `python scripts/evaluate.py --live` only when you're comfortable consuming that API quota. Add `--delay 2` to space requests. The script writes JSON and CSV under `reports/`, which are ignored by Git. The dataset is a starter set, not an independently labeled or representative benchmark. Report actual measured results; do not claim accuracy before running it.

## 8. Deployment

A `Dockerfile` and `render.yaml` blueprint are included. Hosted templates set `REQUIRE_AUTH=true`; configure a strong, unique `APP_ACCESS_PASSWORD` and store `GROQ_API_KEY` only as a server-side secret. If authentication is required but the password is missing, all non-health routes fail closed with HTTP 503 rather than exposing the Groq-backed endpoint. The Docker image defaults to requiring authentication. Local development remains convenient because `run-windows.bat` and the documented Uvicorn command bind to localhost; `.env.example` sets `REQUIRE_AUTH=false` for that local-only use. Never bake keys into the image or repository. `/health` remains public for hosting health checks and reports whether a Groq key is configured, so do not treat it as a secret-bearing endpoint.

The shared HTTP Basic password is a light single-user gate, not multi-user authentication, and this app does not yet have persistent per-user rate limits. Do not expose a publicly accessible instance with an active API key until access protection and usage controls have been reviewed. Hosting free tiers, sleep behavior, build quotas, and provider terms may change; check the current provider dashboard. This project has **not** been deployed by this ZIP-generation task.

## 9. Security limitations

- Only assess systems for which you have permission.
- Model output can be mistaken or manipulated by prompt injection. Treat report text and model responses as untrusted.
- Do not close a report, run an exploit, access data, or perform a sensitive action based only on a model output.
- Thresholds are initial routing settings, not empirically calibrated.
- Before real team use, add per-user authentication, persistent request limits, audit logs that exclude sensitive report contents, a reviewed data-retention policy, and an evaluation set reviewed by human security analysts.

## License

MIT. See [`LICENSE`](LICENSE).
