# SPDX-License-Identifier: MIT
"""Build a minimal synthetic repository that passes scripts/validate.py.

The fixture uses synthetic content for documentation and the catalog, and copies
the real tooling files (validator, catalog model, tests, workflow, Dependabot
configuration) so the validator's text checks also cover them. Its renderer is a
stub; tests/test_render_catalog.py swaps in the real renderer.
"""

from __future__ import annotations

import json
from pathlib import Path
import shutil

REPOSITORY = Path(__file__).resolve().parents[1]
SKILL_NAME = "stand"
TODAY = "2026-10-03"

PRINCIPLE = "**The model proposes. The application enforces.**"
PILLARS = (
    "Scope & Stewardship (S), Trust & Isolation (T), Authority & Access (A), "
    "Notice & Neutralize (N) and Demonstrated Defenses (D)."
)
STATUSES = ("implemented-and-verified, implemented-but-unverified, planned, "
            "not-applicable-with-reason, failing, not-assessed")
SCOPES = "inspection, unit, simulation, integration, isolated-runtime, deployed"
ASI = (
    ("ASI01", "Agent Goal Hijack"),
    ("ASI02", "Tool Misuse & Exploitation"),
    ("ASI03", "Identity & Privilege Abuse"),
    ("ASI04", "Agentic Supply Chain Vulnerabilities"),
    ("ASI05", "Unexpected Code Execution (RCE)"),
    ("ASI06", "Memory & Context Poisoning"),
    ("ASI07", "Insecure Inter-Agent Communication"),
    ("ASI08", "Cascading Failures"),
    ("ASI09", "Human-Agent Trust Exploitation"),
    ("ASI10", "Rogue Agents"),
)
VOCABULARY = [
    "all", "untrusted-input", "sensitive-data", "external-effect", "tools",
    "retrieval", "memory", "delegation", "inter-agent", "queued-work",
    "triggered-runs", "shared-context", "multi-tenant", "approvals",
    "code-execution", "browser-agent", "coding-agent", "mcp", "provider-routing",
    "provider-executed-tools", "client-conversation", "rendered-output",
    "network-egress", "model-artifacts", "separation-pattern",
]
AIUC_URL = "https://standard.aiuc-1.com/security/prevent-unauthorized-ai-agent-actions"
ASI_PAGES = (9, 12, 15, 18, 21, 24, 27, 30, 33, 36)
EVERY_ASI = [key for key, _ in ASI]
# The key controls of each ASI row in the fixture's OWASP view; each carries that ASI in the catalog.
KEY_CONTROLS = {
    "ASI01": "T-01, D-01", "ASI02": "A-01", "ASI03": "A-01, A-02", "ASI04": "A-01", "ASI05": "A-01",
    "ASI06": "T-01", "ASI07": "A-01", "ASI08": "A-01", "ASI09": "A-01", "ASI10": "N-01",
}
TRIGGER_LOCATIONS = (
    "tool dispatcher, tool registry or schemas;",
    "credential broker, secret configuration and token handling (issuance, exchange, storage, logging);",
    "retrieval filters, indexes or caches;",
    "browser runtime;",
    "model, provider, routing, telemetry or tracing configuration.",
)
COPY_COMMAND = 'cp -R SKILL.md references assets agents LICENSE LICENSES THIRD_PARTY_NOTICES.md "$HOME/.agents/skills/stand/"'


def control(cid, title, level, severity, scope, applies, asi, statement=None):
    return {
        "id": cid,
        "pillar": cid[0],
        "title": title,
        "level": level,
        "applies_when": applies,
        "failure_severity": severity,
        "min_evidence_scope": scope,
        "critical_boundary": level == 1 and severity == "critical",
        "asi": asi,
        "statement": statement or f"The application MUST enforce {title.lower()}.",
        "rationale": f"Without {title.lower()} the boundary fails open.",
        "verification": f"Hostile: bypass {title.lower()} and observe denial ({cid}/C1). "
                        "Twin: the authorized case passes (C2).",
        "evidence": [f"Test reference for {cid}"],
        "mappings": {"aiuc1": [], "nist": [], "aisvs": []},
    }


def catalog() -> dict:
    controls = [
        control("S-01", "Accountable owner", 1, "high", "inspection", ["all"], list(EVERY_ASI)),
        control("A-01", "Single dispatch path", 1, "critical", "integration", ["tools"],
                ["ASI02", "ASI03", "ASI04", "ASI05", "ASI07", "ASI08", "ASI09"]),
        control("A-02", "Workload identity", 2, "critical", "integration", ["tools+external-effect"], ["ASI03"]),
        control("T-01", "Untrusted content stays data", 1, "critical", "integration",
                ["untrusted-input"], ["ASI01", "ASI06"]),
        control("D-01", "Real execution path", 1, "high", "integration", ["all"], ["ASI01"]),
        control("N-01", "Tamper-evident audit", 3, "medium", "isolated-runtime", ["tools"], ["ASI10"]),
    ]
    controls[1]["mappings"]["aiuc1"] = [{"ref": "B006.1", "relation": "partial"}]
    controls[1]["mappings"]["nist"] = [{"ref": "GOVERN 1.1", "relation": "supports"}]
    controls[3]["mappings"]["nist"] = [{"ref": "GV-1.1-001", "relation": "supports"}]
    return {
        "catalog": "placeholder",
        "namespace": "STAND",
        "version": "0.1.0",
        "status": "draft",
        "license": "CC-BY-SA-4.0",
        "pillars": [
            {"letter": "S", "name": "Scope & Stewardship", "question": "Who owns it?"},
            {"letter": "T", "name": "Trust & Isolation", "question": "What stays separate?"},
            {"letter": "A", "name": "Authority & Access", "question": "Who may do what?"},
            {"letter": "N", "name": "Notice & Neutralize", "question": "Can we see and stop it?"},
            {"letter": "D", "name": "Demonstrated Defenses", "question": "Can we show it works?"},
        ],
        "levels": [1, 2, 3],
        "applicability_vocabulary": VOCABULARY,
        "status_enum": STATUSES.split(", "),
        "evidence_scope_enum": SCOPES.split(", "),
        "severity_enum": ["critical", "high", "medium", "low"],
        "relation_enum": ["direct", "partial", "supports"],
        "critical_boundary_rule": "level == 1 and failure_severity == critical",
        "asi_categories": [{"id": key, "title": title, "page": page} for (key, title), page in zip(ASI, ASI_PAGES)],
        "source_snapshot": {"checked": TODAY, "sources": []},
        "controls": controls,
    }


def ledger() -> dict:
    return {
        "catalog": "placeholder",
        "id_pattern": "^(S|T|A|N|D)-[0-9]{2}$",
        "status_values": ["active", "deprecated", "withdrawn"],
        "entries": [
            {"id": entry["id"], "title": entry["title"], "status": "active", "introduced": "0.1.0"}
            for entry in catalog()["controls"]
        ],
    }


def mappings() -> dict:
    return {
        "catalog": "placeholder",
        "version": "0.1.0",
        "checked": TODAY,
        "disclaimer": "Engineering mappings, not certification.",
        "relations": {"direct": "Same obligation.", "partial": "Part of it.", "supports": "Helps."},
        "aiuc1": {
            "framework": "AIUC-1",
            "source_version": "AIUC-1 release of July 15, 2026",
            "source_url": "https://standard.aiuc-1.com/",
            "notes": ["Cited by identifier only."],
            "requirement_urls": {"B006": AIUC_URL},
            "application": {"B006": "Mandatory"},
            "refs": {"A-01": [{"ref": "B006.1", "relation": "partial",
                               "justification": "Core control limits agent actions; A-01 adds one dispatcher."}]},
        },
        "nist": {
            "framework": "NIST AI RMF 1.0 with NIST AI 600-1",
            "source_version": "AI 100-1 (2023) and AI 600-1 (2024)",
            "source_url": "https://www.nist.gov/itl/ai-risk-management-framework",
            "notes": ["Subcategories and actions."],
            "refs": {
                "A-01": [{"ref": "GOVERN 1.1", "relation": "supports",
                          "justification": "Policies are documented; A-01 enforces one. [AI 100-1 Table 1 p.22]"}],
                "T-01": [{"ref": "GV-1.1-001", "relation": "supports",
                          "justification": "Align use with law; T-01 keeps content as data. [AI 600-1 p.13]"}],
            },
        },
        "aisvs": {
            "framework": "OWASP AISVS 1.0",
            "source_version": "OWASP AISVS 1.0",
            "source_url": "https://github.com/OWASP/AISVS",
            "notes": ["Cross-references only."],
            "refs": {},
        },
    }


def nist_registry() -> dict:
    return {
        "registry": "fixture",
        "checked": TODAY,
        "subcategories": {"GOVERN 1.1": {"table": 1, "page": 22}, "MAP 2.1": {"table": 2, "page": 26}},
        "actions": {"GV-1.1-001": {"page": 13}},
    }


def aiuc_registry() -> dict:
    return {
        "registry": "fixture",
        "source_version": "AIUC-1 release of July 15, 2026",
        "checked": TODAY,
        "status_values": ["core", "supplemental"],
        "requirements": {"B006": {"capabilities": ["Automation"]}},
        "controls": {"B006.1": {"title": "Limits on which services an agent can reach", "status": "core",
                                "release": "2026-07-15"}},
    }


def counts() -> dict:
    """Per-pillar and per-level counts of the fixture catalog, as the prose states them."""
    controls = catalog()["controls"]
    letters = ("S", "T", "A", "N", "D")
    per_level = {level: sum(1 for c in controls if c["level"] == level) for level in (1, 2, 3)}
    return {
        "total": len(controls),
        "pillars": {letter: [c for c in controls if c["pillar"] == letter] for letter in letters},
        "levels": per_level,
        "critical": sum(1 for c in controls if c["critical_boundary"]),
    }


def pillar_table() -> str:
    data = counts()
    header = "| Pillar | Controls (L1/L2/L3) | " + " | ".join(EVERY_ASI) + " |\n"
    rule = "| --- | --- | " + " | ".join("---" for _ in EVERY_ASI) + " |\n"
    rows = ""
    for letter, items in data["pillars"].items():
        levels = "/".join(str(sum(1 for c in items if c["level"] == level)) for level in (1, 2, 3))
        asi = " | ".join(str(sum(1 for c in items if key in c["asi"])) for key in EVERY_ASI)
        rows += f"| {letter} | {len(items)} ({levels}) | {asi} |\n"
    return header + rule + rows


def level_table() -> str:
    data = counts()
    rows = "".join(
        f"| {letter} | " + " | ".join(str(sum(1 for c in items if c["level"] == level)) for level in (1, 2, 3))
        + f" | {len(items)} |\n" for letter, items in data["pillars"].items())
    levels = data["levels"]
    return ("| Pillar | Level 1 | Level 2 | Level 3 | Total |\n|---|---|---|---|---|\n" + rows
            + f"| Total | {levels[1]} | {levels[2]} | {levels[3]} | {data['total']} |\n")


def readme_counts() -> str:
    data = counts()
    pillars = ", ".join(f"{letter} {len(items)}" for letter, items in data["pillars"].items())
    levels = data["levels"]
    return (f"It holds {data['total']} controls ({pillars}), with {levels[1]} at Level 1, {levels[2]} at Level 2, "
            f"{levels[3]} at Level 3.")


def changelog() -> str:
    data = counts()
    levels = data["levels"]
    return ("# Changelog\n\n## [0.1.0] - Unreleased\n\n- First release.\n"
            f"- Control catalog 0.1.0 with {data['total']} controls across the five pillars: "
            "Authority & Access A-01 to A-02.\n"
            f"- Levels 1 to 3 ({levels[1]}, {levels[2]} and {levels[3]} controls).\n"
            f"- The critical-boundary set: the {data['critical']} Level 1 controls whose default failure severity "
            "is critical.\n")


def owasp_view() -> str:
    rows = "\n".join(f"| **{key}: {title}** (pp. {page}-{page + 2}) | Target outcome. | {KEY_CONTROLS[key]} |"
                     for (key, title), page in zip(ASI, ASI_PAGES))
    return f"""# OWASP Agentic Top 10 view

This file uses identifiers and titles from the OWASP Top 10 for Agentic Applications 2026.

One cross-cutting control (S-01) carries every ASI identifier and is not repeated below.

| Risk | Target outcome (this project) | Key controls |
| --- | --- | --- |
{rows}

Some key controls are Level 2 (A-02) or Level 3 (N-01).

See [frameworks](frameworks.md) and the [control index](controls/index.md).
"""


def pillar_file(letter: str, entries: list[tuple[str, str]]) -> str:
    body = "\n\n".join(f"### {cid} {title}\n\nStatement for {cid}." for cid, title in entries)
    return f"# Pillar {letter}\n\n{body}\n\nBack to the [index](index.md).\n"


def files() -> dict[str, str]:
    return {
        "SKILL.md": f"""---
name: {SKILL_NAME}
description: Builds and hardens agentic applications with enforceable controls and adversarial verification. Unrelated cosmetic or documentation edits do not require this workflow.
license: CC-BY-SA-4.0
metadata:
  version: "0.1.0"
  catalog-version: "0.1.0"
---

# Skill

{PRINCIPLE}

The five pillars are {PILLARS}

## Always-on invariants

<!-- critical-boundary:start -->
- One enforcement path (A-01).
- Untrusted content stays data (T-01).
<!-- critical-boundary:end -->

## Routing

| Trigger location | Control IDs |
| --- | --- |
| Tool dispatcher, registry or schemas | A-01, D-01; L2: A-02 |
| MCP client, server or proxy | A-01, T-01 |
| Browser runtime | T-01 |
| Coding agents, CI workflows, instruction or rules files | D-01 |
| Audit and monitoring | L3: N-01 |

## References

Read [profile and levels](references/profile-and-levels.md), [conformance](references/conformance.md),
[runtime controls](references/runtime-controls.md), [MCP](references/mcp.md),
[patterns](references/patterns.md), [verification](references/verification.md),
the [ASI view](references/owasp-agentic-top-10.md), [frameworks](references/frameworks.md)
and the [control index](references/controls/index.md).

Record results in [the record](assets/agent-security-record.md) and adopt with
[the snippet](assets/AGENTS-snippet.md). Cite S-01, D-01 and N-01 by bare ID.
""",
        "references/profile-and-levels.md": "# Profile and levels\n\nTokens: " + ", ".join(VOCABULARY)
        + ".\n\nCounts:\n\n" + level_table() + "\n### Trigger locations\n\n"
        + "".join(f"- {item}\n" for item in TRIGGER_LOCATIONS)
        + "\nSee [conformance](conformance.md).\n",
        "references/conformance.md": f"""# Conformance

## Status enum

Status values: {STATUSES}.

## Evidence scope

Weakest to strongest: {SCOPES}.

## Critical-boundary set

<!-- critical-boundary:start -->
A-01, T-01
<!-- critical-boundary:end -->

See [profile and levels](profile-and-levels.md).
""",
        "references/runtime-controls.md": "# Runtime controls\n\nPatterns for A-01 and T-01. See [patterns](patterns.md).\n",
        "references/mcp.md": "# MCP\n\nPins MCP specification 2025-11-25. See [controls](controls/A.md#a-01-single-dispatch-path).\n",
        "references/patterns.md": "# Patterns\n\nIllustrative pseudocode for A-01.\n\n```python\ndispatch(request)\n```\n",
        "references/verification.md": "# Verification\n\nA mock proves only the boundary it exercises (D-01).\n",
        "references/owasp-agentic-top-10.md": owasp_view(),
        "references/frameworks.md": f"""# Frameworks

## Source snapshot

Checked {TODAY}. AIUC-1 requirement [B006]({AIUC_URL}). Mappings are in [mappings](mappings.md).

No subcategory fits, so their `nist` lists are empty: S-01, A-02, D-01 and N-01.

Relations:

- **direct**: Same obligation.
- **partial**: Part of it.
- **supports**: Helps.

## Scope & Stewardship

Heading with an ampersand.
""",
        "references/mappings.md": "# Mappings\n\n| Control | AIUC-1 | Relation |\n| --- | --- | --- |\n| A-01 | B006.1 | partial |\n",
        "references/controls/index.md": "# Control index\n\n"
        + "\n".join(f"- [{letter}]({letter}.md)" for letter in ("S", "T", "A", "N", "D")) + "\n",
        "references/controls/S.md": pillar_file("S", [("S-01", "Accountable owner")]),
        "references/controls/A.md": pillar_file("A", [("A-01", "Single dispatch path"), ("A-02", "Workload identity")]),
        "references/controls/T.md": pillar_file("T", [("T-01", "Untrusted content stays data")]),
        "references/controls/D.md": pillar_file("D", [("D-01", "Real execution path")]),
        "references/controls/N.md": pillar_file("N", [("N-01", "Tamper-evident audit")]),
        "assets/agent-security-record.md": f"# Record\n\n- Status: {STATUSES}.\n- Evidence scope: {SCOPES}.\n"
        "- Principal browser agent-capable: yes | no | unknown\n"
        "- Egress destination: <mode (allowlist or public-internet) and tool>\n"
        "- Read-tool exemption: <L>; <ceiling in bits>\n"
        "- Data class: <secret class: entropy in bits, or no>\n"
        "- Browser context: <rule>\n"
        "- Register: impact threshold\n",
        "assets/AGENTS-snippet.md": "# Snippet\n\nUse the skill for agent changes. Trigger locations are those in "
        "the skill's references/profile-and-levels.md (Trigger locations); when unsure, load the skill.\n",
        "agents/openai.yaml": f"""interface:
  display_name: "Skill"
  short_description: "Build agents with security controls and evidence"
  default_prompt: "Use ${SKILL_NAME} to build or review this agentic application."
policy:
  allow_implicit_invocation: true
""",
        "LICENSE": "MIT License\n\nCopyright (c) 2026 Contributors\n",
        "LICENSES/CC-BY-SA-4.0.txt": "Attribution-ShareAlike 4.0 International\n",
        "THIRD_PARTY_NOTICES.md": "# Third-party notices\n\nOWASP material is CC BY-SA 4.0.\n",
        "README.md": f"""# Project

{PRINCIPLE}

The pillars are {PILLARS}

{readme_counts()}

Install with [the install guide](docs/install.md); read [the pillars](docs/pillars.md),
the [skill](SKILL.md) and the [source snapshot](references/frameworks.md#source-snapshot).
See also [the ampersand heading](references/frameworks.md#scope--stewardship).
Home-relative paths such as ~/.agents/skills are portable, and so is https://example.com/home/guide.
""",
        "docs/pillars.md": f"# Pillars\n\n{PRINCIPLE}\n\n{PILLARS}\n\n{pillar_table()}\n"
        "See the [control index](../references/controls/index.md).\n",
        "docs/install.md": f"# Install\n\n```bash\n{COPY_COMMAND}\n```\n",
        "CONTRIBUTING.md": "# Contributing\n\nRun the validator before opening a pull request.\n",
        "SECURITY.md": "# Security\n\nReport privately.\n",
        "CHANGELOG.md": changelog(),
        "evals/README.md": "# Evaluations\n\nCases live in cases.json.\n",
        "evals/cases.json": "[]\n",
        "catalog/controls.json": json.dumps(catalog(), indent=1) + "\n",
        "catalog/ledger.json": json.dumps(ledger(), indent=1) + "\n",
        "catalog/mappings.json": json.dumps(mappings(), indent=1) + "\n",
        "catalog/nist-ids.json": json.dumps(nist_registry(), indent=1) + "\n",
        "catalog/aiuc1-controls.json": json.dumps(aiuc_registry(), indent=1) + "\n",
        "scripts/render_catalog.py": '"""Renderer stub for validator tests."""\nimport sys\n\nsys.exit(0)\n',
    }


REAL_FILES = (
    "scripts/validate.py",
    "scripts/catalog_model.py",
    ".github/workflows/validate.yml",
    ".github/dependabot.yml",
)


def build(root: Path) -> Path:
    """Write the synthetic repository into root and return it."""
    for relative, text in files().items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    for relative in REAL_FILES:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPOSITORY / relative, target)
    (root / "tests").mkdir(exist_ok=True)
    for source in sorted((REPOSITORY / "tests").glob("*.py")):
        shutil.copy2(source, root / "tests" / source.name)
    return root
