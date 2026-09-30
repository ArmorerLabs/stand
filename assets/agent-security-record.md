# Agent security record

Adapt this record to the project's existing evidence format. Remove this instruction after adaptation. Use explicit unknown or unverified entries rather than inventing evidence or approval.

## System and change

- Application, owner, date, change/commit identifier:
- Intended users, use, affected people, and forbidden outcomes:
- Deployment and test environments:
- Model/provider/version, orchestration, prompts, policies, tools, and relevant dependencies:
- Data classes, retention, provider handling, and tenant boundaries:
- Request/data flow and trust boundaries, linked diagram or concise trace:

## Authority

| Actor/workload | Operation | Permitted resources and destinations | Data access | Limits and expiry | Approval policy | Enforcement location |
| --- | --- | --- | --- | --- | --- | --- |

## Threats, controls, and evidence

For a new baseline, assess ASI01 through ASI10. For a scoped change, reference the baseline and update affected categories. Use the exact names in the skill's OWASP reference.

| Risk ID and abuse case | Applicable, with reason | Control and code/config reference | Test and observed result | Evidence scope | Status | Residual risk and owner |
| --- | --- | --- | --- | --- | --- | --- |

Evidence scope: unit, integration with controlled adapter, simulation, isolated runtime, or deployed environment. Status: verified, unverified, planned, not applicable, or failing. Keep an unrun test distinct from a passed test.

## Verification record

- Commands actually executed and environment/configuration:
- Positive behavior preserved:
- Adversarial cases and counts, observed failures, and unresolved cases:
- CI test integration and required-check enforcement, each with evidence:
- Runtime boundaries still needing verification:

## Operation and decision

- Monitoring signals and redacted audit evidence:
- Stop/revoke mechanism, descendant jobs, and in-flight limitations:
- Incident owner, containment, recovery, memory cleanup, and irreversible effects:
- Readiness: ready within stated scope, blocked, or confined prototype:
- Outstanding organizational decisions or infrastructure work:
- Accepted exceptions, human owner, evidence of acceptance, expiry, and compensating controls:
- Review triggers and risk-based review interval:

## Framework context

Record source editions and only the mappings needed by this project. Distinguish this engineering assessment from certification or organization-wide conformance.
