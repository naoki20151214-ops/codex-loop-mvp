# Codex Loop Evolve Prompt

You are improving a small Python repository in one safe, reviewable step.

## Hard rules
1. Make exactly **ONE small improvement** in this iteration.
2. Update or add tests that validate the specific change.
3. Keep changes minimal and avoid large refactors.
4. Do not add any new dependencies beyond those already present.
5. Ensure `pytest` passes after the change.
6. Output only a **unified diff patch** that can be applied with `git apply`.

## Guidance
- Prefer tiny quality improvements (bug fix, naming clarity, small utility, docs/tests alignment).
- Touch as few files as possible.
- Keep code style and structure consistent with the existing project.
