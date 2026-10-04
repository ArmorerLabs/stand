# Contributing

Keep this skill useful across applications, coding agents, programming languages, and model providers. Prefer guidance that changes an implementation decision or provides an observable verification outcome.

Report guidance that leads to an exploitable design, skill instructions that could weaken a control, and validator or CI bypasses privately, as described in [SECURITY.md](SECURITY.md). Do not open a public issue for them. Mapping disagreements, wording problems and feature requests belong in public issues.

## Propose a change

Explain the concrete failure or missing capability, the affected boundary, and the intended behavior after the change. Keep routine contributions focused. A wording change does not require a new application evaluation; a changed permission rule, workflow, or trigger needs an appropriate behavioral check.

For framework claims, cite primary sources and record the edition or snapshot date. Distinguish source requirements from this project's recommendations. Keep the NIST mapping focused on AI RMF and its Generative AI Profile. Do not invent ISO clauses, certify an application through a checklist, or equate a model refusal with runtime authorization.

Use relative links for bundled resources. Keep personal paths, private project names, account details, credentials, production data, and raw customer traces out of the repository. Use synthetic fixtures for examples. Do not introduce external actions as a side effect of merely loading the skill.

Keep the main workflow concise. Put conditional detail in the relevant reference and link to it from the entry point. Preserve the change triage (NONE, SCOPED, FULL): a focused change stays focused, and a full assessment stays complete. Support explicit file loading without assuming every host has automatic skill discovery or honors the same instruction filename.

Keep the principle "The model proposes. The application enforces." and the five pillar names verbatim. Keep the framework name out of control text and IDs, and prefer "this framework", "the skill" or "the catalog" in prose. Do not use the em dash character; the validator rejects it.

## Change the catalog

The catalog is the normative source:

- `catalog/controls.json` holds every control: statement, rationale, `applies_when`, level, failure severity, minimum evidence scope, ASI references, verification and evidence.
- `catalog/ledger.json` lists every ID ever assigned.
- `catalog/mappings.json` holds mapping justifications and source versions.
- `catalog/nist-ids.json` and `catalog/aiuc1-controls.json` are registries of the NIST AI RMF and AI 600-1 identifiers (with their table and printed page) and of the cited AIUC-1 controls (with core or supplemental status, capability and the release checked). The validator rejects a mapping to an identifier that is not in its registry, so update the registry from the primary source in the same change as the mapping.

The generated files are never edited by hand: `references/controls/index.md`, the per-pillar files `references/controls/S.md`, `T.md`, `A.md`, `N.md` and `D.md`, and `references/mappings.md`. Edit the catalog, run `python3 scripts/render_catalog.py`, and commit the regenerated files together with the source change. CI fails if they drift.

IDs follow the scheme in [references/profile-and-levels.md](references/profile-and-levels.md): a pillar letter, a hyphen and two digits, for example A-06. Cite controls by the bare ID.

- Never reuse or renumber an ID, including the ID of a withdrawn control.
- A new control takes the next unused serial in its pillar and is added to the ledger in the same change. Never delete a ledger entry.
- A change of subject, a split or a merge deprecates the old ID and issues new IDs in the same release, with `superseded_by` naming the successors. Withdraw the old ID no earlier than the next minor release, so that claims can migrate. A withdrawn control stays in the catalog as a tombstone that names the version that withdrew it and its successors.
- Label each hostile case and twin in a control's verification text as `(<ID>/C1)`, then `(C2)` and so on, and update any `<ID>/C1..Cn` range in its evidence. Never renumber a case, even before the first release: a new case takes the next unused number, even after the twin. A case that guidance under `references/` adds and the catalog does not have is a local case, labelled `<ID>/L<n>` in its own namespace and defined once. To retire a case, delete its text and leave `(C<n>: retired)` in its place in the verification text, so the number stays reserved and is never reused. The marker still counts in the `<ID>/C1..Cn` range, but evidence never cites a retired case. The validator checks the labels and every cited case number.
- Every active control has at least one labelled authorized twin. Only a control verified purely by inspecting a report or review record may instead carry a `twin_exempt` field that states why; the validator rejects `twin_exempt` on a control that has labelled cases.

Classify each change:

- Editorial: wording, typos or clarifications that leave every obligation unchanged. The ID stays the same.
- Normative: a change to what an implementation must do, when a control applies, or how it is verified (for example a statement, `applies_when`, level or hostile case). It keeps the ID as long as the control's intent is unchanged. Changes to the normative framework text in [references/profile-and-levels.md](references/profile-and-levels.md) and [references/conformance.md](references/conformance.md) are normative too.

The catalog version follows semantic versioning:

- Before 1.0, every normative change bumps MINOR.
- From 1.0, a normative change that can invalidate an existing claim bumps MAJOR. Examples are a new applicable control, a broader `applies_when`, a lower level and a stricter statement. Other normative changes bump MINOR.
- Editorial fixes bump PATCH. Conformance claims do not cite PATCH versions.
- Errata that correct a factual source error ship as PATCH with an advisory in [CHANGELOG.md](CHANGELOG.md).

List every catalog change in CHANGELOG.md. Normative changes go under "Normative changes", naming each affected ID. `python3 scripts/validate.py --ledger-base <base>` compares the catalog with the base revision: every control added or normatively changed must be named in the newest CHANGELOG.md section, and a weakening (MUST to SHOULD or MAY, a higher level, a lower default severity or evidence scope, narrower `applies_when`, or cases replaced by `twin_exempt`) must be stated on a line that names the control with a word such as "relaxes" or "lowers". The newest section also restates the catalog summary (version, total, per-pillar ranges, level split and critical-boundary count), which the validator checks. Normative changes need maintainer review before release. From 1.0, they also need a public comment period of at least 14 days.

Requirement keywords as defined in BCP 14 (the capitalized forms of "must", "should", "may" and their negations) belong only in catalog statements and the normative framework text. Hand-written guidance such as [references/runtime-controls.md](references/runtime-controls.md) explains and cites controls by ID; it does not add requirements.

## Change a mapping

Mappings are engineering mappings, not certification or conformance claims. A new or changed mapping needs:

- a primary source: the publication itself, with its edition or release, a link and the date you checked it. Crosswalks and summaries are not sources for identifiers, titles or relations;
- a relation: `direct` only when the source covers essentially the same obligation, otherwise `partial` or `supports`;
- a justification in your own words that says what the control adds or leaves out.

Rules for each framework:

- OWASP Top 10 for Agentic Applications 2026: use the official identifiers and titles, ASI01 to ASI10. [references/owasp-agentic-top-10.md](references/owasp-agentic-top-10.md) stays under CC BY-SA 4.0 with its attribution and change notes.
- AIUC-1: cite identifiers and links only; do not paste requirement descriptions, control activities or evidence text. Take identifiers from AIUC-1's own pages, say whether a cited control is core or supplemental, and recheck after each quarterly release, because releases renumber controls.
- OWASP AISVS: a related project, cited by version-prefixed requirement identifier only, for example `v1.0-C10.2.7`.
- NIST: AI RMF 1.0 (NIST AI 100-1) subcategories and NIST AI 600-1 suggested actions only, never NIST CSF. Mark short quotations with quotation marks and a table or page reference.
- ISO/IEC 42001: management themes only. Never invent clauses or Annex controls, and never claim clause-level conformance.

Record each source recheck, with its date, in CHANGELOG.md.

## Keep the skill bundle portable

The installed skill bundle is `SKILL.md`, `references/`, `assets/`, `agents/`, `LICENSE`, `LICENSES/` and `THIRD_PARTY_NOTICES.md`. Links inside bundle files must resolve inside the bundle: do not link them to `docs/`, `evals/`, `catalog/` or root documents such as `README.md`. A new file under `references/` or `assets/` must be reachable from `SKILL.md`.

`SKILL.md` frontmatter uses only fields defined by the Agent Skills specification, for portability. Host-specific keys, such as `disable-model-invocation`, are intentionally left out.

## Verify the change

Run:

```bash
python3 scripts/render_catalog.py --check
python3 scripts/validate.py
python3 scripts/validate.py --stage "$(mktemp -d)/stand"
python3 -m unittest discover -s tests -v
```

The first command confirms the generated references match the catalog. The second checks the repository, including the catalog and ledger; add `--ledger-base <base>` to check ledger, case-label and CHANGELOG rules against a base revision, as CI does. The third copies the installed bundle into an empty directory named after the skill (or into a subdirectory with that name when the given directory is named otherwise) and validates it on its own. The last runs the failure tests of the validator and the renderer.

The validator runs the renderer of the tree it checks. To validate a checkout you have not reviewed, pass `--no-render` so its code is not executed.

The validator deliberately supports a small subset of frontmatter syntax and of Markdown link forms (inline, reference-style and HTML links). If a contribution needs another syntax, extend the parser and its failure tests together. Do not weaken a check to hide a broken package.

For behavior changes, choose the relevant cases described in [evals/README.md](evals/README.md). Give an independent coding agent the task, skill, and raw fixture in an isolated workspace. Review its actual changes and tests. Record model/configuration, skill revision, commands, results, limits, and unexpected behavior. Do not give the evaluator a prewritten solution. Never publish unsupported aggregate pass rates or results without their method and evidence scope. A skill change that regresses a case with a pre-registered acceptance bar is blocked until the regression is explained.

External model calls and services require the evaluator's configured credentials and authorization. The default CI runs offline repository checks and makes no model calls. Keep application or model benchmark infrastructure outside the skill unless a concrete maintenance need justifies adding it.

## Sign off your commits

Every contribution must be signed off under the Developer Certificate of Origin (DCO) 1.1. Sign off each commit with:

```bash
git commit -s
```

This adds a `Signed-off-by: Your Name <you@example.com>` line, which certifies the statement below for that commit. Use your real name or the name you normally contribute under, and an email address you control. Every commit in a pull request needs a sign-off. Fix a missing one with `git commit --amend -s` for the last commit, or `git rebase --signoff <base>` for several. If your employer may have rights in your work, make sure you are allowed to contribute it before you sign off. Signing off does not transfer copyright.

For this project, "the open source license indicated in the file" means the license that the licensing summary in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) assigns to the file's path.

<!-- SPDX-SnippetBegin -->
<!-- SPDX-SnippetCopyrightText: 2004, 2006 The Linux Foundation and its contributors -->
<!-- SPDX-License-Identifier: LicenseRef-DCO-1.1 -->
```text
Developer Certificate of Origin
Version 1.1

Copyright (C) 2004, 2006 The Linux Foundation and its contributors.

Everyone is permitted to copy and distribute verbatim copies of this
license document, but changing it is not allowed.


Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I
    have the right to submit it under the open source license
    indicated in the file; or

(b) The contribution is based upon previous work that, to the best
    of my knowledge, is covered under an appropriate open source
    license and I have the right under that license to submit that
    work with modifications, whether created in whole or in part
    by me, under the same open source license (unless I am
    permitted to submit under a different license), as indicated
    in the file; or

(c) The contribution was provided directly to me by some other
    person who certified (a), (b) or (c) and I have not modified
    it.

(d) I understand and agree that this project and the contribution
    are public and that a record of the contribution (including all
    personal information I submit with it, including my sign-off) is
    maintained indefinitely and may be redistributed consistent with
    this project or the open source license(s) involved.
```
<!-- SPDX-SnippetEnd -->

Source: [developercertificate.org](https://developercertificate.org/).

## License of contributions

Contributions are licensed under the license of the path they change, as listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md):

- documentation and data (`SKILL.md`, `README.md` and the other Markdown files at the repository root, `references/`, `assets/`, `agents/`, `docs/`, `catalog/`, and the text and data in `evals/`) under CC BY-SA 4.0 ([LICENSES/CC-BY-SA-4.0.txt](LICENSES/CC-BY-SA-4.0.txt)), except the Developer Certificate of Origin 1.1 text quoted above, which stays under its own terms;
- code (`scripts/`, `tests/`, `.github/` and repository configuration files) under the MIT license ([LICENSE](LICENSE)).

A contribution that adds a path the summary does not cover must update it, and the matching annotation in [REUSE.toml](REUSE.toml), in the same change. REUSE.toml is the machine-readable form of the summary. Changes to the OWASP-derived reference keep its attribution and change notes. Preserve source attribution, license links, and modification notices. Do not copy framework PDFs, standard text, diagrams, or example code without suitable redistribution terms.

## Releases

Before a release:

1. Inspect the complete diff for private content.
2. Run all the checks above, including the staged bundle.
3. Recheck the primary sources whose versions the catalog records, and record each recheck with its date in CHANGELOG.md.
4. Review the relevant behavioral evidence.
5. Give the CHANGELOG.md entry its version and date. The version matches the catalog version.
6. Create a signed version tag (`git tag -s vX.Y.Z`) and write concise release notes from the CHANGELOG.md entry, describing changed behavior and evidence. Optionally attach the staged bundle as an archive with its SHA-256 checksum.

Publishing a release and configuring repository protection, including private vulnerability reporting and sign-off checks, are explicit maintainer operations.
