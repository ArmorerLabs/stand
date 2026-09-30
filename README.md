# RAISE

**Responsible Agentic Innovation through Secure Engineering**

Build capable agents with security by design.

RAISE is a security engineering framework delivered as a reusable coding-agent skill. It helps developers build agentic applications with explicit authority limits, enforceable security controls, and verification evidence.

The model proposes actions. Application code enforces permissions, resource limits, and approval policy. The workflow supports new applications and focused changes to existing systems, across languages, model providers, and orchestration frameworks.

## What the skill does

- Maps all ten OWASP Agentic Application risks to concrete control outcomes and adversarial tests.
- Guides tool authorization, tenant isolation, retrieval and memory, delegation, execution isolation, provider data handling, approvals, revocation, and recovery.
- Requires evidence from actual application boundaries and distinguishes simulation from verified effects.
- Produces a scoped security record with implementation references, test results, owners, and remaining risks.

The [framework reference](references/frameworks.md) records the source snapshot and selected mappings to AIUC-1, ISO/IEC 42001, and NIST AI RMF with its Generative AI Profile. These mappings support engineering decisions. They do not establish certification or complete protection.

## Use with a coding agent

The entry point is [SKILL.md](SKILL.md). Keep it together with `references/` and `assets/` so the agent can load details when needed. Preserve the license and attribution files when distributing a copy.

For any coding agent that can read local files, give it a concrete request such as:

```text
Read SKILL.md in the raise checkout and apply it to this task.
Add a support agent that searches tenant documents and proposes account changes.
Implement the relevant controls, test the execution paths, and record remaining risks.
```

That is explicit file loading. Native discovery, invocation syntax, and supported instruction files depend on the host. The Markdown workflow is portable; integrations must be verified for the agent and version you use. `agents/openai.yaml` contains optional Codex metadata.

### Codex installation

From a reviewed checkout, copy the skill files into the configured personal skills directory. This example uses the personal directory described in [OpenAI's skill evaluation guide](https://developers.openai.com/blog/eval-skills). It refuses to overwrite an existing installation:

```bash
skill_destination="${CODEX_HOME:-$HOME/.codex}/skills/raise"
if [ -e "$skill_destination" ] || [ -L "$skill_destination" ]; then
  printf '%s\n' "Already installed: $skill_destination. Review updates before replacing it."
else
  mkdir -p "$skill_destination" &&
  cp -R SKILL.md references assets agents LICENSE THIRD_PARTY_NOTICES.md "$skill_destination/"
fi
```

Confirm the skill appears in your Codex skill list, starting a new session if needed. Invoke it with a task:

```text
$raise Add a document-search agent with tenant isolation and scoped tools.
```

For a team installation, use the repository or managed skill location supported by your coding agent. Pin a reviewed commit or release and review changes before updating installed copies. This repository contains one skill; it does not require an MCP server or application credentials.

## Make the workflow required in a project

Adapt [assets/AGENTS-snippet.md](assets/AGENTS-snippet.md) into the project's instructions if the chosen coding agent honors `AGENTS.md`. For other hosts, place the equivalent rule in their supported repository instructions. Keep the requirement scoped to changes affecting agentic behavior.

Require the application's relevant security tests in its CI and protect consequential policy changes through code review. Skill activation, passing this repository's checks, and enforced application security are separate properties. Do not rely on automatic discovery alone for a mandatory development policy.

## Repository contents

| Path | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Main development workflow and reference routing |
| [references/owasp-agentic-top-10.md](references/owasp-agentic-top-10.md) | All ten risk categories, control outcomes, and test ideas |
| [references/runtime-controls.md](references/runtime-controls.md) | Implementation guidance for application boundaries |
| [references/verification.md](references/verification.md) | Test design, evidence, and readiness criteria |
| [references/frameworks.md](references/frameworks.md) | Primary sources, versions, and selected framework mappings |
| [assets/agent-security-record.md](assets/agent-security-record.md) | Adaptable evidence template |
| [evals/README.md](evals/README.md) | Behavioral evaluation cases and recording guidance |
| [scripts/validate.py](scripts/validate.py) | Offline package validation used by CI |

## Validate and contribute

With Python 3.10 or newer, run from this checkout:

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

These checks validate metadata, bundled references, package portability, and the validator's failure behavior. They do not evaluate a model or prove the security of an application. Behavioral evaluations are separate and must record the agent, model, environment, changes, and observed results. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License and attribution

Original project material is available under the [MIT license](LICENSE). The OWASP coverage reference is distributed under CC BY-SA 4.0 with attribution. Referenced standards retain their respective terms. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for scope and sources. This independent project does not imply endorsement or certification by the referenced organizations.
