# Repository instruction snippet

Use this only when a team asks to make the skill's workflow mandatory for a repository. Copy the block below into the repository's `AGENTS.md`, replace every `<placeholder>`, and leave these adoption notes out.

Adoption notes:

- Claude Code reads AGENTS.md only when the repository has no CLAUDE.md; if it has one, add `@AGENTS.md` to it.
- A skill is an instruction supply-chain dependency. Install a reviewed, pinned release or commit at the skill path your coding agents load from, and review updates to it like code.
- Make the security test command a required CI check where the repository's CI allows it. Repository instructions guide agents; only CI and runtime controls enforce.

```markdown
## Agent security workflow

- Skill: `stand`, installed at `<configured skill path for your host>` and pinned to `<reviewed release or commit>`.
- Security record: `<path to the agent security record>`.
- Security tests: `<command that runs the security tests non-interactively>`.

For every change, first classify the task-owned diff with these tiers, which summarize Step 0 of the skill. Reading the skill's SKILL.md to classify is allowed; only SCOPED and FULL load anything further.

- NONE: the diff touches no trigger location (copy that never enters model context or an outbound message, styling, static documentation, comments, non-security tests, unrelated business logic). Make the change without loading the skill's references, writing a record or adding security tests, and do not weaken an existing control or test.
- SCOPED: the diff touches a trigger location and the capability profile is unchanged: no new property, autonomy increase, entry point or feature tag (a first MCP server, browser, code execution or triggered runs is a new feature tag). Trigger locations include tool dispatch and schemas, authorization and identity, effect adapters, timeouts and retries, approvals, retrieval, memory, prompts and system prompts, model or provider settings, sandboxes, egress, MCP or A2A configuration, queues and triggers, rendering of model output, CI workflows and agent instruction files, audit, stop and revocation, budgets, dependencies, and security tests. Load the skill, implement and verify only the routed controls, add a compact change record to the security record, and run the security tests.
- FULL: a new agent or agent context, a new entry point, a capability-profile change (including a new feature tag) or higher computed level, a new principal type or tenant model, a replaced enforcement component, external effects added with no baseline record, or a request to assess or threat-model the system. Follow the whole skill procedure and update the security record. Assess every applicable control, but implement only within the requested feature and the boundaries it creates or changes, always including the critical-boundary controls on the requested feature's call path: record gaps in unchanged features as findings, and list other new flows, limits or behavior changes the request did not ask for as owner decisions, building the minimal mechanism (flagged as an owner decision) only when a critical-boundary control for the requested feature cannot otherwise be met.

Prompt, model, provider and agent-framework version changes are never NONE.

Enforce permissions, isolation and resource limits in deterministic controls outside the model (application code, identity and policy services, sandboxes, network policy and infrastructure), independently of model instructions. Verify each changed control with a hostile case and an authorized twin through the real execution path. Run the security tests before claiming readiness. Report the tier, the control IDs with status and evidence scope, the tests actually run, and open risks with severity and an owner or "unassigned".

If the skill cannot be loaded, say so and do not claim that this workflow was completed. Preserve repository scope, review rules and the existing authorization requirements for external actions. The skill complements enforced CI and runtime controls; it does not replace them.
```
