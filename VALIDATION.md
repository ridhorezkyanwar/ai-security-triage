# Validation Record

## Scope

Validation includes local/CI tests and deployment metadata. No real Groq API request was sent, and no Groq key was used. The Vercel project `ai-security-triage` is linked to this repository; deployment `dpl_9ooJHhRx1PQv9CKSu8mDUZNwXVRd` reached `READY` for commit `9b7a76658066fc52bf67425d1d148ae4d0834d40`. The latest runtime-error summary reported no errors in the selected one-hour window. A direct authenticated HTTP smoke test was not completed, and `GROQ_API_KEY` is not configured.

## Automated checks

Run from the repository root:

```bash
python -m pytest
```

The test suite uses mocked HTTP responses to verify request shape, output validation, rate-limit/auth error handling, key secrecy in API responses, offline demo behavior, optional HTTP Basic protection, fail-closed behavior when hosted authentication is required but its password is missing, and the secure-by-default behavior when REQUIRE_AUTH is unset. The tests do not prove that the current Groq service, account, model access, or deployment will work live.

## Live validation still required by the user

1. Test `/health` from a browser or HTTP client.
2. Confirm the root route prompts for HTTP Basic authentication and use the configured app credentials.
3. Test Demo mode using a synthetic report.
4. Add your own Groq API key as a sensitive Vercel environment variable only if the account allows the intended free use; redeploy.
5. Confirm `/api/models` lists the selected model and run one synthetic report in Groq mode.
6. Optionally run a five-case synthetic benchmark only after checking rate limits.
7. Enable GitHub branch protection manually in [Settings → Rules](https://github.com/ridhorezkyanwar/ai-security-triage/settings/rules): require PRs and the `pytest` status check, and block force pushes/deletions.

## Limitations

- The bundled dataset contains 36 synthetic starter examples and is not a representative external benchmark.
- Groq classification outputs do not include calibrated probabilities in this app.
- Human review remains required.
- Cloud inference sends report content to Groq; use synthetic or sanitized reports only.
- Availability, terms, limits, and model identifiers can change. Check official Groq docs before production use.
