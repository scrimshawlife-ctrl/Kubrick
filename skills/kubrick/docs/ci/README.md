# CI hardening (pending `workflow` OAuth scope)

GitHub OAuth tokens without the `workflow` scope cannot push commits that
modify `.github/workflows/*`. The hardened Hermes eval workflow lives here
until a maintainer refreshes auth:

```bash
gh auth refresh -s workflow
cp docs/ci/hermes-evals.hardened.yml .github/workflows/hermes-evals.yml
git commit -am "ci: harden Hermes Skill Evals gates"
git push
```

Hardening adds stdlib surface/io tests, `requirements-ci.txt` installs,
hub-sync checks, and a `dev-static` ruff/mypy/pytest job.
