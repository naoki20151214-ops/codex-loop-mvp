# codex-loop-mvp

Minimal MVP for a CI-tested Python project with a GitHub Actions-driven evolve loop.

## How to run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
pytest
```

## How to evolve 20 times

1. Add `OPENAI_API_KEY` as a repository secret in GitHub.
2. Open **Actions** → **Evolve 20** → **Run workflow**.
3. Keep default `iterations=20` (or choose up to 20).
4. The workflow runs `evolve_once.py` sequentially. Each successful iteration pushes a branch and opens one PR targeting `main`.
5. If an iteration makes no file changes, that iteration skips PR creation.

## Workflows

- `CI`: runs `pytest` on every push and pull request.
- `Evolve 20`: manual workflow that automates one small AI-driven change per iteration.
