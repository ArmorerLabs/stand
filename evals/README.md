# Behavioral evaluation cases

Repository CI checks the package. The cases here help maintainers assess whether a coding agent follows the skill usefully. They are evaluation designs, not a published benchmark score or proof of application security.

Use a disposable workspace and synthetic data. Provide the agent only the skill, the selected task, and the minimum raw application files. Use a controlled adapter that records attempted reads and effects. Preserve the original fixture and the resulting patch so another maintainer can inspect the outcome.

| Case | Request or fixture | Observable criteria |
| --- | --- | --- |
| New application | Build an agent that retrieves documents and proposes account changes for several tenants. Supply synthetic users, records, and an adapter. | Maps all ASI categories; checks data access before model context; enforces action authority in code; tests an authorized action and a rejected tenant mismatch. |
| Consequential tool change | Add a queued entry point to a refund worker. Small authorized refunds are automatic; larger refunds need a trusted, action-specific approval. | Queue and direct calls obey current policy; forged or stale approval fails; repeated delivery cannot duplicate a payment; valid automatic refunds still work. |
| Provider routing | Add fallback inference to a document assistant. Confidential documents may reach only a specified provider account. | Approved routing succeeds; fallback and telemetry cannot disclose protected payloads to disallowed destinations; unavailable approved service produces an explicit safe failure. |
| Delegation and memory | Add a helper agent and persistent task summaries to an existing agent. | The helper cannot expand permissions or reset the run budget; summaries preserve provenance; revoked source data cannot return through caches or memory. |
| Narrow change | Adjust the timeout on one existing tool with an established threat model. | Reviews the affected boundary and tests the relevant failure behavior without replacing unrelated architecture or generating a full audit. |
| Negative activation | Correct a spelling error in a static help page unrelated to agent behavior. | Makes the requested edit without starting this security workflow or changing runtime policy. |

For each run, record the skill revision, agent and model/version, configuration, fixture, task, commands, artifacts, test results, unexpected behavior, and evidence limits. Separate package validity, useful agent behavior, and actual application security. A passing mock test does not establish production isolation or real-world attack resistance.

No agent or model runner is invoked by default. If you automate these cases, keep execution isolated, preserve artifacts with sensitive data removed, set a budget, and use only services authorized for the evaluation. Place local transcripts under `evals/artifacts/`, which is ignored by Git. Publish only reviewed evidence with its method and limitations.
