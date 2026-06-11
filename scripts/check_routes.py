#!/usr/bin/env python3
"""Validate public Investor Harness route and skill metadata.

The check is intentionally lightweight: it protects the public repository from
drifting back to private skill names, private upload requirements, or route
entries that point at missing skill directories.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

ROUTE_FILES = [
    ROOT / "setup" / "keyword-routes.md",
    ROOT / "setup" / "routes-block.template.md",
    ROOT / "ONBOARDING.md",
    ROOT / "README.md",
]

PUBLIC_CORE_SKILLS = {
    "company-analysis",
    "industry-research",
    "company-comparison",
    "event-driven-opportunity",
}

LEGACY_SKILL_NAMES = {"ZZG", "ZZG1", "ZZG2", "ZZG3"}

BLOCKED_PUBLIC_STRINGS = [
    "IMA MCP",
    "IMA 笔记本",
    "note_id",
    "Company Analysis`",
    "Industry Analysis`",
    "Comparison Analysis`",
    "Event Driven Analysis`",
    "上传到 IMA",
    "必须上传",
    "C:\\Users\\zzg1994115",
]


def fail(message: str) -> None:
    print(f"[route-check] ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def parse_manifest_skill_ids(manifest: str) -> set[str]:
    ids: set[str] = set()
    for match in re.finditer(r"^\s*-\s+id:\s+([A-Za-z0-9_.-]+)\s*$", manifest, re.M):
        ids.add(match.group(1))
    return ids


def parse_route_skill_ids(markdown: str) -> set[str]:
    ids: set[str] = set()
    for match in re.finditer(r"`([A-Za-z0-9_.-]+)`", markdown):
        token = match.group(1)
        if (ROOT / "skills" / token).is_dir():
            ids.add(token)
    return ids


def check_manifest() -> None:
    manifest = read(ROOT / "manifest.yaml")
    manifest_ids = parse_manifest_skill_ids(manifest)
    missing = PUBLIC_CORE_SKILLS - manifest_ids
    if missing:
        fail(f"manifest missing public core skills: {sorted(missing)}")

    for skill_id in manifest_ids:
        skill_dir = ROOT / "skills" / skill_id
        if not skill_dir.is_dir():
            fail(f"manifest skill has no directory: {skill_id}")
        if not (skill_dir / "SKILL.md").is_file():
            fail(f"manifest skill has no SKILL.md: {skill_id}")


def check_routes() -> None:
    manifest_ids = parse_manifest_skill_ids(read(ROOT / "manifest.yaml"))
    combined = "\n\n".join(read(path) for path in ROUTE_FILES)
    routed_ids = parse_route_skill_ids(combined)

    missing_public_routes = PUBLIC_CORE_SKILLS - routed_ids
    if missing_public_routes:
        fail(f"public core skills not routed: {sorted(missing_public_routes)}")

    unknown_routes = routed_ids - manifest_ids
    if unknown_routes:
        fail(f"routes reference skills not listed in manifest: {sorted(unknown_routes)}")

    for legacy in LEGACY_SKILL_NAMES:
        if re.search(rf"\b{re.escape(legacy)}\b", combined):
            fail(f"legacy private skill name still appears in public routes: {legacy}")


def check_public_sanitization() -> None:
    scanned_suffixes = {".md", ".yaml", ".yml", ".sh", ".py"}
    for path in ROOT.rglob("*"):
        if "scripts" in path.relative_to(ROOT).parts:
            continue
        if ".git" in path.parts or not path.is_file() or path.suffix not in scanned_suffixes:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for needle in BLOCKED_PUBLIC_STRINGS:
            if needle in text:
                fail(f"blocked public string {needle!r} found in {path.relative_to(ROOT)}")


def main() -> int:
    check_manifest()
    check_routes()
    check_public_sanitization()
    print("[route-check] OK: routes, manifest, and public sanitization checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
