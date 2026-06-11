#!/usr/bin/env python3
"""Run a small public onboarding smoke test.

This does not call external services. It verifies that the workspace bootstrap
script can create the expected public files and that the public route block uses
the current chat-first completion model.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_WORKSPACE_ITEMS = [
    "AGENTS.md",
    "CLAUDE.md",
    "memory.md",
    "coverage.md",
    "active-tasks.md",
    ".task-pulse",
    ".checkpoint",
    "coverage",
    "themes",
    "briefings",
    "user-templates",
    "user-skills",
]


def fail(message: str) -> None:
    print(f"[onboarding-smoke] ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def check_route_block() -> None:
    route_block = (ROOT / "setup" / "routes-block.template.md").read_text(encoding="utf-8")
    required = [
        "company-analysis",
        "industry-research",
        "company-comparison",
        "event-driven-opportunity",
        "当前会话输出完整 Markdown",
    ]
    for needle in required:
        if needle not in route_block:
            fail(f"route block missing {needle!r}")
    forbidden = ["ZZG", "ZZG1", "ZZG2", "ZZG3", "上传到 IMA", "必须上传"]
    for needle in forbidden:
        if needle in route_block:
            fail(f"route block contains private-edition text {needle!r}")


def run_bootstrap() -> None:
    bash = shutil.which("bash")
    if not bash:
        print("[onboarding-smoke] SKIP: bash not available; static route checks completed")
        return

    with tempfile.TemporaryDirectory(prefix="investor-harness-smoke-") as tmp:
        workspace = Path(tmp) / "demo-workspace"
        subprocess.run(
            [bash, str(ROOT / "setup" / "bootstrap.sh"), str(workspace)],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        missing = [item for item in EXPECTED_WORKSPACE_ITEMS if not (workspace / item).exists()]
        if missing:
            fail(f"bootstrap did not create expected workspace items: {missing}")


def main() -> int:
    check_route_block()
    run_bootstrap()
    print("[onboarding-smoke] OK: public onboarding smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
