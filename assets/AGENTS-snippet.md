## Required RAISE workflow for agentic application changes

Use the `raise` skill when creating or changing agent planning, tool execution, MCP integration, retrieval, memory, delegation, autonomous jobs, or their permission boundaries. Load its `SKILL.md` from the team's configured skill location before implementation. Make the skill folder available to every supported coding agent.

For a new application, assess all ten OWASP Agentic Top 10 categories and record applicable controls and evidence. For an existing application, update the affected controls and tests. Enforce permissions and resource limits in application code, independently of model instructions. Verify authorized behavior and adversarial cases through the actual execution path.

Keep the assessment and relevant security tests with the project. Run required checks before claiming readiness. Report missing evidence and unresolved critical failures explicitly. A missing skill must be reported, and must not result in a claim that this workflow was completed.

Apply this requirement to the requested agentic behavior. Unrelated cosmetic or documentation changes do not require a new assessment. Preserve repository scope, review rules, and existing authorization for external actions. Skill invocation complements enforced CI and runtime controls.
