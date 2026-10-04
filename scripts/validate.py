#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the repository and its installable skill bundle without network access.

Standard library only, Python 3.10 or newer. The checks cover the repository
layout, Agent Skills frontmatter, the control catalog and its ledger, the NIST
and AIUC-1 identifier registries, the generated catalog views, the counts and
lists that prose restates from the catalog, Markdown links and anchors, OWASP
ASI identifiers and titles, workflow hygiene, and portability rules for every
text file. Passing does not establish agent behavior or application security.

Usage:
  python3 scripts/validate.py [ROOT]            validate the repository
  python3 scripts/validate.py --stage DIR       copy the bundle to DIR (or DIR/<name>) and validate it alone
  python3 scripts/validate.py --ledger-base REV also reject ledger entries removed and retired
                                                case numbers dropped, reused or cited since REV,
                                                counting every commit in REV..HEAD, and require every
                                                control changed since REV to be named in the newest
                                                CHANGELOG section, with weakenings stated as such
  python3 scripts/validate.py --no-render       skip running ROOT/scripts/render_catalog.py --check

Repository mode runs ROOT/scripts/render_catalog.py --check, so it executes code
from the checked-out tree. Validate an untrusted checkout with --no-render, or
in a sandbox.

Exit codes: 0 without findings, 1 with findings, 2 for usage or staging errors.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import datetime as dt
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
from urllib.parse import unquote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalog_model import (  # noqa: E402
    AIUC_CONTROL, AIUC_ID, AIUC_REGISTRY, CONTROLS_JSON as CATALOG, EVIDENCE_SCOPES, FAILURE_SEVERITIES,
    FRAMEWORK_NAME, LEDGER_JSON as LEDGER, LIFECYCLES, MAPPINGS_JSON as MAPPINGS, NIST_ACTION, NIST_CITATION,
    NIST_REGISTRY, NIST_SUBCATEGORY, PILLARS, RELATIONS, STATUS_ENUM, is_critical, is_withdrawn,
    nist_function, slugify,
)

# The installable skill bundle. docs/install.md copies exactly these entries, and
# links inside bundle files must resolve inside the bundle.
BUNDLE = (
    "SKILL.md", "references", "assets", "agents",
    "LICENSE", "LICENSES", "THIRD_PARTY_NOTICES.md",
)

RENDERER = "scripts/render_catalog.py"
CATALOG_MODEL = "scripts/catalog_model.py"
INSTALL_DOC = "docs/install.md"
CHANGELOG = "CHANGELOG.md"
OWASP_VIEW = "references/owasp-agentic-top-10.md"
CRITICAL_BOUNDARY_FILES = ("SKILL.md", "references/conformance.md")
CRITICAL_START = "<!-- critical-boundary:start -->"
CRITICAL_END = "<!-- critical-boundary:end -->"
ENUM_FILES = ("references/conformance.md", "assets/agent-security-record.md")
# The canonical compact change record appears verbatim in each of these files. SKILL.md
# links to the template skeleton and the worked example instead of repeating it.
RECORD_EXAMPLE_FILES = ("references/profile-and-levels.md", "README.md")
PILLARS_DOC = "docs/pillars.md"
FRAMEWORKS_DOC = "references/frameworks.md"
PATTERNS = "references/patterns.md"
# SKILL.md routing rows that must list every Level 1 critical-boundary control tagged with the feature.
FEATURE_ROUTES = {
    "MCP client, server or proxy": "mcp",
    "Browser runtime": "browser-agent",
    "Coding agents, CI workflows, instruction or rules files": "coding-agent",
}
# Internal evaluation references and viewer page labels do not belong in normative control text.
INTERNAL_CITATION = re.compile(r"\bprobe P\d|\bPDF p\.")
IDENTITY_FILES = ("SKILL.md", "README.md", "docs/pillars.md")
SNAPSHOT_FILES = ("references/frameworks.md", CATALOG, MAPPINGS, NIST_REGISTRY, AIUC_REGISTRY)
PROFILE_DOC = "references/profile-and-levels.md"
SNIPPET = "assets/AGENTS-snippet.md"
INFOGRAPHIC = "docs/stand-infographic.svg"
EVAL_CASES = "evals/cases.json"
# The SKILL.md Step 2 routing table: a table whose first two header cells are these.
ROUTING_HEADER = ("Trigger location", "Control IDs")

# Rendered by scripts/render_catalog.py and never edited by hand.
GENERATED = (
    "references/controls/index.md",
    "references/controls/S.md", "references/controls/T.md",
    "references/controls/A.md", "references/controls/N.md",
    "references/controls/D.md",
    "references/mappings.md",
)

REQUIRED_BUNDLE = (
    "SKILL.md", "LICENSE", "LICENSES/CC-BY-SA-4.0.txt", "THIRD_PARTY_NOTICES.md",
    "agents/openai.yaml",
    "references/profile-and-levels.md", "references/conformance.md",
    "references/runtime-controls.md", "references/mcp.md",
    "references/patterns.md", "references/verification.md",
    OWASP_VIEW, "references/frameworks.md",
    *GENERATED,
    "assets/agent-security-record.md", "assets/AGENTS-snippet.md",
)
REQUIRED_REPO = REQUIRED_BUNDLE + (
    "README.md", "CONTRIBUTING.md", "SECURITY.md", CHANGELOG,
    "docs/pillars.md", INSTALL_DOC,
    "evals/README.md", EVAL_CASES,
    CATALOG, LEDGER, MAPPINGS, NIST_REGISTRY, AIUC_REGISTRY,
    RENDERER, CATALOG_MODEL, "scripts/validate.py", "tests/test_validate.py", "tests/test_render_catalog.py",
    ".github/workflows/validate.yml", ".github/dependabot.yml",
)

IGNORED = {".git", ".venv", "venv", "__pycache__", "node_modules", ".mypy_cache", ".pytest_cache"}
TEXT_SUFFIXES = {
    ".md", ".yaml", ".yml", ".json", ".svg", ".py", ".txt", ".toml",
    ".cff", ".cfg", ".ini", ".sh", ".html", ".xml", ".csv",
}
TEXT_NAMES = {"LICENSE", ".gitignore", ".gitattributes", "CODEOWNERS"}
TITLE_SUFFIXES = {".md", ".yaml", ".yml", ".json"}

PRINCIPLE = "The model proposes. The application enforces."

# OWASP Top 10 for Agentic Applications 2026, published December 9, 2025:
# https://genai.owasp.org/download/52117/ (checked 2026-10-03). The "&" forms of
# ASI02 and ASI03 follow the publication's At-a-Glance summary and Appendix A;
# its section headings use "and". ASI06 uses "&" throughout the publication.
ASI_TITLES = {
    "ASI01": "Agent Goal Hijack",
    "ASI02": "Tool Misuse & Exploitation",
    "ASI03": "Identity & Privilege Abuse",
    "ASI04": "Agentic Supply Chain Vulnerabilities",
    "ASI05": "Unexpected Code Execution (RCE)",
    "ASI06": "Memory & Context Poisoning",
    "ASI07": "Insecure Inter-Agent Communication",
    "ASI08": "Cascading Failures",
    "ASI09": "Human-Agent Trust Exploitation",
    "ASI10": "Rogue Agents",
}

# The OWASP Top 10 for LLM Applications 2025 titles start with these words. Written after an ASI
# identifier ("ASI01 Prompt Injection"), they show a title taken from the wrong list.
TITLE_START_WORDS = {title.split()[0] for title in ASI_TITLES.values()} | {
    "Goal", "Prompt", "Sensitive", "Supply", "Data", "Improper", "Excessive", "System", "Vector",
    "Misinformation", "Unbounded", "Memory", "Insecure", "Rogue", "Cascading",
}
# Fallback when the catalog does not declare its closed applicability vocabulary.
VOCABULARY = (
    "all", "untrusted-input", "sensitive-data", "external-effect", "tools",
    "retrieval", "memory", "delegation", "inter-agent", "queued-work",
    "triggered-runs", "shared-context", "multi-tenant", "approvals",
    "code-execution", "browser-agent", "coding-agent", "mcp", "provider-routing",
    "provider-executed-tools", "client-conversation", "rendered-output",
    "network-egress", "model-artifacts", "separation-pattern",
)
REQUIRED_CONTROL_FIELDS = (
    "id", "pillar", "title", "statement", "rationale", "applies_when", "level",
    "failure_severity", "min_evidence_scope", "asi", "verification", "evidence",
)
TEXT_CONTROL_FIELDS = ("title", "statement", "rationale", "verification")

# Agent Skills specification (https://agentskills.io/specification). Host-specific
# keys are excluded on purpose so the bundle stays portable across hosts.
FRONTMATTER_KEYS = ("name", "description", "license", "compatibility", "metadata", "allowed-tools")
RESERVED_NAME_WORDS = ("anthropic", "claude")
MAX_NAME = 64
MAX_DESCRIPTION = 1024
MAX_COMPATIBILITY = 500
MAX_BODY_LINES = 500
TOKEN_BUDGET = 5000
TOKEN_WARN = 4500  # warn above this; the target for the body is TOKEN_TARGET or fewer
TOKEN_TARGET = 4400
# Words x 1.3 under-counts dense Markdown full of IDs and punctuation; characters / 4 is a
# closer estimate there. The larger of the two is used, and a body over the budget fails.
TOKENS_PER_WORD = 1.3
CHARS_PER_TOKEN = 4

# Codex skill metadata (agents/openai.yaml).
OPENAI_TOP_KEYS = ("interface", "policy", "dependencies")
OPENAI_INTERFACE_KEYS = (
    "display_name", "short_description", "icon_small", "icon_large",
    "brand_color", "default_prompt",
)
OPENAI_POLICY_KEYS = ("allow_implicit_invocation",)

SNAPSHOT_MAX_AGE_DAYS = 92

CONTROL_ID = re.compile(r"(?<![\w-])((?:S|T|A|N|D)-\d{2})(?![\w-])")
CONTROL_ID_FULL = re.compile(r"^(S|T|A|N|D)-[0-9]{2}$")
CONTROL_RANGE = re.compile(
    r"(?<![\w-])((?:S|T|A|N|D)-\d{2})\s*(?:to|through|\u2013)\s*((?:S|T|A|N|D)-\d{2})(?![\w-])")
LOWER_ID = re.compile(r"(?<![\w-])(?:s|t|a|n|d)-\d{2}(?![\w-])")
UNHYPHENATED_ID = re.compile(r"(?<![\w-])(?:S|T|A|N|D)\d{2}(?![\w:-])(?!\.\d)")
ASI_ANY = re.compile(r"\bASI(\d+)\b")
ASI_FULL = re.compile(r"^ASI(0[1-9]|10)$")
ASI_TITLE_USE = re.compile(
    r"\b(ASI(?:0[1-9]|10))\b(?:\*\*|__)?(?:[ \t]*:|[ \t]+[-\u2013][ \t]+)(?:\*\*|__)?[ \t]*")
# "ASI01 Agent Goal Hijack" and "ASI01 (Agent Goal Hijack)": checked when the next word starts an ASI title,
# or an OWASP Top 10 for LLM Applications 2025 title, so named scenarios after an identifier are left alone.
ASI_TITLE_ALT = re.compile(r"\b(ASI(?:0[1-9]|10))\b(?:\*\*|__)?[ \t]+(?:\*\*|__)?\(?(?:\*\*|__)?(?=[A-Z])")
# A statement states an obligation: MAY and OPTIONAL alone grant permissions and oblige nothing.
BCP14_OBLIGATION = re.compile(r"\b(?:MUST|SHALL|SHOULD|REQUIRED)\b")
STRONG_KEYWORD = re.compile(r"\b(?:MUST|SHALL|REQUIRED)\b")
WEAK_KEYWORD = re.compile(r"\b(?:SHOULD|RECOMMENDED|MAY|OPTIONAL)\b")
AIUC_HOST = "standard.aiuc-1.com"

# Escapes keep the banned characters out of this source file.
EM_DASH = re.compile("\u2014|&(?:mdash|#8212|#[xX]0*2014);")
JSON_EM_DASH = re.compile(r"\\u2014", re.IGNORECASE)
URL = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*://[^\s)>\]\"'`]*")
MACHINE_PATH = re.compile(
    r"(?<![\w.~$}/-])/(?:home|Users|root)/[^\s/\"'`)<>\]|]+"
    r"|\b[A-Za-z]:[\\/]Users[\\/][^\\/\s\"'`]+")

# The OWASP mark is used as an adjective, never in the possessive (OWASP mark usage guidelines).
OWASP_POSSESSIVE = re.compile("OWASP['\u2019]s\\b")
# Case labels in a control's verification text: "(A-06/C1)" for the first case, then "(C2)" and so on.
# The letter C (case) avoids a clash with the pillar letter T. A case removed after a release keeps
# its number as a retired marker, "(C3: retired)", so the number is never reused.
CASE_LABEL = re.compile(r"\((?:((?:S|T|A|N|D)-\d{2})/)?C(\d+)\)")
RETIRED_CASE = re.compile(r"\((?:((?:S|T|A|N|D)-\d{2})/)?C(\d+): retired\)")
CASE_RANGE = re.compile(r"(?<![\w-])((?:S|T|A|N|D)-\d{2})/C1\.\.C(\d+)\b")

FENCE = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")
LIST_ITEM = re.compile(r"^\s{0,3}(?:[-*+]|\d{1,9}[.)])(?:[ \t]|$)")
CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)")
ATX = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*$")
SETEXT = re.compile(r"^ {0,3}(?:=+|-+)[ \t]*$")
HTML_ID = re.compile(r"""<[^>]*?\s(?:id|name)\s*=\s*["']([^"']+)["']""", re.IGNORECASE)
INLINE_LINK = re.compile(
    r"!?\[(?P<text>(?:[^\[\]\\\n]|\\.|\[(?:[^\[\]\\\n]|\\.)*\])*)\]"
    r"\([ \t]*(?P<dest><[^<>\n]*>|(?:[^\s()\\]|\\.|\((?:[^\s()\\]|\\.)*\))*)"
    r"(?:[ \t]+(?:\"(?:[^\"\\\n]|\\.)*\"|'(?:[^'\\\n]|\\.)*'|\((?:[^()\\\n]|\\.)*\)))?[ \t]*\)")
REF_DEF = re.compile(
    r"^ {0,3}\[(?P<label>(?!\^)(?:[^\[\]\\\n]|\\.)+)\]:[ \t]*(?P<dest><[^<>\n]*>|\S+)"
    r"(?:[ \t]+(?:\"[^\"\n]*\"|'[^'\n]*'|\([^()\n]*\)))?[ \t]*$")
REF_USE = re.compile(r"!?\[(?P<text>(?:[^\[\]\\\n]|\\.)+)\]\[(?P<label>(?:[^\[\]\\\n]|\\.)*)\]")
HTML_LINK = re.compile(
    r"""<(?:a|img|source|link|script|iframe|video|audio)\b[^>]*?\s(?:href|src)\s*=\s*(?:"([^"]*)"|'([^']*)')""",
    re.IGNORECASE)
YAML_NON_STRING = re.compile(
    r"(?i)^(?:~|null|true|false|yes|no|on|off"
    r"|[-+]?\d[\d_]*(?:\.\d*)?(?:e[-+]?\d+)?|[-+]?\.\d+(?:e[-+]?\d+)?"
    r"|0x[0-9a-f_]+|0o[0-7_]+|0b[01_]+|[-+]?\.inf|\.nan|\d{4}-\d{2}-\d{2}.*)$")
SNAPSHOT_DATE = re.compile(r"(?i)\bchecked\b[^.\n]{0,80}?(\d{4}-\d{2}-\d{2})")
NEXT_RELEASE = re.compile(
    r"(?i)\bnext\b[^.\n]{0,40}?\brelease\b[^.\n]{0,40}?"
    r"(\d{4}-\d{2}-\d{2}|(?:January|February|March|April|May|June|July|August|September"
    r"|October|November|December) \d{1,2}, \d{4})")
USES = re.compile(r"^\s*(?:-\s+)?uses:\s*['\"]?([^'\"\s#]+)")
PINNED_ACTION = re.compile(r"^[\w.-]+/[\w.-]+(?:/[\w./-]+)?@[0-9a-f]{40}$")


@dataclass(frozen=True)
class Finding:
    code: str
    path: str
    message: str


@dataclass
class Result:
    findings: list[Finding] = field(default_factory=list)
    warnings: list[Finding] = field(default_factory=list)


@dataclass
class Catalog:
    ids: set[str]
    critical: set[str]
    version: str | None
    lifecycle: dict[str, str] = field(default_factory=dict)
    titles: dict[str, str] = field(default_factory=dict)
    cases: dict[str, int] = field(default_factory=dict)
    retired: dict[str, set[int]] = field(default_factory=dict)
    controls: list = field(default_factory=list)
    asi_pages: dict[str, int] = field(default_factory=dict)

    def listed(self) -> list:
        """Controls that count and route: every control with a string ID except withdrawn tombstones."""
        return [c for c in self.controls if isinstance(c.get("id"), str) and not is_withdrawn(c)]

    def by_id(self) -> dict:
        return {c["id"]: c for c in self.controls if isinstance(c.get("id"), str)}

    def cross_cutting(self) -> set[str]:
        """Listed controls that carry every ASI identifier."""
        return {c["id"] for c in self.listed() if isinstance(c.get("asi"), list) and set(c["asi"]) >= set(ASI_TITLES)}


class StageError(Exception):
    """Raised when the bundle cannot be staged."""


class YamlError(ValueError):
    """Raised for YAML constructs outside the supported subset."""


class Reporter:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.result = Result()

    def _rel(self, path: Path | str) -> str:
        if isinstance(path, Path):
            try:
                return path.relative_to(self.root).as_posix()
            except ValueError:
                return path.as_posix()
        return path

    def report(self, code: str, path: Path | str, message: str) -> None:
        self.result.findings.append(Finding(code, self._rel(path), message))

    def warn(self, code: str, path: Path | str, message: str) -> None:
        self.result.warnings.append(Finding(code, self._rel(path), message))


# ---------------------------------------------------------------------------
# Markdown helpers


def blank_frontmatter(text: str) -> str:
    """Replace leading YAML frontmatter with blank lines, keeping line numbers."""
    match = re.match(r"\A---\r?\n.*?\r?\n---[ \t]*(?:\r?\n|\Z)", text, re.DOTALL)
    if not match:
        return text
    return "\n" * match.group(0).count("\n") + text[match.end():]


def markdown_lines(text: str) -> tuple[list[str], int | None]:
    """Blank fenced and indented code. Return the lines and the line of an unclosed fence."""
    out: list[str] = []
    fence: tuple[str, int, int] | None = None
    in_list = False
    prev_blank = True
    in_code = False
    for number, line in enumerate(text.split("\n"), 1):
        if fence:
            match = FENCE.match(line)
            if match and match.group(2)[0] == fence[0] and len(match.group(2)) >= fence[1] \
                    and not match.group(3).strip():
                fence = None
            out.append("")
            continue
        match = FENCE.match(line)
        indented_code = len(match.group(1).expandtabs(4)) >= 4 and not in_list and (prev_blank or in_code) \
            if match else False
        if match and not (match.group(2)[0] == "`" and "`" in match.group(3)) and not indented_code:
            fence = (match.group(2)[0], len(match.group(2)), number)
            out.append("")
            prev_blank = False
            continue
        if not line.strip():
            out.append("")
            prev_blank = True
            continue
        indented = line.startswith("    ") or line.startswith("\t")
        if indented and not in_list and (prev_blank or in_code):
            in_code = True
            out.append("")
            prev_blank = False
            continue
        in_code = False
        if LIST_ITEM.match(line):
            in_list = True
        elif not line[:1].isspace() and prev_blank:
            in_list = False
        out.append(line)
        prev_blank = False
    return out, (fence[2] if fence else None)


def strip_code_spans(line: str) -> str:
    return CODE_SPAN.sub(lambda match: " " * len(match.group(0)), line)


def heading_anchors(lines: list[str]) -> set[str]:
    anchors: set[str] = set()
    counts: dict[str, int] = {}

    def add(heading: str) -> None:
        slug = slugify(heading)
        seen = counts.get(slug, 0)
        anchors.add(slug if seen == 0 else f"{slug}-{seen}")
        counts[slug] = seen + 1

    previous_paragraph = ""
    for line in lines:
        for found in HTML_ID.finditer(line):
            anchors.add(found.group(1))
        match = ATX.match(line)
        if match:
            add(match.group(2) or "")
            previous_paragraph = ""
            continue
        if previous_paragraph and SETEXT.match(line):
            add(previous_paragraph.strip())
            previous_paragraph = ""
            continue
        stripped = line.strip()
        is_paragraph = bool(stripped) and not stripped.startswith(("|", ">", "<")) \
            and not LIST_ITEM.match(line) and not line.startswith(("    ", "\t"))
        previous_paragraph = line if is_paragraph else ""
    return anchors


def table_cells(line: str) -> list[str]:
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|") and not body.endswith("\\|"):
        body = body[:-1]
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", body)]


def plain_cell(cell: str) -> str:
    cell = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", cell)
    return cell.replace("**", "").replace("__", "").replace("`", "").strip()


def markdown_tables(lines: list[str]) -> list[tuple[list[str], list[tuple[int, list[str]]]]]:
    """Return (header cells, [(line number, cells)]) for each pipe table."""
    tables = []
    index = 0
    while index < len(lines) - 1:
        line, separator = lines[index], lines[index + 1]
        if "|" in line and re.match(r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)*\|?\s*$", separator):
            header = table_cells(line)
            rows = []
            index += 2
            while index < len(lines) and "|" in lines[index] and lines[index].strip():
                rows.append((index + 1, table_cells(lines[index])))
                index += 1
            tables.append((header, rows))
            continue
        index += 1
    return tables


# ---------------------------------------------------------------------------
# YAML subset (frontmatter and agents/openai.yaml)


def parse_scalar(raw: str) -> tuple[str, bool]:
    """Parse a single YAML scalar. Return (value, is_plain)."""
    raw = raw.strip()
    if raw.startswith('"'):
        out = []
        index = 1
        escapes = {'"': '"', "\\": "\\", "/": "/", "n": "\n", "t": "\t", " ": " ",
                   "0": "\0", "r": "\r", "b": "\b", "e": "\x1b", "a": "\a"}
        while index < len(raw):
            char = raw[index]
            if char == "\\":
                following = raw[index + 1:index + 2]
                if following in escapes:
                    out.append(escapes[following])
                    index += 2
                    continue
                width = {"x": 2, "u": 4, "U": 8}.get(following)
                digits = raw[index + 2:index + 2 + width] if width else ""
                if not width or not re.fullmatch(r"[0-9A-Fa-f]+", digits) or len(digits) != width:
                    raise YamlError(f"invalid escape in double-quoted value: \\{following}")
                out.append(chr(int(digits, 16)))
                index += 2 + width
                continue
            if char == '"':
                rest = raw[index + 1:]
                if rest.strip() and not re.match(r"\s+#", rest):
                    raise YamlError("unexpected text after the closing quote")
                return "".join(out), False
            out.append(char)
            index += 1
        raise YamlError("unclosed double quote")
    if raw.startswith("'"):
        out = []
        index = 1
        while index < len(raw):
            if raw[index] == "'":
                if raw[index + 1:index + 2] == "'":
                    out.append("'")
                    index += 2
                    continue
                rest = raw[index + 1:]
                if rest.strip() and not re.match(r"\s+#", rest):
                    raise YamlError("unexpected text after the closing quote")
                return "".join(out), False
            out.append(raw[index])
            index += 1
        raise YamlError("unclosed single quote")
    if not raw:
        return "", True
    if raw[0] in "[]{},&*!|>%@`#" or raw[:2] in ("- ", "? ", ": ") or raw in ("-", "?", ":"):
        raise YamlError(f"a plain value cannot start with {raw[0]!r}; quote the value")
    if re.search(r"\s#", raw):
        raise YamlError("' #' starts a YAML comment and truncates the value; quote the value")
    if re.search(r":(?:\s|$)", raw):
        raise YamlError("': ' inside a plain value is read as a mapping; quote the value")
    return raw, True


def parse_block_scalar(indicator: str, block: list[str]) -> str:
    match = re.fullmatch(r"([|>])([+-]?)([1-9]?)([+-]?)\s*(?:#.*)?", indicator)
    if not match:
        raise YamlError(f"invalid block scalar indicator {indicator!r}")
    style, chomp = match.group(1), match.group(2) or match.group(4)
    content = [line for line in block if line.strip()]
    if not content:
        return ""
    indent = int(match.group(3)) if match.group(3) else min(len(l) - len(l.lstrip(" ")) for l in content)
    lines = [line[indent:] if line.strip() else "" for line in block]
    if style == "|":
        value = "\n".join(lines)
    else:
        paragraphs, current = [], []
        for line in lines:
            if line:
                current.append(line)
            else:
                paragraphs.append(" ".join(current))
                current = []
        paragraphs.append(" ".join(current))
        value = "\n".join(paragraphs)
    value = value.rstrip("\n")
    return value if chomp == "-" else value + "\n"


def parse_frontmatter(header: str) -> tuple[dict[str, object], list[str], list[str], list[str]]:
    """Parse the supported YAML subset. Return (data, errors, duplicates, non_string_keys)."""
    data: dict[str, object] = {}
    errors: list[str] = []
    duplicates: list[str] = []
    non_strings: list[str] = []
    lines = header.split("\n")
    index = 0
    while index < len(lines):
        line = lines[index].rstrip("\r")
        number = index + 2
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        if line[0] in " \t":
            errors.append(f"line {number}: unexpected indentation")
            index += 1
            continue
        match = re.fullmatch(r"([^\s:#][^:]*?):(?:[ \t]+(.*))?", line)
        if not match:
            errors.append(f"line {number}: expected 'key: value'")
            index += 1
            continue
        key, rest = match.group(1), (match.group(2) or "").strip()
        block = []
        index += 1
        while index < len(lines) and (lines[index][:1] in (" ", "\t") or not lines[index].strip()):
            block.append(lines[index].rstrip("\r"))
            index += 1
        while block and not block[-1].strip():
            block.pop()
        if key in data:
            duplicates.append(key)
        try:
            if not rest or rest.startswith("#"):
                if not block:
                    data[key] = None
                elif key == "metadata" or not block[0].lstrip().startswith("- "):
                    mapping: dict[str, str] = {}
                    indent = len(block[0]) - len(block[0].lstrip(" "))
                    for child in block:
                        if not child.strip() or child.lstrip().startswith("#"):
                            continue
                        child_indent = len(child) - len(child.lstrip(" "))
                        child_match = re.fullmatch(r"([^\s:#][^:]*?):(?:[ \t]+(.*))?", child.strip())
                        if child_indent != indent or not child_match or not (child_match.group(2) or "").strip():
                            raise YamlError(f"'{key}' must be a one-level map of string values")
                        child_key = child_match.group(1)
                        value, plain = parse_scalar(child_match.group(2))
                        if plain and YAML_NON_STRING.match(value):
                            non_strings.append(f"{key}.{child_key}")
                        if child_key in mapping:
                            duplicates.append(f"{key}.{child_key}")
                        mapping[child_key] = value
                    data[key] = mapping
                else:
                    data[key] = [item.strip()[2:].strip() for item in block if item.strip()]
            elif rest[0] in "|>":
                data[key] = parse_block_scalar(rest, block)
            else:
                joined = " ".join([rest] + [item.strip() for item in block if item.strip()])
                value, plain = parse_scalar(joined)
                if plain and YAML_NON_STRING.match(value):
                    non_strings.append(key)
                data[key] = value
        except YamlError as error:
            errors.append(f"'{key}': {error}")
            data.setdefault(key, None)
    return data, errors, duplicates, non_strings


def parse_simple_yaml(text: str) -> tuple[dict[str, object], list[str]]:
    """Parse a two-level YAML map; deeper nesting is accepted but not interpreted."""
    data: dict[str, object] = {}
    errors: list[str] = []
    current: dict[str, object] | None = None
    child_indent: int | None = None
    for number, raw in enumerate(text.split("\n"), 1):
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        if line[indent:indent + 1] == "\t":
            errors.append(f"line {number}: tabs are not allowed for indentation")
            continue
        body = line.strip()
        match = re.fullmatch(r"([A-Za-z0-9_-]+):(?:[ \t]+(.*))?", body)
        if indent == 0:
            current, child_indent = None, None
            if not match:
                errors.append(f"line {number}: expected 'key: value'")
                continue
            key, rest = match.group(1), (match.group(2) or "").strip()
            if key in data:
                errors.append(f"line {number}: duplicate key {key!r}")
            if not rest or rest.startswith("#"):
                current = {}
                data[key] = current
            else:
                try:
                    data[key] = parse_scalar(rest)
                except YamlError as error:
                    errors.append(f"line {number}: {error}")
            continue
        if current is None:
            errors.append(f"line {number}: unexpected indentation")
            continue
        if child_indent is None:
            child_indent = indent
        if indent > child_indent:
            continue
        if indent < child_indent:
            errors.append(f"line {number}: inconsistent indentation")
            continue
        if body.startswith("- "):
            current["- "] = ("list", False)
            continue
        if not match:
            errors.append(f"line {number}: expected 'key: value'")
            continue
        key, rest = match.group(1), (match.group(2) or "").strip()
        if key in current:
            errors.append(f"line {number}: duplicate key {key!r}")
        if not rest or rest.startswith("#"):
            current[key] = {}
        else:
            try:
                current[key] = parse_scalar(rest)
            except YamlError as error:
                errors.append(f"line {number}: {error}")
    return data, errors


# ---------------------------------------------------------------------------
# File walking and per-file checks


def walk(root: Path):
    """Yield (path, relative path, is_symlink) without following symlinked directories."""
    for dirpath, dirnames, filenames in os.walk(root):
        directory = Path(dirpath)
        relative_dir = directory.relative_to(root)
        kept = []
        for name in sorted(dirnames):
            relative = relative_dir / name
            if name in IGNORED or relative.parts[:2] == ("evals", "artifacts"):
                continue
            if (directory / name).is_symlink():
                yield directory / name, relative, True
                continue
            kept.append(name)
        dirnames[:] = kept
        for name in sorted(filenames):
            path = directory / name
            yield path, relative_dir / name, path.is_symlink()


def is_text(relative: Path) -> bool:
    return relative.suffix.lower() in TEXT_SUFFIXES or relative.name in TEXT_NAMES


def check_text(rep: Reporter, path: Path, relative: Path, text: str) -> None:
    without_urls = URL.sub(" ", text)
    match = MACHINE_PATH.search(without_urls)
    if match:
        rep.report("machine-path", path, f"Use a portable path or environment variable instead of {match.group(0)!r}")
    if EM_DASH.search(text) or (relative.suffix == ".json" and JSON_EM_DASH.search(text)):
        rep.report("punctuation", path, "Replace the em dash with a comma, colon, parentheses, or plain hyphen")
    if relative.suffix in TITLE_SUFFIXES and OWASP_POSSESSIVE.search(text):
        rep.report("owasp-mark", path, "Use the OWASP mark as an adjective, never in the possessive; name the "
                   "publication instead (for example 'the OWASP Top 10 for Agentic Applications 2026')")
    for found in ASI_ANY.finditer(text):
        number = found.group(1)
        if len(number) != 2 or not 1 <= int(number) <= 10:
            rep.report("asi-id", path, f"ASI{number} is not an identifier; use ASI01 to ASI10")
    if relative.suffix in TITLE_SUFFIXES:
        source = text
        if relative.suffix == ".md":
            lines, _ = markdown_lines(blank_frontmatter(text))
            source = "\n".join(strip_code_spans(line) for line in lines)
        check_asi_titles(rep, path, source)


def title_matches(text: str, title: str) -> bool:
    """True when text starts with the exact title and the title is not cut mid-word."""
    return text.startswith(title) and not text[len(title):len(title) + 1].isalnum()


def check_asi_titles(rep: Reporter, path: Path, text: str) -> None:
    for number, line in enumerate(text.split("\n"), 1):
        for match in ASI_TITLE_USE.finditer(line):
            rest = line[match.end():]
            if not rest[:1].isupper() or rest.startswith("ASI"):
                continue
            title = ASI_TITLES[match.group(1)]
            if not title_matches(rest, title):
                rep.report("asi-title", path,
                           f"Line {number}: use the exact title '{match.group(1)}: {title}', "
                           "or do not follow the identifier with a colon")
        for match in ASI_TITLE_ALT.finditer(line):
            rest = line[match.end():]
            first = re.match(r"[A-Za-z]+(?:-[A-Za-z]+)?", rest)
            title = ASI_TITLES[match.group(1)]
            if first and first.group(0) in TITLE_START_WORDS and not title_matches(rest, title):
                rep.report("asi-title", path, f"Line {number}: a title after {match.group(1)} must be its exact "
                           f"title, '{title}'")


# ---------------------------------------------------------------------------
# Links


@dataclass
class MarkdownDoc:
    path: Path
    relative: str
    text: str
    lines: list[str]
    unclosed: int | None
    _anchors: set[str] | None = None

    @property
    def anchors(self) -> set[str]:
        if self._anchors is None:
            self._anchors = heading_anchors(self.lines)
        return self._anchors


HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


def blank_html_comments(lines: list[str]) -> list[str]:
    """Blank HTML comments outside code, keeping line numbers: GitHub does not render them."""
    joined = "\n".join(lines)
    blanked = HTML_COMMENT.sub(lambda match: re.sub(r"[^\n]", " ", match.group(0)), joined)
    return blanked.split("\n")


def load_markdown(path: Path, relative: str, text: str) -> MarkdownDoc:
    lines, unclosed = markdown_lines(blank_frontmatter(text))
    return MarkdownDoc(path, relative, text, blank_html_comments(lines), unclosed)


def in_bundle(relative: str) -> bool:
    return relative.split("/", 1)[0] in BUNDLE


def iter_link_targets(doc: MarkdownDoc):
    """Yield (line number, raw target, link text) for every local or remote link."""
    definitions: dict[str, str] = {}
    prose = [strip_code_spans(line) for line in doc.lines]
    for number, line in enumerate(prose, 1):
        match = REF_DEF.match(line)
        if match:
            label = " ".join(match.group("label").split()).casefold()
            definitions.setdefault(label, match.group("dest"))
            yield number, match.group("dest"), match.group("label")
    for number, line in enumerate(prose, 1):
        if REF_DEF.match(line):
            continue
        for match in INLINE_LINK.finditer(line):
            yield number, match.group("dest"), match.group("text")
        scrubbed = INLINE_LINK.sub(" ", line)
        for match in REF_USE.finditer(scrubbed):
            label = match.group("label") or match.group("text")
            if " ".join(label.split()).casefold() not in definitions:
                yield number, None, label
        for match in HTML_LINK.finditer(line):
            yield number, match.group(1) if match.group(1) is not None else match.group(2), None


def link_targets(doc: MarkdownDoc, root: Path) -> list[Path]:
    """Existing local files that a document links to (for reachability)."""
    found = []
    for _, raw, _ in iter_link_targets(doc):
        if raw is None:
            continue
        raw = raw[1:-1] if raw.startswith("<") and raw.endswith(">") else raw
        try:
            target = urlsplit(raw)
        except ValueError:
            continue
        if target.scheme or target.netloc or not target.path or target.path.startswith("/"):
            continue
        destination = (doc.path.parent / unquote(target.path)).resolve()
        if destination.is_file() and destination.is_relative_to(root):
            found.append(destination)
    return found


def check_links(rep: Reporter, doc: MarkdownDoc, root: Path, docs: dict[str, MarkdownDoc],
                bundle_mode: bool) -> None:
    if doc.unclosed:
        rep.report("unclosed-fence", doc.path,
                   f"Line {doc.unclosed}: code fence is never closed, so later content is unchecked")
    source_in_bundle = in_bundle(doc.relative)
    for number, raw, text in iter_link_targets(doc):
        where = f"Line {number}"
        if raw is None:
            rep.report("missing-reference", doc.path, f"{where}: no definition for reference link [{text}]")
            continue
        raw = raw[1:-1] if raw.startswith("<") and raw.endswith(">") else raw
        if not raw.strip():
            rep.report("invalid-link", doc.path, f"{where}: empty link target")
            continue
        try:
            target = urlsplit(raw)
            _ = target.port
        except ValueError:
            rep.report("invalid-link", doc.path, f"{where}: invalid link {raw}")
            continue
        if target.scheme in {"http", "https", "mailto"}:
            check_aiuc_link(rep, doc.path, where, raw, target, text)
            continue
        if target.scheme or target.netloc or target.path.startswith("/"):
            rep.report("nonportable-link", doc.path, f"{where}: use a relative bundled link: {raw}")
            continue
        fragment = unquote(target.fragment)
        if not target.path:
            if fragment and fragment not in doc.anchors:
                rep.report("missing-anchor", doc.path, f"{where}: no heading or id for #{fragment}")
            continue
        destination = (doc.path.parent / unquote(target.path)).resolve()
        if not destination.is_relative_to(root):
            rep.report("link-escape", doc.path, f"{where}: link leaves the {'bundle' if bundle_mode else 'repository'}: {raw}")
            continue
        relative = destination.relative_to(root).as_posix()
        if not bundle_mode and source_in_bundle and not in_bundle(relative):
            rep.report("bundle-link", doc.path,
                       f"{where}: a bundle file links outside the installed bundle: {raw}")
            continue
        if not destination.exists():
            rep.report("missing-link", doc.path, f"{where}: missing link target: {raw}")
            continue
        if fragment and destination.suffix == ".md" and destination.is_file():
            target_doc = docs.get(relative)
            if target_doc is None:
                try:
                    target_doc = load_markdown(destination, relative, destination.read_text(encoding="utf-8"))
                except (OSError, UnicodeError):
                    continue
                docs[relative] = target_doc
            if fragment not in target_doc.anchors:
                rep.report("missing-anchor", doc.path, f"{where}: no heading or id for #{fragment} in {relative}")


def check_aiuc_link(rep: Reporter, path: Path, where: str, raw: str, target, text: str | None) -> None:
    label = plain_cell(text or "")
    if target.hostname != AIUC_HOST or not AIUC_ID.match(label):
        return
    segments = [part for part in target.path.split("/") if part]
    if len(segments) != 2 or target.path.endswith("/") or target.query:
        rep.report("aiuc-link", path,
                   f"{where}: link {label} to its requirement page (two path segments, no trailing slash), not {raw}")


# ---------------------------------------------------------------------------
# Skill metadata


def check_frontmatter(rep: Reporter, root: Path, text: str, bundle_mode: bool) -> dict[str, object]:
    path = root / "SKILL.md"
    header = re.match(r"\A---\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", text, re.DOTALL)
    if not header:
        rep.report("frontmatter", path, "Expected YAML frontmatter at the start of SKILL.md")
        return {}
    data, errors, duplicates, non_strings = parse_frontmatter(header.group(1))
    for error in errors:
        rep.report("frontmatter", path, error)
    for key in duplicates:
        rep.report("duplicate-field", path, f"Duplicate frontmatter key: {key}")
    for key in non_strings:
        rep.report("frontmatter", path, f"'{key}' is not a string in YAML; quote the value")
    for key in data:
        if key not in FRONTMATTER_KEYS:
            rep.report("frontmatter-key", path,
                       f"Unexpected frontmatter key {key!r}; the Agent Skills specification allows "
                       + ", ".join(FRONTMATTER_KEYS))

    name = data.get("name")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > MAX_NAME:
        rep.report("skill-name", path,
                   f"Use 1-{MAX_NAME} lowercase letters, digits and single hyphens, not starting or ending with a hyphen")
        name = name if isinstance(name, str) else ""
    elif any(word in name for word in RESERVED_NAME_WORDS):
        rep.report("skill-name", path, "The name cannot contain a reserved word: " + ", ".join(RESERVED_NAME_WORDS))
    if bundle_mode and name and root.name != name:
        rep.report("skill-dir-name", path, f"The skill directory is {root.name!r} but the frontmatter name is {name!r}")

    description = data.get("description")
    if not isinstance(description, str) or not description.strip():
        rep.report("description", path, "Provide a non-empty description")
    else:
        if len(description) > MAX_DESCRIPTION:
            rep.report("description", path, f"Description has {len(description)} characters; the limit is {MAX_DESCRIPTION}")
        if "[TODO" in description:
            rep.report("description", path, "Finish the description (it contains a TODO marker)")
        if "<" in description or ">" in description:
            rep.report("description", path, "The description cannot contain XML tags or angle brackets")

    license_value = data.get("license")
    if not isinstance(license_value, str) or not license_value.strip():
        rep.report("license", path, "Identify the package license in the frontmatter")
    else:
        check_license(rep, root, path, license_value.strip())

    compatibility = data.get("compatibility")
    if compatibility is not None and (not isinstance(compatibility, str) or not compatibility.strip()
                                      or len(compatibility) > MAX_COMPATIBILITY):
        rep.report("compatibility", path, f"compatibility must be 1-{MAX_COMPATIBILITY} characters")
    metadata = data.get("metadata")
    if metadata is not None and not isinstance(metadata, dict):
        rep.report("frontmatter", path, "metadata must be a one-level map of string values")
    tools = data.get("allowed-tools")
    if tools is not None and not isinstance(tools, str):
        rep.report("frontmatter", path, "allowed-tools must be a space-separated string")

    body = text[header.end():]
    body_lines = len(body.splitlines())
    if body_lines >= MAX_BODY_LINES:
        rep.report("skill-size", path, f"The SKILL.md body has {body_lines} lines; keep it under {MAX_BODY_LINES}")
    estimate = token_estimate(body)
    if estimate > TOKEN_BUDGET:
        rep.report("skill-tokens", path, f"The SKILL.md body is about {estimate} tokens (the larger of words x "
                   f"{TOKENS_PER_WORD} and characters / {CHARS_PER_TOKEN}); keep it under {TOKEN_BUDGET}, the "
                   "specification's recommendation and the part a host keeps after compaction")
    elif estimate > TOKEN_WARN:
        rep.warn("skill-tokens", path, f"The SKILL.md body is about {estimate} tokens; the target is {TOKEN_TARGET} "
                 f"or fewer, so that a denser real tokenizer still keeps the procedure under {TOKEN_BUDGET}")
    return data


def token_estimate(body: str) -> int:
    """Estimate the tokens of a skill body as max(words x 1.3, characters / 4)."""
    return int(max(len(body.split()) * TOKENS_PER_WORD, len(body) / CHARS_PER_TOKEN))


def check_license(rep: Reporter, root: Path, path: Path, value: str) -> None:
    """Accept a bundled license file, or an SPDX expression whose license texts are bundled."""
    if (root / value).is_file() and in_bundle(value):
        return
    tokens = re.findall(r"[A-Za-z0-9.+-]+|\(|\)", value)
    identifiers = [token for token in tokens if token not in {"AND", "OR", "WITH", "(", ")"}]
    if not identifiers or re.sub(r"[A-Za-z0-9.+\-()\s]", "", value):
        rep.report("license", path, f"Use an SPDX expression or a bundled license file, not {value!r}")
        return
    for identifier in identifiers:
        text_file = root / ("LICENSE" if identifier == "MIT" else f"LICENSES/{identifier}.txt")
        if not text_file.is_file():
            rep.report("license", path, f"No bundled license text for {identifier!r} (expected {text_file.relative_to(root).as_posix()})")


def check_openai_yaml(rep: Reporter, root: Path, name: str) -> None:
    path = root / "agents/openai.yaml"
    if not path.is_file():
        return
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return
    data, errors = parse_simple_yaml(text)
    for error in errors:
        rep.report("openai-yaml", path, error)
    for key in data:
        if key not in OPENAI_TOP_KEYS:
            rep.report("openai-yaml", path, f"Unexpected top-level key {key!r}; allowed: " + ", ".join(OPENAI_TOP_KEYS))
    interface = data.get("interface")
    if not isinstance(interface, dict):
        rep.report("openai-yaml", path, "Expected an 'interface' map")
        interface = {}
    for key in interface:
        if key not in OPENAI_INTERFACE_KEYS:
            rep.report("openai-yaml", path, f"Unexpected interface key {key!r}; allowed: " + ", ".join(OPENAI_INTERFACE_KEYS))
    prompt = interface.get("default_prompt")
    if not isinstance(prompt, tuple):
        rep.report("openai-yaml", path, "interface.default_prompt must be a string that names the skill")
    elif name and not re.search(rf"\${re.escape(name)}(?![a-z0-9-])", prompt[0]):
        rep.report("openai-yaml", path, f"interface.default_prompt must reference ${name}")
    policy = data.get("policy")
    if policy is not None:
        if not isinstance(policy, dict):
            rep.report("openai-yaml", path, "policy must be a map")
        else:
            for key, value in policy.items():
                if key not in OPENAI_POLICY_KEYS:
                    rep.report("openai-yaml", path, f"Unexpected policy key {key!r}")
                elif not (isinstance(value, tuple) and value[1] and value[0] in ("true", "false")):
                    rep.report("openai-yaml", path, f"policy.{key} must be true or false")
    dependencies = data.get("dependencies")
    if dependencies is not None and not isinstance(dependencies, dict):
        rep.report("openai-yaml", path, "dependencies must be a map")


# ---------------------------------------------------------------------------
# Catalog, ledger and mappings


def load_json(rep: Reporter, path: Path, code: str):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        rep.report(code, path, f"Cannot parse JSON: {error}")
        return None


def lookup(data: object, *names: str):
    """Find a declared vocabulary or enum at the top level or one level down."""
    if not isinstance(data, dict):
        return None
    for name in names:
        if name in data:
            return data[name]
    for value in data.values():
        if isinstance(value, dict):
            for name in names:
                if name in value:
                    return value[name]
    return None


def catalog_controls(data: object) -> list | None:
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("controls"), list):
        return data["controls"]
    return None


def read_catalog(root: Path) -> Catalog | None:
    """Load control IDs for citation checks without reporting (used when staging)."""
    try:
        data = json.loads((root / CATALOG).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    controls = catalog_controls(data)
    if controls is None:
        return None
    ids, critical, lifecycles, titles = set(), set(), {}, {}
    for control in controls:
        if isinstance(control, dict) and isinstance(control.get("id"), str):
            cid = control["id"]
            ids.add(cid)
            lifecycles[cid] = control.get("lifecycle", "active")
            if isinstance(control.get("title"), str):
                titles[cid] = control["title"]
            if is_critical(control):
                critical.add(cid)
    return Catalog(ids, critical, None, lifecycles, titles,
                   controls=[control for control in controls if isinstance(control, dict)],
                   asi_pages=asi_pages(data))


def asi_pages(data: object) -> dict[str, int]:
    """The start page of each ASI entry, from the catalog's asi_categories."""
    categories = lookup(data, "asi_categories")
    if not isinstance(categories, list):
        return {}
    return {item["id"]: item["page"] for item in categories
            if isinstance(item, dict) and isinstance(item.get("id"), str) and type(item.get("page")) is int}


def nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def check_declared_enum(rep: Reporter, path: Path, data: object, expected: tuple[str, ...],
                        ordered: bool, label: str, *names: str) -> None:
    declared = lookup(data, *names)
    if declared is None:
        return
    if not isinstance(declared, list) or (list(declared) if ordered else sorted(map(str, declared))) != \
            (list(expected) if ordered else sorted(expected)):
        rep.report("catalog-enum", path, f"The catalog's {label} must be exactly: " + ", ".join(expected))


def check_catalog(rep: Reporter, root: Path) -> Catalog | None:
    path = root / CATALOG
    data = load_json(rep, path, "catalog")
    if data is None:
        return None
    controls = catalog_controls(data)
    if controls is None:
        rep.report("catalog", path, "Expected a 'controls' list")
        return None

    vocabulary = lookup(data, "applicability_vocabulary", "applies_when_vocabulary")
    if vocabulary is None:
        vocabulary = VOCABULARY
    elif not isinstance(vocabulary, list) or not all(isinstance(token, str) for token in vocabulary) \
            or len(set(vocabulary)) != len(vocabulary):
        rep.report("catalog-enum", path, "applicability_vocabulary must be a list of unique strings")
        vocabulary = VOCABULARY
    check_declared_enum(rep, path, data, STATUS_ENUM, False, "status enum", "status_enum", "statuses")
    check_declared_enum(rep, path, data, EVIDENCE_SCOPES, True, "evidence scope enum (weakest to strongest)",
                        "evidence_scope_enum", "evidence_scopes", "min_evidence_scope_enum")
    check_declared_enum(rep, path, data, FAILURE_SEVERITIES, False, "failure severity enum",
                        "failure_severity_enum", "severity_enum")
    check_declared_enum(rep, path, data, RELATIONS, False, "mapping relation enum",
                        "relation_enum", "mapping_relations", "relations")
    pillars = lookup(data, "pillars")
    if pillars is not None:
        declared = [(item.get("letter"), item.get("name")) for item in pillars if isinstance(item, dict)] \
            if isinstance(pillars, list) else None
        if declared != list(PILLARS.items()):
            rep.report("catalog-enum", path, "The catalog's pillars must be exactly, in this order: "
                       + ", ".join(f"{name} ({letter})" for letter, name in PILLARS.items()))
    levels = lookup(data, "levels")
    if isinstance(levels, list) and levels != [1, 2, 3]:
        rep.report("catalog-enum", path, "The catalog's levels must be [1, 2, 3]")
    categories = lookup(data, "asi_categories")
    if categories is not None:
        declared_asi = [(item.get("id"), item.get("title")) for item in categories if isinstance(item, dict)] \
            if isinstance(categories, list) else None
        if declared_asi != list(ASI_TITLES.items()):
            rep.report("asi-title", path, "asi_categories must list ASI01 to ASI10 in order with their exact titles")
        if isinstance(categories, list) and len(asi_pages(data)) != len(ASI_TITLES):
            rep.report("asi-title", path, "Give each asi_categories entry the printed start page of its entry ('page')")
    namespace = data.get("namespace") if isinstance(data, dict) else None
    if namespace != FRAMEWORK_NAME:
        rep.report("catalog-field", path, f"The catalog namespace must be {FRAMEWORK_NAME!r}, not {namespace!r}; "
                   "citations use it, for example 'STAND:A-06@0.1'")

    ids: list[str] = []
    critical: set[str] = set()
    lifecycles: dict[str, str] = {}
    titles: dict[str, str] = {}
    supersessions: list[tuple[str, object]] = []
    for position, control in enumerate(controls, 1):
        if not isinstance(control, dict):
            rep.report("catalog-field", path, f"Control #{position} is not an object")
            continue
        cid = control.get("id")
        label = cid if isinstance(cid, str) else f"Control #{position}"
        for name in REQUIRED_CONTROL_FIELDS:
            if name not in control:
                rep.report("catalog-field", path, f"{label} is missing {name!r}")
        if isinstance(cid, str):
            if not CONTROL_ID_FULL.match(cid):
                rep.report("catalog-id", path, f"{cid!r} does not match ^(S|T|A|N|D)-[0-9]{{2}}$")
            elif control.get("pillar") != cid[0]:
                rep.report("catalog-id", path, f"{cid} must have pillar {cid[0]!r}, not {control.get('pillar')!r}")
            if cid in ids:
                rep.report("catalog-id", path, f"Duplicate control ID {cid}")
            ids.append(cid)
        elif "id" in control:
            rep.report("catalog-id", path, f"{label} has a non-string id")
        if "pillar" in control and control.get("pillar") not in PILLARS:
            rep.report("catalog-field", path, f"{label} has unknown pillar {control.get('pillar')!r}")
        for name in TEXT_CONTROL_FIELDS:
            if name in control and not nonempty_string(control[name]):
                rep.report("catalog-field", path, f"{label}: {name} must be non-empty text")
        statement = control.get("statement")
        if nonempty_string(statement) and not BCP14_OBLIGATION.search(statement):
            rep.report("catalog-field", path, f"{label}: the statement needs an obligation in BCP 14 language "
                       "(MUST, MUST NOT, SHALL, SHOULD or REQUIRED); MAY and OPTIONAL alone oblige nothing")
        exemption = control.get("twin_exempt")
        if "twin_exempt" in control and not nonempty_string(exemption):
            rep.report("catalog-field", path, f"{label}: twin_exempt must state why the control has no authorized twin")
        evidence = control.get("evidence")
        if "evidence" in control and not (
                nonempty_string(evidence)
                or (isinstance(evidence, list) and evidence and all(nonempty_string(item) for item in evidence))):
            rep.report("catalog-field", path, f"{label}: evidence must list at least one artifact")
        texts = [control.get(name) for name in TEXT_CONTROL_FIELDS]
        texts += evidence if isinstance(evidence, list) else [evidence]
        if any(isinstance(item, str) and re.search(rf"\b{re.escape(FRAMEWORK_NAME)}\b", item) for item in texts):
            rep.report("framework-name", path, f"{label}: control text must not contain the framework name")
        if any(isinstance(item, str) and INTERNAL_CITATION.search(item) for item in texts):
            rep.report("catalog-field", path, f"{label}: cite printed page numbers as 'p. N' and no internal "
                       "evaluation probes")

        level = control.get("level")
        if "level" in control and (isinstance(level, bool) or level not in (1, 2, 3)):
            rep.report("catalog-enum", path, f"{label}: level must be 1, 2 or 3, not {level!r}")
        severity = control.get("failure_severity")
        if "failure_severity" in control and severity not in FAILURE_SEVERITIES:
            rep.report("catalog-enum", path, f"{label}: failure_severity {severity!r} is not one of " + ", ".join(FAILURE_SEVERITIES))
        scope = control.get("min_evidence_scope")
        if "min_evidence_scope" in control and scope not in EVIDENCE_SCOPES:
            rep.report("catalog-enum", path, f"{label}: min_evidence_scope {scope!r} is not one of " + ", ".join(EVIDENCE_SCOPES))
        verification = control.get("verification")
        if isinstance(verification, str):
            stated = re.search(r"Minimum evidence scope:\s*([a-z-]+)", verification)
            if stated and stated.group(1) != scope:
                rep.report("catalog-field", path, f"{label}: verification states scope {stated.group(1)!r} but min_evidence_scope is {scope!r}")
        rationale = control.get("rationale")
        if isinstance(rationale, str):
            stated = re.search(r"Default failure severity:\s*([a-z]+)", rationale)
            if stated and stated.group(1) != severity:
                rep.report("catalog-field", path, f"{label}: rationale states severity {stated.group(1)!r} but failure_severity is {severity!r}")

        applies = control.get("applies_when")
        if "applies_when" in control:
            if not isinstance(applies, list) or not applies:
                rep.report("applies-when", path, f"{label}: applies_when must be a non-empty list")
            else:
                for item in applies:
                    tokens = item.split("+") if isinstance(item, str) else [None]
                    unknown = [token for token in tokens if token not in vocabulary]
                    if unknown:
                        rep.report("applies-when", path, f"{label}: {item!r} uses tokens outside the vocabulary: "
                                   + ", ".join(repr(token) for token in unknown))
                    elif len(set(tokens)) != len(tokens) or ("all" in tokens and len(tokens) > 1):
                        rep.report("applies-when", path, f"{label}: {item!r} repeats a token or joins 'all' with '+'")

        asi = control.get("asi")
        if "asi" in control:
            if not isinstance(asi, list):
                rep.report("asi-id", path, f"{label}: asi must be a list")
            else:
                for value in asi:
                    if not isinstance(value, str) or not ASI_FULL.match(value):
                        rep.report("asi-id", path, f"{label}: {value!r} is not ASI01 to ASI10")
                if len(set(map(str, asi))) != len(asi):
                    rep.report("asi-id", path, f"{label}: duplicate ASI identifier")

        lifecycle = control.get("lifecycle", "active")
        if isinstance(cid, str):
            lifecycles[cid] = lifecycle
            if nonempty_string(control.get("title")):
                titles[cid] = control["title"]
        if lifecycle not in LIFECYCLES:
            rep.report("catalog-enum", path, f"{label}: lifecycle {lifecycle!r} is not one of " + ", ".join(LIFECYCLES))
        if lifecycle == "withdrawn":
            if not control.get("withdrawn_in") or not control.get("superseded_by"):
                rep.report("catalog-field", path, f"{label}: a withdrawn control needs withdrawn_in and superseded_by")
            supersessions.append((label, control.get("superseded_by")))

        derived = is_critical(control)
        if derived and isinstance(cid, str):
            critical.add(cid)
        if "critical_boundary" in control and control["critical_boundary"] is not derived:
            rep.report("critical-boundary", path,
                       f"{label}: critical_boundary must be {str(derived).lower()} (Level 1 and default severity critical)")

        mappings = control.get("mappings")
        if mappings is not None:
            check_control_mappings(rep, path, label, mappings)

    known = set(ids)
    for label, superseded in supersessions:
        targets = superseded if isinstance(superseded, list) else [superseded]
        for target in targets:
            if target and target not in known:
                rep.report("catalog-field", path, f"{label}: superseded_by names unknown control {target!r}")
    declared_set = lookup(data, "critical_boundary", "critical_boundary_set")
    if isinstance(declared_set, list) and set(declared_set) != critical:
        rep.report("critical-boundary", path, "The declared critical-boundary list differs from the derived set")
    version = data.get("version") if isinstance(data, dict) else None
    cases, retired = check_case_labels(rep, path, controls)
    return Catalog(known, critical, version if isinstance(version, str) else None, lifecycles, titles,
                   cases, retired, [control for control in controls if isinstance(control, dict)],
                   asi_pages(data))


def check_case_labels(rep: Reporter, path: Path, controls: list) -> tuple[dict[str, int], dict[str, set[int]]]:
    """Every hostile case and twin carries a label, (<ID>/C1) then (C2) and so on.

    A case removed after a release leaves a retired marker, (C<n>: retired), in the
    verification text. The marker reserves the number: it counts toward the run
    C1..Cn, is never cited as evidence and is never reused for another case.
    Return the highest case number and the retired numbers of each control.
    """
    counts: dict[str, int] = {}
    retired: dict[str, set[int]] = {}
    for control in controls:
        if not isinstance(control, dict) or not isinstance(control.get("id"), str):
            continue
        cid, text = control["id"], control.get("verification")
        if not isinstance(text, str):
            continue
        labels = [(match.group(1), int(match.group(2)), match.start()) for match in CASE_LABEL.finditer(text)]
        markers = [(match.group(1), int(match.group(2)), match.start()) for match in RETIRED_CASE.finditer(text)]
        numbers = [number for _, number, _ in labels]
        reserved = [number for _, number, _ in markers]
        counts[cid] = max(numbers + reserved, default=0)
        retired[cid] = set(reserved)
        if control.get("lifecycle", "active") != "active":
            continue
        if "twin_exempt" in control:
            if labels:
                rep.report("case-label", path, f"{cid}: twin_exempt is only for a control verified by inspection "
                           "with no labelled cases; label its authorized twin and remove twin_exempt")
            continue
        if not labels:
            rep.report("case-label", path, f"{cid}: label each hostile case and the authorized twin in the "
                       f"verification text as ({cid}/C1), (C2) and so on, or record why there is no twin in "
                       "twin_exempt")
            continue
        if not re.search(r"\bTwins?\b", text):
            rep.report("case-label", path, f"{cid}: name the authorized twin ('Twin: ... (C<n>)') or record why "
                       "there is none in twin_exempt")
        reused = sorted(set(numbers) & set(reserved))
        if reused:
            rep.report("case-label", path, f"{cid}: retired case numbers are never reused: "
                       + ", ".join(f"C{number}" for number in reused))
        ordered = sorted(labels + markers, key=lambda item: item[2])
        if numbers != sorted(set(numbers)) or sorted(numbers + reserved) != list(range(1, counts[cid] + 1)) \
                or ordered[0][0] != cid or any(owner not in (None, cid) for owner, _, _ in ordered):
            rep.report("case-label", path, f"{cid}: case labels must run ({cid}/C1), (C2) and so on, in order, "
                       "with a marker such as (C3: retired) for each retired number")
        twin = text.rfind("Twin")
        if twin >= 0 and labels[-1][2] < twin:
            rep.report("case-label", path, f"{cid}: give the twin a case label")
    for control in controls:
        if not isinstance(control, dict) or not isinstance(control.get("id"), str) \
                or control.get("lifecycle", "active") != "active":
            continue
        cid, evidence = control["id"], control.get("evidence")
        for item in evidence if isinstance(evidence, list) else [evidence]:
            item = item if isinstance(item, str) else ""
            for match in CASE_RANGE.finditer(item):
                if match.group(1) == cid and int(match.group(2)) != counts.get(cid):
                    rep.report("case-label", path, f"{cid}: evidence cites {cid}/C1..C{match.group(2)} but the "
                               f"verification text numbers {counts.get(cid)} cases")
            for match in TEST_ID.finditer(item):
                if item[match.end():].startswith(".."):
                    continue  # A range C1..Cn covers every number of the control; checked above.
                owner, number = match.group(1).split("/C")
                if int(number) in retired.get(owner, set()):
                    rep.report("case-label", path, f"{cid}: evidence cites {match.group(1)}, a retired case")
                elif owner in counts and int(number) > counts[owner]:
                    rep.report("case-label", path, f"{cid}: evidence cites {match.group(1)}, which is not a case "
                               f"in the catalog ({owner} numbers {counts[owner]})")
    return counts, retired


def check_retired_cases(rep: Reporter, path: Path, catalog: Catalog, base: dict[str, set[int]]) -> None:
    """A case number marked retired at the base revision or in any commit since stays reserved.

    Its marker stays in the verification text, and the number is never reused or cited.
    The numbers are then added to the catalog's retired set, so the document citation
    check also rejects them.
    """
    reserved: dict[str, set[int]] = {}
    for cid, numbers in sorted(base.items()):
        if catalog.lifecycle.get(cid, "active") != "active" or cid not in catalog.cases:
            continue
        reserved[cid] = set(numbers)
        for number in sorted(numbers - catalog.retired.get(cid, set())):
            rep.report("case-label", path, f"{cid}/C{number} was marked retired at the base revision or in a "
                       f"commit since; keep its marker (C{number}: retired) and never reuse or cite the number")
    for control in catalog.controls:
        if not isinstance(control.get("id"), str) or control.get("lifecycle", "active") != "active":
            continue
        evidence = control.get("evidence")
        for item in evidence if isinstance(evidence, list) else [evidence]:
            item = item if isinstance(item, str) else ""
            for match in TEST_ID.finditer(item):
                if item[match.end():].startswith(".."):
                    continue
                owner, number = match.group(1).split("/C")
                if int(number) in reserved.get(owner, set()) - catalog.retired.get(owner, set()):
                    rep.report("case-label", path, f"{control['id']}: evidence cites {match.group(1)}, a case "
                               "retired at the base revision or in a commit since")
    for cid, numbers in reserved.items():
        catalog.retired.setdefault(cid, set()).update(numbers)


def check_case_citations(rep: Reporter, docs: dict[str, MarkdownDoc], catalog: Catalog) -> None:
    """A cited catalog case exists and is not retired; a local case uses its own label, <ID>/L<n>.

    Catalog case numbers are never reused or renumbered, so a local case never borrows a C number:
    it takes the next L number of its control, defined once ('<ID>/L<n>:' or '<ID>/L<n> (twin):')
    in exactly one place, and every citation of an L label points at a definition.
    """
    for doc in docs.values():
        for match in TEST_ID.finditer(doc.text):
            cid, number = match.group(1).split("/C")
            count = catalog.cases.get(cid)
            if count is None:
                continue
            after = doc.text[match.end():match.end() + 12]
            if after.startswith(": retired)"):
                continue
            if re.match(r"\s*[(,]\s*local\b", after) is not None:
                rep.report("case-label", doc.path, f"{match.group(1)} is marked local; catalog case labels are "
                           f"never local. Label a local case {cid}/L<n> and drop '(local)'")
            elif int(number) in catalog.retired.get(cid, set()):
                rep.report("case-label", doc.path, f"{match.group(1)} is a retired case; cite a live case, and "
                           f"label a local case {cid}/L<n>")
            elif int(number) > count:
                rep.report("case-label", doc.path, f"{match.group(1)} is not a case in the catalog ({cid} numbers "
                           f"{count}); label a local case {cid}/L<n>")
    defined: dict[str, str] = {}
    cited: list[tuple[MarkdownDoc, str]] = []
    for doc in docs.values():
        for match in LOCAL_DEF.finditer(doc.text):
            label = match.group(1)
            if label in defined:
                rep.report("case-label", doc.path, f"{label} is defined twice (also in {defined[label]}); give each "
                           "local case its own L number and never reuse one")
            else:
                defined[label] = doc.relative
        cited.extend((doc, match.group(1)) for match in LOCAL_ID.finditer(doc.text))
    for doc, label in cited:
        cid = label.split("/L")[0]
        if cid not in catalog.cases:
            rep.report("case-label", doc.path, f"{label} names a control that is not in the catalog")
        elif label not in defined:
            rep.report("case-label", doc.path, f"{label} is cited but never defined; define it once as "
                       f"'{label}: <case>'")


FLOOR_SENTENCE = "MUST be rated"
FLOOR_LISTS = (
    ("references/conformance.md", "a floor applies when the profile or register shows the floor's precondition",
     "applies when that failure is found"),
    (CHANGELOG, "are now floors in the statements of", "."),
)


def floor_ids(text: str, start: str, end: str) -> set[str] | None:
    """Return the control IDs between start and the next end marker after it, or None if start is absent."""
    begin = text.find(start)
    if begin < 0:
        return None
    stop = text.find(end, begin + len(start))
    return set(CONTROL_ID.findall(text[begin:stop if stop >= 0 else len(text)]))


def check_severity_floors(rep: Reporter, root: Path, docs: dict[str, MarkdownDoc], catalog: Catalog) -> None:
    """Every control whose statement sets a severity floor is named in the floor lists of D-06,
    references/conformance.md and CHANGELOG.md, and those lists name no control without a floor."""
    floors = {c["id"] for c in catalog.controls if isinstance(c.get("statement"), str)
              and FLOOR_SENTENCE in c["statement"] and c.get("id") != "D-06"
              and c.get("lifecycle", "active") == "active"}
    gate = next((c for c in catalog.controls if c.get("id") == "D-06"), None)
    sources: list[tuple[Path | str, str, set[str] | None]] = []
    if gate is not None and isinstance(gate.get("statement"), str):
        sources.append((root / CATALOG, "D-06 statement",
                        floor_ids(gate["statement"], "a floor applies when", "applies when that failure is found")))
    for relative, start, end in FLOOR_LISTS:
        doc = docs.get(relative)
        if doc is not None:
            sources.append((doc.path, relative, floor_ids(doc.text, start, end)))
    for path, where, named in sources:
        if named is None:
            if floors:
                expect_fact(rep, path, f"the severity floor list in {where}", "... a floor applies when ...")
            continue
        missing, extra = sorted(floors - named), sorted(named - floors - {"A-08", "D-06"})
        if missing:
            rep.report("severity-floor", path, f"{where}: the floor list omits " + ", ".join(missing)
                       + f", whose statements set a floor ('{FLOOR_SENTENCE}')")
        if extra:
            rep.report("severity-floor", path, f"{where}: the floor list names " + ", ".join(extra)
                       + ", whose statements set no floor")


def expect_fact(rep: Reporter, path: Path | str, what: str, form: str) -> None:
    """Report a stated fact that a check needs but cannot find, so a rewording never disables a check."""
    rep.report("expected-fact-missing", path, f"Cannot find {what}, so it cannot be checked against the catalog. "
               f"Keep it in the form {form!r}, or update scripts/validate.py with the new wording")


def level_split(controls: list) -> tuple[int, int, int]:
    return tuple(sum(1 for c in controls if c.get("level") == level) for level in (1, 2, 3))


def newest_section(doc: MarkdownDoc) -> tuple[str | None, list[tuple[int, str]]]:
    """The heading and the numbered lines of the topmost '## ' release section of a changelog."""
    heading, lines = None, []
    for number, line in enumerate(doc.lines, 1):
        if line.startswith("## "):
            if heading is not None:
                break
            heading = line
            continue
        if heading is not None:
            lines.append((number, line))
    return heading, lines


def check_changelog_summary(rep: Reporter, docs: dict[str, MarkdownDoc], catalog: Catalog) -> None:
    """The newest release section's catalog summary matches the catalog: version, total, per-pillar
    ranges, levels and the critical-boundary count. Older sections describe older catalogs."""
    doc = docs.get(CHANGELOG)
    controls = catalog.listed()
    if doc is None or not controls:
        return
    heading, section = newest_section(doc)
    if heading is None:
        expect_fact(rep, doc.path, "a release section", "## [0.1.0] - Unreleased")
        return
    found_total = found_levels = found_critical = False
    for number, line in section:
        found = re.search(r"Control catalog ([\d.]+)(?: with|,) (\d+) controls", line)
        if found:
            found_total = True
            if catalog.version and found.group(1) != catalog.version:
                rep.report("changelog-summary", doc.path, f"Line {number}: the catalog summary names version "
                           f"{found.group(1)}; the catalog is {catalog.version}")
            if int(found.group(2)) != len(controls):
                rep.report("changelog-summary", doc.path, f"The catalog summary says {found.group(2)} controls; "
                           f"the catalog has {len(controls)}")
            for span in re.finditer(r"\b(S|T|A|N|D)-(\d{2}) to \1-(\d{2})\b", line):
                serials = sorted(int(c["id"][2:]) for c in controls if c["id"][0] == span.group(1))
                if serials and (int(span.group(2)), int(span.group(3))) != (serials[0], serials[-1]):
                    rep.report("changelog-summary", doc.path, f"The catalog summary range {span.group(0)} differs "
                               f"from the catalog ({span.group(1)}-{serials[0]:02d} to {span.group(1)}-{serials[-1]:02d})")
        levels = re.search(r"Levels 1 to 3 \((\d+), (\d+) and (\d+) controls\)", line)
        if levels:
            found_levels = True
            expected = level_split(controls)
            if tuple(int(value) for value in levels.groups()) != expected:
                rep.report("changelog-summary", doc.path, "The level split in the catalog summary differs from the "
                           "catalog (" + ", ".join(map(str, expected)) + ")")
        critical = re.search(r"the (\d+) Level 1 controls whose default failure severity is critical", line)
        if critical:
            found_critical = True
            if int(critical.group(1)) != len(catalog.critical):
                rep.report("changelog-summary", doc.path, f"The catalog summary counts {critical.group(1)} "
                           f"critical-boundary controls; the catalog has {len(catalog.critical)}")
    if not found_total:
        expect_fact(rep, doc.path, "the catalog total in the newest release section",
                    f"Control catalog {catalog.version or 'X.Y.Z'} with N controls")
    if not found_levels:
        expect_fact(rep, doc.path, "the level split in the newest release section", "Levels 1 to 3 (A, B and C controls)")
    if not found_critical:
        expect_fact(rep, doc.path, "the critical-boundary count in the newest release section",
                    "the N Level 1 controls whose default failure severity is critical")


def check_readme_summary(rep: Reporter, docs: dict[str, MarkdownDoc], catalog: Catalog) -> None:
    """The catalog counts stated in README.md (total, per pillar and per level) match the catalog."""
    doc = docs.get("README.md")
    controls = catalog.listed()
    if doc is None or not controls:
        return
    flat = " ".join(" ".join(doc.lines).split())
    letters = tuple(PILLARS)
    expected = (len(controls), *(sum(1 for c in controls if c["id"][0] == letter) for letter in letters))
    want = f"{expected[0]} controls (" + ", ".join(
        f"{letter} {count}" for letter, count in zip(letters, expected[1:])) + ")"
    # Any per-pillar count list, so a list in an outdated pillar order or with old letters is reported too.
    lists = list(re.finditer(r"(\d+) controls \(((?:[A-Z] \d+, )+[A-Z] \d+)\)", flat))
    for found in lists:
        stated = (int(found.group(1)), *(int(part.split()[1]) for part in found.group(2).split(", ")))
        named = tuple(part.split()[0] for part in found.group(2).split(", "))
        if named != letters or stated != expected:
            rep.report("readme-summary", doc.path, f"README.md states {found.group(0)}; the catalog has {want}")
    if not lists:
        expect_fact(rep, doc.path, "the per-pillar control counts in README.md", want)
    split = level_split(controls)
    splits = list(re.finditer(r"(\d+) at Level 1, (\d+) at Level 2, (\d+) at Level 3", flat))
    for found in splits:
        if tuple(int(value) for value in found.groups()) != split:
            rep.report("readme-summary", doc.path, f"README.md states {found.group(0)}; the catalog has "
                       + ", ".join(f"{count} at Level {level}" for level, count in zip((1, 2, 3), split)))
    if not splits:
        expect_fact(rep, doc.path, "the level split in README.md", "A at Level 1, B at Level 2, C at Level 3")
    for found in re.finditer(r"\b(?:catalog of|[Ee]ach of the|holds|[Aa]ll) (\d+) controls\b"
                             r"|\b(\d+) controls with stable IDs\b", flat):
        stated = int(found.group(1) or found.group(2))
        if stated != len(controls):
            rep.report("readme-summary", doc.path, f"README.md states '{found.group(0)}'; the catalog has "
                       f"{len(controls)} controls")


def check_pillar_table(rep: Reporter, docs: dict[str, MarkdownDoc], catalog: Catalog) -> None:
    """The per-pillar ASI count table in docs/pillars.md is recomputed from the catalog."""
    doc = docs.get(PILLARS_DOC)
    controls = catalog.listed()
    if doc is None or not controls:
        return
    found = False
    for header, rows in markdown_tables([strip_code_spans(line) for line in doc.lines]):
        names = [plain_cell(cell) for cell in header]
        if not names or "Controls (L1/L2/L3)" not in names:
            continue
        found = True
        for number, cells in rows:
            values = [plain_cell(cell) for cell in cells]
            letter = values[0][:1] if values else ""
            items = [c for c in controls if c["id"][0] == letter]
            if not items:
                continue
            levels = level_split(items)
            expected = {"Controls (L1/L2/L3)": f"{len(items)} ({levels[0]}/{levels[1]}/{levels[2]})"}
            for name in names:
                if ASI_FULL.match(name):
                    expected[name] = str(sum(1 for c in items if name in (c.get("asi") or [])))
            wrong = [f"{name} {values[index]} (catalog: {expected[name]})" for index, name in enumerate(names)
                     if name in expected and index < len(values) and values[index] != expected[name]]
            if wrong:
                rep.report("pillar-table", doc.path, f"Line {number}: the {letter} row differs from the catalog: "
                           + "; ".join(wrong))
    if not found:
        expect_fact(rep, doc.path, "the per-pillar ASI table", "| Pillar | Controls (L1/L2/L3) | ASI01 | ... |")


def check_level_table(rep: Reporter, docs: dict[str, MarkdownDoc], catalog: Catalog) -> None:
    """The count table and the per-level counts in references/profile-and-levels.md match the catalog."""
    doc = docs.get(PROFILE_DOC)
    controls = catalog.listed()
    if doc is None or not controls:
        return
    columns = ["Pillar", "Level 1", "Level 2", "Level 3", "Total"]
    found = False
    for header, rows in markdown_tables([strip_code_spans(line) for line in doc.lines]):
        if [plain_cell(cell) for cell in header] != columns:
            continue
        found = True
        for number, cells in rows:
            values = [plain_cell(cell) for cell in cells]
            name = values[0] if values else ""
            items = controls if name == "Total" else [c for c in controls if c["id"][0] == name[:1]
                                                      and name[1:2] in ("", " ")]
            if not items or name[:1] not in PILLARS and name != "Total":
                continue
            expected = [str(count) for count in level_split(items)] + [str(len(items))]
            if values[1:5] != expected:
                rep.report("count-drift", doc.path, f"Line {number}: the {name} row reads "
                           f"{' | '.join(values[1:5])}; the catalog has {' | '.join(expected)}")
    if not found:
        expect_fact(rep, doc.path, "the count table", "| " + " | ".join(columns) + " |")
    split = level_split(controls)
    for number, line in enumerate(doc.lines, 1):
        for stated in re.finditer(r"\bLevel ([123])\b[^()\n]{0,80}?\((\d+) controls\b", line):
            level, count = int(stated.group(1)), int(stated.group(2))
            if count != split[level - 1]:
                rep.report("count-drift", doc.path, f"Line {number}: Level {level} is stated as {count} controls; "
                           f"the catalog has {split[level - 1]}")


def check_infographic(rep: Reporter, root: Path, catalog: Catalog) -> None:
    """The per-pillar control counts drawn in, and described by, docs/stand-infographic.svg match the catalog."""
    path = root / INFOGRAPHIC
    controls = catalog.listed()
    if not path.is_file() or not controls:
        return
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return
    expected = [sum(1 for c in controls if c["id"][0] == letter) for letter in PILLARS]
    drawn = [int(value) for value in re.findall(r">\s*(\d+) controls?\s*</text>", text)]
    if not drawn:
        expect_fact(rep, path, "the per-pillar counts drawn in the SVG", "<text ...>6 controls</text>")
    elif drawn != expected:
        rep.report("count-drift", path, "The pillar counts drawn left to right read "
                   + ", ".join(map(str, drawn)) + "; the catalog has " + ", ".join(map(str, expected)))
    desc = re.search(r"<desc\b[^>]*>(.*?)</desc>", text, re.DOTALL)
    described = re.findall(r"\b[Ll]etter ([A-Z])\b.*?\bIt has (\d+) controls?\b", desc.group(1), re.DOTALL) \
        if desc else []
    if not described:
        expect_fact(rep, path, "the per-pillar counts in the SVG description",
                    "Pillar 01, letter S, ... It has 6 controls.")
    else:
        stated = {letter: int(count) for letter, count in described}
        wrong = [f"{letter} {stated.get(letter)} (catalog: {count})" for letter, count in zip(PILLARS, expected)
                 if stated.get(letter) != count]
        if wrong:
            rep.report("count-drift", path, "The SVG description's pillar counts differ from the catalog: "
                       + "; ".join(wrong))


NUMBER_WORDS = {word: number for number, word in enumerate(
    ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"))}


def check_cross_cutting(rep: Reporter, docs: dict[str, MarkdownDoc], catalog: Catalog) -> None:
    """A sentence that lists the cross-cutting controls (those carrying every ASI identifier) lists all of them."""
    expected = catalog.cross_cutting()
    if not catalog.controls:
        return
    for relative, doc in docs.items():
        if relative == CHANGELOG or relative in GENERATED:
            continue
        for number, line in enumerate(doc.lines, 1):
            if "cross-cutting" not in line.lower():
                continue
            for sentence in re.split(r"(?<=[.!?])\s+(?=[A-Z])", strip_code_spans(line)):
                if "cross-cutting" not in sentence.lower():
                    continue
                listed_ids = expand_ids(sentence)
                if not listed_ids:
                    continue
                if listed_ids != expected:
                    rep.report("cross-cutting", doc.path, f"Line {number}: the cross-cutting controls are "
                               + ", ".join(sorted(expected)) + "; the sentence lists " + ", ".join(sorted(listed_ids)))
                word = re.search(r"\b(" + "|".join(NUMBER_WORDS) + r")\b[\w\s-]{0,40}?cross-cutting",
                                 sentence, re.IGNORECASE)
                if word and NUMBER_WORDS[word.group(1).lower()] != len(expected):
                    rep.report("cross-cutting", doc.path, f"Line {number}: '{word.group(1)}' cross-cutting "
                               f"controls; the catalog has {len(expected)}")


def check_eval_cases(rep: Reporter, root: Path, catalog: Catalog) -> None:
    """Control IDs and case numbers cited in evals/cases.json exist; catalog_version is the catalog MAJOR.MINOR."""
    path = root / EVAL_CASES
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return
    strings: list[str] = []

    def walk_json(value: object) -> None:
        if isinstance(value, str):
            strings.append(value)
        elif isinstance(value, list):
            for item in value:
                walk_json(item)
        elif isinstance(value, dict):
            for key, item in value.items():
                strings.append(str(key))
                walk_json(item)
    walk_json(data)
    text = "\n".join(strings)
    unknown = sorted({cid for cid in CONTROL_ID.findall(text) if cid not in catalog.ids})
    if unknown:
        rep.report("unknown-control", path, "Cited control IDs are not in the catalog: " + ", ".join(unknown))
    for match in TEST_ID.finditer(text):
        cid, number = match.group(1).split("/C")
        if cid in catalog.cases and (int(number) > catalog.cases[cid] or int(number) in catalog.retired.get(cid, set())):
            rep.report("case-label", path, f"{match.group(1)} is not a live case in the catalog")
    stated = data.get("catalog_version") if isinstance(data, dict) else None
    if stated is not None and catalog.version:
        wanted = ".".join(catalog.version.split(".")[:2])
        if stated != wanted:
            rep.report("eval-cases", path, f"catalog_version is {stated!r}; claims cite the catalog MAJOR.MINOR, "
                       f"{wanted!r}")


def check_mapping_claims(rep: Reporter, docs: dict[str, MarkdownDoc], catalog: Catalog) -> None:
    """Relations and empty mapping lists stated in frameworks.md agree with the catalog."""
    doc = docs.get(FRAMEWORKS_DOC)
    if doc is None or not catalog.controls:
        return
    by_id = catalog.by_id()
    text = " ".join(" ".join(doc.lines).split())
    for claim in re.finditer(r"(?<![\w-])((?:S|T|A|N|D)-\d{2}) \(([^()]*?), direct\)", text):
        mappings = by_id.get(claim.group(1), {}).get("mappings") or {}
        for ref in (part.strip() for part in claim.group(2).split(",")):
            relations = {entry.get("relation") for framework in mappings.values() if isinstance(framework, list)
                         for entry in framework if isinstance(entry, dict) and entry.get("ref") == ref}
            if relations != {"direct"}:
                rep.report("mapping-claim", doc.path, f"{claim.group(1)} to {ref} is labelled direct, but the catalog "
                           "records " + (", ".join(sorted(map(str, relations))) or "no such mapping"))
    actual = {c["id"] for c in catalog.listed() if not (c.get("mappings") or {}).get("nist")}
    stated = list(re.finditer(r"`nist` lists are empty: ([^.]*)\.", text))
    for empty in stated:
        if expand_ids(empty.group(1)) != actual:
            rep.report("mapping-claim", doc.path, "The list of controls with empty nist mappings differs from the "
                       "catalog: " + ", ".join(sorted(actual)))
    if actual and not stated:
        expect_fact(rep, doc.path, "the list of controls with no NIST mapping", "`nist` lists are empty: A-03, ...")


def check_relation_definitions(rep: Reporter, root: Path, docs: dict[str, MarkdownDoc]) -> None:
    """frameworks.md, which is not rendered, defines each relation in the words of catalog/mappings.json."""
    doc = docs.get(FRAMEWORKS_DOC)
    if doc is None:
        return
    try:
        declared = json.loads((root / MAPPINGS).read_text(encoding="utf-8")).get("relations")
    except (OSError, UnicodeError, json.JSONDecodeError, AttributeError):
        return
    if not isinstance(declared, dict):
        return
    stated = {}
    for line in doc.lines:
        match = re.match(r"\s*- \*\*(direct|partial|supports)\*\*: (.+)$", line)
        if match:
            stated.setdefault(match.group(1), " ".join(match.group(2).split()))
    for relation in RELATIONS:
        wanted = declared.get(relation)
        if not isinstance(wanted, str):
            continue
        if relation not in stated:
            expect_fact(rep, doc.path, f"the definition of the {relation!r} relation", f"- **{relation}**: ...")
        elif stated[relation] != " ".join(wanted.split()):
            rep.report("mapping-claim", doc.path, f"The {relation!r} relation is defined differently from "
                       f"{MAPPINGS} 'relations'; use the same text in both")


def check_control_mappings(rep: Reporter, path: Path, label: str, mappings: object) -> None:
    if not isinstance(mappings, dict):
        rep.report("mapping", path, f"{label}: mappings must be an object of lists")
        return
    for framework, entries in mappings.items():
        if not isinstance(entries, list):
            rep.report("mapping", path, f"{label}: mappings.{framework} must be a list")
            continue
        for entry in entries:
            if not isinstance(entry, dict) or not nonempty_string(entry.get("ref")):
                rep.report("mapping", path, f"{label}: each mappings.{framework} entry needs a ref")
            elif entry.get("relation") not in RELATIONS:
                rep.report("mapping", path, f"{label}: {framework} {entry.get('ref')} relation "
                           f"{entry.get('relation')!r} is not one of " + ", ".join(RELATIONS))


def ledger_ids(data: object) -> list | None:
    if isinstance(data, dict):
        for key in ("entries", "ids", "ledger", "assigned", "controls"):
            if key in data:
                data = data[key]
                break
        else:
            return None
    if not isinstance(data, list):
        return None
    ids = []
    for item in data:
        if isinstance(item, str):
            ids.append(item)
        elif isinstance(item, dict) and isinstance(item.get("id"), str):
            ids.append(item["id"])
        else:
            return None
    return ids


def check_ledger(rep: Reporter, root: Path, catalog: Catalog | None, base: list[str] | None) -> None:
    path = root / LEDGER
    data = load_json(rep, path, "ledger")
    if data is None:
        return
    ids = ledger_ids(data)
    if ids is None:
        rep.report("ledger", path, "Expected a list of IDs or of objects with an 'id'")
        return
    if isinstance(data, dict):
        pattern = data.get("id_pattern")
        if pattern is not None and pattern != CONTROL_ID_FULL.pattern:
            rep.report("ledger", path, f"id_pattern must be {CONTROL_ID_FULL.pattern}")
        statuses = data.get("status_values")
        if statuses is not None and sorted(map(str, statuses)) != sorted(LIFECYCLES):
            rep.report("ledger", path, "status_values must be exactly: " + ", ".join(LIFECYCLES))
        entries = next((data[key] for key in ("entries", "ids", "ledger", "assigned", "controls") if key in data), [])
        for entry in entries:
            if not isinstance(entry, dict) or "status" not in entry:
                continue
            status = entry["status"]
            if status not in LIFECYCLES:
                rep.report("ledger", path, f"{entry.get('id')}: status {status!r} is not one of " + ", ".join(LIFECYCLES))
            elif catalog is not None and entry.get("id") in catalog.lifecycle \
                    and catalog.lifecycle[entry["id"]] != status:
                rep.report("ledger", path, f"{entry['id']}: ledger status {status!r} differs from catalog lifecycle "
                           f"{catalog.lifecycle[entry['id']]!r}")
    seen = set()
    for cid in ids:
        if not CONTROL_ID_FULL.match(cid):
            rep.report("ledger", path, f"{cid!r} does not match ^(S|T|A|N|D)-[0-9]{{2}}$")
        if cid in seen:
            rep.report("ledger", path, f"{cid} is listed twice; IDs are never reused")
        seen.add(cid)
    for pillar in PILLARS:
        serials = sorted(int(cid[2:]) for cid in seen if CONTROL_ID_FULL.match(cid) and cid[0] == pillar)
        missing = sorted(set(range(1, max(serials, default=0) + 1)) - set(serials))
        if missing:
            rep.report("ledger-removed", path, "Ledger serials have gaps (removed entries?): "
                       + ", ".join(f"{pillar}-{serial:02d}" for serial in missing))
    if catalog is not None:
        for cid in sorted(catalog.ids - seen):
            rep.report("ledger-missing", path, f"{cid} is in the catalog but not in the ledger")
        for cid in sorted(seen - catalog.ids):
            rep.report("ledger-removed", path, f"{cid} is in the ledger but missing from the catalog; keep withdrawn controls as tombstones")
    if base is not None:
        for cid in sorted(set(base) - seen):
            rep.report("ledger-removed", path, f"{cid} was in the ledger at the base revision or in a commit "
                       "since and is missing now; never delete a ledger entry")


def git_run(root: Path, *args: str, **options) -> subprocess.CompletedProcess:
    """Run git in root with captured output (text unless text=False is given) and a timeout."""
    options.setdefault("text", True)
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, timeout=60, **options)


def read_base_file(root: Path, revision: str, relative: str) -> tuple[str | None, str | None]:
    """Read a file at a git revision. Return (text or None when absent, error)."""
    try:
        if git_run(root, "rev-parse", "--verify", "--quiet", f"{revision}^{{commit}}").returncode != 0:
            return None, f"cannot resolve git revision {revision!r}"
        if git_run(root, "cat-file", "-e", f"{revision}:{relative}").returncode != 0:
            return None, None
        shown = git_run(root, "show", f"{revision}:{relative}")
    except (OSError, subprocess.SubprocessError) as error:
        return None, f"cannot run git: {error}"
    if shown.returncode != 0:
        return None, shown.stderr.strip() or "git show failed"
    return shown.stdout, None


def read_base_ledger(root: Path, revision: str) -> tuple[list[str] | None, str | None]:
    """Read the ledger at a git revision. Return (ids or None when absent, error)."""
    text, error = read_base_file(root, revision, LEDGER)
    if text is None:
        return None, error
    try:
        ids = ledger_ids(json.loads(text))
    except json.JSONDecodeError as error:
        return None, f"base ledger is not JSON: {error}"
    if ids is None:
        return None, "base ledger has an unrecognized structure"
    return ids, None


def read_base_retired(root: Path, revision: str) -> tuple[dict[str, set[int]] | None, str | None]:
    """Read the retired case numbers of each control at a git revision. Return (numbers or None, error)."""
    text, error = read_base_file(root, revision, CATALOG)
    if text is None:
        return None, error
    try:
        controls = catalog_controls(json.loads(text))
    except json.JSONDecodeError as error:
        return None, f"base catalog is not JSON: {error}"
    if controls is None:
        return None, "base catalog has an unrecognized structure"
    return retired_numbers(controls), None


def retired_numbers(controls: list) -> dict[str, set[int]]:
    """Return the case numbers that carry a retired marker in each control's verification text."""
    return {control["id"]: {int(match.group(2)) for match in RETIRED_CASE.finditer(control["verification"])}
            for control in controls if isinstance(control, dict) and isinstance(control.get("id"), str)
            and isinstance(control.get("verification"), str)}


@dataclass
class History:
    """Ledger IDs and retired case numbers committed after a base revision."""
    ledger: set[str] | None = None
    retired: dict[str, set[int]] | None = None
    skipped: list[str] = field(default_factory=list)


def read_blobs(root: Path, names: list[str]) -> tuple[list[bytes | None] | None, str | None]:
    """Read objects named like REV:PATH with one git process. Return (contents, None for absent ones)."""
    request = "".join(f"{name}\n" for name in names).encode()
    try:
        batch = git_run(root, "cat-file", "--batch", input=request, text=False)
    except (OSError, subprocess.SubprocessError) as error:
        return None, f"cannot run git: {error}"
    if batch.returncode != 0:
        return None, batch.stderr.decode(errors="replace").strip() or "git cat-file failed"
    output, offset, blobs = batch.stdout, 0, []
    for name in names:
        end = output.find(b"\n", offset)
        header = output[offset:end].split() if end >= 0 else []
        if header == [name.encode(), b"missing"]:
            blobs.append(None)
            offset = end + 1
            continue
        if len(header) != 3 or header[1] != b"blob" or not header[2].isdigit():
            return None, f"unexpected git cat-file output for {name}"
        start = end + 1
        offset = start + int(header[2]) + 1
        if offset > len(output):
            return None, f"truncated git cat-file output for {name}"
        blobs.append(output[start:offset - 1])
    return blobs, None


def read_history(root: Path, revision: str, base_has_ledger: bool) -> tuple[History | None, str | None]:
    """Collect the ledger IDs and retired case numbers of every commit in REV..HEAD that changes either file.

    Comparing only the two endpoints misses a number retired in one commit and reused in a
    later one, and an ID added in one commit and deleted in a later one. Only commits that
    change the catalog or the ledger are read (one rev-list and one cat-file process).
    While the base has no ledger, the catalog is not yet published there, so a commit whose
    ledger declares a different id_pattern belongs to an earlier draft ID scheme and is
    skipped (reported in History.skipped). Once the base has a ledger, every commit counts.
    """
    try:
        resolved = git_run(root, "rev-parse", "--verify", "--quiet", f"{revision}^{{commit}}")
        if resolved.returncode != 0:
            return None, f"cannot resolve git revision {revision!r}"
        # --full-history: a merge that leaves a file as it was must not hide the branch's commits.
        listed = git_run(root, "rev-list", "--full-history", f"{resolved.stdout.strip()}..HEAD", "--", CATALOG, LEDGER)
    except (OSError, subprocess.SubprocessError) as error:
        return None, f"cannot run git: {error}"
    if listed.returncode != 0:
        return None, listed.stderr.strip() or "git rev-list failed"
    commits = listed.stdout.split()
    history = History()
    if not commits:
        return history, None
    blobs, error = read_blobs(root, [f"{commit}:{relative}" for commit in commits for relative in (LEDGER, CATALOG)])
    if blobs is None:
        return None, error
    parsed: dict[bytes, object] = {}

    def load(commit: str, relative: str, blob: bytes) -> tuple[object, str | None]:
        if blob not in parsed:
            try:
                parsed[blob] = json.loads(blob.decode("utf-8"))
            except (UnicodeError, json.JSONDecodeError) as error:
                return None, f"{relative} at {commit[:12]} is not JSON: {error}"
        return parsed[blob], None

    for index, commit in enumerate(commits):
        ledger_blob, catalog_blob = blobs[2 * index], blobs[2 * index + 1]
        if ledger_blob is not None:
            data, error = load(commit, LEDGER, ledger_blob)
            if error:
                return None, error
            ids = ledger_ids(data)
            if ids is None:
                return None, f"{LEDGER} at {commit[:12]} has an unrecognized structure"
            declared = data.get("id_pattern") if isinstance(data, dict) else None
            if not base_has_ledger and declared is not None and declared != CONTROL_ID_FULL.pattern:
                history.skipped.append(commit)
                continue
            history.ledger = (history.ledger or set()) | set(ids)
        if catalog_blob is not None:
            data, error = load(commit, CATALOG, catalog_blob)
            if error:
                return None, error
            controls = catalog_controls(data)
            if controls is None:
                return None, f"{CATALOG} at {commit[:12]} has an unrecognized structure"
            history.retired = history.retired or {}
            for cid, numbers in retired_numbers(controls).items():
                history.retired.setdefault(cid, set()).update(numbers)
    return history, None


@dataclass
class Baseline:
    """What --ledger-base compares the working tree with: every ledger ID and retired case
    number at the base revision or in a commit since, and the base catalog's controls and
    version. None means nothing to compare."""
    ledger: list[str] | None = None
    retired: dict[str, set[int]] | None = None
    notes: list[str] = field(default_factory=list)
    controls: list | None = None
    version: str | None = None


def read_baseline(root: Path, revision: str) -> tuple[Baseline, Finding | None]:
    """Read the base revision and the commits since it. Return (baseline, finding when unreadable)."""
    baseline = Baseline()
    ledger, error = read_base_ledger(root, revision)
    if error:
        return baseline, Finding("ledger-removed", LEDGER, f"Cannot compare with the base ledger: {error}")
    baseline.ledger = ledger
    retired, error = read_base_retired(root, revision)
    if error:
        return baseline, Finding("case-label", CATALOG, f"Cannot compare with the base catalog: {error}")
    baseline.retired = retired
    text, _ = read_base_file(root, revision, CATALOG)
    if text is not None:
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = None
        baseline.controls = catalog_controls(data)
        version = data.get("version") if isinstance(data, dict) else None
        baseline.version = version if isinstance(version, str) else None
    history, error = read_history(root, revision, base_has_ledger=ledger is not None)
    if history is None:
        return baseline, Finding("ledger-removed", LEDGER, f"Cannot compare with the commits since {revision}: {error}")
    for commit in history.skipped:
        baseline.notes.append(f"{LEDGER} at {commit[:12]} declares another id_pattern before {revision} has a "
                              "ledger; that draft ID scheme is not compared")
    if history.ledger is not None:
        baseline.ledger = sorted(set(ledger or ()) | history.ledger)
    elif ledger is None:
        baseline.notes.append(f"no {LEDGER} at {revision} or in a commit since; skipping the removal comparison")
    if history.retired is not None:
        merged = {cid: set(numbers) for cid, numbers in (retired or {}).items()}
        for cid, numbers in history.retired.items():
            merged.setdefault(cid, set()).update(numbers)
        baseline.retired = merged
    return baseline, None


def check_mappings(rep: Reporter, root: Path, catalog: Catalog | None) -> None:
    path = root / MAPPINGS
    data = load_json(rep, path, "mapping")
    if data is None:
        return
    frameworks = data.get("frameworks", data) if isinstance(data, dict) else None
    if not isinstance(frameworks, dict):
        rep.report("mapping", path, "Expected an object keyed by framework")
        return
    controls_data = None
    try:
        controls_data = catalog_controls(json.loads((root / CATALOG).read_text(encoding="utf-8")))
    except (OSError, UnicodeError, json.JSONDecodeError):
        pass
    declared = frameworks.get("relations")
    if isinstance(declared, (dict, list)) and sorted(declared) != sorted(RELATIONS):
        rep.report("mapping", path, "relations must define exactly: " + ", ".join(RELATIONS))
    for key, framework in frameworks.items():
        if not isinstance(framework, dict) or key == "relations":
            continue  # catalog metadata such as version, license or checked date
        if not isinstance(framework.get("refs"), dict):
            rep.report("mapping", path, f"{key}: expected an object with a 'refs' map")
            continue
        urls = framework.get("requirement_urls")
        if isinstance(urls, dict):
            for requirement, url in urls.items():
                if isinstance(url, str) and AIUC_ID.match(str(requirement)):
                    try:
                        check_aiuc_link(rep, path, f"{key}.requirement_urls", url, urlsplit(url), requirement)
                    except ValueError:
                        rep.report("mapping", path, f"{key}: invalid URL for {requirement}")
        if not nonempty_string(framework.get("source_version")):
            rep.report("mapping", path, f"{key}: record the source_version")
        for cid, entries in framework["refs"].items():
            if catalog is not None and cid not in catalog.ids:
                rep.report("mapping", path, f"{key}: {cid} is not a catalog control")
            if not isinstance(entries, list):
                rep.report("mapping", path, f"{key}.{cid}: expected a list")
                continue
            for entry in entries:
                if not isinstance(entry, dict) or not nonempty_string(entry.get("ref")):
                    rep.report("mapping", path, f"{key}.{cid}: each entry needs a ref")
                    continue
                if entry.get("relation") not in RELATIONS:
                    rep.report("mapping", path, f"{key}.{cid} {entry['ref']}: relation {entry.get('relation')!r} is not one of " + ", ".join(RELATIONS))
                if not nonempty_string(entry.get("justification")):
                    rep.report("mapping", path, f"{key}.{cid} {entry['ref']}: add a justification")
                url = entry.get("source_url")
                if isinstance(url, str) and AIUC_ID.match(entry["ref"]):
                    try:
                        check_aiuc_link(rep, path, f"{key}.{cid}", url, urlsplit(url), entry["ref"])
                    except ValueError:
                        rep.report("mapping", path, f"{key}.{cid}: invalid source_url {url!r}")
        if isinstance(urls, dict):
            check_requirement_application(rep, root, path, key, framework)
        if controls_data is None:
            continue
        for control in controls_data:
            if not isinstance(control, dict) or not isinstance(control.get("mappings"), dict):
                continue
            cid = control.get("id")
            if key not in control["mappings"]:
                continue
            summary = {(e.get("ref"), e.get("relation")) for e in control["mappings"][key] if isinstance(e, dict)}
            detail = {(e.get("ref"), e.get("relation")) for e in framework["refs"].get(cid, []) if isinstance(e, dict)}
            if summary != detail:
                rep.report("mapping", path, f"{key}.{cid}: refs and relations differ from {CATALOG}")


APPLICATION_VALUES = ("Mandatory", "Optional")
FRAMEWORKS_DOC = "references/frameworks.md"


def check_requirement_application(rep: Reporter, root: Path, path: Path, key: str, framework: dict) -> None:
    """Every cited AIUC-1 requirement records whether it is mandatory or optional, and the
    requirement table in references/frameworks.md agrees with that record."""
    application = framework.get("application")
    if not isinstance(application, dict):
        rep.report("mapping", path, f"{key}: record an 'application' map (Mandatory or Optional) for each cited requirement")
        return
    for requirement, value in application.items():
        if value not in APPLICATION_VALUES:
            rep.report("mapping", path, f"{key}.application.{requirement}: {value!r} is not one of "
                       + ", ".join(APPLICATION_VALUES))
    cited = {entry["ref"].split(".")[0] for entries in framework["refs"].values() if isinstance(entries, list)
             for entry in entries if isinstance(entry, dict) and nonempty_string(entry.get("ref"))}
    missing = sorted(cited - set(application))
    if missing:
        rep.report("mapping", path, f"{key}: no application value for cited requirements " + ", ".join(missing))
    doc = root / FRAMEWORKS_DOC
    try:
        lines = doc.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return
    for header, rows in markdown_tables(lines):
        column = next((i for i, cell in enumerate(header) if plain_cell(cell).startswith("Application")), None)
        if column is None:
            continue
        for number, cells in rows:
            requirement = plain_cell(cells[0]) if cells else ""
            if not AIUC_ID.match(requirement) or column >= len(cells):
                continue
            stated = plain_cell(cells[column]).split(";")[0].strip()
            recorded = application.get(requirement)
            if recorded is not None and stated != recorded:
                rep.report("mapping", doc, f"Line {number}: {requirement} is {stated or 'blank'} here but "
                           f"{recorded} in {MAPPINGS}")


# ---------------------------------------------------------------------------
# Identifier registries (catalog/nist-ids.json and catalog/aiuc1-controls.json)


NIST_MENTION = re.compile(r"\b(?:GOVERN|MAP|MEASURE|MANAGE) \d+\.\d+\b|\b(?:GV|MP|MS|MG)-\d+\.\d+-\d{3}\b")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MONTH_DATE = re.compile(r"(January|February|March|April|May|June|July|August|September|October|November"
                        r"|December) (\d{1,2}), (\d{4})")


def mapping_entries(root: Path, framework: str) -> list[tuple[str, dict]]:
    """(control ID, entry) for each mapping entry of a framework in catalog/mappings.json."""
    try:
        data = json.loads((root / MAPPINGS).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return []
    section = data.get(framework) if isinstance(data, dict) else None
    refs = section.get("refs") if isinstance(section, dict) else None
    if not isinstance(refs, dict):
        return []
    return [(cid, entry) for cid, entries in refs.items() if isinstance(entries, list)
            for entry in entries if isinstance(entry, dict) and nonempty_string(entry.get("ref"))]


def check_nist_registry(rep: Reporter, root: Path, docs: dict[str, MarkdownDoc]) -> None:
    """Every NIST identifier is an AI RMF 1.0 subcategory or AI 600-1 action in the pinned registry,
    and every nist justification ends with a citation whose table and page match the registry."""
    path = root / NIST_REGISTRY
    registry = load_json(rep, path, "nist-id")
    if registry is None:
        return
    subcategories = registry.get("subcategories") if isinstance(registry, dict) else None
    actions = registry.get("actions") if isinstance(registry, dict) else None
    if not isinstance(subcategories, dict) or not isinstance(actions, dict):
        rep.report("nist-id", path, "Expected 'subcategories' and 'actions' maps")
        return
    for ref, entry in subcategories.items():
        if not NIST_SUBCATEGORY.match(ref) or not isinstance(entry, dict) \
                or type(entry.get("table")) is not int or type(entry.get("page")) is not int:
            rep.report("nist-id", path, f"{ref}: a subcategory needs the form 'GOVERN 1.1' and integer table and page")
        elif entry["table"] != 1 + ("GOVERN", "MAP", "MEASURE", "MANAGE").index(ref.split()[0]):
            rep.report("nist-id", path, f"{ref}: AI 100-1 lists its function in Table "
                       f"{1 + ('GOVERN', 'MAP', 'MEASURE', 'MANAGE').index(ref.split()[0])}")
    for ref, entry in actions.items():
        if not NIST_ACTION.match(ref) or not isinstance(entry, dict) or type(entry.get("page")) is not int:
            rep.report("nist-id", path, f"{ref}: an action needs the form 'GV-1.1-001' and an integer page")
        elif nist_function(ref) not in subcategories:
            rep.report("nist-id", path, f"{ref}: its subcategory {nist_function(ref)} is not in the registry")

    for cid, entry in mapping_entries(root, "nist"):
        ref, where = entry["ref"], f"nist.{cid} {entry['ref']}"
        citation = NIST_CITATION.search(str(entry.get("justification", "")))
        if NIST_SUBCATEGORY.match(ref):
            known = subcategories.get(ref)
            if not isinstance(known, dict):
                rep.report("nist-id", root / MAPPINGS, f"{where}: not an AI RMF 1.0 subcategory in {NIST_REGISTRY}")
            elif not citation or citation.group(1) != "100" \
                    or (citation.group(2), citation.group(3)) != (str(known.get("table")), str(known.get("page"))):
                rep.report("nist-id", root / MAPPINGS, f"{where}: end the justification with "
                           f"[AI 100-1 Table {known.get('table')} p.{known.get('page')}]")
        elif NIST_ACTION.match(ref):
            known = actions.get(ref)
            if not isinstance(known, dict):
                rep.report("nist-id", root / MAPPINGS, f"{where}: not an AI 600-1 action in {NIST_REGISTRY}")
            elif not citation or citation.group(1) != "600" or citation.group(2) is not None \
                    or citation.group(3) != str(known.get("page")):
                rep.report("nist-id", root / MAPPINGS, f"{where}: end the justification with "
                           f"[AI 600-1 p.{known.get('page')}]")
        else:
            rep.report("nist-id", root / MAPPINGS, f"{where}: use an AI RMF 1.0 subcategory ('GOVERN 1.1') or an "
                       "AI 600-1 action ID ('GV-1.1-001')")
    for relative, doc in docs.items():
        for found in sorted(set(NIST_MENTION.findall(" ".join(doc.lines)))):
            if found not in subcategories and found not in actions:
                rep.report("nist-id", doc.path, f"{found} is not an AI RMF 1.0 subcategory or AI 600-1 action "
                           f"in {NIST_REGISTRY}")


def release_date(text: object) -> str | None:
    """The ISO date of an AIUC-1 release named like 'AIUC-1 release of July 15, 2026'."""
    if not isinstance(text, str):
        return None
    match = MONTH_DATE.search(text)
    if not match:
        return None
    try:
        return dt.datetime.strptime(match.group(0), "%B %d, %Y").date().isoformat()
    except ValueError:
        return None


def check_aiuc_registry(rep: Reporter, root: Path) -> None:
    """Every cited AIUC-1 control is in the registry with its status, subject and checked release;
    a justification that opens 'Core control' or 'Supplemental control' agrees with the status."""
    path = root / AIUC_REGISTRY
    registry = load_json(rep, path, "aiuc-registry")
    if registry is None:
        return
    controls = registry.get("controls") if isinstance(registry, dict) else None
    requirements = registry.get("requirements") if isinstance(registry, dict) else None
    if not isinstance(controls, dict) or not isinstance(requirements, dict):
        rep.report("aiuc-registry", path, "Expected 'requirements' and 'controls' maps")
        return
    for requirement, entry in requirements.items():
        capabilities = entry.get("capabilities") if isinstance(entry, dict) else None
        if not re.fullmatch(r"[A-F]\d{3}", requirement) or not isinstance(capabilities, list) or not capabilities \
                or not all(nonempty_string(item) for item in capabilities):
            rep.report("aiuc-registry", path, f"{requirement}: a requirement needs the form 'B006' and a non-empty "
                       "capabilities list")
    for ref, entry in controls.items():
        if not AIUC_CONTROL.match(ref) or not isinstance(entry, dict):
            rep.report("aiuc-registry", path, f"{ref}: a control needs the form 'B006.1' and an object")
            continue
        if entry.get("status") not in ("core", "supplemental"):
            rep.report("aiuc-registry", path, f"{ref}: status must be core or supplemental")
        if not nonempty_string(entry.get("title")):
            rep.report("aiuc-registry", path, f"{ref}: give the subject in this project's own words")
        if not isinstance(entry.get("release"), str) or not ISO_DATE.match(entry["release"]):
            rep.report("aiuc-registry", path, f"{ref}: record the release it was checked against (YYYY-MM-DD)")
        if ref.split(".")[0] not in requirements:
            rep.report("aiuc-registry", path, f"{ref}: record the capabilities of requirement {ref.split('.')[0]}")

    try:
        mappings = json.loads((root / MAPPINGS).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        mappings = {}
    section = mappings.get("aiuc1") if isinstance(mappings, dict) else None
    mapped_version = section.get("source_version") if isinstance(section, dict) else None
    mapped_release = release_date(mapped_version)
    if registry.get("source_version") != mapped_version:
        rep.warn("aiuc-registry", path, f"The registry was checked against {registry.get('source_version')!r}, "
                 f"but the mappings name {mapped_version!r}; recheck every control below")
    cited: set[str] = set()
    for cid, entry in mapping_entries(root, "aiuc1"):
        ref = entry["ref"]
        cited.add(ref)
        known = controls.get(ref) if AIUC_CONTROL.match(ref) else requirements.get(ref)
        if not isinstance(known, dict):
            rep.report("aiuc-registry", root / MAPPINGS, f"aiuc1.{cid} {ref}: not in {AIUC_REGISTRY}; check the "
                       "identifier against the AIUC-1 release and record it")
            continue
        opening = re.match(r"\s*(Core|Supplemental) control", str(entry.get("justification", "")))
        if opening and AIUC_CONTROL.match(ref) and opening.group(1).lower() != known.get("status"):
            rep.report("aiuc-registry", root / MAPPINGS, f"aiuc1.{cid} {ref}: the justification opens "
                       f"'{opening.group(1)} control' but {AIUC_REGISTRY} records it as {known.get('status')}")
    for ref, entry in controls.items():
        if ref not in cited:
            rep.report("aiuc-registry", path, f"{ref} is cited by no mapping; remove it from the registry")
        elif mapped_release and isinstance(entry, dict) and entry.get("release") != mapped_release:
            rep.warn("aiuc-registry", path, f"{ref} was last checked against the {entry.get('release')} release; "
                     f"the mappings use {mapped_release}")
    used = {ref.split(".")[0] for ref in cited}
    for requirement in sorted(set(requirements) - used):
        rep.report("aiuc-registry", path, f"{requirement} is cited by no mapping; remove it from the registry")



# ---------------------------------------------------------------------------
# Cross-file consistency


def expand_ids(text: str) -> set[str]:
    found = set(CONTROL_ID.findall(text))
    for match in CONTROL_RANGE.finditer(text):
        start, end = match.group(1), match.group(2)
        if start[0] == end[0] and int(start[2:]) <= int(end[2:]):
            found.update(f"{start[0]}-{serial:02d}" for serial in range(int(start[2:]), int(end[2:]) + 1))
    return found


EXAMPLE_START = re.compile(r"^\*\*(\d+)\. [^*]+\*\* One context\.", re.MULTILINE)
EXAMPLE_END = re.compile(r"^(?:\*\*\d+\. |#{1,6} )", re.MULTILINE)
PROPERTY_LETTERS = (("untrusted-input", "U"), ("sensitive-data", "D"), ("external-effect", "X"))


def applicable_ids(controls: list, tokens: set[str]) -> list:
    """Listed controls with at least one applies_when alternative whose tokens all hold."""
    return [c for c in controls if any(all(token in tokens for token in str(alternative).split("+"))
                                       for alternative in c.get("applies_when") or [])]


def check_worked_examples(rep: Reporter, docs: dict[str, MarkdownDoc], catalog: Catalog) -> None:
    """Each single-context worked example in references/profile-and-levels.md states counts and a
    not-applicable list that the catalog reproduces from its stated properties and tags."""
    doc = docs.get(PROFILE_DOC)
    if doc is None:
        return
    listed = catalog.listed()
    for start in EXAMPLE_START.finditer(doc.text):
        after = EXAMPLE_END.search(doc.text, start.end())
        block = doc.text[start.end():after.start() if after else len(doc.text)]
        name = f"worked example {start.group(1)}"
        tags = re.search(r"Tags: (.*?)\.(?:\s|$)", block)
        if not tags:
            expect_fact(rep, doc.path, f"the tags of {name}", "Tags: a, b, c.")
            continue
        tokens = {"all"} | {tag.strip() for tag in re.sub(r"\([^()]*\)", "", tags.group(1)).split(",")}
        tokens |= {prop for prop, letter in PROPERTY_LETTERS if re.search(rf"\b{letter} present\b", block)}
        found = applicable_ids(listed, tokens)
        computed = [sum(1 for c in found if c.get("level", 0) <= level) for level in (1, 2, 3)]
        stated = re.search(r"(\d+) applicable controls at Level 1, (\d+) through Level 2 and (\d+) through Level 3",
                           block)
        single = re.search(r"Level 1, with (\d+) applicable controls", block)
        if stated:
            claimed = [int(value) for value in stated.groups()]
        elif single:
            claimed = [int(single.group(1)), computed[1], computed[2]]
        else:
            expect_fact(rep, doc.path, f"the applicable-control counts of {name}",
                        "N applicable controls at Level 1, N through Level 2 and N through Level 3")
            continue
        if claimed != computed:
            rep.report("worked-example", doc.path, f"{name} states {claimed[0]}, {claimed[1]} and {claimed[2]} "
                       f"applicable controls through Levels 1, 2 and 3; its properties and tags give {computed[0]}, "
                       f"{computed[1]} and {computed[2]}")
        absent = re.search(r"The other (\d+) controls are not applicable because their tags are absent: (.*?)\.\n",
                           block)
        if absent:
            missing = sorted({c["id"] for c in listed} - {c["id"] for c in found})
            named = sorted(expand_ids(absent.group(2)))
            if named != missing or int(absent.group(1)) != len(missing):
                rep.report("worked-example", doc.path, f"{name} lists not-applicable controls "
                           f"{', '.join(named)}; its properties and tags leave {', '.join(missing)}")


def check_control_citations(rep: Reporter, doc: MarkdownDoc, catalog: Catalog | None) -> None:
    if catalog is not None:
        unknown = sorted({cid for cid in CONTROL_ID.findall(doc.text) if cid not in catalog.ids})
        if unknown:
            rep.report("unknown-control", doc.path, "Cited control IDs are not in the catalog: " + ", ".join(unknown))
    for number, line in enumerate(doc.lines, 1):
        prose = strip_code_spans(line)
        prose = re.sub(r"\]\([^)]*\)", "]", prose)
        prose = re.sub(r"<[^>]+>", " ", URL.sub(" ", prose))
        bad = LOWER_ID.findall(prose) + UNHYPHENATED_ID.findall(prose)
        if bad:
            rep.report("id-form", doc.path, f"Line {number}: write control IDs as an uppercase letter, hyphen and two digits: "
                       + ", ".join(bad))


def check_critical_blocks(rep: Reporter, root: Path, docs: dict[str, MarkdownDoc], catalog: Catalog) -> None:
    for relative in CRITICAL_BOUNDARY_FILES:
        doc = docs.get(relative)
        if doc is None:
            continue
        starts, ends = doc.text.count(CRITICAL_START), doc.text.count(CRITICAL_END)
        begin, finish = doc.text.find(CRITICAL_START), doc.text.find(CRITICAL_END)
        if starts != 1 or ends != 1 or finish < begin:
            rep.report("critical-boundary", doc.path, f"Mark the critical-boundary list once with {CRITICAL_START} and {CRITICAL_END}")
            continue
        listed = expand_ids(doc.text[begin + len(CRITICAL_START):finish])
        missing, extra = sorted(catalog.critical - listed), sorted(listed - catalog.critical)
        if missing:
            rep.report("critical-boundary", doc.path, "Critical-boundary list is missing: " + ", ".join(missing))
        if extra:
            rep.report("critical-boundary", doc.path, "Critical-boundary list includes non-members: " + ", ".join(extra))


def enumerates(lines: list[str], values: tuple[str, ...]) -> bool:
    """True when one line names every value, or a table column or list gives exactly the values in order."""
    patterns = [re.compile(rf"(?<![\w-]){re.escape(value)}(?![\w-])") for value in values]
    if any(all(pattern.search(line) for pattern in patterns) for line in lines):
        return True
    for _, rows in markdown_tables(lines):
        if [plain_cell(cells[0]) for _, cells in rows] == list(values):
            return True
    heads: list[str] = []
    for line in lines + [""]:
        item = re.match(r"^\s*(?:[-*+]|\d+[.)])\s+(?:\*\*|`)?([a-z][a-z-]*)", line)
        if item:
            heads.append(item.group(1))
            continue
        if heads == list(values):
            return True
        if line.strip():
            heads = []
    return False


def check_control_headings(rep: Reporter, docs: dict[str, MarkdownDoc], catalog: Catalog) -> None:
    """Each control sits in its pillar file under the heading '### <ID> <Title>'."""
    for cid, title in sorted(catalog.titles.items()):
        if not CONTROL_ID_FULL.match(cid):
            continue
        doc = docs.get(f"references/controls/{cid[0]}.md")
        if doc is not None and f"### {cid} {title}" not in (line.rstrip() for line in doc.lines):
            rep.report("control-heading", doc.path, f"Missing the heading '### {cid} {title}'")


TEST_ID = re.compile(r"(?<![\w-])((?:S|T|A|N|D)-\d{2}/C\d+)(?![\w/])")
LOCAL_ID = re.compile(r"(?<![\w-])((?:S|T|A|N|D)-\d{2}/L\d+)(?![\w/])")
LOCAL_DEF = re.compile(r"(?<![\w-])((?:S|T|A|N|D)-\d{2}/L\d+)(?: \(twin\))?:")
PATTERN_TWIN = re.compile(r"(?<![\w-])((?:S|T|A|N|D)-\d{2}/[CL]\d+)\s*\(twin\)")


def record_example(doc: MarkdownDoc) -> str | None:
    """Return the fenced compact change record example (first line 'Change: '), if any."""
    lines = doc.text.split("\n")
    for index, line in enumerate(lines):
        if line.startswith("Change: ") and index and FENCE.match(lines[index - 1]):
            end = next((j for j in range(index, len(lines)) if FENCE.match(lines[j])), len(lines))
            return "\n".join(lines[index:end])
    return None


def check_record_examples(rep: Reporter, docs: dict[str, MarkdownDoc]) -> None:
    """The canonical compact record is identical everywhere and cites tests with their roles in patterns.md."""
    skill = docs.get("SKILL.md")
    if skill is not None and record_example(skill) is not None:
        rep.report("record-example", skill.path, "Keep the compact change record example out of SKILL.md; link to "
                   "the template skeleton and the worked example in references/profile-and-levels.md")
    examples = {name: record_example(docs[name]) for name in RECORD_EXAMPLE_FILES if name in docs}
    present = {name: text for name, text in examples.items() if text is not None}
    if not present:
        return
    reference = next(iter(present.values()))
    for name, text in examples.items():
        if text is None:
            rep.report("record-example", docs[name].path, "Add the compact change record example that the other files show")
        elif reference is not None and text != reference:
            rep.report("record-example", docs[name].path, "The compact change record example differs from "
                       + next(iter(present)))
    patterns = docs.get(PATTERNS)
    if patterns is None:
        return
    known = set(TEST_ID.findall(patterns.text))
    twins = set(PATTERN_TWIN.findall(patterns.text))
    for name, text in present.items():
        for item in re.split(r",\s*", text):
            for test_id in TEST_ID.findall(item):
                if test_id not in known:
                    rep.report("record-example", docs[name].path, f"{test_id} is not defined in {PATTERNS}")
                elif ("twin" in item.split()) != (test_id in twins):
                    role = "twin" if test_id in twins else "hostile case"
                    rep.report("record-example", docs[name].path,
                               f"{test_id} is the {role} in {PATTERNS}; label it the same way")


RECORD_TEMPLATE = "assets/agent-security-record.md"
RECORD_FIELDS = (
    ("T-12", "egress mode per tool", "<mode (allowlist or public-internet) and tool>"),
    ("A-06", "read-tool exemption parameters", "Read-tool exemption"),
    ("A-06", "per-run bound and ceiling", "<ceiling in bits"),
    ("S-06", "secret class entropy", "<secret class: entropy in bits"),
    ("A-12", "agent-capable principal browser", "Principal browser agent-capable"),
    ("T-17", "browser context rule", "Browser context"),
    ("S-05", "impact threshold", "impact threshold"),
)


def check_record_template(rep: Reporter, docs: dict[str, MarkdownDoc]) -> None:
    """The record template carries a field for each record obligation that a control statement sets."""
    doc = docs.get(RECORD_TEMPLATE)
    if doc is None:
        return
    for cid, what, snippet in RECORD_FIELDS:
        if snippet not in doc.text:
            rep.report("record-template", doc.path, f"Add the {what} field that {cid} requires the record to state "
                       f"(expected text: {snippet!r})")


def check_enum_docs(rep: Reporter, docs: dict[str, MarkdownDoc]) -> None:
    for relative in ENUM_FILES:
        doc = docs.get(relative)
        if doc is None:
            continue
        lines = [strip_code_spans(line) for line in doc.text.split("\n")]
        for label, values in (("status", STATUS_ENUM), ("evidence scope", EVIDENCE_SCOPES)):
            if not enumerates(lines, values):
                rep.report("enum-doc", doc.path, f"Enumerate the closed {label} enum exactly, in one line, "
                           "table column or list, in this order: " + ", ".join(values))


def check_identity(rep: Reporter, root: Path, docs: dict[str, MarkdownDoc], bundle_mode: bool) -> None:
    for relative in IDENTITY_FILES:
        if bundle_mode and not in_bundle(relative):
            continue
        doc = docs.get(relative)
        if doc is None:
            continue
        flat = " ".join(doc.text.replace("*", "").split())
        missing = [phrase for phrase in (PRINCIPLE, *PILLARS.values()) if phrase not in flat]
        if missing:
            rep.report("framework-identity", doc.path, "Missing the exact principle or pillar names: "
                       + "; ".join(missing))


def check_feature_routes(rep: Reporter, docs: dict[str, MarkdownDoc], catalog: Catalog | None) -> None:
    """The SKILL.md Step 2 routing table is normative: each ID sits under its level ('L2:', 'L3:'), and each
    feature row lists every control whose applies_when names the feature's tag, at every level."""
    doc = docs.get("SKILL.md")
    if doc is None or catalog is None or not catalog.controls:
        return
    by_id = catalog.by_id()
    seen_rows: set[str] = set()
    tables = 0
    for header, rows in markdown_tables([strip_code_spans(line) for line in doc.lines]):
        if tuple(plain_cell(cell) for cell in header[:2]) != ROUTING_HEADER:
            continue
        tables += 1
        for number, cells in rows:
            if len(cells) < 2:
                continue
            label = plain_cell(cells[0])
            seen_rows.add(label)
            for segment in cells[1].split(";"):
                prefix = re.match(r"\s*L([123]):", segment)
                level = int(prefix.group(1)) if prefix else 1
                for cid in sorted(expand_ids(segment)):
                    control = by_id.get(cid)
                    if control is None:
                        continue
                    if is_withdrawn(control):
                        rep.report("routing", doc.path, f"Line {number}: {cid} is withdrawn; route its successors")
                    elif control.get("level") != level:
                        rep.report("routing", doc.path, f"Line {number}: {cid} is a Level {control.get('level')} "
                                   f"control; list it after 'L{control.get('level')}:'"
                                   if control.get("level") != 1 else
                                   f"Line {number}: {cid} is a Level 1 control; list it before any 'L2:' or 'L3:'")
            tag = FEATURE_ROUTES.get(label)
            if tag is None:
                continue
            listed_ids = expand_ids(cells[1])
            missing = sorted(
                c["id"] for c in catalog.listed()
                if any(tag in str(clause).split("+") for clause in c.get("applies_when") or [])
                and c["id"] not in listed_ids)
            if missing:
                rep.report("routing", doc.path, f"Line {number}: the '{label}' row misses controls whose "
                           f"applies_when names {tag}: " + ", ".join(missing))
    if not tables:
        expect_fact(rep, doc.path, "the Step 2 routing table", "| Trigger location | Control IDs |")
        return
    for label in FEATURE_ROUTES:
        if label not in seen_rows:
            expect_fact(rep, doc.path, f"the routing row '{label}'", f"| {label} | <control IDs> |")


GENERIC_WORDS = {
    "a", "an", "and", "or", "the", "of", "by", "for", "to", "in", "on", "its", "their", "them", "they", "between",
    "used", "code", "configuration", "config", "settings", "setting", "file", "handling", "version", "content",
    "entry", "point", "mechanism", "boundary", "agent", "including", "other", "any", "all", "change", "new", "use",
}


def word_stem(word: str) -> str:
    word = word.lower().strip("'")
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    if word.endswith(("sses", "xes", "ches", "shes")):
        return word[:-2]
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def stems(text: str) -> set[str]:
    return {word_stem(word) for word in re.findall(r"[A-Za-z0-9]+", text)}


def stem_matches(stem: str, vocabulary: set[str]) -> bool:
    """True when the stem, or a word sharing its first five letters with it, occurs in the vocabulary."""
    if stem in vocabulary:
        return True
    return len(stem) >= 5 and any(len(other) >= 5 and (other.startswith(stem) or stem.startswith(other))
                                  for other in vocabulary)


def trigger_items(bullet: str) -> list[str]:
    """Split a Trigger locations bullet into the locations it names."""
    text = re.sub(r"\([^)]*\)", " ", bullet).strip().rstrip(";.").strip()
    text = re.sub(r",\s*including\b.*$", "", text)
    items = []
    for part in re.split(r"[,;]", text):
        part = re.sub(r"^\s*(?:and|or)\s+", "", part).strip()
        if part:
            items.append(part)
    return items


def check_trigger_list(rep: Reporter, docs: dict[str, MarkdownDoc]) -> None:
    """The AGENTS.md snippet decides whether the skill loads at all, so its trigger list either points to the
    normative list in references/profile-and-levels.md or names every location that list names."""
    profile, snippet = docs.get(PROFILE_DOC), docs.get(SNIPPET)
    if profile is None or snippet is None:
        return
    bullets: list[str] = []
    inside = False
    for line in profile.lines:
        heading = ATX.match(line)
        if heading:
            if inside:
                break
            inside = plain_cell(heading.group(2) or "").lower() == "trigger locations"
            continue
        if inside and LIST_ITEM.match(line):
            bullets.append(re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", line))
        elif inside and bullets and line.strip() and not line[:1].isspace():
            break
    if not bullets:
        expect_fact(rep, profile.path, "the Trigger locations list", "### Trigger locations, then one bullet each")
        return
    text = " ".join(snippet.text.split())
    if "profile-and-levels.md" in text and re.search(r"trigger locations?", text, re.IGNORECASE):
        return
    stated = re.search(r"[Tt]rigger locations (?:include|are)\b:?(.*?)(?:\.\s|\.$)", text)
    if not stated:
        rep.report("trigger-list", snippet.path, "Name every trigger location from references/profile-and-levels.md "
                   "('Trigger locations include ...'), or point to that list by name")
        return
    vocabulary = stems(stated.group(1))
    missing = []
    for bullet in bullets:
        for item in trigger_items(bullet):
            words = {stem for stem in stems(item) if stem not in GENERIC_WORDS and len(stem) > 1}
            if words and not any(stem_matches(stem, vocabulary) for stem in words):
                missing.append(item)
    if missing:
        rep.report("trigger-list", snippet.path, "The trigger list names nothing for these locations from "
                   f"{PROFILE_DOC}: " + "; ".join(missing) + ". Add them, or point to that list instead")


def check_owasp_view(rep: Reporter, docs: dict[str, MarkdownDoc], catalog: Catalog | None = None) -> None:
    doc = docs.get(OWASP_VIEW)
    if doc is None:
        return
    expected = list(ASI_TITLES)
    prose = [strip_code_spans(line) for line in doc.lines]
    for header, rows in markdown_tables(prose):
        title_column = next((i for i, cell in enumerate(header) if "title" in plain_cell(cell).lower()
                             or plain_cell(cell).lower() in {"risk", "name"}), None)
        key_column = next((i for i, cell in enumerate(header) if plain_cell(cell).lower().startswith("key control")),
                          None)
        entries = []
        for number, cells in rows:
            match = re.match(r"^(ASI\d{2})\b(?:\s*:\s*(.+?))?(?:\s*\((?:pp?\.)[^)]*\))?$", plain_cell(cells[0]))
            if not match:
                continue
            title = match.group(2)
            if title is None:
                column = title_column if title_column not in (None, 0) else 1
                title = plain_cell(cells[column]) if column < len(cells) else ""
            entries.append((number, match.group(1), title.strip(), cells))
        if not entries:
            continue
        if [identifier for _, identifier, _, _ in entries] != expected:
            rep.report("coverage", doc.path, "The ASI table must list ASI01 to ASI10 once each, in order")
        for number, identifier, title, _ in entries:
            if identifier in ASI_TITLES and not title_matches(title, ASI_TITLES[identifier]):
                rep.report("asi-title", doc.path, f"Line {number}: {identifier} must be titled '{ASI_TITLES[identifier]}'")
        if catalog is not None and catalog.controls:
            check_key_controls(rep, doc, catalog, entries, key_column)
        return
    headings = []
    for line in prose:
        match = ATX.match(line)
        found = re.match(r"^(ASI\d{2})\b", plain_cell(match.group(2) or "")) if match else None
        if found:
            headings.append(found.group(1))
    if headings != expected:
        rep.report("coverage", doc.path, "List ASI01 to ASI10 once each, in order, as table rows or headings")


def check_key_controls(rep: Reporter, doc: MarkdownDoc, catalog: Catalog, entries: list, key_column: int | None) -> None:
    """Each key control carries the row's ASI identifier, each row cites the entry's start page, and the
    sentence naming the Level 2 and Level 3 key controls matches their catalog levels."""
    by_id = catalog.by_id()
    if key_column is None:
        expect_fact(rep, doc.path, "the Key controls column of the ASI table", "| Risk | ... | Key controls |")
        return
    keyed: set[str] = set()
    for number, identifier, _, cells in entries:
        pages = re.search(r"\(pp?\. (\d+)", plain_cell(cells[0]))
        start = catalog.asi_pages.get(identifier)
        if not pages:
            rep.report("asi-view", doc.path, f"Line {number}: give {identifier}'s pages in the publication, "
                       f"'(pp. {start or 'N'}-M)'")
        elif start is not None and int(pages.group(1)) != start:
            rep.report("asi-view", doc.path, f"Line {number}: {identifier} starts on p. {start} (catalog "
                       f"asi_categories), not p. {pages.group(1)}")
        if key_column >= len(cells):
            continue
        for cid in sorted(expand_ids(cells[key_column])):
            control = by_id.get(cid)
            if control is None:
                continue
            keyed.add(cid)
            if is_withdrawn(control):
                rep.report("asi-view", doc.path, f"Line {number}: {cid} is withdrawn; list its successors")
            elif identifier not in (control.get("asi") or []):
                rep.report("asi-view", doc.path, f"Line {number}: {cid} does not carry {identifier} in its catalog "
                           "asi field; tag it there or remove it from this row")
    higher = {level: {cid for cid in keyed if by_id[cid].get("level") == level} for level in (2, 3)}
    if not any(higher.values()):
        return
    sentence = next(((number, line) for number, line in enumerate(doc.lines, 1)
                     if re.search(r"key controls are Level 2", line, re.IGNORECASE)), None)
    if sentence is None:
        expect_fact(rep, doc.path, "the sentence naming the Level 2 and Level 3 key controls",
                    "Some key controls are Level 2 (A-13, ...) or Level 3 (A-14)")
        return
    number, line = sentence
    stated = {int(level): expand_ids(ids) for level, ids in re.findall(r"\bLevel ([23]) \(([^)]*)\)", line)}
    for level in (2, 3):
        if stated.get(level, set()) != higher[level]:
            rep.report("asi-view", doc.path, f"Line {number}: the Level {level} key controls are "
                       + (", ".join(sorted(higher[level])) or "none") + "; the sentence lists "
                       + (", ".join(sorted(stated.get(level, set()))) or "none"))


def copy_commands(text: str):
    """Yield the bundle list of each shell copy command or loop that names SKILL.md."""
    joined = re.sub(r"\\\r?\n", " ", text)
    for line in joined.split("\n"):
        loop = re.match(r"^\s*for\s+\w+\s+in\s+(.+?)\s*;\s*do\b", line)
        if loop and "SKILL.md" in loop.group(1):
            try:
                yield shlex.split(loop.group(1))
            except ValueError:
                pass
            continue
        if "Copy-Item" in line and "SKILL.md" in line:
            match = re.search(r"Copy-Item\s+(?:-Recurse\s+)?(?:-Path\s+)?(.+?)\s+-Destination\b", line)
            if match:
                yield [part.strip().strip("'\"") for part in match.group(1).split(",")]
            continue
        for segment in re.split(r"&&|\|\||;|\|", line):
            try:
                tokens = shlex.split(segment, comments=True)
            except ValueError:
                continue
            while tokens and tokens[0] in {"$", ">", "sudo"}:
                tokens = tokens[1:]
            if len(tokens) > 1 and tokens[0] == "cp" and "SKILL.md" in tokens:
                yield [token for token in tokens[1:] if not token.startswith("-")][:-1]


def check_install_docs(rep: Reporter, root: Path, docs: dict[str, MarkdownDoc], name: str) -> None:
    for relative in (INSTALL_DOC, "README.md", "CONTRIBUTING.md"):
        doc = docs.get(relative)
        if doc is None:
            continue
        if name:
            wrong = sorted({found for found in re.findall(r"\bskills/([A-Za-z0-9._-]+)", URL.sub(" ", doc.text))
                            if found != name})
            if wrong:
                rep.report("install-copy", doc.path, f"Install into a skill directory named {name!r}, not: "
                           + ", ".join(wrong))
        commands = list(copy_commands(doc.text))
        if not commands and relative == INSTALL_DOC:
            rep.report("install-copy", doc.path, "Give a copy command that lists exactly: " + " ".join(BUNDLE))
        for sources in commands:
            normalized = [source.rstrip("/").removeprefix("./") for source in sources]
            missing = [entry for entry in BUNDLE if entry not in normalized]
            extra = [entry for entry in normalized if entry not in BUNDLE]
            if missing or extra or len(normalized) != len(set(normalized)):
                detail = []
                if missing:
                    detail.append("missing " + ", ".join(missing))
                if extra:
                    detail.append("unexpected " + ", ".join(extra))
                rep.report("install-copy", doc.path, "The copy command must list exactly the bundle ("
                           + "; ".join(detail or ["duplicate entries"]) + ")")


def check_version(rep: Reporter, root: Path, frontmatter: dict[str, object], docs: dict[str, MarkdownDoc],
                  catalog: Catalog | None = None) -> None:
    metadata = frontmatter.get("metadata")
    version = metadata.get("version") if isinstance(metadata, dict) else None
    stated_catalog = metadata.get("catalog-version") if isinstance(metadata, dict) else None
    if stated_catalog and catalog is not None and catalog.version \
            and stated_catalog not in (catalog.version, ".".join(catalog.version.split(".")[:2])):
        rep.report("version", root / "SKILL.md", f"metadata catalog-version {stated_catalog!r} differs from the "
                   f"catalog version {catalog.version!r}")
    for key, value in (("version", version), ("catalog-version", stated_catalog)):
        if not value:
            expect_fact(rep, root / "SKILL.md", f"metadata {key} in the SKILL.md frontmatter, which lets an installed "
                        "copy name its revision", f'metadata:\n  {key}: "X.Y.Z"')
    changelog = docs.get(CHANGELOG)
    if not version or changelog is None:
        return
    headings = [line for line in changelog.lines if line.startswith("## ")]
    if not any(re.search(rf"(?<![\w.]){re.escape(version)}(?![\w.])", line) for line in headings):
        rep.report("version", changelog.path, f"Add a CHANGELOG heading for SKILL.md metadata version {version}")


def check_workflows(rep: Reporter, root: Path) -> None:
    directory = root / ".github/workflows"
    if not directory.is_dir():
        return
    for path in sorted(directory.iterdir()):
        if path.suffix not in {".yml", ".yaml"} or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        if not re.search(r"(?m)^permissions:", text):
            rep.report("workflow-permissions", path, "Declare top-level permissions, read-only unless a job needs more")
        for found in re.finditer(r"(?m)^\s*permissions:\s*(write-all|read-all)\b", text):
            rep.report("workflow-permissions", path, f"Line {text.count(chr(10), 0, found.start()) + 1}: replace "
                       f"'permissions: {found.group(1)}' with the scopes the job needs")
        if re.search(r"(?m)^\s*(?:-\s*)?['\"]?pull_request_target['\"]?\s*(?::|$)|\bpull_request_target\b\s*[,\]]", text):
            rep.report("workflow-trigger", path, "Do not trigger on pull_request_target: it runs with the base "
                       "repository's secrets and write token on code from the pull request")
        check_workflow_steps(rep, path, text)
        for number, line in enumerate(text.split("\n"), 1):
            match = USES.match(line)
            if not match:
                continue
            action = match.group(1)
            if action.startswith("./") or re.match(r"^docker://.+@sha256:[0-9a-f]{64}$", action):
                continue
            if not PINNED_ACTION.match(action):
                rep.report("workflow-pin", path, f"Line {number}: pin {action} to a full commit SHA")


def check_workflow_steps(rep: Reporter, path: Path, text: str) -> None:
    """Checkout steps do not persist credentials, and run scripts take expressions only through env."""
    lines = text.split("\n")
    for number, line in enumerate(lines, 1):
        match = re.match(r"^(\s*)(?:-\s+)?uses:\s*['\"]?actions/checkout@", line)
        if match:
            step_indent = len(line) - len(line.lstrip(" -"))
            step = []
            for later in lines[number:]:
                if later.strip() and (len(later) - len(later.lstrip(" ")) < step_indent
                                      or re.match(rf"^\s{{{max(step_indent - 2, 0)}}}-\s", later)):
                    break
                step.append(later)
            if not re.search(r"(?m)^\s*persist-credentials:\s*false\b", "\n".join(step)):
                rep.report("workflow-credentials", path, f"Line {number}: set persist-credentials: false on the "
                           "checkout, so later steps cannot read the token from .git/config")
        run = re.match(r"^(\s*)(?:-\s+)?run:\s*(.*)$", line)
        if not run:
            continue
        indent = len(run.group(1)) + (2 if line.lstrip().startswith("-") else 0)
        script = [run.group(2)]
        if run.group(2).strip()[:1] in ("|", ">"):
            for later in lines[number:]:
                if later.strip() and len(later) - len(later.lstrip(" ")) <= indent:
                    break
                script.append(later)
        if "${{" in "\n".join(script):
            rep.report("workflow-injection", path, f"Line {number}: pass expressions to run scripts through env, "
                       "never inline as ${{ ... }}, so event data cannot become shell code")


def check_renderer(rep: Reporter, root: Path) -> None:
    path = root / RENDERER
    if not path.is_file():
        rep.report("render-missing", path, "Cannot verify generated views: the renderer is missing")
        return
    try:
        completed = subprocess.run([sys.executable, str(path), "--check"], cwd=root,
                                   capture_output=True, text=True, timeout=300)
    except (OSError, subprocess.SubprocessError) as error:
        rep.report("generated-drift", path, f"The renderer did not run: {error}")
        return
    if completed.returncode != 0:
        output = (completed.stdout + completed.stderr).strip().splitlines()
        rep.report("generated-drift", path, "Generated views are out of date; run scripts/render_catalog.py. "
                   + " | ".join(output[-5:]))


def check_snapshot_age(rep: Reporter, root: Path, today: dt.date) -> None:
    for relative in SNAPSHOT_FILES:
        try:
            text = (root / relative).read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        dates = []
        for match in SNAPSHOT_DATE.finditer(text):
            try:
                dates.append(dt.date.fromisoformat(match.group(1)))
            except ValueError:
                pass
        if dates and (today - max(dates)).days > SNAPSHOT_MAX_AGE_DAYS:
            rep.warn("stale-snapshot", relative, f"Sources were last checked {max(dates)}; recheck them (quarterly)")
        for match in NEXT_RELEASE.finditer(text):
            raw = match.group(1)
            try:
                date = dt.date.fromisoformat(raw) if raw[0].isdigit() else dt.datetime.strptime(raw, "%B %d, %Y").date()
            except ValueError:
                continue
            if today > date and (not dates or max(dates) < date):
                rep.warn("stale-snapshot", relative, f"A source release was scheduled for {raw}; recheck the mappings against it")
                break


def check_orphans(rep: Reporter, root: Path, docs: dict[str, MarkdownDoc]) -> None:
    start = docs.get("SKILL.md")
    if start is None:
        return
    reachable = {start.path.resolve()}
    queue = [start]
    while queue:
        doc = queue.pop()
        for target in link_targets(doc, root):
            if target in reachable:
                continue
            reachable.add(target)
            relative = target.relative_to(root).as_posix()
            if target.suffix == ".md" and in_bundle(relative) and relative in docs:
                queue.append(docs[relative])
    for directory in ("references", "assets"):
        base = root / directory
        if not base.is_dir():
            continue
        for path, relative, symlink in walk(base):
            if not symlink and path.is_file() and path.resolve() not in reachable:
                rep.report("orphan", path, "Not reachable by links from SKILL.md; link it or remove it")


# ---------------------------------------------------------------------------
# Normative changes since the base revision (--ledger-base)

NORMATIVE_FIELDS = ("statement", "applies_when", "level", "failure_severity", "min_evidence_scope", "lifecycle",
                    "twin_exempt")
WEAKENING_WORDS = re.compile(r"\b(?:weaken\w*|relax\w*|downgrad\w*|narrow\w*|lower\w*|loosen\w*)\b", re.IGNORECASE)


def case_numbers(control: dict) -> tuple[set[int], set[int]]:
    """Live and retired case numbers in a control's verification text."""
    text = control.get("verification") if isinstance(control.get("verification"), str) else ""
    return ({int(m.group(2)) for m in CASE_LABEL.finditer(text)},
            {int(m.group(2)) for m in RETIRED_CASE.finditer(text)})


def normative_differences(before: dict, after: dict) -> list[str]:
    """The normative fields that differ between two versions of a control."""
    changed = [name for name in NORMATIVE_FIELDS
               if (before.get(name, "active" if name == "lifecycle" else None)
                   != after.get(name, "active" if name == "lifecycle" else None))]
    if case_numbers(before) != case_numbers(after):
        changed.append("cases")
    elif " ".join(str(before.get("verification", "")).split()) != " ".join(str(after.get("verification", "")).split()):
        # The verification text is normative as to the cases it requires, so editing a hostile case or its
        # authorized twin under an unchanged label is a normative change too.
        changed.append("verification")
    return changed


def applies_narrowed(before: list, after: list) -> bool:
    """True when some situation the old applies_when covered is no longer covered."""
    old = [set(str(clause).split("+")) for clause in before or []]
    new = [set(str(clause).split("+")) for clause in after or []]
    if any("all" in clause for clause in new):
        return False
    return any(not any(clause <= previous for clause in new) for previous in old)


def weakenings(before: dict, after: dict) -> list[str]:
    """Describe the ways a control became weaker: MUST to SHOULD or MAY, a higher level, a lower default
    severity or evidence scope, narrower applicability, or a removed twin."""
    found = []
    old_statement, new_statement = str(before.get("statement", "")), str(after.get("statement", ""))
    strong = (len(STRONG_KEYWORD.findall(old_statement)), len(STRONG_KEYWORD.findall(new_statement)))
    weak = (len(WEAK_KEYWORD.findall(old_statement)), len(WEAK_KEYWORD.findall(new_statement)))
    if strong[1] < strong[0] and weak[1] > weak[0]:
        found.append(f"statement moves from MUST to SHOULD or MAY ({strong[0]} to {strong[1]} MUST/SHALL/REQUIRED, "
                     f"{weak[0]} to {weak[1]} SHOULD/MAY)")
    elif strong[0] and not strong[1]:
        found.append("statement drops every MUST, SHALL and REQUIRED")
    elif strong[1] < strong[0]:
        # A removed requirement is a weakening even when other requirements remain.
        found.append(f"statement loses {strong[0] - strong[1]} of its MUST, SHALL and REQUIRED keywords "
                     f"({strong[0]} to {strong[1]})")
    if isinstance(before.get("level"), int) and isinstance(after.get("level"), int) \
            and after["level"] > before["level"]:
        found.append(f"level {before['level']} to {after['level']}")
    if before.get("failure_severity") in FAILURE_SEVERITIES and after.get("failure_severity") in FAILURE_SEVERITIES \
            and FAILURE_SEVERITIES.index(after["failure_severity"]) > FAILURE_SEVERITIES.index(before["failure_severity"]):
        found.append(f"default severity {before['failure_severity']} to {after['failure_severity']}")
    if before.get("min_evidence_scope") in EVIDENCE_SCOPES and after.get("min_evidence_scope") in EVIDENCE_SCOPES \
            and EVIDENCE_SCOPES.index(after["min_evidence_scope"]) < EVIDENCE_SCOPES.index(before["min_evidence_scope"]):
        found.append(f"minimum evidence scope {before['min_evidence_scope']} to {after['min_evidence_scope']}")
    if isinstance(before.get("applies_when"), list) and isinstance(after.get("applies_when"), list) \
            and applies_narrowed(before["applies_when"], after["applies_when"]):
        found.append("applies_when covers fewer situations")
    if "twin_exempt" in after and "twin_exempt" not in before and case_numbers(before)[0]:
        found.append("labelled cases are replaced by twin_exempt")
    return found


def check_normative_changes(rep: Reporter, root: Path, docs: dict[str, MarkdownDoc], catalog: Catalog,
                            base_controls: list, base_version: str | None) -> None:
    """Every control added or normatively changed since the base revision is named in the newest CHANGELOG
    section, a weakening is named there with a word that says so, and a released section needs a new
    catalog version."""
    path = root / CATALOG
    before = {c["id"]: c for c in base_controls if isinstance(c, dict) and isinstance(c.get("id"), str)}
    changed: dict[str, list[str]] = {}
    weakened: dict[str, list[str]] = {}
    for control in catalog.controls:
        cid = control.get("id")
        if not isinstance(cid, str):
            continue
        if cid not in before:
            changed[cid] = ["new control"]
            continue
        differences = normative_differences(before[cid], control)
        if differences:
            changed[cid] = differences
        found = weakenings(before[cid], control)
        if found:
            weakened[cid] = found
    if not changed:
        return
    doc = docs.get(CHANGELOG)
    heading, section = newest_section(doc) if doc is not None else (None, [])
    named = set().union(*(expand_ids(line) for _, line in section)) if section else set()
    for cid, fields in sorted(changed.items()):
        if cid not in named:
            rep.report("normative-change", path, f"{cid} changed since the base revision ({', '.join(fields)}); "
                       f"name it in the newest {CHANGELOG} section")
    for cid, found in sorted(weakened.items()):
        acknowledged = any(cid in expand_ids(line) and WEAKENING_WORDS.search(line) for _, line in section)
        if not acknowledged:
            rep.report("normative-weakening", path, f"{cid} is weaker than at the base revision ({'; '.join(found)}). "
                       f"If that is intended, say so on a {CHANGELOG} line that names {cid} (for example "
                       "'relaxes' or 'lowers'); otherwise restore the obligation")
    if heading is not None and "unreleased" not in heading.lower() and base_version \
            and catalog.version == base_version:
        rep.report("normative-change", path, f"Normative changes after the {heading.strip('# ').strip()} release "
                   f"need a new catalog version and a new {CHANGELOG} section; the version is still {base_version}")



# ---------------------------------------------------------------------------
# Entry points


def run(root: Path, *, bundle_mode: bool = False, catalog_root: Path | None = None,
        base_ledger: list[str] | None = None, base_retired: dict[str, set[int]] | None = None,
        base_controls: list | None = None, base_version: str | None = None,
        today: dt.date | None = None, run_renderer: bool = True) -> Result:
    root = Path(root).resolve()
    rep = Reporter(root)

    for name in (REQUIRED_BUNDLE if bundle_mode else REQUIRED_REPO):
        if not (root / name).is_file():
            rep.report("missing-file", root / name, "Required file is missing")

    texts: dict[str, str] = {}
    docs: dict[str, MarkdownDoc] = {}
    for path, relative, symlink in walk(root):
        if symlink:
            rep.report("symlink", path, "Bundle real files so copies stay portable")
            continue
        if not is_text(relative):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeError, OSError) as error:
            rep.report("unreadable", path, str(error))
            continue
        key = relative.as_posix()
        texts[key] = text
        check_text(rep, path, relative, text)
        if relative.suffix == ".md":
            docs[key] = load_markdown(path, key, text)

    if bundle_mode:
        catalog = read_catalog(catalog_root) if catalog_root else None
    else:
        catalog = check_catalog(rep, root)
        check_ledger(rep, root, catalog, base_ledger)
        if catalog is not None and base_retired is not None:
            check_retired_cases(rep, root / CATALOG, catalog, base_retired)
        check_mappings(rep, root, catalog)

    for doc in list(docs.values()):
        check_links(rep, doc, root, docs, bundle_mode)
        check_control_citations(rep, doc, catalog)

    frontmatter = check_frontmatter(rep, root, texts.get("SKILL.md", ""), bundle_mode) if "SKILL.md" in texts else {}
    name = frontmatter.get("name") if isinstance(frontmatter.get("name"), str) else ""
    check_openai_yaml(rep, root, name)
    check_orphans(rep, root, docs)
    check_identity(rep, root, docs, bundle_mode)
    check_owasp_view(rep, docs, catalog)
    check_enum_docs(rep, docs)
    check_record_template(rep, docs)
    check_record_examples(rep, docs)
    check_feature_routes(rep, docs, catalog)
    check_trigger_list(rep, docs)
    if catalog is not None:
        check_critical_blocks(rep, root, docs, catalog)
        check_control_headings(rep, docs, catalog)
        check_cross_cutting(rep, docs, catalog)
        if not bundle_mode:
            check_case_citations(rep, docs, catalog)
            check_changelog_summary(rep, docs, catalog)
            check_severity_floors(rep, root, docs, catalog)
            check_worked_examples(rep, docs, catalog)
            check_readme_summary(rep, docs, catalog)
            check_pillar_table(rep, docs, catalog)
            check_level_table(rep, docs, catalog)
            check_infographic(rep, root, catalog)
            check_eval_cases(rep, root, catalog)
            check_mapping_claims(rep, docs, catalog)
            check_relation_definitions(rep, root, docs)
            if base_controls is not None:
                check_normative_changes(rep, root, docs, catalog, base_controls, base_version)

    if not bundle_mode:
        check_nist_registry(rep, root, docs)
        check_aiuc_registry(rep, root)
        check_install_docs(rep, root, docs, name)
        check_version(rep, root, frontmatter, docs, catalog)
        check_workflows(rep, root)
        check_snapshot_age(rep, root, today or dt.date.today())
        if run_renderer:
            check_renderer(rep, root)
    return rep.result


def validate(root: Path, **options) -> list[Finding]:
    """Validate a repository (or, with bundle_mode=True, a skill bundle) and return findings."""
    return run(root, **options).findings


def stage_bundle(source: Path, destination: Path) -> Path:
    """Copy exactly the bundle entries into an empty or absent destination directory."""
    source = Path(source).resolve()
    destination = Path(destination).expanduser().absolute()
    if destination.resolve().is_relative_to(source):
        raise StageError("Stage outside the repository, for example in a temporary directory")
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise StageError(f"Stage directory must be absent or empty: {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    ignore = shutil.ignore_patterns(*IGNORED, ".DS_Store")
    for entry in BUNDLE:
        origin = source / entry
        target = destination / entry
        if origin.is_symlink():
            os.symlink(os.readlink(origin), target)
        elif origin.is_dir():
            shutil.copytree(origin, target, symlinks=True, ignore=ignore)
        elif origin.is_file():
            shutil.copy2(origin, target)
    return destination


def skill_name(root: Path) -> str:
    """Return the frontmatter name from root/SKILL.md, or an empty string if it cannot be read."""
    try:
        text = (Path(root) / "SKILL.md").read_text(encoding="utf-8")
    except OSError:
        return ""
    header = re.match(r"\A---\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", text, re.DOTALL)
    if not header:
        return ""
    name = parse_frontmatter(header.group(1))[0].get("name")
    return name if isinstance(name, str) else ""


def stage_target(root: Path, requested: Path) -> Path:
    """Return the skill directory to stage into for a --stage argument.

    A directory already named after the skill is used as is. Any other directory
    must be absent or empty and receives the bundle in a subdirectory named after
    the skill, as an installer would create it. The staged copy is then checked
    against the folder-name rule like any installed skill.
    """
    requested = Path(requested).expanduser().absolute()
    name = skill_name(root)
    if not name or requested.name == name:
        return requested
    if requested.exists() and (not requested.is_dir() or any(requested.iterdir())):
        raise StageError(f"Stage directory must be absent or empty: {requested}")
    return requested / name


def print_result(result: Result, success: str, failure: str) -> int:
    for warning in result.warnings:
        print(f"warning: {warning.path}: {warning.code}: {warning.message}")
    for finding in result.findings:
        print(f"{finding.path}: {finding.code}: {finding.message}")
    if result.findings:
        print(f"{failure}: {len(result.findings)} finding(s).")
        return 1
    print(success)
    print("This does not establish agent behavior or application security.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1],
                        help="repository root (default: this script's repository)")
    parser.add_argument("--stage", metavar="DIR", type=Path,
                        help="copy the skill bundle into DIR, or into DIR/<name> when DIR is not named after the skill "
                             "(DIR absent or empty), and validate it on its own")
    parser.add_argument("--ledger-base", metavar="REV",
                        help="git revision; every ledger entry present at it or in any commit since must still "
                             "be present, every case number marked retired there must stay retired, and every "
                             "control changed since must be named in the newest CHANGELOG section")
    parser.add_argument("--no-render", action="store_true",
                        help="do not run ROOT/scripts/render_catalog.py --check (it executes code from ROOT); "
                             "use it for an untrusted checkout")
    args = parser.parse_args(argv)
    root = args.root.resolve()

    if args.stage:
        try:
            staged = stage_bundle(root, stage_target(root, args.stage))
        except (StageError, OSError) as error:
            print(f"error: {error}", file=sys.stderr)
            return 2
        result = run(staged, bundle_mode=True, catalog_root=root)
        return print_result(result, f"Staged skill bundle at {staged} passed on its own.",
                            "Staged bundle validation failed")

    baseline = Baseline()
    if args.ledger_base:
        baseline, failure = read_baseline(root, args.ledger_base)
        for note in baseline.notes:
            print(f"note: {note}")
        if failure:
            result = run(root, base_ledger=baseline.ledger, base_retired=baseline.retired,
                         run_renderer=not args.no_render)
            result.findings.append(failure)
            return print_result(result, "", "Repository validation failed")
    if args.no_render:
        print(f"note: --no-render: {RENDERER} --check was not run, so generated views are unchecked")
    result = run(root, base_ledger=baseline.ledger, base_retired=baseline.retired,
                 base_controls=baseline.controls, base_version=baseline.version, run_renderer=not args.no_render)
    return print_result(result, "Repository layout, skill metadata, catalog, links and portability checks passed.",
                        "Repository validation failed")


if __name__ == "__main__":
    raise SystemExit(main())
