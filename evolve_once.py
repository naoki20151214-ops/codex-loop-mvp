from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Iterable

from openai import OpenAI

REPO_ROOT = Path(__file__).resolve().parent
PROMPT_FILE = REPO_ROOT / "prompts" / "evolve.md"
LOG_FILE = REPO_ROOT / "evolve_log.md"
FORBIDDEN_PATHS = {".github/workflows/ci.yml"}


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=REPO_ROOT, text=True, capture_output=True, check=check)


def tracked_files() -> list[str]:
    result = run(["git", "ls-files"])
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def read_repo_state() -> str:
    chunks: list[str] = []
    for rel_path in tracked_files():
        path = REPO_ROOT / rel_path
        if not path.is_file() or path.suffix in {".png", ".jpg", ".jpeg", ".gif", ".lock"}:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if len(content) > 4000:
            content = content[:4000] + "\n...<truncated>...\n"
        chunks.append(f"### FILE: {rel_path}\n{content}")
    return "\n\n".join(chunks)


def extract_patch(text: str) -> str:
    match = re.search(r"```diff\n(.*?)```", text, flags=re.DOTALL)
    if match:
        return match.group(1).strip() + "\n"
    return text.strip() + "\n"


def changed_paths_from_patch(patch: str) -> set[str]:
    paths: set[str] = set()
    for line in patch.splitlines():
        if line.startswith("+++ b/"):
            paths.add(line.removeprefix("+++ b/").strip())
    return paths


def forbidden_touched(paths: Iterable[str]) -> set[str]:
    allowed = {
        p.strip() for p in os.getenv("ALLOW_FORBIDDEN_PATHS", "").split(",") if p.strip()
    }
    return {p for p in paths if p in FORBIDDEN_PATHS and p not in allowed}


def apply_patch(patch: str) -> None:
    with NamedTemporaryFile("w", delete=False, encoding="utf-8") as temp:
        temp.write(patch)
        temp_path = temp.name
    try:
        run(["git", "apply", "--check", temp_path])
        run(["git", "apply", temp_path])
    finally:
        Path(temp_path).unlink(missing_ok=True)


def run_pytest() -> tuple[bool, str]:
    result = subprocess.run(
        [sys.executable, "-m", "pytest"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    output = f"{result.stdout}\n{result.stderr}".strip()
    return result.returncode == 0, output


def request_patch(client: OpenAI, system_prompt: str, user_prompt: str) -> str:
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return extract_patch(response.output_text)


def append_log(iteration: str, paths: Iterable[str], test_ok: bool) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(
            f"- iteration: {iteration} | files: {', '.join(sorted(paths)) or 'none'} | "
            f"pytest: {'pass' if test_ok else 'fail'}\n"
        )


def main() -> int:
    if not PROMPT_FILE.exists():
        print(f"Missing prompt file: {PROMPT_FILE}", file=sys.stderr)
        return 1

    iteration = os.getenv("ITERATION", "local")
    rules = PROMPT_FILE.read_text(encoding="utf-8")
    repo_state = read_repo_state()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    system_prompt = "You are a careful software engineer. Return only valid unified diff patches."
    user_prompt = (
        f"Iteration: {iteration}\n\n"
        f"Follow these rules exactly:\n{rules}\n\n"
        f"Current repository state:\n{repo_state}\n"
    )

    patch = request_patch(client, system_prompt, user_prompt)
    paths = changed_paths_from_patch(patch)
    blocked = forbidden_touched(paths)
    if blocked:
        print(f"Patch rejected; forbidden paths touched: {sorted(blocked)}", file=sys.stderr)
        return 1

    try:
        apply_patch(patch)
    except subprocess.CalledProcessError as exc:
        print(f"Failed to apply initial patch:\n{exc.stderr}", file=sys.stderr)
        return 1

    test_ok, test_output = run_pytest()
    if not test_ok:
        retry_prompt = (
            "The previous patch caused tests to fail. Provide a minimal follow-up unified diff "
            "that fixes tests without reverting the intended improvement.\n\n"
            f"Pytest output:\n{test_output}\n"
        )
        retry_patch = request_patch(client, system_prompt, retry_prompt)
        retry_paths = changed_paths_from_patch(retry_patch)
        blocked_retry = forbidden_touched(retry_paths)
        if blocked_retry:
            print(f"Retry patch rejected; forbidden paths touched: {sorted(blocked_retry)}", file=sys.stderr)
            run(["git", "reset", "--hard", "HEAD"])
            return 1

        try:
            apply_patch(retry_patch)
        except subprocess.CalledProcessError as exc:
            print(f"Failed to apply retry patch:\n{exc.stderr}", file=sys.stderr)
            run(["git", "reset", "--hard", "HEAD"])
            return 1

        paths |= retry_paths
        test_ok, test_output = run_pytest()
        if not test_ok:
            print("Pytest still failing after retry; aborting.", file=sys.stderr)
            print(test_output, file=sys.stderr)
            run(["git", "reset", "--hard", "HEAD"])
            return 1

    append_log(iteration, paths, test_ok)
    print("evolve_once completed successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
