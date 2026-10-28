# Validation Record

## Scope

Validation includes GitHub Actions tests and direct fetch checks of Vercel routes. No live Groq inference has been run. The `GROQ_API_KEY` environment variable is configured as a Vercel sensitive secret; its value was not printed. The latest code on `main` includes `vercel.json` with `templates/**`, explicit Python dependencies, and CSS served from `public/static/styles.css`. The canonical URL `https://ai-security-triage.vercel.app/health` returned HTTP 200 with `template_ready: true`; `/static/styles.css` also returned HTTP 200. The older hash-specific URL supplied earlier returned HTTP 500 because it points to a previous deployment. An unauthenticated fetch cannot complete the app's HTTP Basic Auth flow; direct login and homepage render remain to be checked in a browser.

## Automated checks

Run from the repository root:

```bash
python -m pytest
```

The test suite uses mocked HTTP responses to verify request shape, output validation, rate-limit/auth error handling, key secrecy in API responses, offline demo behavior, optional HTTP Basic protection, fail-closed behavior when hosted authentication is required but its password is missing, and the secure-by-default behavior when REQUIRE_AUTH is unset. The tests do not prove that the current Groq service, account, model access, or deployment will work live.

## Live validation still required by the user

1. Open the canonical deployment alias `https://ai-security-triage.vercel.app`, not a stale hash-specific deployment URL.
2. Confirm the root route prompts for HTTP Basic authentication and use the configured app credentials.
3. Test Demo mode using a synthetic report; the CSS file is now published under `public/static/styles.css`.
4. Confirm `/health` from a browser or HTTP client.
5. Confirm `/api/models` lists the selected model and run one synthetic report in Groq mode. This is still pending.
6. Optionally run a five-case synthetic benchmark only after checking rate limits.
7. Enable GitHub branch protection manually in [Settings → Rules](https://github.com/ridhorezkyanwar/ai-security-triage/settings/rules): require PRs and the `pytest` status check, and block force pushes/deletions. The connected GitHub integration cannot write rulesets in this session.

## Limitations

- The bundled dataset contains 36 synthetic starter examples and is not a representative external benchmark.
- Groq classification outputs do not include calibrated probabilities in this app.
- Human review remains required.
- Cloud inference sends report content to Groq; use synthetic or sanitized reports only.
- Availability, terms, limits, and model identifiers can change. Check official Groq docs before production use.
