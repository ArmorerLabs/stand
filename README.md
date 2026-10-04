# STAND

**Secure, Trustworthy Agents by Non-negotiable Design.** The model proposes. The application enforces.

An engineering framework for secure agentic applications, delivered as a coding-agent skill.

"Non-negotiable" refers to the critical-boundary controls: no owner exception, prompt or model behavior turns a failure of one of them into a pass, and an excepted high-severity failure never counts toward conformance.

## Why STAND

- **Levels computed from capability.** Each agent context's required level follows from what it can actually do: read untrusted input, reach sensitive data, cause external effects, act autonomously. An unknown property counts as present.
- **Every control is testable.** Each of the 78 controls names a hostile case, an authorized twin that must still succeed, and a minimum evidence scope, exercised through the real execution path rather than through model behavior.
- **One record keyed by control ID.** Results are recorded per control with a closed status and the evidence scope achieved, so reviewers can trace, sample and re-run them.

## What it is

This framework helps coding agents, and the engineers who direct them, build agentic applications whose security does not depend on model behavior. A coding agent that loads the skill triages each change, profiles every agent context, and selects the relevant controls from a catalog of 78 controls with stable IDs and three levels. It implements them as deterministic enforcement, verifies each one with a hostile test and an authorized twin through the real execution path, and records the result by control ID. The workflow supports new applications and focused changes to existing systems, across languages, model providers, and orchestration frameworks.

## The principle

**The model proposes. The application enforces.**

"The application" means the deterministic controls the model cannot alter: application code, identity and policy services, sandboxes, network policy and infrastructure. Permissions, approvals, isolation, and resource limits must remain effective when a model follows an injected instruction or produces a harmful proposal.

## Who it is for

- Developers, and the coding agents they direct, who build or change applications with tool calling, MCP, retrieval, memory, delegation, code execution, browser or computer use, or autonomous jobs.
- Application security engineers and reviewers who need controls they can trace by ID and evidence they can sample and re-run.
- Platform and engineering leads who set the rules coding agents follow in their repositories.
- Assessors who relate engineering evidence to OWASP, AIUC-1, NIST AI RMF or ISO/IEC 42001 programs, through engineering mappings only.

## Scope and non-goals

In scope: the enforcement path of an agentic application. That includes tool dispatch and authorization, consequential values and approvals, delegation and tokens, retrieval and memory, provider routing and provider-executed tools, network egress and rendered output, sandboxes, browser and computer-use agents, MCP, inter-agent messages, coding and CI agents, budgets, audit, detection, stop and recovery, and the tests and records that show these controls work. The skill also governs the coding agent's own conduct while it works in a repository.

Not in scope:

- model training, alignment or capability evaluation;
- content safety and moderation policy, except where content crosses a security boundary;
- general application security unrelated to agent behavior, which still needs your existing secure development practice;
- organization-level management systems, certification, audit opinions or legal compliance;
- a runtime product: nothing here runs in production, calls a model, or needs credentials;
- guarantees: a conformance statement is a self-declared engineering statement about this catalog's controls, not proof of security.

"Trustworthy" in the name refers to security properties of the enforcement path. It does not cover the broader characteristics of trustworthy AI, such as validity, fairness or explainability, that frameworks like the NIST AI RMF describe.

## The five pillars

| Pillar | Question | Contents |
| --- | --- | --- |
| Scope & Stewardship (S) | What could go wrong, and who owns it? | Scope and a named owner, the capability profile that sets the required level, Least Agency, the threat model, and the register of consequential operations. |
| Trust & Isolation (T) | What must stay separate and trustworthy? | Untrusted content stays data; tenant, memory, provider, egress, rendering, sandbox, browser, MCP and coding-agent boundaries; component integrity. |
| Authority & Access (A) | Who may do what, and under which limits? | One dispatch path, deny by default, authority from trusted state at the moment of effect, provenance of consequential values, approvals, delegation, identity, and budgets. |
| Notice & Neutralize (N) | Can we see, stop, and improve behavior? | Audit of proposed, attempted, denied and confirmed effects, signals routed to an owner, stop without deploy, recovery, and governed change. |
| Demonstrated Defenses (D) | Can we show that the controls work? | Hostile tests with authorized twins through the real path, a test for every injection channel, evidence scope, and the severity-rated release gate. |

![STAND: five pillars (Scope & Stewardship, Trust & Isolation, Authority & Access, Notice & Neutralize, Demonstrated Defenses) support secure agentic applications on a foundation of security enforced in application code. Central principle: the model proposes, the application enforces. The pillar guide in docs/pillars.md is the text equivalent.](docs/stand-infographic.png)

The [pillar guide and worked example](docs/pillars.md) is the text equivalent of the artwork. Download the [PNG](docs/stand-infographic.png), or edit the [SVG](docs/stand-infographic.svg).

## What is included

- **The skill**: [SKILL.md](SKILL.md) holds the workflow, the always-on critical-boundary invariants and the routing table. [agents/openai.yaml](agents/openai.yaml) is optional Codex metadata.
- **The control catalog**: [catalog/controls.json](catalog/controls.json) is the normative source, rendered per pillar into [references/controls/](references/controls/index.md). It holds 78 controls (S 6, T 27, A 25, N 10, D 10), each with a statement in BCP 14 language, applicability conditions, one level (61 at Level 1, 12 at Level 2, 5 at Level 3), a default failure severity, a minimum evidence scope, OWASP ASI identifiers, verification cases and evidence. IDs such as A-06 are never reused ([catalog/ledger.json](catalog/ledger.json)).
- **Profile, levels and conformance**: [references/profile-and-levels.md](references/profile-and-levels.md) explains how to compute the required level and triage a change. [references/conformance.md](references/conformance.md) defines statuses, evidence scopes, the release gate, and self-declared conformance and progress statements.
- **References** loaded on demand: [runtime controls](references/runtime-controls.md), [MCP](references/mcp.md), [implementation patterns](references/patterns.md), [verification method](references/verification.md), the [ASI risk view](references/owasp-agentic-top-10.md) (adapted from the OWASP Top 10 for Agentic Applications 2026), [framework sources](references/frameworks.md) and [control mappings](references/mappings.md).
- **Templates**: a [security record](assets/agent-security-record.md) keyed by control ID, and an [AGENTS.md snippet](assets/AGENTS-snippet.md) for making the workflow required in a project.
- **Evaluations**: [evals/](evals/README.md) defines behavioral cases and how runs are recorded, for testing whether the skill changes what a coding agent builds.

The [repository map](#repository-map) below is the complete file inventory.

## How it works

1. **Triage.** Classify the task from its diff. NONE (no security trigger location) ends the workflow. SCOPED (trigger locations touched, capability profile unchanged) gets a focused set of controls and a compact record. FULL (a new application, agent context or entry point, or a profile change) gets a complete assessment.
2. **Profile and level.** For each agent context, record whether it reads untrusted input, can reach sensitive data and can cause an external effect, and how autonomous it is. The combination computes the required level, and an unknown property counts as present (S-02).
3. **Route controls.** A routing table maps the touched code locations to control IDs, filtered by applicability and level. The agent loads only the selected entries.
4. **Enforce.** Implement each control in code, policy or infrastructure that the model cannot alter, inside the requested feature and the boundaries it creates or changes. FULL assesses every applicable control, but gaps in unchanged features are recorded as findings and new flows or limits the request did not ask for as owner decisions, not built unasked; the critical-boundary controls on the requested feature's path are always built.
5. **Verify.** Exercise each control with a hostile case and an authorized twin through the real execution path, at or above its minimum evidence scope (D-01 to D-03).
6. **Record.** Record each control by ID with a closed status and the evidence scope achieved, apply the severity-rated release gate (D-06), and report what ran, what failed and which risks remain. Owner decisions are left to a human.

A SCOPED change produces a record like this one, taken from the worked example in [references/profile-and-levels.md](references/profile-and-levels.md). Its budget is 12 lines plus one per routed control, counting every non-blank line added to the record, fences included:

```text
Change: CH-142, payments adapter timeout 30s to 10s
Tier: SCOPED (timeout and retry handling only); locations: timeouts and retries (payments adapter)
Profile: unchanged (no new tool, data source, renderer or autonomy)
A-21: implemented-and-verified, integration, A-21/C1 stalled transport abandoned at 10s, A-21/C2 denial not retried via fallback, A-21/C3 end-to-end deadline held, A-21/C4 twin pass
A-05: implemented-and-verified, integration, A-05/C1 duplicate delivery one effect, A-05/C2 timeout-after-commit reconciled, A-05/C3 split amount capped, A-05/C4 twin pass
D-05 (touched rows): implemented-and-verified, integration, "transport ignores its timeout" A-21/C1 and A-21/C3, "timeout after possible commit" A-05/C2
Tests run: pytest tests/security -k "A-21 or A-05": 8 passed
Residual risk: none new
Owner decisions: retry cap 3 to 2 proposed (not implemented)
Readiness: ready-within-scope (baseline value; routed rows re-verified, no new finding)
Approver: unassigned
Other controls: not re-assessed (outside change scope)
```

## Install

Install only the skill bundle, never a clone of the whole repository: `SKILL.md references assets agents LICENSE LICENSES THIRD_PARTY_NOTICES.md`, copied into a folder named `stand`.

| Host | Destination | Invoke |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/stand` (user-scoped) or `.claude/skills/stand` (project) | `/stand` |
| Codex | `$HOME/.agents/skills/stand` (user-scoped) or `.agents/skills/stand` (repository) | `$stand` |
| Other Agent Skills hosts | `.agents/skills/stand` | see the host's documentation |

The [installation guide](docs/install.md) explains cloning and pinning a reviewed commit, a copy command that refuses to overwrite an existing installation, adoption through `AGENTS.md`, and how to verify the result. The installed bundle is Markdown, YAML and license text: it ships no executable code and needs no network access, MCP server or credentials. Preserve LICENSE, LICENSES/ and THIRD_PARTY_NOTICES.md when distributing a copy.

## Relationship to OWASP and other work

The framework basis is fixed. Every mapping below is an engineering mapping, not a certification, conformance or coverage claim.

| Group | Source | How it is used |
| --- | --- | --- |
| Basis | OWASP GenAI Security Project, [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) | Risk taxonomy. Each control lists the ASI01 to ASI10 risks it is designed to address. |
| Basis | [AIUC-1](https://standard.aiuc-1.com/) | Mappings to requirement and control IDs. |
| Basis | [NIST AI RMF 1.0 (NIST AI 100-1)](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf), with its [Generative AI Profile (NIST AI 600-1)](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf) as supporting guidance | Mappings to subcategories and suggested actions. |
| Basis | [ISO/IEC 42001](https://www.iso.org/standard/42001) | Themes only, never clauses. |
| Related OWASP | [OWASP AISVS 1.0](https://github.com/OWASP/AISVS) | Cross-referenced by version-prefixed requirement ID where a requirement corresponds, for example A-11 to v1.0-C9.2.8 (partial). AISVS levels are assurance depths an organization selects; this catalog's levels are computed from a capability profile. |
| Related OWASP | [Agent Control Standard](https://genai.owasp.org/resource/agent-control-standard-acs/) (specification v0.1.0, resource published September 1, 2026) | Specifies middleware hooks through which a separate guardian can permit, deny or modify actions. In specification v0.1.0 (checked 2026-10-03), ACS defaults to fail-open (§4.1 Handshake failure, §6.4 Honoring decisions), while A-02 requires denial when a policy check fails or times out. Where a platform implements those hooks, authorization and stop tests should exercise them. |
| Related OWASP | [Securing Agentic Applications Guide 1.0](https://genai.owasp.org/resource/securing-agentic-applications-guide-1-0/), [AI Agent Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html) | Design and implementation guidance. |
| Related OWASP | [OWASP Agentic Skills Top 10](https://owasp.org/projects/agentic-skills-top-10) (Incubator) | Risks in skills themselves. It applies to this skill too; review the bundle against it before installing. This project's own assessment is in [docs/ast10-self-assessment.md](docs/ast10-self-assessment.md). |
| Related OWASP | [OWASP AI Exchange](https://owaspai.org/) (Flagship project since March 2025; CC0 1.0; checked 2026-10-04) | Body of knowledge on AI threats and controls, including agentic AI. Related reading, not mapped per control. |
| Related OWASP | [OWASP Non-Human Identities Top 10](https://owasp.org/www-project-non-human-identities-top-10/) (2025; Incubator) | Risks of machine identities and their credentials. Appendix C of the ASI publication (pp. 42-43) maps each NHI risk to ASI entries. Related to A-03, A-16, A-17 and T-05; not mapped per control. |
| Related OWASP | [OWASP CycloneDX](https://cyclonedx.org/) | Bill of materials standard. Appendix B of the ASI publication (p. 41) presents CycloneDX and AIBOM as the supply-chain complement to the risk taxonomy. The S-04 inventory can be exported as a CycloneDX ML-BOM; the catalog does not require it. |
| Related work | [Meta's Agents Rule of Two](https://ai.meta.com/blog/practical-ai-agent-security/), [AWS Agentic AI Security Scoping Matrix](https://aws.amazon.com/blogs/security/the-agentic-ai-security-scoping-matrix-a-framework-for-securing-autonomous-ai-systems/), [CSA MAESTRO](https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro) | Capability scoping, autonomy scoping and threat modeling. |
| Related work | [Praxen](https://open-agent-ai-security.github.io/praxen/) (contributed by Exabeam, June 2026, Apache-2.0) with [RAISE](https://open-agent-ai-security.github.io/praxen/guide/RAISE.html), Responsible AI Software Engineering by Steve Wilson (checked 2026-10-04) | A coding-agent plugin that compares an agent's declared policy with its code, live deployment state and behavioral logs, maps findings to OWASP Top 10 lists, and scores the six RAISE categories on a 0 to 5 maturity scale. Not mapped. STAND is unrelated to that RAISE; this project's former working name was RAISE, and the rename avoids the confusion. |

### At a glance

Descriptions of other work are taken from their own public pages. The table compares what each work is, not how good it is; the works answer different questions and are often used together.

| Work | Kind | Unit | Levels or scale | Delivered as |
| --- | --- | --- | --- | --- |
| OWASP Top 10 for Agentic Applications 2026 | Risk taxonomy | Ten risk entries (ASI01 to ASI10) with examples and mitigations | None | Publication |
| OWASP AISVS 1.0 | Verification standard | Requirements | Levels 1 to 3, an assurance depth the organization selects | Document and repository |
| Agent Control Standard v0.1.0 | Runtime interface specification | Hooks an agent platform exposes to a policy guardian | None | Specification |
| Securing Agentic Applications Guide 1.0 | Design and implementation guide | Guidance by topic | None | Publication |
| CSA MAESTRO | Threat-modeling method | Threats per layer of a seven-layer reference architecture | None | Published method |
| Meta's Agents Rule of Two | Design rule | Three properties, of which an agent should hold at most two in one session | None | Article |
| AWS Agentic AI Security Scoping Matrix | Scoping model | Autonomy scopes | Four scopes | Article |
| Praxen with RAISE | Verification tool and maturity model | Gaps between an agent's declared policy and observed evidence | 0 to 5 per category, six categories | Coding-agent plugin |
| STAND | Engineering control catalog and build workflow | 78 controls with stable IDs, each with a hostile case, an authorized twin and a minimum evidence scope | Levels 1 to 3, computed per agent context from its capability profile | Coding-agent skill, with a security record keyed by control ID |

What this project adds is an agent-executable workflow in which every control names a hostile case, an authorized twin, a minimum evidence scope and a record artifact, with levels computed from what each agent context can actually do. Source editions, check dates and the limits of each mapping are in [references/frameworks.md](references/frameworks.md); control-level mappings are in [references/mappings.md](references/mappings.md).

## Status and version

- Catalog version 0.1.0, status **draft**. Before 1.0, every normative change bumps the minor version and is listed in [CHANGELOG.md](CHANGELOG.md).
- No release is tagged yet. Pin a reviewed commit.
- No behavioral results are published yet. The [evaluation cases](evals/README.md) define what will be measured and the acceptance bar; that page also summarizes a small internal pilot, labelled as such, which is not a benchmark.
- Control IDs are frozen from the first tagged release. If the framework or a pillar is ever renamed, IDs keep their current letters: the letters are identifiers, not abbreviations of the name. The catalog records its namespace, `STAND`, for references that need to qualify an ID outside this catalog ([references/profile-and-levels.md](references/profile-and-levels.md)).

## Origin

STAND was started by engineers at Armorer Labs. Its guidance is vendor neutral and never requires a commercial product or service.

## License

- Documentation and data are licensed under [CC BY-SA 4.0](LICENSES/CC-BY-SA-4.0.txt). That includes SKILL.md, references/, assets/, agents/, docs/ (including the infographic), the text and data in evals/, catalog/, this README and the other Markdown files at the repository root, except the Developer Certificate of Origin 1.1 text quoted in CONTRIBUTING.md, which is reproduced verbatim under its own terms.
- Code in scripts/, tests/ and .github/, and repository configuration files such as .gitattributes and .gitignore, are licensed under the [MIT license](LICENSE).
- [references/owasp-agentic-top-10.md](references/owasp-agentic-top-10.md) uses identifiers and titles from the OWASP Top 10 for Agentic Applications 2026 by the OWASP GenAI Security Project and is distributed under CC BY-SA 4.0 with attribution.
- Sharing an adapted version of the documentation, including an adapted SKILL.md, carries the ShareAlike condition of CC BY-SA 4.0.

[REUSE.toml](REUSE.toml) records the same per-path licensing in machine-readable form. Referenced standards and publications keep their own terms. See [LICENSE](LICENSE), [LICENSES/](LICENSES/CC-BY-SA-4.0.txt) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). This independent project does not imply endorsement or certification by the referenced organizations.

## Repository map

| Path | Purpose | Installed |
| --- | --- | --- |
| [SKILL.md](SKILL.md) | Skill entry point: workflow, invariants and routing | yes |
| [agents/openai.yaml](agents/openai.yaml) | Optional Codex metadata | yes |
| [references/controls/](references/controls/index.md) | Generated per-pillar control files and index | yes |
| [references/mappings.md](references/mappings.md) | Generated control mappings to AIUC-1, NIST and AISVS | yes |
| [references/profile-and-levels.md](references/profile-and-levels.md) | Capability profile, applicability, levels, triage, ID scheme | yes |
| [references/conformance.md](references/conformance.md) | Normative language, statuses, evidence scope, conformance, release gate | yes |
| [references/runtime-controls.md](references/runtime-controls.md) | Implementation guidance keyed by control ID | yes |
| [references/mcp.md](references/mcp.md) | MCP guidance keyed by control ID | yes |
| [references/patterns.md](references/patterns.md) | Illustrative implementation patterns | yes |
| [references/verification.md](references/verification.md) | Test design and evidence method | yes |
| [references/owasp-agentic-top-10.md](references/owasp-agentic-top-10.md) | ASI view (CC BY-SA 4.0, OWASP attribution) | yes |
| [references/integrations.md](references/integrations.md) | Framework-owned loops, hosted platforms and enforcement in other repositories | yes |
| [references/frameworks.md](references/frameworks.md) | Framework basis, related work, source editions | yes |
| [assets/agent-security-record.md](assets/agent-security-record.md) | Security record template keyed by control ID | yes |
| [assets/AGENTS-snippet.md](assets/AGENTS-snippet.md) | Project instruction snippet | yes |
| [LICENSE](LICENSE), [LICENSES/](LICENSES/CC-BY-SA-4.0.txt), [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) | Licenses and attribution | yes |
| [catalog/](catalog/controls.json) | Normative catalog, ID ledger, mapping justifications, and the NIST and AIUC-1 identifier registries | no |
| [docs/pillars.md](docs/pillars.md) | Pillar guide and worked example | no |
| [docs/install.md](docs/install.md) | Installation guide | no |
| [docs/ast10-self-assessment.md](docs/ast10-self-assessment.md) | Self-assessment of this skill against the OWASP Agentic Skills Top 10 | no |
| [docs/stand-infographic.svg](docs/stand-infographic.svg), [PNG](docs/stand-infographic.png) | Pillar infographic | no |
| [evals/](evals/README.md) | Behavioral evaluation cases | no |
| [scripts/catalog_model.py](scripts/catalog_model.py) | Catalog model shared by the renderer and the validator | no |
| [scripts/render_catalog.py](scripts/render_catalog.py) | Renders and checks the generated reference files | no |
| [scripts/validate.py](scripts/validate.py) | Offline repository and bundle validation | no |
| [tests/](tests) | Validator and renderer tests | no |
| [.github/](.github/workflows/validate.yml) | CI workflow and dependency updates | no |
| [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), [CHANGELOG.md](CHANGELOG.md) | Contribution rules, vulnerability reporting, change history | no |
| [REUSE.toml](REUSE.toml) | Machine-readable per-path licensing | no |

## Contributing and security

Read [CONTRIBUTING.md](CONTRIBUTING.md) before proposing a change. Report vulnerabilities, including guidance that would lead implementers to an exploitable design, privately as described in [SECURITY.md](SECURITY.md), not in a public issue.

With Python 3.10 or newer, run from this branch:

```bash
python3 scripts/render_catalog.py --check
python3 scripts/validate.py
python3 scripts/validate.py --stage "$(mktemp -d)/stand"
python3 -m unittest discover -s tests -v
```

These checks validate the catalog, the generated reference files, metadata, links, package portability, and the failure behavior of the validator and the renderer. They do not evaluate a model or prove the security of an application.
