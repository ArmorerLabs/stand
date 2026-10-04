# SPDX-License-Identifier: MIT
"""Catalog model shared by scripts/render_catalog.py and scripts/validate.py.

One definition of the catalog's closed vocabularies, the control lifecycle and
the critical-boundary rule, so the renderer and the validator can never demand
different values for the same control. Standard library only.
"""

from __future__ import annotations

import re
import unicodedata

CONTROLS_JSON = "catalog/controls.json"
LEDGER_JSON = "catalog/ledger.json"
MAPPINGS_JSON = "catalog/mappings.json"
NIST_REGISTRY = "catalog/nist-ids.json"
AIUC_REGISTRY = "catalog/aiuc1-controls.json"

# The framework name. It is the catalog namespace and never appears in control text.
FRAMEWORK_NAME = "STAND"

PILLARS = {
    "S": "Scope & Stewardship",
    "T": "Trust & Isolation",
    "A": "Authority & Access",
    "N": "Notice & Neutralize",
    "D": "Demonstrated Defenses",
}
LEVELS = (1, 2, 3)
STATUS_ENUM = (
    "implemented-and-verified", "implemented-but-unverified", "planned",
    "not-applicable-with-reason", "failing", "not-assessed",
)
# Weakest to strongest; "at or above" uses this order.
EVIDENCE_SCOPES = ("inspection", "unit", "simulation", "integration", "isolated-runtime", "deployed")
# Most to least severe.
FAILURE_SEVERITIES = ("critical", "high", "medium", "low")
RELATIONS = ("direct", "partial", "supports")
LIFECYCLES = ("active", "deprecated", "withdrawn")
FRAMEWORKS = ("aiuc1", "nist", "aisvs")
FRAMEWORK_LABELS = {"aiuc1": "AIUC-1", "nist": "NIST", "aisvs": "AISVS"}

ID_PATTERN = re.compile(r"^(S|T|A|N|D)-[0-9]{2}$")
AIUC_ID = re.compile(r"^[A-F]\d{3}(?:\.\d+)?$")
AIUC_CONTROL = re.compile(r"^([A-F])(\d{3})\.(\d+)$")
NIST_SUBCATEGORY = re.compile(r"^(GOVERN|MAP|MEASURE|MANAGE) (\d+)\.(\d+)$")
NIST_ACTION = re.compile(r"^(GV|MP|MS|MG)-(\d+)\.(\d+)-(\d{3})$")
NIST_FUNCTIONS = ("GOVERN", "MAP", "MEASURE", "MANAGE")
NIST_ACTION_PREFIXES = ("GV", "MP", "MS", "MG")
# The citation that ends every nist justification: "[AI 100-1 Table 1 p.23]" or "[AI 600-1 p.14]".
NIST_CITATION = re.compile(r"\[AI (100|600)-1(?: Table (\d+))? p\.(\d+)\]\s*$")


def lifecycle(control: dict) -> str:
    """The control's lifecycle; a control without the field is active."""
    return control.get("lifecycle", "active")


def is_withdrawn(control: dict) -> bool:
    return lifecycle(control) == "withdrawn"


def is_critical(control: dict) -> bool:
    """The critical-boundary rule: Level 1, default failure severity critical, not withdrawn."""
    level = control.get("level")
    return type(level) is int and level == 1 and control.get("failure_severity") == "critical" \
        and not is_withdrawn(control)


def listed(controls: list) -> list:
    """Controls that count and route: every control except withdrawn tombstones."""
    return [c for c in controls if isinstance(c, dict) and not is_withdrawn(c)]


def superseded_ids(control: dict) -> list:
    """The superseded_by field as a list of IDs (it may be one ID or a list)."""
    value = control.get("superseded_by")
    if not value:
        return []
    return [value] if isinstance(value, str) else [item for item in value if isinstance(item, str)]


def nist_function(ref: str) -> str | None:
    """The AI RMF subcategory an AI 600-1 action belongs to (GV-1.3-001 -> GOVERN 1.3)."""
    match = NIST_ACTION.match(ref)
    if not match:
        return None
    return f"{NIST_FUNCTIONS[NIST_ACTION_PREFIXES.index(match.group(1))]} {match.group(2)}.{match.group(3)}"


def render_inline(text: str) -> str:
    """Approximate the rendered text of a Markdown heading for anchor generation."""
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\[[^\]]*\]", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("`", "")
    text = re.sub(r"\\([!-/:-@\[-`{-~])", r"\1", text)
    text = re.sub(r"(\*{1,3})(?=\S)(.+?)(?<=\S)\1", r"\2", text)
    text = re.sub(r"(?<!\w)(_{1,3})(?=\S)(.+?)(?<=\S)\1(?!\w)", r"\2", text)
    return text


def slugify(heading: str) -> str:
    """GitHub-style heading anchor."""
    text = render_inline(heading).strip().lower()
    kept = (ch for ch in text if ch.isalnum() or ch in "-_ " or unicodedata.category(ch).startswith("M"))
    return "".join(kept).replace(" ", "-")
