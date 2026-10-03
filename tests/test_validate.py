# SPDX-License-Identifier: MIT
"""Exercise every validator finding code, the CLI contract and bundle staging.

All tests run against a synthetic repository built by fixture_repo.py, so they
pass regardless of the state of the real documentation and catalog. The real
tooling files are copied into the fixture and must pass the text checks too.
"""

from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

TESTS = Path(__file__).resolve().parent
REPOSITORY = TESTS.parent
sys.path.insert(0, str(TESTS))
sys.path.insert(0, str(REPOSITORY / "scripts"))

import fixture_repo  # noqa: E402
import validate  # noqa: E402

TODAY = dt.date(2026, 10, 3)
# Built at runtime so this source never contains the banned forms it tests.
EM_DASH = "\u2014"
EM_ENTITY = "&" + "mdash;"
EM_NUMERIC = "&#" + "8212;"
HOME_PATH = "/" + "home/example/private/config.json"
ROOT_PATH = "/" + "root/.ssh/id_rsa"
WINDOWS_PATH = "C:\\" + "Users\\alice\\notes.txt"
STRAY_ASI = "ASI" + "11"
SHORT_ASI = "ASI" + "1"
FINDING_LINE = re.compile(r"^[^:\s][^:]*: [a-z][a-z-]*: .+$")


class FixtureTestCase(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = fixture_repo.build(self.base / "repo")

    # Mutation helpers -----------------------------------------------------

    def path(self, relative):
        return self.root / relative

    def read(self, relative):
        return self.path(relative).read_text(encoding="utf-8")

    def write(self, relative, text):
        path = self.path(relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def append(self, relative, text):
        self.write(relative, self.read(relative) + text)

    def replace(self, relative, old, new):
        text = self.read(relative)
        self.assertIn(old, text, f"fixture text not found in {relative}: {old!r}")
        self.write(relative, text.replace(old, new, 1))

    def edit_json(self, relative, change):
        data = json.loads(self.read(relative))
        change(data)
        self.write(relative, json.dumps(data, indent=1) + "\n")

    def control(self, data, cid):
        return next(item for item in data["controls"] if item["id"] == cid)

    def edit_control(self, cid, change):
        self.edit_json("catalog/controls.json", lambda data: change(self.control(data, cid)))

    def result(self, **options):
        options.setdefault("today", TODAY)
        return validate.run(self.root, **options)

    def codes(self, **options):
        return {finding.code for finding in self.result(**options).findings}

    def stage(self, name=fixture_repo.SKILL_NAME):
        return validate.stage_bundle(self.root, self.base / "stage" / name)

    # Git history helpers (a throwaway repository inside the temporary directory) ---

    def git(self, *args):
        if shutil.which("git") is None:
            self.skipTest("git unavailable")
        env = dict(os.environ, GIT_CEILING_DIRECTORIES=str(self.base), GIT_CONFIG_NOSYSTEM="1",
                   GIT_CONFIG_GLOBAL=os.devnull)
        completed = subprocess.run(
            ["git", "-C", str(self.root), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.com",
             "-c", "commit.gpgsign=false", "-c", "init.defaultBranch=main", *args],
            capture_output=True, text=True, timeout=60, env=env)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return completed.stdout.strip()

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)
        return self.git("rev-parse", "HEAD")

    def remove_highest_serial(self):
        """Remove A-02 with its ledger entry and heading: consistent in-tree, caught only against a base."""
        _remove_control("A-02")(self)
        _drop_ledger("A-02")(self)
        self.write("references/controls/A.md", fixture_repo.pillar_file("A", [("A-01", "Single dispatch path")]))

    def history_with_early_removal(self):
        """Commit the fixture, then a removal, then an unrelated change. Return the first commit."""
        self.git("init", "-q")
        first = self.commit("Fixture")
        self.remove_highest_serial()
        self.commit("Remove a control and its ledger entry")
        self.append("CONTRIBUTING.md", "\nA later, unrelated change.\n")
        self.commit("Unrelated change")
        return first

    def codes_against(self, revision):
        """Codes against the base revision alone, without the commits since it."""
        base, error = validate.read_base_ledger(self.root, revision)
        self.assertIsNone(error)
        retired, error = validate.read_base_retired(self.root, revision)
        self.assertIsNone(error)
        return {finding.code for finding in self.result(base_ledger=base, base_retired=retired).findings}

    def findings_since(self, revision):
        """Findings against the base revision and every commit since it, as --ledger-base compares."""
        baseline, failure = validate.read_baseline(self.root, revision)
        self.assertIsNone(failure)
        return self.result(base_ledger=baseline.ledger, base_retired=baseline.retired).findings

    def cli(self, *args):
        return subprocess.run([sys.executable, str(self.root / "scripts/validate.py"), *args],
                              capture_output=True, text=True, timeout=120)


class BaselineTests(FixtureTestCase):
    def test_fixture_repository_passes_without_findings_or_warnings(self):
        result = self.result()
        self.assertEqual(result.findings, [])
        self.assertEqual(result.warnings, [])

    def test_staged_fixture_bundle_passes(self):
        staged = self.stage()
        result = validate.run(staged, bundle_mode=True, catalog_root=self.root)
        self.assertEqual(result.findings, [])

    def test_validate_returns_findings_list(self):
        self.assertEqual(validate.validate(self.root, today=TODAY), [])


# (description, expected code, mutation). Each mutation runs on a fresh fixture.
def _symlink(test):
    outside = test.base / "external.md"
    outside.write_text("external", encoding="utf-8")
    reference = test.path("references/mcp.md")
    reference.unlink()
    reference.symlink_to(outside)


def _outside_link(test):
    (test.base / "private.md").write_text("outside", encoding="utf-8")
    test.append("README.md", "\n[outside](../private.md)\n")


def _set_description(value):
    return lambda t: t.replace(
        "SKILL.md", "description: Builds and hardens agentic applications with enforceable controls and adversarial "
        "verification. Unrelated cosmetic or documentation edits do not require this workflow.",
        f"description: {value}")


def _frontmatter_line(old, new):
    return lambda t: t.replace("SKILL.md", old, new)


def _drop_ledger(cid):
    def change(data):
        data["entries"] = [entry for entry in data["entries"] if entry["id"] != cid]
    return lambda t: t.edit_json("catalog/ledger.json", change)


def _remove_control(cid):
    def change(data):
        data["controls"] = [item for item in data["controls"] if item["id"] != cid]
    return lambda t: t.edit_json("catalog/controls.json", change)


def _owasp_rows(change):
    def mutate(test):
        lines = test.read("references/owasp-agentic-top-10.md").split("\n")
        rows = [i for i, line in enumerate(lines) if line.startswith("| **ASI")]
        change(lines, rows)
        test.write("references/owasp-agentic-top-10.md", "\n".join(lines))
    return mutate


def _swap_rows(lines, rows):
    lines[rows[0]], lines[rows[1]] = lines[rows[1]], lines[rows[0]]


def _drop_asi07(lines, rows):
    del lines[rows[6]]


CASES = [
    # Layout and portability
    ("required file removed", "missing-file", lambda t: t.path("references/mcp.md").unlink()),
    ("symlinked reference", "symlink", _symlink),
    ("invalid UTF-8", "unreadable", lambda t: t.path("references/mcp.md").write_bytes(b"\xff\xfe bad")),
    ("home path in Markdown", "machine-path", lambda t: t.append("README.md", f"\nRead {HOME_PATH}\n")),
    ("root path in Markdown", "machine-path", lambda t: t.append("README.md", f"\nKeys in {ROOT_PATH}\n")),
    ("home path in SVG comment", "machine-path",
     lambda t: t.write("docs/diagram.svg", f"<svg><!-- {HOME_PATH} --></svg>\n")),
    ("Windows path in Python", "machine-path",
     lambda t: t.append("scripts/render_catalog.py", f"# {WINDOWS_PATH}\n")),
    ("em dash in Markdown", "punctuation", lambda t: t.append("README.md", f"\nA {EM_DASH} B\n")),
    ("em dash entity in SVG", "punctuation", lambda t: t.write("docs/diagram.svg", f"<svg>A {EM_ENTITY} B</svg>\n")),
    ("numeric em dash entity in Python", "punctuation",
     lambda t: t.append("scripts/render_catalog.py", f"# A {EM_NUMERIC} B\n")),
    ("escaped em dash in JSON", "punctuation", lambda t: t.write("evals/cases.json", '["A \\u2014 B"]\n')),
    # Links
    ("invalid URL", "invalid-link", lambda t: t.append("README.md", "\n[x](http://[oops/)\n")),
    ("empty link target", "invalid-link", lambda t: t.append("README.md", "\n[x]()\n")),
    ("file URL", "nonportable-link", lambda t: t.append("README.md", "\n[local](file:///private/notes.md)\n")),
    ("root-absolute link", "nonportable-link", lambda t: t.append("README.md", "\n[x](/abs.md)\n")),
    ("link escapes the repository", "link-escape", _outside_link),
    ("missing inline target", "missing-link", lambda t: t.append("README.md", "\n[x](references/missing.md)\n")),
    ("missing image with empty alt", "missing-link", lambda t: t.append("README.md", "\n![](docs/missing.png)\n")),
    ("missing HTML img src", "missing-link", lambda t: t.append("README.md", '\n<img src="docs/missing.png">\n')),
    ("missing HTML href", "missing-link",
     lambda t: t.append("README.md", '\n<a href="references/missing.md">x</a>\n')),
    ("single-quoted title", "missing-link", lambda t: t.append("README.md", "\n[x](references/missing.md 'title')\n")),
    ("angle-bracket target", "missing-link", lambda t: t.append("README.md", "\n[x](<references/missing file.md>)\n")),
    ("reference-style target", "missing-link",
     lambda t: t.append("README.md", "\nSee [x][r].\n\n[r]: references/missing.md\n")),
    ("missing link in list continuation", "missing-link",
     lambda t: t.append("README.md", "\n- Item\n\n    [x](references/missing.md)\n")),
    ("missing anchor in another file", "missing-anchor",
     lambda t: t.append("README.md", "\n[x](references/frameworks.md#no-such-heading)\n")),
    ("missing local anchor", "missing-anchor", lambda t: t.append("README.md", "\n[x](#nope)\n")),
    ("undefined reference label", "missing-reference", lambda t: t.append("README.md", "\nSee [x][undefined].\n")),
    ("bundle file links to docs", "bundle-link", lambda t: t.append("SKILL.md", "\n[p](docs/pillars.md)\n")),
    ("unclosed fence", "unclosed-fence", lambda t: t.append("README.md", "\n```\n[x](missing.md)\n")),
    ("orphan reference", "orphan", lambda t: t.write("references/extra.md", "# Extra\n")),
    ("orphan asset", "orphan", lambda t: t.write("assets/unused.json", "{}\n")),
    # Frontmatter
    ("colon in plain description", "frontmatter", _set_description("Note: builds things")),
    ("unclosed quote", "frontmatter", _set_description('"Builds things')),
    ("comment truncates value", "frontmatter", _set_description("Builds things #1 for agents")),
    ("non-string metadata", "frontmatter", _frontmatter_line('version: "0.1.0"', "version: 0.1")),
    ("nested metadata", "frontmatter", _frontmatter_line('version: "0.1.0"', "version:\n    major: one")),
    ("missing frontmatter", "frontmatter", lambda t: t.write("SKILL.md", t.read("SKILL.md").split("---\n", 2)[2])),
    ("indented first key", "frontmatter", _frontmatter_line("name: stand", " name: stand")),
    ("unknown key", "frontmatter-key", _frontmatter_line("license:", "foo: bar\nlicense:")),
    ("duplicate key", "duplicate-field", _frontmatter_line("license:", "name: stand\nlicense:")),
    ("uppercase name", "skill-name", _frontmatter_line("name: stand", "name: Stand")),
    ("consecutive hyphens", "skill-name", _frontmatter_line("name: stand", "name: stand--x")),
    ("leading hyphen", "skill-name", _frontmatter_line("name: stand", "name: '-stand'")),
    ("reserved word", "skill-name", _frontmatter_line("name: stand", "name: claude-helper")),
    ("name too long", "skill-name", _frontmatter_line("name: stand", "name: " + "a" * 65)),
    ("description too long", "description", _set_description("x" * 1025)),
    ("description TODO", "description", _set_description('"[TODO: write this]"')),
    ("description XML", "description", _set_description('"<b>Builds</b> agents"')),
    ("empty description", "description", _set_description('""')),
    ("unknown license", "license", _frontmatter_line("license: CC-BY-SA-4.0", "license: MTI")),
    ("missing license", "license", _frontmatter_line("license: CC-BY-SA-4.0\n", "")),
    ("compatibility too long", "compatibility", _frontmatter_line("license:", "compatibility: " + "x" * 501 + "\nlicense:")),
    ("body too long", "skill-size", lambda t: t.append("SKILL.md", "line\n" * 500)),
    # Codex metadata
    ("broken flow value", "openai-yaml", lambda t: t.replace("agents/openai.yaml", 'display_name: "Skill"', "display_name: [")),
    ("wrong skill reference", "openai-yaml", lambda t: t.replace("agents/openai.yaml", "$stand ", "$stande ")),
    ("unknown interface key", "openai-yaml",
     lambda t: t.replace("agents/openai.yaml", '  display_name: "Skill"', '  display_name: "Skill"\n  colour: red')),
    ("unknown top-level key", "openai-yaml", lambda t: t.append("agents/openai.yaml", "extras:\n  a: b\n")),
    ("non-boolean policy", "openai-yaml", lambda t: t.replace("agents/openai.yaml", "invocation: true", "invocation: maybe")),
    # Install command and identity
    ("copy command misses LICENSES", "install-copy", lambda t: t.replace("docs/install.md", " LICENSES ", " ")),
    ("copy command adds docs", "install-copy", lambda t: t.replace("docs/install.md", " agents ", " agents docs ")),
    ("no copy command", "install-copy", lambda t: t.write("docs/install.md", "# Install\n\nCopy the files.\n")),
    ("README copy command drifts", "install-copy",
     lambda t: t.append("README.md", "\n```bash\ncp -R SKILL.md references \"$HOME/x/\"\n```\n")),
    ("principle missing", "framework-identity",
     lambda t: t.replace("README.md", fixture_repo.PRINCIPLE, "Principle.")),
    ("pillar renamed", "framework-identity",
     lambda t: t.replace("docs/pillars.md", "Authority & Access", "Authority and Access")),
    # ASI identifiers and titles
    ("ASI row missing", "coverage", _owasp_rows(_drop_asi07)),
    ("ASI rows out of order", "coverage", _owasp_rows(_swap_rows)),
    ("stray ASI identifier", "asi-id", lambda t: t.append("docs/pillars.md", f"\n{STRAY_ASI} is a new risk.\n")),
    ("one-digit ASI identifier", "asi-id", lambda t: t.append("docs/pillars.md", f"\nSee {SHORT_ASI}.\n")),
    ("catalog ASI out of range", "asi-id", lambda t: t.edit_control("S-01", lambda c: c["asi"].append(STRAY_ASI))),
    ("duplicate catalog ASI", "asi-id", lambda t: t.edit_control("S-01", lambda c: c["asi"].append("ASI01"))),
    ("wrong title in prose", "asi-title", lambda t: t.append("README.md", "\nASI01: Prompt Injection matters.\n")),
    ("'and' form of a title", "asi-title",
     lambda t: t.append("README.md", "\n- **ASI02: Tool Misuse and Exploitation**\n")),
    ("wrong title in table", "asi-title",
     lambda t: t.replace("references/owasp-agentic-top-10.md", "ASI10: Rogue Agents", "ASI10: Rogue Agent")),
    ("wrong title in catalog", "asi-title",
     lambda t: t.edit_json("catalog/controls.json", lambda d: d["asi_categories"][0].update(title="Goal Hijack"))),
    # Catalog
    ("catalog not JSON", "catalog", lambda t: t.write("catalog/controls.json", "{not json")),
    ("catalog without controls", "catalog", lambda t: t.write("catalog/controls.json", "{}\n")),
    ("missing verification", "catalog-field", lambda t: t.edit_control("A-01", lambda c: c.pop("verification"))),
    ("statement without BCP 14 keyword", "catalog-field",
     lambda t: t.edit_control("A-01", lambda c: c.update(statement="The application enforces dispatch."))),
    ("empty evidence", "catalog-field", lambda t: t.edit_control("A-01", lambda c: c.update(evidence=[]))),
    ("stated scope mismatch", "catalog-field",
     lambda t: t.edit_control("A-01", lambda c: c.update(verification="Hostile case. Minimum evidence scope: unit."))),
    ("withdrawn without successor", "catalog-field",
     lambda t: t.edit_control("N-01", lambda c: c.update(lifecycle="withdrawn"))),
    ("lowercase ID", "catalog-id", lambda t: t.edit_control("A-01", lambda c: c.update(id="a-01"))),
    ("one-digit serial", "catalog-id", lambda t: t.edit_control("A-01", lambda c: c.update(id="A-1"))),
    ("pillar mismatch", "catalog-id", lambda t: t.edit_control("A-01", lambda c: c.update(pillar="T"))),
    ("duplicate ID", "catalog-id", lambda t: t.edit_control("A-02", lambda c: c.update(id="A-01"))),
    ("level out of range", "catalog-enum", lambda t: t.edit_control("A-02", lambda c: c.update(level=4))),
    ("boolean level", "catalog-enum", lambda t: t.edit_control("A-02", lambda c: c.update(level=True))),
    ("unknown severity", "catalog-enum", lambda t: t.edit_control("A-02", lambda c: c.update(failure_severity="severe"))),
    ("unknown evidence scope", "catalog-enum", lambda t: t.edit_control("A-02", lambda c: c.update(min_evidence_scope="e2e"))),
    ("unknown lifecycle", "catalog-enum", lambda t: t.edit_control("A-02", lambda c: c.update(lifecycle="retired"))),
    ("status enum drift", "catalog-enum",
     lambda t: t.edit_json("catalog/controls.json", lambda d: d["status_enum"].remove("not-assessed"))),
    ("evidence scope order", "catalog-enum",
     lambda t: t.edit_json("catalog/controls.json", lambda d: d["evidence_scope_enum"].reverse())),
    ("pillar name drift", "catalog-enum",
     lambda t: t.edit_json("catalog/controls.json", lambda d: d["pillars"][0].update(name="Risk & Responsibility"))),
    ("pillars out of STAND order", "catalog-enum",
     lambda t: t.edit_json("catalog/controls.json", lambda d: d["pillars"].reverse())),
    ("unknown pillar letter", "catalog-field", lambda t: t.edit_control("A-01", lambda c: c.update(pillar="R"))),
    ("control ID with a former pillar letter", "catalog-id",
     lambda t: t.edit_control("N-01", lambda c: c.update(id="E-01", pillar="E"))),
    ("unknown applies_when token", "applies-when", lambda t: t.edit_control("A-01", lambda c: c.update(applies_when=["toolz"]))),
    ("all joined with plus", "applies-when", lambda t: t.edit_control("A-01", lambda c: c.update(applies_when=["all+tools"]))),
    ("dangling plus", "applies-when", lambda t: t.edit_control("A-01", lambda c: c.update(applies_when=["tools+"]))),
    ("repeated token", "applies-when", lambda t: t.edit_control("A-01", lambda c: c.update(applies_when=["tools+tools"]))),
    ("empty applies_when", "applies-when", lambda t: t.edit_control("A-01", lambda c: c.update(applies_when=[]))),
    ("framework name in control text", "framework-name",
     lambda t: t.edit_control("A-01", lambda c: c.update(statement=f"{validate.FRAMEWORK_NAME} systems MUST dispatch."))),
    # Critical-boundary set
    ("SKILL.md list misses a member", "critical-boundary",
     lambda t: t.replace("SKILL.md", "- One enforcement path (A-01).\n", "")),
    ("conformance list adds a non-member", "critical-boundary",
     lambda t: t.replace("references/conformance.md", "A-01, T-01", "A-01, T-01, D-01")),
    ("markers missing", "critical-boundary",
     lambda t: t.replace("references/conformance.md", "<!-- critical-boundary:end -->", "")),
    ("catalog flag inconsistent", "critical-boundary",
     lambda t: t.edit_control("D-01", lambda c: c.update(critical_boundary=True))),
    # Ledger
    ("ledger ID grammar", "ledger", lambda t: t.edit_json("catalog/ledger.json", lambda d: d["entries"].append({"id": "X-01"}))),
    ("ledger duplicate", "ledger", lambda t: t.edit_json("catalog/ledger.json", lambda d: d["entries"].append({"id": "S-01"}))),
    ("ledger shape", "ledger", lambda t: t.write("catalog/ledger.json", '{"entries": [1]}\n')),
    ("ledger pattern drift", "ledger", lambda t: t.edit_json("catalog/ledger.json", lambda d: d.update(id_pattern="^[A-Z]-\\d+$"))),
    ("ledger status values drift", "ledger",
     lambda t: t.edit_json("catalog/ledger.json", lambda d: d.update(status_values=["active"]))),
    ("ledger status unknown", "ledger",
     lambda t: t.edit_json("catalog/ledger.json", lambda d: d["entries"][0].update(status="retired"))),
    ("ledger status differs from lifecycle", "ledger",
     lambda t: t.edit_json("catalog/ledger.json", lambda d: d["entries"][0].update(status="deprecated"))),
    ("ledger misses a catalog ID", "ledger-missing", _drop_ledger("A-02")),
    ("control removed without tombstone", "ledger-removed", _remove_control("D-01")),
    ("ledger serial gap", "ledger-removed", _drop_ledger("A-01")),
    # Mappings
    ("unknown relation in catalog", "mapping",
     lambda t: t.edit_control("A-01", lambda c: c["mappings"]["aiuc1"][0].update(relation="equivalent"))),
    ("mapping for unknown control", "mapping",
     lambda t: t.edit_json("catalog/mappings.json", lambda d: d["aiuc1"]["refs"].update({"A-99": []}))),
    ("mapping drift between files", "mapping",
     lambda t: t.edit_json("catalog/mappings.json", lambda d: d["aiuc1"]["refs"]["A-01"][0].update(relation="supports"))),
    ("missing justification", "mapping",
     lambda t: t.edit_json("catalog/mappings.json", lambda d: d["aiuc1"]["refs"]["A-01"][0].pop("justification"))),
    ("missing source version", "mapping",
     lambda t: t.edit_json("catalog/mappings.json", lambda d: d["aiuc1"].pop("source_version"))),
    ("relation definitions drift", "mapping",
     lambda t: t.edit_json("catalog/mappings.json", lambda d: d["relations"].update(equivalent="x"))),
    ("AIUC section index link in Markdown", "aiuc-link",
     lambda t: t.append("references/frameworks.md", "\n[D004](https://standard.aiuc-1.com/reliability/)\n")),
    ("AIUC trailing slash", "aiuc-link",
     lambda t: t.replace("references/frameworks.md", f"({fixture_repo.AIUC_URL})", f"({fixture_repo.AIUC_URL}/)")),
    ("AIUC index URL in mappings", "aiuc-link",
     lambda t: t.edit_json("catalog/mappings.json",
                           lambda d: d["aiuc1"]["requirement_urls"].update(B006="https://standard.aiuc-1.com/security/"))),
    ("AIUC application missing for a cited requirement", "mapping",
     lambda t: t.edit_json("catalog/mappings.json", lambda d: d["aiuc1"]["application"].pop("B006"))),
    ("AIUC application value unknown", "mapping",
     lambda t: t.edit_json("catalog/mappings.json", lambda d: d["aiuc1"]["application"].update(B006="Required"))),
    ("AIUC application differs from the requirement table", "mapping",
     lambda t: t.append("references/frameworks.md",
                        f"\n| Requirement | Application; capability; frequency |\n| --- | --- |\n"
                        f"| [B006]({fixture_repo.AIUC_URL}) | Optional; Automation; 12 months |\n")),
    # Citations and enums
    ("unknown control cited", "unknown-control", lambda t: t.append("README.md", "\nSee A-99.\n")),
    ("lowercase control ID", "id-form", lambda t: t.append("README.md", "\nSee a-01.\n")),
    ("unhyphenated control ID", "id-form", lambda t: t.append("README.md", "\nSee A01 for dispatch.\n")),
    ("status value missing", "enum-doc",
     lambda t: t.replace("assets/agent-security-record.md", ", not-assessed", "")),
    ("evidence scope missing", "enum-doc", lambda t: t.replace("references/conformance.md", "isolated-runtime, ", "")),
    ("enum values scattered", "enum-doc",
     lambda t: t.replace("assets/agent-security-record.md", ", failing, not-assessed",
                         ".\n\nAlso failing and not-assessed")),
    ("enum table out of order", "enum-doc",
     lambda t: t.replace("references/conformance.md", f"Weakest to strongest: {fixture_repo.SCOPES}.",
                         "| Scope | Meaning |\n| --- | --- |\n" + "".join(
                             f"| {scope} | x |\n" for scope in reversed(fixture_repo.SCOPES.split(", "))))),
    ("install loop drifts", "install-copy",
     lambda t: t.append("docs/install.md", "\n```bash\nfor item in SKILL.md references; do echo \"$item\"; done\n```\n")),
    ("install path uses another skill name", "install-copy",
     lambda t: t.append("docs/install.md", "\nOr use `$HOME/.claude/skills/stand-old`.\n")),
    ("internal probe cited in rationale", "catalog-field",
     lambda t: t.edit_control("A-01", lambda c: c.update(rationale="Both arms failed (probe P3)."))),
    ("viewer page label in rationale", "catalog-field",
     lambda t: t.edit_control("A-01", lambda c: c.update(rationale="See the publication, PDF p.13."))),
    ("record example only in SKILL.md", "record-example",
     lambda t: t.append("SKILL.md", "\n```text\nChange: CH-1, x\nA-01: implemented-and-verified, integration, "
                        "A-01/C1 twin pass\n```\n")),
    ("verification text without case labels", "case-label",
     lambda t: t.edit_control("A-01", lambda c: c.update(verification="Hostile: bypass it. Twin: it passes."))),
    ("case labels out of order", "case-label",
     lambda t: t.edit_control("A-01", lambda c: c.update(verification="Hostile: x (A-01/C2). Twin: y (C1)."))),
    ("evidence range differs from the case labels", "case-label",
     lambda t: t.edit_control("A-01", lambda c: c.update(evidence=["Dispatcher tests A-01/C1..C5"]))),
    ("cited case number beyond the catalog", "case-label",
     lambda t: t.append("references/patterns.md", "\nA-01/C7: an extra case.\n")),
    ("changelog summary count drift", "changelog-summary",
     lambda t: t.append("CHANGELOG.md", "\n- Control catalog 0.1.0 with 99 controls across the five pillars: "
                        "Authority & Access A-01 to A-09.\n- Levels 1 to 3 (9, 9 and 9 controls).\n")),
    ("README catalog count drift", "readme-summary",
     lambda t: t.append("README.md", "\nIt holds 99 controls (S 1, T 2, A 3, N 4, D 5), with 9 at Level 1, 9 at Level 2, "
                        "9 at Level 3.\n")),
    ("README counts in the former pillar order", "readme-summary",
     lambda t: t.append("README.md", "\nIt holds 6 controls (R 1, A 2, I 1, S 1, E 1).\n")),
    ("lowercase control ID with a new pillar letter", "id-form", lambda t: t.append("README.md", "\nSee t-01.\n")),
    ("unhyphenated control ID with a new pillar letter", "id-form",
     lambda t: t.append("README.md", "\nSee N01 for audit.\n")),
    ("pillar ASI table drift", "pillar-table",
     lambda t: t.append("docs/pillars.md", "\n| Pillar | Controls (L1/L2/L3) | ASI01 | ASI02 |\n| --- | --- | --- | --- |\n"
                        "| A | 3 (2/1/0) | 0 | 1 |\n")),
    ("mapping labelled direct against the catalog", "mapping-claim",
     lambda t: t.append("references/frameworks.md", "\nThe dispatcher row: A-01 (B006.1, direct).\n")),
    ("empty nist list drift", "mapping-claim",
     lambda t: t.append("references/frameworks.md", "\nSo their `nist` lists are empty: A-01.\n")),
    ("OWASP mark in the possessive", "owasp-mark",
     lambda t: t.append("README.md", "\nThe " + "OWASP" + "'s list.\n")),
    ("routing row misses a tagged critical control", "routing",
     lambda t: (t.edit_control("A-01", lambda c: c.update(applies_when=["tools", "mcp"])),
                t.append("SKILL.md", "\n| Trigger location | Control IDs |\n| --- | --- |\n"
                         "| MCP client, server or proxy | T-01 |\n"))),
    ("control heading drift", "control-heading",
     lambda t: t.replace("references/controls/A.md", "### A-02 Workload identity", "### A-02: Workload identity")),
    # Generated views, versions and workflows
    ("renderer missing", "render-missing", lambda t: t.path("scripts/render_catalog.py").unlink()),
    ("generated views drift", "generated-drift",
     lambda t: t.write("scripts/render_catalog.py", 'import sys\nprint("references/controls/A.md: stale")\nsys.exit(1)\n')),
    ("changelog lacks version", "version", lambda t: t.replace("CHANGELOG.md", "## [0.1.0]", "## [0.2.0]")),
    ("unpinned action", "workflow-pin",
     lambda t: t.write(".github/workflows/extra.yml", "permissions:\n  contents: read\njobs:\n  x:\n    steps:\n      - uses: actions/checkout@v7\n")),
    ("missing workflow permissions", "workflow-permissions",
     lambda t: t.write(".github/workflows/extra.yml", "jobs:\n  x:\n    runs-on: ubuntu-latest\n")),
]


class FindingCodeTests(FixtureTestCase):
    def test_each_mutation_reports_its_code(self):
        for description, code, mutate in CASES:
            with self.subTest(description, code=code):
                self.setUp()
                if mutate is _symlink and not hasattr(os, "symlink"):
                    self.skipTest("symlinks unsupported")
                mutate(self)
                self.assertIn(code, self.codes())

    def test_every_finding_code_has_a_failure_case(self):
        source = (REPOSITORY / "scripts/validate.py").read_text(encoding="utf-8")
        emitted = set(re.findall(r'report\(\s*"([a-z-]+)"', source))
        emitted |= set(re.findall(r'Finding\("([a-z-]+)"', source))
        covered = {code for _, code, _ in CASES} | {"skill-dir-name"}
        self.assertEqual(emitted - covered, set())

    def test_ledger_entry_removed_since_base_revision(self):
        base = [entry["id"] for entry in fixture_repo.ledger()["entries"]] + ["S-02"]
        self.assertIn("ledger-removed", self.codes(base_ledger=base))

    def test_removal_in_an_earlier_commit_is_caught_against_the_push_base(self):
        # Greptile P1: the parent of HEAD already lacks A-02, so only the push's previous head
        # (or the pull request's base commit) reveals the removal.
        first = self.history_with_early_removal()
        self.assertEqual(self.codes_against("HEAD^1"), set())
        self.assertIn("ledger-removed", self.codes_against(first))


def _retire(verification, evidence=None):
    def change(control):
        control["verification"] = verification
        if evidence is not None:
            control["evidence"] = evidence
    return change


RETIRED_TEXT = "Hostile: bypass it (A-01/C1). A removed case (C2: retired). Twin: it passes (C3)."


class RetiredCaseTests(FixtureTestCase):
    """Greptile P2: a retired case keeps its number, so removing a case after a release passes."""

    def assertCode(self, code):
        self.assertIn(code, self.codes())

    def assertClean(self):
        self.assertEqual(self.result().findings, [])

    def test_retired_marker_keeps_the_run_contiguous(self):
        self.edit_control("A-01", _retire(RETIRED_TEXT, ["Dispatcher tests A-01/C1..C3"]))
        self.assertClean()

    def test_retired_marker_may_follow_the_twin(self):
        self.edit_control("A-01", _retire("Hostile: x (A-01/C1). Twin: y (C3). Retired: (C2: retired)."))
        self.assertClean()

    def test_retired_first_case_carries_the_control_id(self):
        self.edit_control("A-01", _retire("Old case (A-01/C1: retired). Hostile: x (C2). Twin: y (C3)."))
        self.assertClean()

    def test_gap_without_marker_fails(self):
        self.edit_control("A-01", _retire("Hostile: x (A-01/C1). Twin: y (C3)."))
        self.assertCode("case-label")

    def test_retired_number_cannot_be_reused(self):
        self.edit_control("A-01", _retire("Hostile: x (A-01/C1). Old (C2: retired). Twin: y (C2)."))
        self.assertCode("case-label")

    def test_number_retired_twice_fails(self):
        self.edit_control("A-01", _retire("Hostile: x (A-01/C1). (C2: retired). (C2: retired). Twin: y (C3)."))
        self.assertCode("case-label")

    def test_marker_for_another_control_fails(self):
        self.edit_control("A-01", _retire("Hostile: x (A-01/C1). (A-02/C2: retired). Twin: y (C3)."))
        self.assertCode("case-label")

    def test_retired_case_counts_toward_the_evidence_range(self):
        self.edit_control("A-01", _retire(RETIRED_TEXT, ["Dispatcher tests A-01/C1..C2"]))
        self.assertCode("case-label")

    def test_evidence_may_not_cite_a_retired_case(self):
        self.edit_control("A-01", _retire(RETIRED_TEXT, ["Dispatcher test A-01/C2"]))
        self.assertCode("case-label")

    def test_evidence_may_not_cite_a_case_beyond_the_catalog(self):
        self.edit_control("A-01", _retire(RETIRED_TEXT, ["Dispatcher test A-01/C4"]))
        self.assertCode("case-label")

    def test_documents_may_not_cite_a_retired_case(self):
        self.edit_control("A-01", _retire(RETIRED_TEXT))
        self.append("references/patterns.md", "\nA-01/C2: the removed case.\n")
        self.assertCode("case-label")

    def test_documents_may_cite_live_cases_and_show_the_marker(self):
        self.edit_control("A-01", _retire(RETIRED_TEXT))
        self.append("references/patterns.md", "\nA-01/C1 and A-01/C3 (twin). The verification text keeps "
                    "(A-01/C2: retired).\n")
        self.assertClean()

    def test_retired_number_stays_retired_since_the_base_revision(self):
        self.edit_control("A-01", _retire(RETIRED_TEXT))
        self.assertEqual(self.result(base_retired={"A-01": {2}}).findings, [])
        self.edit_control("A-01", _retire("Hostile: x (A-01/C1). Reused (C2). Twin: y (C3)."))
        self.assertIn("case-label", {f.code for f in self.result(base_retired={"A-01": {2}}).findings})

    def test_dropping_the_marker_is_caught_against_a_git_base(self):
        self.git("init", "-q")
        self.edit_control("A-01", _retire(RETIRED_TEXT))
        first = self.commit("Retire A-01/C2")
        self.assertEqual(validate.read_base_retired(self.root, first), ({**{c["id"]: set() for c in
                         fixture_repo.catalog()["controls"]}, "A-01": {2}}, None))
        self.edit_control("A-01", _retire("Hostile: x (A-01/C1). Reused (C2). Twin: y (C3)."))
        self.commit("Reuse the number")
        self.assertIn("case-label", self.codes_against(first))
        self.assertEqual(self.codes_against("HEAD"), set())


THREE_CASES = "Hostile: x (A-01/C1). Hostile: z (C2). Twin: y (C3)."
REUSED_TEXT = "Hostile: x (A-01/C1). A new case (C2). Twin: y (C3)."
A03 = ("A-03", "Bounded delegation")


class RangeHistoryTests(FixtureTestCase):
    """A change undone inside one push or pull request is invisible at both endpoints.

    --ledger-base therefore also reads every commit in BASE..HEAD that changes the catalog
    or the ledger.
    """

    def retire_then_reuse(self):
        """Commit three cases, retire C2, then reuse C2 in a later commit. Return the base commit."""
        self.git("init", "-q")
        self.edit_control("A-01", _retire(THREE_CASES))
        base = self.commit("Three cases")
        self.edit_control("A-01", _retire(RETIRED_TEXT))
        self.commit("Retire A-01/C2")
        self.edit_control("A-01", _retire(REUSED_TEXT))
        self.commit("Reuse C2 for a new case")
        return base

    def add_then_remove_ledger_id(self):
        """Commit the fixture, add A-03 with its ledger entry, then delete both. Return the base commit."""
        self.git("init", "-q")
        base = self.commit("Fixture")
        cid, title = A03
        self.edit_json("catalog/controls.json", lambda data: data["controls"].append(
            fixture_repo.control(cid, title, 2, "high", "integration", ["tools"], ["ASI02"])))
        self.edit_json("catalog/ledger.json", lambda data: data["entries"].append(
            {"id": cid, "title": title, "status": "active", "introduced": "0.1.0"}))
        self.write("references/controls/A.md", fixture_repo.pillar_file(
            "A", [("A-01", "Single dispatch path"), ("A-02", "Workload identity"), A03]))
        self.assertEqual(self.result().findings, [])
        self.commit("Add A-03")
        _remove_control(cid)(self)
        _drop_ledger(cid)(self)
        self.write("references/controls/A.md", fixture_repo.files()["references/controls/A.md"])
        self.commit("Delete A-03 and its ledger entry")
        return base

    def test_case_retired_and_reused_within_one_range_is_caught(self):
        base = self.retire_then_reuse()
        self.assertEqual(self.result().findings, [])
        self.assertEqual(self.codes_against(base), set())
        messages = [(f.code, f.path, f.message) for f in self.findings_since(base)]
        self.assertTrue(any(code == "case-label" and path == "catalog/controls.json" and "A-01/C2" in message
                            for code, path, message in messages), messages)

    def test_case_retired_and_reused_on_a_merged_branch_is_caught(self):
        # The merge leaves the catalog as it was at the base, so default history
        # simplification would hide the branch; every commit must still be read.
        self.git("init", "-q")
        self.edit_control("A-01", _retire(THREE_CASES))
        base = self.commit("Three cases")
        self.git("checkout", "-q", "-b", "side")
        self.edit_control("A-01", _retire(RETIRED_TEXT))
        self.commit("Retire A-01/C2")
        self.edit_control("A-01", _retire(THREE_CASES))
        self.commit("Reuse C2")
        self.git("checkout", "-q", "main")
        self.append("CONTRIBUTING.md", "\nA change on main.\n")
        self.commit("Change on main")
        self.git("merge", "-q", "--no-ff", "-m", "Merge side", "side")
        self.assertEqual(self.codes_against(base), set())
        self.assertIn("case-label", {f.code for f in self.findings_since(base)})

    def test_case_retired_within_one_range_may_not_be_cited(self):
        base = self.retire_then_reuse()
        self.append("references/patterns.md", "\nA-01/C2 covers the new case.\n")
        self.edit_control("A-01", lambda c: c.update(evidence=["Dispatcher test A-01/C2"]))
        self.assertEqual(self.result().findings, [])
        findings = self.findings_since(base)
        self.assertIn(("case-label", "references/patterns.md"), {(f.code, f.path) for f in findings})
        self.assertTrue(any("evidence cites A-01/C2" in f.message for f in findings), findings)

    def test_case_retired_within_one_range_and_kept_passes(self):
        self.git("init", "-q")
        self.edit_control("A-01", _retire(THREE_CASES))
        base = self.commit("Three cases")
        self.edit_control("A-01", _retire(RETIRED_TEXT))
        self.commit("Retire A-01/C2")
        self.append("CONTRIBUTING.md", "\nA later, unrelated change.\n")
        self.commit("Unrelated change")
        self.assertEqual(self.findings_since(base), [])

    def test_ledger_id_added_and_removed_within_one_range_is_caught(self):
        base = self.add_then_remove_ledger_id()
        self.assertEqual(self.result().findings, [])
        self.assertEqual(self.codes_against(base), set())
        messages = [(f.code, f.message) for f in self.findings_since(base)]
        self.assertTrue(any(code == "ledger-removed" and message.startswith("A-03 ")
                            for code, message in messages), messages)

    def test_command_line_compares_every_commit_since_the_base(self):
        base = self.retire_then_reuse()
        completed = self.cli(str(self.root), "--ledger-base", base)
        self.assertEqual(completed.returncode, 1, completed.stdout + completed.stderr)
        self.assertIn("catalog/controls.json: case-label: A-01/C2 was marked retired", completed.stdout)
        self.setUp()
        base = self.add_then_remove_ledger_id()
        completed = self.cli(str(self.root), "--ledger-base", base)
        self.assertEqual(completed.returncode, 1, completed.stdout + completed.stderr)
        self.assertIn("catalog/ledger.json: ledger-removed: A-03 was in the ledger", completed.stdout)
        completed = self.cli(str(self.root), "--ledger-base", "HEAD")
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_draft_id_scheme_before_the_base_has_a_ledger_is_not_compared(self):
        # The catalog's own history: IDs were remapped to new pillar letters before the
        # ledger was first published, so the draft scheme's IDs are not reserved.
        self.git("init", "-q")
        ledger = self.read("catalog/ledger.json")
        self.path("catalog/ledger.json").unlink()
        base = self.commit("Before the catalog was published")
        self.write("catalog/ledger.json", json.dumps({"id_pattern": "^(R|A)-[0-9]{2}$",
                                                      "entries": [{"id": "R-01"}, {"id": "A-09"}]}) + "\n")
        self.commit("Draft ID scheme")
        self.write("catalog/ledger.json", ledger)
        self.commit("Remap to the current scheme")
        baseline, failure = validate.read_baseline(self.root, base)
        self.assertIsNone(failure)
        self.assertEqual(len(baseline.notes), 1, baseline.notes)
        self.assertIn("declares another id_pattern", baseline.notes[0])
        self.assertEqual(self.findings_since(base), [])

    def test_another_id_pattern_after_the_base_has_a_ledger_still_counts(self):
        self.git("init", "-q")
        base = self.commit("Fixture")
        ledger = self.read("catalog/ledger.json")

        def other_scheme(data):
            data["id_pattern"] = "^(A|X)-[0-9]{2}$"
            data["entries"].append({"id": "A-03", "status": "active"})
        self.edit_json("catalog/ledger.json", other_scheme)
        self.commit("Another pattern and A-03")
        self.write("catalog/ledger.json", ledger)
        self.commit("Restore the pattern and delete A-03")
        self.assertIn("ledger-removed", {f.code for f in self.findings_since(base)})

    def test_unreadable_catalog_in_a_commit_since_the_base_fails_closed(self):
        self.git("init", "-q")
        base = self.commit("Fixture")
        catalog = self.read("catalog/controls.json")
        self.write("catalog/controls.json", "{\n")
        self.commit("Broken catalog")
        self.write("catalog/controls.json", catalog)
        self.commit("Repaired catalog")
        baseline, failure = validate.read_baseline(self.root, base)
        self.assertIsNotNone(failure)
        self.assertEqual(failure.code, "ledger-removed")
        self.assertIn("catalog/controls.json at ", failure.message)
        self.assertIn("is not JSON", failure.message)
        completed = self.cli(str(self.root), "--ledger-base", base)
        self.assertEqual(completed.returncode, 1)
        self.assertIn("ledger-removed: Cannot compare with the commits since", completed.stdout)


class NoFalsePositiveTests(FixtureTestCase):
    def assertClean(self):
        self.assertEqual(self.result().findings, [])

    def test_fenced_and_inline_code_links_are_ignored(self):
        self.append("README.md", "\n```markdown\n[example](not-a-real-file.md)\n```\n\nUse `[x](not-real.md)` syntax.\n")
        self.assertClean()

    def test_indented_code_after_blank_line_is_ignored(self):
        self.append("README.md", "\nParagraph.\n\n    [x](not-real.md)\n")
        self.assertClean()

    def test_fence_with_info_string_does_not_close_a_fence(self):
        self.append("README.md", "\n```\n```python\n[x](missing.md)\n```\n")
        self.assertClean()

    def test_title_variants_inside_inline_code_are_allowed(self):
        self.append("references/frameworks.md", "\nThe headings read `ASI02: Tool Misuse and Exploitation`.\n")
        self.assertClean()

    def test_prose_after_identifier_colon_in_lowercase_is_allowed(self):
        self.append("README.md", "\nASI08: see the cascading row.\n")
        self.assertClean()

    def test_folded_description_and_quotes_are_parsed(self):
        self.replace("SKILL.md", "description: Builds", "description: >-\n  Builds")
        self.replace("SKILL.md", "license: CC-BY-SA-4.0", "license: 'CC-BY-SA-4.0'")
        self.assertClean()

    def test_spdx_expression_with_bundled_texts(self):
        self.replace("SKILL.md", "license: CC-BY-SA-4.0", "license: MIT AND CC-BY-SA-4.0")
        self.assertClean()

    def test_ledger_as_plain_list(self):
        ids = [entry["id"] for entry in fixture_repo.ledger()["entries"]]
        self.write("catalog/ledger.json", json.dumps(ids) + "\n")
        self.assertClean()

    def test_duplicate_headings_get_numbered_anchors(self):
        self.append("references/frameworks.md", "\n## Source snapshot\n")
        self.append("README.md", "\n[again](references/frameworks.md#source-snapshot-1)\n")
        self.assertClean()

    def test_explicit_html_anchor(self):
        self.append("references/frameworks.md", '\n<a id="custom-anchor"></a>\n')
        self.append("README.md", "\n[custom](references/frameworks.md#custom-anchor)\n")
        self.assertClean()

    def test_case_labels_and_similar_tokens_are_not_control_ids(self):
        self.append("references/patterns.md",
                    "\nCases A-01/C1, A-01/C2 (twin) and the range A-01/C1..C2. Labels (C1), (C10) and C12 in "
                    "prose. AIUC-1 D004, A003.2 and B006.1; OWASP A01:2021; pillar files S.md, T.md, A.md, "
                    "N.md and D.md; Amazon S3 and T-shirt sizes.\n")
        self.assertClean()

    def test_control_id_ranges_expand_in_critical_blocks(self):
        self.assertEqual(validate.expand_ids("A-01 to A-03, T-01"), {"A-01", "A-02", "A-03", "T-01"})

    def test_enum_tables_and_lists_are_accepted(self):
        scopes = fixture_repo.SCOPES.split(", ")
        self.replace("references/conformance.md", f"Weakest to strongest: {fixture_repo.SCOPES}.",
                     "| Scope | Meaning |\n| --- | --- |\n" + "".join(f"| {scope} | x |\n" for scope in scopes))
        self.replace("references/conformance.md", f"Status values: {fixture_repo.STATUSES}.",
                     "".join(f"- **{status}**: meaning.\n" for status in fixture_repo.STATUSES.split(", ")))
        self.assertClean()

    def test_install_loop_and_destinations_are_accepted(self):
        self.append("docs/install.md", "\n```bash\nfor item in SKILL.md references assets agents LICENSE LICENSES "
                    "THIRD_PARTY_NOTICES.md; do\n  echo \"$item\"\ndone\n```\n\nInstall into "
                    "`$HOME/.claude/skills/stand` or `~/.agents/skills`.\n")
        self.assertClean()

    def test_withdrawn_tombstone_is_accepted(self):
        def withdraw(data):
            control = self.control(data, "N-01")
            control.update(lifecycle="withdrawn", withdrawn_in="0.2.0", superseded_by=["D-01"])
        self.edit_json("catalog/controls.json", withdraw)
        self.edit_json("catalog/ledger.json", lambda d: d["entries"][-1].update(status="withdrawn"))
        self.assertClean()


class WarningTests(FixtureTestCase):
    def test_token_budget_warns_without_failing(self):
        self.append("SKILL.md", ("word " * 100 + "\n") * 45)
        result = self.result()
        self.assertEqual(result.findings, [])
        self.assertIn("skill-tokens", {warning.code for warning in result.warnings})

    def test_stale_snapshot_warns_without_failing(self):
        result = self.result(today=dt.date(2027, 6, 1))
        self.assertEqual(result.findings, [])
        self.assertIn("stale-snapshot", {warning.code for warning in result.warnings})

    def test_passed_release_date_warns(self):
        self.append("references/frameworks.md", "\nThe next AIUC-1 release is October 15, 2026.\n")
        result = self.result(today=dt.date(2026, 10, 20))
        self.assertIn("stale-snapshot", {warning.code for warning in result.warnings})


class StagingTests(FixtureTestCase):
    def test_bundle_constant(self):
        self.assertEqual(validate.BUNDLE, ("SKILL.md", "references", "assets", "agents",
                                           "LICENSE", "LICENSES", "THIRD_PARTY_NOTICES.md"))
        for required in validate.REQUIRED_BUNDLE:
            self.assertIn(required.split("/")[0], validate.BUNDLE)

    def test_stage_copies_exactly_the_bundle(self):
        staged = self.stage()
        self.assertEqual(sorted(entry.name for entry in staged.iterdir()), sorted(validate.BUNDLE))

    def test_staged_directory_name_must_match_skill_name(self):
        staged = self.stage("stand-main")
        codes = {f.code for f in validate.run(staged, bundle_mode=True, catalog_root=self.root).findings}
        self.assertIn("skill-dir-name", codes)

    def test_staged_link_outside_bundle_fails(self):
        self.append("SKILL.md", "\n[p](docs/pillars.md)\n")
        self.append("references/mcp.md", "\n[readme](../README.md)\n")
        staged = self.stage()
        codes = {f.code for f in validate.run(staged, bundle_mode=True, catalog_root=self.root).findings}
        self.assertIn("missing-link", codes)
        self.assertNotIn("bundle-link", codes)

    def test_staged_link_escaping_bundle_fails(self):
        self.append("references/mcp.md", "\n[up](../../outside.md)\n")
        (self.base / "stage").mkdir()
        (self.base / "stage" / "outside.md").write_text("x", encoding="utf-8")
        staged = self.stage()
        codes = {f.code for f in validate.run(staged, bundle_mode=True, catalog_root=self.root).findings}
        self.assertIn("link-escape", codes)

    def test_staged_citations_use_the_repository_catalog(self):
        self.append("references/mcp.md", "\nSee A-99.\n")
        staged = self.stage()
        codes = {f.code for f in validate.run(staged, bundle_mode=True, catalog_root=self.root).findings}
        self.assertIn("unknown-control", codes)

    def test_stage_refuses_non_empty_directory(self):
        target = self.base / "stage" / fixture_repo.SKILL_NAME
        target.mkdir(parents=True)
        (target / "keep.txt").write_text("existing install", encoding="utf-8")
        with self.assertRaises(validate.StageError):
            validate.stage_bundle(self.root, target)

    def test_stage_refuses_directory_inside_repository(self):
        with self.assertRaises(validate.StageError):
            validate.stage_bundle(self.root, self.root / "build" / fixture_repo.SKILL_NAME)


class CommandLineTests(FixtureTestCase):
    def test_success_exit_code_and_message(self):
        completed = self.cli(str(self.root))
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("passed", completed.stdout)
        self.assertIn("does not establish agent behavior", completed.stdout)

    def test_failure_exit_code_and_output_format(self):
        self.append("README.md", "\n[x](references/missing.md)\n")
        completed = self.cli(str(self.root))
        self.assertEqual(completed.returncode, 1)
        lines = [line for line in completed.stdout.splitlines()
                 if line and not line.startswith(("warning:", "Repository validation failed"))]
        self.assertTrue(lines)
        for line in lines:
            self.assertRegex(line, FINDING_LINE)
        self.assertIn("README.md: missing-link: ", completed.stdout)
        self.assertIn("Repository validation failed: 1 finding(s).", completed.stdout)

    def test_stage_option_validates_the_installed_copy(self):
        target = self.base / "stage" / fixture_repo.SKILL_NAME
        completed = self.cli(str(self.root), "--stage", str(target))
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertTrue((target / "SKILL.md").is_file())
        self.assertFalse((target / "README.md").exists())

    def test_stage_option_fails_on_bundle_finding(self):
        self.append("SKILL.md", "\n[p](docs/pillars.md)\n")
        completed = self.cli(str(self.root), "--stage", str(self.base / "stage" / fixture_repo.SKILL_NAME))
        self.assertEqual(completed.returncode, 1)
        self.assertIn("SKILL.md: missing-link: ", completed.stdout)

    def test_stage_option_nests_under_skill_name(self):
        target = self.base / "stage-check"
        completed = self.cli(str(self.root), "--stage", str(target))
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertTrue((target / fixture_repo.SKILL_NAME / "SKILL.md").is_file())
        self.assertEqual([entry.name for entry in target.iterdir()], [fixture_repo.SKILL_NAME])

    def test_stage_option_usage_error(self):
        target = self.base / "occupied"
        target.mkdir()
        (target / "file").write_text("x", encoding="utf-8")
        completed = self.cli(str(self.root), "--stage", str(target))
        self.assertEqual(completed.returncode, 2)
        self.assertIn("error:", completed.stderr)

    def test_unknown_option_is_a_usage_error(self):
        self.assertEqual(self.cli("--no-such-option").returncode, 2)

    def test_ledger_base_outside_git_fails_clearly(self):
        env = dict(os.environ, GIT_CEILING_DIRECTORIES=str(self.base))
        completed = subprocess.run([sys.executable, str(self.root / "scripts/validate.py"), str(self.root),
                                    "--ledger-base", "HEAD^1"], capture_output=True, text=True, timeout=120, env=env)
        self.assertEqual(completed.returncode, 1)
        self.assertIn("ledger-removed: Cannot compare with the base ledger", completed.stdout)


def workflow_step(name):
    """Return the run script of a named step in the real validate workflow."""
    lines = (REPOSITORY / ".github/workflows/validate.yml").read_text(encoding="utf-8").split("\n")
    start = lines.index(f"      - name: {name}")
    run = next(i for i in range(start, len(lines)) if lines[i] == "        run: |")
    body = []
    for line in lines[run + 1:]:
        if line and not line.startswith(" " * 10):
            break
        body.append(line[10:])
    return "\n".join(body)


class WorkflowTests(FixtureTestCase):
    """The workflow compares the ledger with the base of the whole push or pull request."""

    def select(self, event, before="", pr_base=""):
        if shutil.which("bash") is None:
            self.skipTest("bash unavailable")
        output = self.base / "github-output"
        output.write_text("", encoding="utf-8")
        env = dict(os.environ, EVENT_NAME=event, PUSH_BEFORE=before, PR_BASE=pr_base, GITHUB_OUTPUT=str(output),
                   GIT_CEILING_DIRECTORIES=str(self.base))
        completed = subprocess.run(["bash", "-e", "-c", workflow_step("Select the ledger base revision")],
                                   cwd=self.root, capture_output=True, text=True, timeout=60, env=env)
        found = re.search(r"^revision=(.*)$", output.read_text(encoding="utf-8"), re.MULTILINE)
        return completed.returncode, found.group(1) if found else None

    def test_workflow_does_not_compare_only_with_the_parent_commit(self):
        text = (REPOSITORY / ".github/workflows/validate.yml").read_text(encoding="utf-8")
        self.assertIn("github.event.before", text)
        self.assertIn("github.event.pull_request.base.sha", text)
        self.assertIn("fetch-depth: 0", text)
        self.assertNotIn("--ledger-base HEAD^1", text)

    def test_push_compares_with_the_previous_head(self):
        first = self.history_with_early_removal()
        code, revision = self.select("push", before=first)
        self.assertEqual((code, revision), (0, first))
        self.assertIn("ledger-removed", self.codes_against(revision))

    def test_pull_request_compares_with_the_base_commit(self):
        first = self.history_with_early_removal()
        self.assertEqual(self.select("pull_request", before="", pr_base=first), (0, first))

    def test_new_branch_skips_the_comparison(self):
        self.git("init", "-q")
        self.commit("Fixture")
        self.assertEqual(self.select("push", before="0" * 40), (0, ""))

    def test_manual_run_compares_with_the_parent(self):
        self.git("init", "-q")
        first = self.commit("Fixture")
        self.append("CONTRIBUTING.md", "\nMore.\n")
        self.commit("Change")
        self.assertEqual(self.select("workflow_dispatch"), (0, first))

    def test_unreachable_base_fails_closed(self):
        self.git("init", "-q")
        self.commit("Fixture")
        code, revision = self.select("push", before="a" * 40)
        self.assertNotEqual(code, 0)
        self.assertIsNone(revision)

    def test_malformed_base_fails(self):
        self.git("init", "-q")
        self.commit("Fixture")
        code, revision = self.select("push", before="HEAD~3; echo injected")
        self.assertNotEqual(code, 0)
        self.assertIsNone(revision)


class ParserTests(unittest.TestCase):
    def test_slugify_matches_github(self):
        self.assertEqual(validate.slugify("A-06 Approval binding"), "a-06-approval-binding")
        self.assertEqual(validate.slugify("Scope & Stewardship (S)"), "scope--stewardship-s")
        self.assertEqual(validate.slugify("S: Scope & Stewardship"), "s-scope--stewardship")
        self.assertEqual(validate.slugify("D: Demonstrated Defenses"), "d-demonstrated-defenses")
        self.assertEqual(validate.slugify("`snake_case` and **bold**"), "snake_case-and-bold")

    def test_markdown_lines_reports_unclosed_fence(self):
        lines, unclosed = validate.markdown_lines("text\n```\ncode\n")
        self.assertEqual(unclosed, 2)
        self.assertEqual(lines[2], "")

    def test_parse_scalar(self):
        self.assertEqual(validate.parse_scalar("'it''s'"), ("it's", False))
        self.assertEqual(validate.parse_scalar('"a\\"b"'), ('a"b', False))
        self.assertEqual(validate.parse_scalar("plain text"), ("plain text", True))
        for bad in ("[x", "a: b", "a #b", '"open', "'open"):
            with self.subTest(bad=bad), self.assertRaises(validate.YamlError):
                validate.parse_scalar(bad)

    def test_fence_after_indented_code_is_a_fence(self):
        lines, unclosed = validate.markdown_lines("para\n\n    code\n```\nfenced\n```\n[x](y.md)\n")
        self.assertIsNone(unclosed)
        self.assertEqual(lines[4], "")
        self.assertEqual(lines[6], "[x](y.md)")

    def test_copy_command_parsing(self):
        text = "```bash\ncp -R SKILL.md references \\\n  assets \"$HOME/x/\"\n```\n"
        self.assertEqual(list(validate.copy_commands(text)), [["SKILL.md", "references", "assets"]])


if __name__ == "__main__":
    unittest.main()
