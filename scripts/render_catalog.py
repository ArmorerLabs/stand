#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Render the control catalog into its generated Markdown views.

The normative source is catalog/controls.json (with catalog/ledger.json,
catalog/mappings.json and the capability scopes in catalog/aiuc1-controls.json).
The control lifecycle and the critical-boundary rule come from
scripts/catalog_model.py, which the validator shares. This script writes, and
with --check verifies:

    references/controls/index.md
    references/controls/S.md, T.md, A.md, N.md, D.md
    references/mappings.md

Deprecated controls carry a Lifecycle line. Withdrawn controls are rendered as
tombstones under a Withdrawn heading and are left out of the routing tables,
the critical-boundary set, the counts and the mapping tables. Rendering is
deterministic and uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from catalog_model import (
    AIUC_CONTROL, AIUC_REGISTRY, CONTROLS_JSON, FRAMEWORK_LABELS, FRAMEWORKS, ID_PATTERN, LEDGER_JSON,
    LIFECYCLES, MAPPINGS_JSON, NIST_ACTION, NIST_ACTION_PREFIXES, NIST_FUNCTIONS, NIST_SUBCATEGORY,
    is_critical, is_withdrawn, lifecycle, listed, slugify, superseded_ids,
)

CONTROLS_DIR = "references/controls"
MAPPINGS_MD = "references/mappings.md"
CONTROL_FIELDS = (
    "id", "pillar", "title", "level", "applies_when", "failure_severity", "min_evidence_scope",
    "critical_boundary", "asi", "statement", "rationale", "verification", "evidence", "mappings",
)
EM_DASH = chr(0x2014)  # the em dash, written as a code point so this file contains none

HEADER = (
    "<!-- Generated from catalog/controls.json in the source repository by scripts/render_catalog.py. "
    "Do not edit; propose changes upstream. -->\n"
    "<!-- License: CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/). "
    "SPDX-License-Identifier: CC-BY-SA-4.0 -->\n"
)
MAPPINGS_HEADER = HEADER.replace(
    "by scripts/render_catalog.py.",
    "by scripts/render_catalog.py, with catalog/mappings.json.",
)

# Tokens shown as code spans so Markdown renders them literally: URLs,
# placeholders such as <canary>, template expressions and home-relative paths.
CODE_TOKEN = re.compile(
    r"https?://[^\s'\"]*[^\s'\".,;:)]"
    r"|[^\s'\"(]*<[A-Za-z][^\s>]*>(?:[^\s'\",;:)]*[^\s'\".,;:)])?"
    r"|\{\{[^\s}]*\}\}"
    r"|~/[^\s,;:)'\"]*[^\s,;:)'\".]"
)
ESCAPE = re.compile(r"([\\`*<])")


# ----------------------------------------------------------------- helpers


def inline(text: str) -> str:
    """Format catalog prose for Markdown without changing its words."""
    parts = []
    position = 0
    for match in CODE_TOKEN.finditer(text):
        parts.append(ESCAPE.sub(r"\\\1", text[position:match.start()]))
        parts.append(f"`{match.group(0)}`")
        position = match.end()
    parts.append(ESCAPE.sub(r"\\\1", text[position:]))
    return "".join(parts)


def cell(text: str) -> str:
    """Format text for a Markdown table cell."""
    return inline(text).replace("|", "\\|")


def applies(clauses: list) -> str:
    return " or ".join(f"`{clause}`" for clause in clauses)


def join_ids(ids: list) -> str:
    return ", ".join(ids) if ids else "-"


def count_phrase(number: int, noun: str) -> str:
    return f"{number} {noun}" + ("" if number == 1 else "s")


def and_list(items: list) -> str:
    items = list(items)
    if len(items) < 3:
        return " and ".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def or_list(items: list) -> str:
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " or " + items[-1]


def lifecycle_note(control: dict) -> str:
    """'deprecated in 0.3.0; superseded by A-26' style text for a non-active control."""
    state = lifecycle(control)
    version = control.get("withdrawn_in") if state == "withdrawn" else control.get("deprecated_in")
    text = state + (f" in {version}" if version else "")
    successors = superseded_ids(control)
    if successors:
        text += "; superseded by " + and_list(successors)
    return text


def capability_scope(control_ref: str, registry: dict) -> str:
    """'Code-generation only' for an AIUC-1 control whose requirement is not Universal, else ''."""
    requirement = control_ref.split(".")[0]
    capabilities = registry.get("requirements", {}).get(requirement, {}).get("capabilities") or []
    if not capabilities or "Universal" in capabilities:
        return ""
    if len(capabilities) > 1 and all(item.endswith("-generation") for item in capabilities):
        heads = [item[:-len("generation")] for item in capabilities]
        return or_list(heads[:-1] + [capabilities[-1]]) + " only"
    return or_list(capabilities) + " only"


def mapping_label(framework: str, ref: dict, registry: dict) -> str:
    """'A008.3 (supports; Code-generation only)' or 'GOVERN 1.1 (partial)'."""
    scope = capability_scope(ref["ref"], registry) if framework == "aiuc1" else ""
    return f"{ref['ref']} ({ref['relation']}{'; ' + scope if scope else ''})"


# ------------------------------------------------------------- validation


def check_sources(catalog: dict, ledger: dict, mappings: dict, registry: dict | None = None) -> list:
    """Return consistency errors that would make rendering misleading."""
    registry = registry if registry is not None else {}
    errors = []
    required = (
        "catalog", "version", "status", "license", "pillars", "levels",
        "applicability_vocabulary", "status_enum", "evidence_scope_enum",
        "severity_enum", "relation_enum", "asi_categories", "source_snapshot", "controls",
    )
    for key in required:
        if key not in catalog:
            errors.append(f"{CONTROLS_JSON}: missing top-level field {key!r}")
    if errors:
        return errors

    for pillar in catalog["pillars"]:
        if not isinstance(pillar, dict) or not all(pillar.get(key) for key in ("letter", "name", "question")):
            errors.append(f"{CONTROLS_JSON}: each pillar needs a letter, a name and a question")
    for category in catalog["asi_categories"]:
        if not isinstance(category, dict) or not category.get("id") or not category.get("title"):
            errors.append(f"{CONTROLS_JSON}: each asi_categories entry needs an id and a title")
    if errors:
        return errors
    pillars = {pillar["letter"] for pillar in catalog["pillars"]}
    vocabulary = set(catalog["applicability_vocabulary"])
    asi_ids = {entry["id"] for entry in catalog["asi_categories"]}
    seen = set()
    for control in catalog["controls"]:
        cid = control.get("id", "?")
        where = f"{CONTROLS_JSON}: {cid}"
        missing = [field for field in CONTROL_FIELDS if field not in control]
        if missing:
            errors.append(f"{where}: missing field(s) {', '.join(missing)}")
            continue
        if not ID_PATTERN.match(cid):
            errors.append(f"{where}: ID does not match {ID_PATTERN.pattern}")
        if cid in seen:
            errors.append(f"{where}: duplicate ID")
        seen.add(cid)
        if control.get("pillar") != cid[:1] or control.get("pillar") not in pillars:
            errors.append(f"{where}: pillar does not match the ID letter")
        if control.get("level") not in catalog["levels"]:
            errors.append(f"{where}: unknown level")
        if control.get("failure_severity") not in catalog["severity_enum"]:
            errors.append(f"{where}: unknown failure_severity")
        if control.get("min_evidence_scope") not in catalog["evidence_scope_enum"]:
            errors.append(f"{where}: unknown min_evidence_scope")
        if lifecycle(control) not in LIFECYCLES:
            errors.append(f"{where}: lifecycle must be one of {', '.join(LIFECYCLES)}")
        if is_withdrawn(control) and (not control.get("withdrawn_in") or not superseded_ids(control)):
            errors.append(f"{where}: a withdrawn control needs withdrawn_in and superseded_by")
        expected = is_critical(control)
        if control.get("critical_boundary") is not expected:
            errors.append(f"{where}: critical_boundary must be {str(expected).lower()} "
                          "(Level 1, default severity critical, not withdrawn)")
        for clause in control.get("applies_when", []):
            for token in clause.split("+"):
                if token not in vocabulary:
                    errors.append(f"{where}: applies_when token {token!r} is not in the vocabulary")
        if not control.get("applies_when"):
            errors.append(f"{where}: empty applies_when")
        for asi in control.get("asi", []):
            if asi not in asi_ids:
                errors.append(f"{where}: unknown ASI identifier {asi!r}")
        for field in ("title", "statement", "rationale", "verification"):
            if not control.get(field):
                errors.append(f"{where}: empty {field}")
        if not control.get("evidence"):
            errors.append(f"{where}: empty evidence")
        for framework in FRAMEWORKS:
            for ref in control.get("mappings", {}).get(framework, []):
                if ref.get("relation") not in catalog["relation_enum"]:
                    errors.append(f"{where}: unknown relation in {framework} mapping {ref.get('ref')!r}")
                if framework == "aiuc1" and AIUC_CONTROL.match(str(ref.get("ref"))) \
                        and ref["ref"].split(".")[0] not in registry.get("requirements", {}):
                    errors.append(f"{AIUC_REGISTRY}: no capabilities recorded for {ref['ref'].split('.')[0]}, "
                                  f"which {cid} cites")
    for control in catalog["controls"]:
        for successor in superseded_ids(control):
            if successor not in seen:
                errors.append(f"{CONTROLS_JSON}: {control.get('id')}: superseded_by names unknown control {successor}")

    ledger_ids = {}
    for entry in ledger.get("entries", []):
        if entry.get("id") in ledger_ids:
            errors.append(f"{LEDGER_JSON}: duplicate ID {entry.get('id')}")
        ledger_ids[entry.get("id")] = entry
    if errors:
        return errors
    for control in catalog["controls"]:
        entry = ledger_ids.get(control["id"])
        if entry is None:
            errors.append(f"{LEDGER_JSON}: {control['id']} is missing")
            continue
        if entry.get("title") != control["title"]:
            errors.append(f"{LEDGER_JSON}: {control['id']} title differs from the catalog")
        if entry.get("status", "active") != lifecycle(control):
            errors.append(f"{LEDGER_JSON}: {control['id']} status differs from the catalog lifecycle")
    for cid, entry in ledger_ids.items():
        if entry.get("status") == "active" and cid not in seen:
            errors.append(f"{LEDGER_JSON}: active ID {cid} is not in the catalog")

    for key in ("disclaimer", "checked", "relations"):
        if key not in mappings:
            errors.append(f"{MAPPINGS_JSON}: missing top-level field {key!r}")
    for relation in catalog["relation_enum"]:
        if relation not in mappings.get("relations", {}):
            errors.append(f"{MAPPINGS_JSON}: relations does not define {relation!r}")
    for framework in FRAMEWORKS:
        section = mappings.get(framework)
        if not isinstance(section, dict) or "refs" not in section:
            errors.append(f"{MAPPINGS_JSON}: missing framework {framework!r}")
            continue
        for key in ("framework", "source_version", "source_url", "notes"):
            if key not in section:
                errors.append(f"{MAPPINGS_JSON}: {framework} is missing {key!r}")
        refs = section["refs"]
        for control in catalog["controls"]:
            cid = control["id"]
            in_catalog = [(r["ref"], r["relation"]) for r in control.get("mappings", {}).get(framework, [])]
            in_mappings = [(r.get("ref"), r.get("relation")) for r in refs.get(cid, [])]
            if in_catalog != in_mappings:
                errors.append(f"{MAPPINGS_JSON}: {framework} refs for {cid} differ from {CONTROLS_JSON}")
            for ref in refs.get(cid, []):
                if not ref.get("justification"):
                    errors.append(f"{MAPPINGS_JSON}: {framework} {cid} {ref.get('ref')} has no justification")
        for cid in refs:
            if cid not in seen:
                errors.append(f"{MAPPINGS_JSON}: {framework} maps unknown control {cid}")

    sources = ((CONTROLS_JSON, catalog), (LEDGER_JSON, ledger), (MAPPINGS_JSON, mappings), (AIUC_REGISTRY, registry))
    for name, data in sources:
        if EM_DASH in json.dumps(data, ensure_ascii=False):
            errors.append(f"{name}: contains an em dash (U+2014)")
    return errors


# -------------------------------------------------------------- rendering


def render_pillar(catalog: dict, pillar: dict, registry: dict | None = None) -> str:
    registry = registry if registry is not None else {}
    letter = pillar["letter"]
    everything = [c for c in catalog["controls"] if c["pillar"] == letter]
    controls = listed(everything)
    withdrawn = [c for c in everything if is_withdrawn(c)]
    by_level = {level: [c for c in controls if c["level"] == level] for level in catalog["levels"]}
    level_counts = ", ".join(
        f"{len(items)} at Level {level}" for level, items in by_level.items() if items
    )
    summary = f"This pillar has {count_phrase(len(controls), 'control')}"
    summary += f": {level_counts}." if level_counts else "."
    if withdrawn:
        summary += (f" {count_phrase(len(withdrawn), 'withdrawn control')} "
                    f"{'is' if len(withdrawn) == 1 else 'are'} kept as a tombstone under Withdrawn and not counted.")
    lines = [
        HEADER,
        f"# {letter}: {pillar['name']}",
        "",
        f"**{pillar['question']}**",
        "",
        f"Catalog version {catalog['version']} ({catalog['status']}). {summary} "
        "Routing tables, the critical-boundary set and counts are in [index.md](index.md).",
        "",
        "\"Applies when\" lists alternatives; `+` joins tags that must all hold in the same agent context "
        "([profile-and-levels.md](../profile-and-levels.md)). "
        "Statuses, evidence scopes and severities are defined in [conformance.md](../conformance.md), "
        "and mapping relations in [mappings.md](../mappings.md).",
        "",
    ]
    for level, items in by_level.items():
        if not items:
            continue
        lines += [f"## Level {level}", ""]
        for control in items:
            lines += render_control(control, registry)
    if withdrawn:
        lines += [
            "## Withdrawn",
            "",
            "Tombstones of withdrawn controls. Their IDs are never reused. Do not select, apply or claim them; "
            "apply their successors instead.",
            "",
        ]
        for control in withdrawn:
            lines += [
                f"### {control['id']} {control['title']}",
                "",
                f"- **Lifecycle:** {lifecycle_note(control)}.",
                "",
            ]
    return "\n".join(lines).rstrip("\n") + "\n"


def render_control(control: dict, registry: dict | None = None) -> list:
    registry = registry if registry is not None else {}
    lines = [f"### {control['id']} {control['title']}", ""]
    if lifecycle(control) != "active":
        lines.append(f"- **Lifecycle:** {lifecycle_note(control)}. Claims should migrate before it is withdrawn.")
    lines += [
        f"- **Level:** {control['level']}",
        f"- **Applies when:** {applies(control['applies_when'])}",
        f"- **Failure severity:** {control['failure_severity']}",
        f"- **Minimum evidence scope:** {control['min_evidence_scope']}",
        f"- **Critical boundary:** {'yes' if control['critical_boundary'] else 'no'}",
        f"- **ASI:** {', '.join(control['asi']) if control['asi'] else 'none'}",
        "",
        f"**Statement:** {inline(control['statement'])}",
        "",
        f"**Rationale:** {inline(control['rationale'])}",
        "",
        f"**Verification:** {inline(control['verification'])}",
        "",
        "**Evidence:**",
        "",
    ]
    lines += [f"- {inline(item)}" for item in control["evidence"]]
    lines += ["", "**Mappings:**", ""]
    for framework in FRAMEWORKS:
        refs = control["mappings"].get(framework, [])
        rendered = ", ".join(mapping_label(framework, r, registry) for r in refs) if refs else "none"
        lines.append(f"- {FRAMEWORK_LABELS[framework]}: {rendered}")
    lines.append("")
    return lines


def tag_routes(catalog: dict, tag: str) -> dict:
    """Map level to entries for controls whose applies_when names the tag (withdrawn controls excluded)."""
    routes = {level: [] for level in catalog["levels"]}
    for control in listed(catalog["controls"]):
        clauses = [clause.split("+") for clause in control["applies_when"] if tag in clause.split("+")]
        if not clauses:
            continue
        if any(tokens == [tag] for tokens in clauses):
            entry = control["id"]
        else:
            others = [
                "+" + "+".join(token for token in tokens if token != tag) for tokens in clauses
            ]
            entry = f"{control['id']} ({' or '.join(others)})"
        routes[control["level"]].append(entry)
    return routes


def cross_cutting(catalog: dict) -> list:
    """IDs of listed controls that carry every ASI identifier."""
    every_category = {entry["id"] for entry in catalog["asi_categories"]}
    return [c["id"] for c in listed(catalog["controls"]) if set(c["asi"]) >= every_category]


def render_index(catalog: dict) -> str:
    controls = listed(catalog["controls"])
    withdrawn = [c for c in catalog["controls"] if is_withdrawn(c)]
    levels = catalog["levels"]
    critical = [c for c in controls if is_critical(c)]
    total = f"{len(controls)} controls in {len(catalog['pillars'])} pillars"
    if withdrawn:
        total += f", plus {count_phrase(len(withdrawn), 'withdrawn control')} kept as tombstones and not counted"
    lines = [
        HEADER,
        "# Control catalog index",
        "",
        f"Catalog version {catalog['version']} ({catalog['status']}). {total}. "
        "Control IDs are stable: they are never reused or renumbered. "
        "Framework mappings are listed in [mappings.md](../mappings.md).",
        "",
        "How to use the catalog:",
        "",
        "1. Compute the capability profile and level, then select every control whose applies_when matches "
        "at or below that level, as defined in [profile-and-levels.md](../profile-and-levels.md).",
        "2. Record each selected control's status and evidence by ID and apply the release gate defined in "
        "[conformance.md](../conformance.md).",
        "",
    ]

    for pillar in catalog["pillars"]:
        letter = pillar["letter"]
        lines += [
            f"## {letter}: {pillar['name']}",
            "",
            f"{pillar['question']} Full entries: [{letter}.md]({letter}.md).",
            "",
            "| ID | Title | Level | Applies when | Failure severity |",
            "| --- | --- | --- | --- | --- |",
        ]
        for control in (c for c in controls if c["pillar"] == letter):
            anchor = slugify(f"{control['id']} {control['title']}")
            title = cell(control["title"])
            if lifecycle(control) != "active":
                title += f" ({cell(lifecycle_note(control))})"
            lines.append(
                f"| [{control['id']}]({letter}.md#{anchor}) | {title} | "
                f"{control['level']} | {applies(control['applies_when'])} | {control['failure_severity']} |"
            )
        lines.append("")
        tombstones = [c for c in withdrawn if c["pillar"] == letter]
        if tombstones:
            lines += [
                f"Withdrawn, not selected or counted (tombstones in [{letter}.md]({letter}.md#withdrawn)): "
                + "; ".join(f"{c['id']} ({lifecycle_note(c)})" for c in tombstones) + ".",
                "",
            ]

    lines += [
        "## Critical-boundary set",
        "",
        "Every Level 1 control whose failure severity is critical"
        + (", except withdrawn controls" if withdrawn else "") + f" ({len(critical)} controls). "
        "[conformance.md](../conformance.md) defines how the set gates readiness and conformance claims.",
        "",
    ]
    for pillar in catalog["pillars"]:
        ids = [c["id"] for c in critical if c["pillar"] == pillar["letter"]]
        lines.append(f"- {pillar['letter']}: {', '.join(ids) if ids else 'none'}")
    lines.append("")

    level_columns = " | ".join(f"Level {level}" for level in levels)
    level_rule = " | ".join("---" for _ in levels)
    rows = []
    for tag in catalog["applicability_vocabulary"]:
        routes = tag_routes(catalog, tag)
        rows.append(f"| `{tag}` | " + " | ".join(join_ids(routes[level]) for level in levels) + " |")
    example = next((entry for tag in catalog["applicability_vocabulary"]
                    for level, entries in tag_routes(catalog, tag).items() for entry in entries if "(+" in entry), None)
    lines += [
        "## Routing by applicability tag",
        "",
        "Controls whose applies_when names the tag. "
        + (f"An entry such as `{example}` applies only when the listed tags also hold in the same agent context. "
           if example else "")
        + "Controls tagged `all` apply to every system in scope. Tags are defined in "
        "[profile-and-levels.md](../profile-and-levels.md).",
        "",
        f"| Tag | {level_columns} |",
        f"| --- | {level_rule} |",
        *rows,
        "",
    ]

    shared = cross_cutting(catalog)
    lines += [
        "## Routing by ASI category",
        "",
        "Controls whose asi field names the category. The asi field shows which risks a control is designed "
        "to address, govern or verify; it is not a coverage claim. ASI identifiers and titles are from the "
        "OWASP Top 10 for Agentic Applications 2026 by the OWASP GenAI Security Project, used under "
        "CC BY-SA 4.0 (see [owasp-agentic-top-10.md](../owasp-agentic-top-10.md)).",
        "",
        "Cross-cutting (every category): " + join_ids(shared) + ". These controls carry every ASI identifier "
        "and are not repeated in the rows below.",
        "",
        f"| ASI | Title | {level_columns} |",
        f"| --- | --- | {level_rule} |",
    ]
    for category in catalog["asi_categories"]:
        row = []
        for level in levels:
            ids = [c["id"] for c in controls if c["level"] == level and category["id"] in c["asi"]
                   and c["id"] not in shared]
            row.append(join_ids(ids))
        lines.append(f"| {category['id']} | {cell(category['title'])} | " + " | ".join(row) + " |")
    lines.append("")

    lines += [
        "## Counts",
        "",
        f"| Pillar | {level_columns} | Total | Critical boundary |",
        f"| --- | {level_rule} | --- | --- |",
    ]
    for pillar in catalog["pillars"]:
        items = [c for c in controls if c["pillar"] == pillar["letter"]]
        per_level = " | ".join(str(sum(1 for c in items if c["level"] == level)) for level in levels)
        lines.append(
            f"| {pillar['letter']}: {pillar['name']} | {per_level} | {len(items)} | "
            f"{sum(1 for c in items if is_critical(c))} |"
        )
    totals = " | ".join(str(sum(1 for c in controls if c["level"] == level)) for level in levels)
    lines.append(f"| Total | {totals} | {len(controls)} | {len(critical)} |")
    lines.append("")
    severities = ", ".join(
        f"{severity} {sum(1 for c in controls if c['failure_severity'] == severity)}"
        for severity in catalog["severity_enum"]
    )
    lines += [f"Default failure severity: {severities}.", ""]
    if withdrawn:
        lines += ["Withdrawn controls, not counted: " + ", ".join(c["id"] for c in withdrawn) + ".", ""]
    return "\n".join(lines).rstrip("\n") + "\n"


def ref_key(framework: str, ref: str) -> tuple:
    if framework == "aiuc1":
        match = AIUC_CONTROL.match(ref)
        if match:
            return (0, match.group(1), int(match.group(2)), int(match.group(3)))
    elif framework == "nist":
        match = NIST_SUBCATEGORY.match(ref)
        if match:
            return (0, NIST_FUNCTIONS.index(match.group(1)), int(match.group(2)), int(match.group(3)), 0)
        match = NIST_ACTION.match(ref)
        if match:
            return (1, NIST_ACTION_PREFIXES.index(match.group(1)), int(match.group(2)), int(match.group(3)),
                    int(match.group(4)))
    elif framework == "aisvs":
        match = re.match(r"^v1\.0-C(\d+)\.(\d+)\.(\d+)$", ref)
        if match:
            return (0, int(match.group(1)), int(match.group(2)), int(match.group(3)))
        match = re.match(r"^v1\.0-AC\.(\d+)\.(\d+)$", ref)
        if match:
            return (1, int(match.group(1)), int(match.group(2)), 0)
    return (9, ref)


def ref_table(controls: list, framework: str, refs: set, label: str, url_for=None, note_for=None) -> list:
    rows = {}
    for control in controls:
        for ref in control["mappings"].get(framework, []):
            if ref["ref"] in refs:
                rows.setdefault(ref["ref"], []).append(f"{control['id']} ({ref['relation']})")
    lines = [f"| {label} | Catalog controls (relation) |", "| --- | --- |"]
    for ref in sorted(rows, key=lambda r: ref_key(framework, r)):
        name = f"[{ref}]({url_for(ref)})" if url_for and url_for(ref) else ref
        note = note_for(ref) if note_for else ""
        lines.append(f"| {name}{f' ({note})' if note else ''} | {', '.join(rows[ref])} |")
    return lines + [""]


def render_by_pillar(catalog: dict) -> list:
    """Summarize, per pillar, which external identifiers its controls map to."""
    lines = [
        "## By pillar",
        "",
        "Distinct AIUC-1 requirements, AI RMF 1.0 subcategories and AISVS chapters, and the number of "
        "distinct AI 600-1 actions, that each pillar's controls map to with any relation. Per-control "
        "details are in the tables below.",
        "",
        "| Pillar | AIUC-1 requirements | AI RMF 1.0 subcategories | AI 600-1 actions | AISVS chapters |",
        "| --- | --- | --- | --- | --- |",
    ]
    for pillar in catalog["pillars"]:
        refs = {framework: set() for framework in FRAMEWORKS}
        for control in listed(catalog["controls"]):
            if control["pillar"] != pillar["letter"]:
                continue
            for framework in FRAMEWORKS:
                refs[framework].update(r["ref"] for r in control["mappings"].get(framework, []))
        requirements = sorted({ref.split(".")[0] for ref in refs["aiuc1"]},
                              key=lambda ref: ref_key("aiuc1", ref + ".0"))
        subcategories = sorted((ref for ref in refs["nist"] if not NIST_ACTION.match(ref)),
                               key=lambda ref: ref_key("nist", ref))
        actions = [ref for ref in refs["nist"] if NIST_ACTION.match(ref)]
        chapters = set()
        for ref in refs["aisvs"]:
            match = re.match(r"^v1\.0-(C\d+|AC)\.", ref)
            chapters.add(match.group(1) if match else ref)
        chapter_list = sorted(chapters, key=lambda ch: (ch == "AC", int(ch[1:]) if ch[1:].isdigit() else 0))
        chapter_text = ", ".join("Appendix C" if ch == "AC" else ch for ch in chapter_list)
        lines.append(
            f"| {pillar['letter']}: {pillar['name']} | {join_ids(requirements)} | {join_ids(subcategories)} | "
            f"{len(actions)} | {chapter_text or '-'} |"
        )
    return lines + [""]


def render_mappings(catalog: dict, mappings: dict, registry: dict | None = None) -> str:
    registry = registry if registry is not None else {}
    controls = listed(catalog["controls"])
    lines = [
        MAPPINGS_HEADER,
        "# Framework mappings",
        "",
        f"**Disclaimer.** {inline(mappings['disclaimer'])}",
        "",
        f"Catalog version {catalog['version']} ({catalog['status']}); mappings checked {mappings['checked']}. "
        "This file lists identifiers and relations. The justification for every mapping is recorded in "
        "`catalog/mappings.json` in the source repository. Control entries are listed in "
        "[controls/index.md](controls/index.md)."
        + (" Withdrawn controls are not listed." if len(controls) < len(catalog["controls"]) else ""),
        "",
        "Relations:",
        "",
    ]
    for relation in catalog["relation_enum"]:
        lines.append(f"- **{relation}:** {inline(mappings['relations'][relation])}")
    lines += ["", "## Source versions", "", "| Framework | Source version | Source |", "| --- | --- | --- |"]
    for framework in FRAMEWORKS:
        section = mappings[framework]
        lines.append(f"| {cell(section['framework'])} | {cell(section['source_version'])} | {section['source_url']} |")
    lines += [
        "",
        "## Summary",
        "",
        "| Framework | References | " + " | ".join(r.capitalize() for r in catalog["relation_enum"])
        + " | Controls mapped | Controls unmapped |",
        "| --- | --- | " + " | ".join("---" for _ in catalog["relation_enum"]) + " | --- | --- |",
    ]
    for framework in FRAMEWORKS:
        refs = [r for c in controls for r in c["mappings"].get(framework, [])]
        mapped = sum(1 for c in controls if c["mappings"].get(framework))
        by_relation = " | ".join(
            str(sum(1 for r in refs if r["relation"] == relation)) for relation in catalog["relation_enum"]
        )
        lines.append(
            f"| {cell(mappings[framework]['framework'])} | {len(refs)} | {by_relation} | {mapped} | "
            f"{len(controls) - mapped} |"
        )
    lines.append("")
    lines += render_by_pillar(catalog)

    for framework in FRAMEWORKS:
        section = mappings[framework]
        all_refs = {r["ref"] for c in controls for r in c["mappings"].get(framework, [])}
        lines += [f"## {section['framework']}", "", "Notes:", ""]
        lines += [f"- {inline(note)}" for note in section.get("notes", [])]
        lines.append("")
        if framework == "aiuc1":
            urls = section.get("requirement_urls", {})
            lines += [f"### {section['framework']} references", ""]
            lines += ref_table(controls, framework, all_refs, "AIUC-1 control",
                               lambda ref: urls.get(ref.split(".")[0]),
                               lambda ref: capability_scope(ref, registry))
        elif framework == "nist":
            subcategories = {r for r in all_refs if not NIST_ACTION.match(r)}
            actions = all_refs - subcategories
            lines += ["### AI RMF 1.0 subcategories (NIST AI 100-1)", ""]
            lines += ref_table(controls, framework, subcategories, "Subcategory")
            lines += ["### Generative AI Profile actions (NIST AI 600-1)", ""]
            lines += ref_table(controls, framework, actions, "Action")
        else:
            lines += [f"### {section['framework']} references", ""]
            lines += ref_table(controls, framework, all_refs, "Requirement")
        unmapped = [c["id"] for c in controls if not c["mappings"].get(framework)]
        supports_only = [
            c["id"] for c in controls
            if c["mappings"].get(framework)
            and all(r["relation"] == "supports" for r in c["mappings"][framework])
        ]
        label = FRAMEWORK_LABELS[framework]
        lines += [
            f"### Controls with no {label} mapping",
            "",
            (", ".join(unmapped) if unmapped else "None") + ".",
            "",
            f"### Controls mapped to {label} only through supports relations",
            "",
            (", ".join(supports_only) if supports_only else "None") + ".",
            "",
        ]
    return "\n".join(lines).rstrip("\n") + "\n"


def render_all(catalog: dict, mappings: dict, registry: dict | None = None) -> dict:
    """Return the generated files as {relative path: text}."""
    registry = registry if registry is not None else {}
    outputs = {f"{CONTROLS_DIR}/index.md": render_index(catalog)}
    for pillar in catalog["pillars"]:
        outputs[f"{CONTROLS_DIR}/{pillar['letter']}.md"] = render_pillar(catalog, pillar, registry)
    outputs[MAPPINGS_MD] = render_mappings(catalog, mappings, registry)
    return outputs


# ------------------------------------------------------------------- main


def load(root: Path, relative: str) -> dict:
    with (root / relative).open(encoding="utf-8") as handle:
        return json.load(handle)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true",
                        help="verify that the generated files match the catalog; write nothing")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1],
                        help="repository root (default: the parent of scripts/)")
    args = parser.parse_args(argv)
    root = args.root.resolve()

    try:
        catalog = load(root, CONTROLS_JSON)
        ledger = load(root, LEDGER_JSON)
        mappings = load(root, MAPPINGS_JSON)
        registry = load(root, AIUC_REGISTRY)
    except (OSError, ValueError) as error:
        print(f"render_catalog: cannot read catalog sources: {error}", file=sys.stderr)
        return 2
    errors = check_sources(catalog, ledger, mappings, registry)
    if errors:
        for error in errors:
            print(f"render_catalog: {error}", file=sys.stderr)
        print(f"render_catalog: {len(errors)} catalog error(s); nothing rendered.", file=sys.stderr)
        return 2

    outputs = render_all(catalog, mappings, registry)
    controls_dir = root / CONTROLS_DIR
    unexpected = []
    if controls_dir.is_dir():
        generated = {Path(path).name for path in outputs if path.startswith(CONTROLS_DIR + "/")}
        unexpected = sorted(
            f"{CONTROLS_DIR}/{p.name}" for p in controls_dir.iterdir() if p.name not in generated
        )

    if args.check:
        drift = []
        for path, text in outputs.items():
            target = root / path
            if not target.is_file():
                drift.append(f"{path}: missing")
            elif target.read_bytes() != text.encode("utf-8"):
                drift.append(f"{path}: out of date")
        drift += [f"{path}: not generated by the renderer" for path in unexpected]
        if drift:
            for line in drift:
                print(line)
            print(f"Generated catalog views drifted from {CONTROLS_JSON}: {len(drift)} file(s). "
                  "Run python3 scripts/render_catalog.py and commit the result.")
            return 1
        print(f"Generated catalog views match {CONTROLS_JSON} ({len(outputs)} files).")
        return 0

    for path, text in outputs.items():
        target = root / path
        data = text.encode("utf-8")
        if target.is_file() and target.read_bytes() == data:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        print(f"wrote {path}")
    for path in unexpected:
        print(f"warning: {path} is not generated by the renderer; remove it or --check fails")
    print(f"Rendered {len(outputs)} files from {CONTROLS_JSON}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
