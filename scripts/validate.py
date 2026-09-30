#!/usr/bin/env python3
"""Validate this repository's portable skill package without network access."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


REQUIRED = (
    "SKILL.md", "README.md", "CONTRIBUTING.md", "LICENSE",
    "THIRD_PARTY_NOTICES.md", "agents/openai.yaml",
    "references/frameworks.md", "references/runtime-controls.md",
    "references/verification.md", "references/owasp-agentic-top-10.md",
    "assets/AGENTS-snippet.md", "assets/agent-security-record.md",
    "evals/README.md", ".github/workflows/validate.yml",
)
IGNORED = {".git", ".venv", "__pycache__", "node_modules"}
LINK = re.compile(r'\[[^\]]+\]\(([^\s)]+)(?:\s+"[^"\n]*")?\)')
MACHINE_PATH = re.compile(r"/(?:home|Users)/[^/\s]+|[A-Za-z]:\\Users\\[^\\\s]+")


@dataclass(frozen=True)
class Finding:
    code: str
    path: str
    message: str


def prose(text: str) -> str:
    """Remove fenced examples from the inline-link scan."""
    lines = []
    fence = None
    for line in text.splitlines():
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if match:
            marker = match.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            continue
        if fence is None:
            lines.append(line)
    return "\n".join(lines)


def validate(root: Path) -> list[Finding]:
    root = root.resolve()
    findings = []

    def report(code: str, path: Path, message: str) -> None:
        findings.append(Finding(code, str(path.relative_to(root)), message))

    for name in REQUIRED:
        path = root / name
        if not path.is_file():
            report("missing-file", path, "Required repository file is missing")

    documents = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in IGNORED for part in relative.parts):
            continue
        if relative.parts[:2] == ("evals", "artifacts"):
            continue
        if path.is_symlink():
            report("symlink", path, "Bundle real files so checkout contents are portable")
            continue
        if not path.is_file() or path.suffix not in {".md", ".yaml", ".yml"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeError, OSError) as error:
            report("unreadable", path, str(error))
            continue
        documents[relative.as_posix()] = text
        if MACHINE_PATH.search(text):
            report("machine-path", path, "Use a portable path or environment variable")
        if "\u2014" in text:
            report("punctuation", path, "Use a comma, colon, parentheses, or plain hyphen")
        if path.suffix != ".md":
            continue
        for match in LINK.finditer(prose(text)):
            raw = match.group(1)
            try:
                target = urlsplit(raw)
            except ValueError:
                report("invalid-link", path, f"Invalid link: {raw}")
                continue
            if target.scheme in {"http", "https", "mailto"}:
                continue
            if target.scheme or target.netloc or target.path.startswith("/"):
                report("nonportable-link", path, f"Use a relative bundled link: {raw}")
                continue
            if not target.path:
                continue
            destination = (path.parent / unquote(target.path)).resolve()
            if not destination.is_relative_to(root):
                report("link-escape", path, f"Bundled link leaves the repository: {raw}")
            elif not destination.exists():
                report("missing-link", path, f"Missing bundled link target: {raw}")

    skill = documents.get("SKILL.md", "")
    header = re.match(r"\A---\n(.*?)\n---(?:\n|$)", skill, re.DOTALL)
    metadata = {}
    if not header:
        report("frontmatter", root / "SKILL.md", "Expected YAML frontmatter at the start")
    else:
        for line in header.group(1).splitlines():
            match = re.fullmatch(r"([a-z][a-z_-]*):\s+(.+)", line)
            if not match:
                report("frontmatter", root / "SKILL.md", "Use simple single-line metadata fields")
                continue
            key, value = match.groups()
            if key in metadata:
                report("duplicate-field", root / "SKILL.md", f"Duplicate metadata: {key}")
            metadata[key] = value.strip().strip('"').strip("'")
        name = metadata.get("name", "")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
            report("skill-name", root / "SKILL.md", "Use a lowercase hyphenated name, at most 64 characters")
        description = metadata.get("description", "")
        if not description or len(description) > 1024 or "[TODO" in description:
            report("description", root / "SKILL.md", "Provide a finished description of at most 1024 characters")
        if not metadata.get("license"):
            report("license", root / "SKILL.md", "Identify the package licensing in metadata")

    coverage = documents.get("references/owasp-agentic-top-10.md", "")
    identifiers = Counter(re.findall(r"\*\*ASI(\d{2}):", coverage))
    if identifiers != Counter(f"{number:02d}" for number in range(1, 11)):
        report("coverage", root / "references/owasp-agentic-top-10.md", "Include each ASI01 through ASI10 row once")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    findings = validate(args.root)
    for finding in findings:
        print(f"{finding.path}: {finding.code}: {finding.message}")
    if findings:
        print(f"Repository validation failed: {len(findings)} finding(s).")
        return 1
    print("Repository metadata, local links, portability, and coverage rows passed.")
    print("This does not establish agent behavior or application security.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
