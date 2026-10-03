# Security policy

This repository publishes security guidance, a control catalog and a coding-agent skill. A flaw in them can lead many applications to the same insecure design, or lead a coding agent to weaken an application it is changing. Report such flaws privately so they can be fixed before they are public.

## How to report

Use GitHub private vulnerability reporting: open this repository's **Security** tab, choose **Advisories**, then **Report a vulnerability**. Only you and the maintainers can see the report.

If that button is not available, open a public issue that asks the maintainers for a private contact, and include no vulnerability details in it. Do not report vulnerabilities in public issues, pull requests or discussions.

## In scope

- **Guidance that leads to an exploitable design.** A control statement, routing rule, pattern or example that, if followed, leaves an attacker-reachable path to unauthorized data, privilege escalation, an unapproved consequential effect, sandbox escape or loss of the ability to stop an agent.
- **Skill instructions that weaken controls.** Text in `SKILL.md`, `references/`, `assets/` or `agents/` that could cause a coding agent to weaken or remove a control or security test, exfiltrate data, or take unauthorized external actions.
- **Validator and CI bypasses.** Defects in `scripts/` or `.github/` that let a broken or tampered package pass, for example a staged bundle that validates with links leaving the bundle, generated references that drift from the catalog without failing the render check, or a workflow that exposes credentials or runs untrusted code with write access.

## Out of scope

Use public issues for these:

- disagreements about mappings to OWASP, AIUC-1, NIST, ISO/IEC 42001 or AISVS, and outdated source versions;
- wording, typos, broken links, and requests for new controls or wider coverage, unless current guidance actively leads to an exploitable design.

Report elsewhere:

- vulnerabilities in an application built with this skill, to that application's owner;
- vulnerabilities in coding-agent hosts, model providers, MCP servers or other third-party products, to their vendors;
- errors in a referenced standard, to its publisher.

## What to include

- the affected file, and the commit or catalog version;
- the control IDs involved, if any;
- the attack path: what an attacker controls, and which data, authority or effect they gain;
- a minimal reproduction or hostile test that uses synthetic data only, with no real credentials, customer data or production traces;
- a suggested fix, if you have one, and how you would like to be credited.

Test only systems that you own or are authorized to test.

## What to expect

- We aim to acknowledge a report within 5 business days.
- We triage with the severity rubric in [references/conformance.md](references/conformance.md#severity-rubric) and tell you the outcome.
- We prepare the fix privately and agree a disclosure date with you. We aim to publish within 90 days of acknowledgement; if we need longer, we explain why and agree a new date with you.
- We publish the fix with a GitHub security advisory and a "Security" entry in [CHANGELOG.md](CHANGELOG.md). A fix that changes a control statement is a normative change and follows the catalog versioning rules in [CONTRIBUTING.md](CONTRIBUTING.md#change-the-catalog). The advisory names the affected catalog versions and controls, and conformance claims against those versions lapse for those controls until they are reassessed against the fixed version ([references/conformance.md](references/conformance.md#lapse)).
- We credit reporters in the advisory and the changelog unless they prefer to stay anonymous.

Please keep the details private until the advisory is published.

## Supported versions

Fixes are made on the default branch and included in the next release. Reports against the default branch and the most recent release are accepted.

## No bounty

This project does not run a bug bounty and does not pay for reports.
