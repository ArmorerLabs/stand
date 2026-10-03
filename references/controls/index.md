<!-- Generated from catalog/controls.json in the source repository by scripts/render_catalog.py. Do not edit; propose changes upstream. -->
<!-- License: CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/). SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Control catalog index

Catalog version 0.1.0 (draft). 78 controls in 5 pillars. Control IDs are stable: they are never reused or renumbered. Framework mappings are listed in [mappings.md](../mappings.md).

How to use the catalog:

1. Compute the capability profile and level, then select every control whose applies_when matches at or below that level, as defined in [profile-and-levels.md](../profile-and-levels.md).
2. Record each selected control's status and evidence by ID and apply the release gate defined in [conformance.md](../conformance.md).

## R: Risk & Responsibility

What could go wrong, and who owns it? Full entries: [R.md](R.md).

| ID | Title | Level | Applies when | Failure severity |
| --- | --- | --- | --- | --- |
| [R-01](R.md#r-01-accountable-scope-owner-and-risk-acceptance) | Accountable scope, owner and risk acceptance | 1 | `all` | high |
| [R-02](R.md#r-02-capability-profile-and-required-level) | Capability profile and required level | 1 | `all` | high |
| [R-03](R.md#r-03-least-agency) | Least Agency | 1 | `all` | medium |
| [R-04](R.md#r-04-threat-model-inventory-boundary-trace-and-asi-applicability) | Threat model: inventory, boundary trace and ASI applicability | 1 | `all` | high |
| [R-05](R.md#r-05-consequential-operations-register-and-trusted-sources) | Consequential operations register and trusted sources | 1 | `external-effect` | high |
| [R-06](R.md#r-06-data-classification-and-disclosure-policy) | Data classification and disclosure policy | 1 | `sensitive-data` | high |

## A: Authority & Access

Who may do what, and under which limits? Full entries: [A.md](A.md).

| ID | Title | Level | Applies when | Failure severity |
| --- | --- | --- | --- | --- |
| [A-01](A.md#a-01-single-dispatch-path) | Single dispatch path | 1 | `tools` or `mcp` or `delegation` or `queued-work` | critical |
| [A-02](A.md#a-02-deny-by-default-strict-schemas-and-canonical-requests) | Deny by default, strict schemas and canonical requests | 1 | `tools` or `mcp` | critical |
| [A-03](A.md#a-03-authority-from-trusted-context) | Authority from trusted context | 1 | `tools` | critical |
| [A-04](A.md#a-04-authorization-evaluated-at-the-moment-of-effect) | Authorization evaluated at the moment of effect | 1 | `tools` or `queued-work` | critical |
| [A-05](A.md#a-05-durable-idempotency-and-atomic-effects) | Durable idempotency and atomic effects | 1 | `external-effect` | high |
| [A-06](A.md#a-06-provenance-aware-consequential-values) | Provenance-aware consequential values | 1 | `untrusted-input+external-effect` or `separation-pattern+external-effect` | critical |
| [A-07](A.md#a-07-task-scope-binding) | Task-scope binding | 1 | `untrusted-input+external-effect` or `separation-pattern+external-effect` | critical |
| [A-08](A.md#a-08-rule-of-two-gating) | Rule of Two gating | 1 | `untrusted-input+sensitive-data+external-effect` | critical |
| [A-09](A.md#a-09-least-privilege-tool-profiles-and-auto-run-limits) | Least-privilege tool profiles and auto-run limits | 1 | `tools` or `mcp` or `coding-agent` | high |
| [A-10](A.md#a-10-destructive-and-irreversible-operation-guard) | Destructive and irreversible operation guard | 1 | `external-effect` | critical |
| [A-11](A.md#a-11-approval-binding) | Approval binding | 1 | `approvals` | critical |
| [A-12](A.md#a-12-approval-presentation-integrity) | Approval presentation integrity | 1 | `approvals` or `browser-agent` | high |
| [A-13](A.md#a-13-approval-anomaly-cues-and-fatigue-management) | Approval anomaly cues and fatigue management | 2 | `approvals` | medium |
| [A-14](A.md#a-14-step-up-and-dual-control-for-highest-impact-effects) | Step-up and dual control for highest-impact effects | 3 | `approvals` | high |
| [A-15](A.md#a-15-delegation-by-intersection-and-receiver-re-authorization) | Delegation by intersection and receiver re-authorization | 1 | `delegation` or `inter-agent` | critical |
| [A-16](A.md#a-16-token-handling-and-mcp-authorization) | Token handling and MCP authorization | 1 | `tools` or `mcp` or `delegation` | critical |
| [A-17](A.md#a-17-agent-workload-identity-and-token-exchange) | Agent workload identity and token exchange | 2 | `tools` | high |
| [A-18](A.md#a-18-sender-constrained-tokens) | Sender-constrained tokens | 3 | `tools` or `mcp` or `delegation` | high |
| [A-19](A.md#a-19-principals-triggers-and-shared-contexts) | Principals, triggers and shared contexts | 1 | `triggered-runs` or `shared-context` | critical |
| [A-20](A.md#a-20-cumulative-run-budgets) | Cumulative run budgets | 1 | `tools` or `delegation` | high |
| [A-21](A.md#a-21-bounded-retries-and-caller-enforced-deadlines) | Bounded retries and caller-enforced deadlines | 1 | `tools` or `queued-work` | high |
| [A-22](A.md#a-22-principal-tenant-and-provider-quotas) | Principal, tenant and provider quotas | 2 | `tools` | medium |
| [A-23](A.md#a-23-no-self-modification-or-self-replication) | No self-modification or self-replication | 1 | `tools` or `delegation` or `coding-agent` | critical |
| [A-24](A.md#a-24-outbound-payload-checks) | Outbound payload checks | 1 | `untrusted-input+external-effect` or `separation-pattern+external-effect` or `shared-context+external-effect` or `triggered-runs+external-effect` | critical |
| [A-25](A.md#a-25-verified-changes-to-redirecting-values) | Verified changes to redirecting values | 1 | `tools+external-effect` | critical |

## I: Isolation & Integrity

What must stay separate and trustworthy? Full entries: [I.md](I.md).

| ID | Title | Level | Applies when | Failure severity |
| --- | --- | --- | --- | --- |
| [I-01](I.md#i-01-untrusted-content-stays-data-and-taints-its-context) | Untrusted content stays data and taints its context | 1 | `untrusted-input` | critical |
| [I-02](I.md#i-02-enforced-separation-patterns) | Enforced separation patterns | 1 | `separation-pattern` | critical |
| [I-03](I.md#i-03-hidden-text-normalization-and-reviewer-view) | Hidden-text normalization and reviewer view | 2 | `untrusted-input` | medium |
| [I-04](I.md#i-04-system-prompts-hold-no-secrets-or-enforcement) | System prompts hold no secrets or enforcement | 1 | `all` | high |
| [I-05](I.md#i-05-no-ambient-credentials-or-enforcement-access-in-model-influenced-processes) | No ambient credentials or enforcement access in model-influenced processes | 1 | `tools` or `code-execution` or `browser-agent` or `mcp` or `coding-agent` | critical |
| [I-06](I.md#i-06-retrieval-authorization-before-context) | Retrieval authorization before context | 1 | `retrieval` | critical |
| [I-07](I.md#i-07-memory-provenance-scope-expiry-and-revocation) | Memory provenance, scope, expiry and revocation | 1 | `memory` | high |
| [I-08](I.md#i-08-system-of-record-for-consequential-facts) | System of record for consequential facts | 1 | `external-effect` | critical |
| [I-09](I.md#i-09-server-held-conversation-state) | Server-held conversation state | 1 | `client-conversation` | critical |
| [I-10](I.md#i-10-provider-data-routing) | Provider data routing | 1 | `sensitive-data+provider-routing` or `sensitive-data+mcp` | critical |
| [I-11](I.md#i-11-provider-executed-tools) | Provider-executed tools | 1 | `provider-executed-tools` | critical |
| [I-12](I.md#i-12-network-egress-boundary) | Network egress boundary | 1 | `network-egress` | critical |
| [I-13](I.md#i-13-rendered-output-exfiltration-channels) | Rendered-output exfiltration channels | 1 | `rendered-output+untrusted-input` or `rendered-output+separation-pattern` | critical |
| [I-14](I.md#i-14-sink-safe-output-handling-and-no-implicit-execution) | Sink-safe output handling and no implicit execution | 1 | `rendered-output` or `tools` | critical |
| [I-15](I.md#i-15-code-execution-sandbox-baseline) | Code-execution sandbox baseline | 1 | `code-execution` | critical |
| [I-16](I.md#i-16-strong-isolation-tier) | Strong isolation tier | 2 | `code-execution+untrusted-input` | high |
| [I-17](I.md#i-17-browser-and-computer-use-containment) | Browser and computer-use containment | 1 | `browser-agent` | critical |
| [I-18](I.md#i-18-pinned-descriptors-and-fully-qualified-tool-identity) | Pinned descriptors and fully qualified tool identity | 1 | `mcp` or `inter-agent` | high |
| [I-19](I.md#i-19-local-tool-and-third-party-component-confinement) | Local tool and third-party component confinement | 1 | `mcp` or `coding-agent` | critical |
| [I-20](I.md#i-20-mcp-sampling-and-elicitation) | MCP sampling and elicitation | 1 | `mcp` | high |
| [I-21](I.md#i-21-inter-agent-message-integrity) | Inter-agent message integrity | 1 | `inter-agent` | high |
| [I-22](I.md#i-22-fault-propagation-containment) | Fault propagation containment | 2 | `delegation` or `inter-agent` or `queued-work` | high |
| [I-23](I.md#i-23-coding-and-ci-agent-boundaries) | Coding and CI agent boundaries | 1 | `coding-agent` | critical |
| [I-24](I.md#i-24-component-pinning-and-intake) | Component pinning and intake | 1 | `all` | high |
| [I-25](I.md#i-25-model-artifact-integrity) | Model artifact integrity | 1 | `model-artifacts` | high |
| [I-26](I.md#i-26-agent-to-human-communication-integrity) | Agent-to-human communication integrity | 2 | `rendered-output` | medium |
| [I-27](I.md#i-27-per-tenant-kernel-isolation-for-code-execution) | Per-tenant kernel isolation for code execution | 1 | `code-execution+multi-tenant` | high |

## S: Security Verification

Can we show that the controls work? Full entries: [S.md](S.md).

| ID | Title | Level | Applies when | Failure severity |
| --- | --- | --- | --- | --- |
| [S-01](S.md#s-01-enforcement-path-tests) | Enforcement-path tests | 1 | `all` | high |
| [S-02](S.md#s-02-hostile-proposals-with-authorized-twins) | Hostile proposals with authorized twins | 1 | `tools` | medium |
| [S-03](S.md#s-03-evidence-scope-runtime-boundaries-and-record-integrity) | Evidence scope, runtime boundaries and record integrity | 1 | `all` | high |
| [S-04](S.md#s-04-injection-channel-coverage-with-within-authority-payloads) | Injection channel coverage with within-authority payloads | 1 | `untrusted-input+external-effect` or `separation-pattern+external-effect` | high |
| [S-05](S.md#s-05-failure-revocation-and-concurrency-test-matrix) | Failure, revocation and concurrency test matrix | 1 | `tools` | high |
| [S-06](S.md#s-06-severity-rated-release-gate) | Severity-rated release gate | 1 | `all` | critical |
| [S-07](S.md#s-07-security-regressions-as-required-checks) | Security regressions as required checks | 1 | `all` | high |
| [S-08](S.md#s-08-live-model-adversarial-evaluation) | Live-model adversarial evaluation | 2 | `untrusted-input` | medium |
| [S-09](S.md#s-09-independent-adversarial-review-with-adaptive-attacks) | Independent adversarial review with adaptive attacks | 3 | `all` | high |
| [S-10](S.md#s-10-replay-before-rollout-and-before-authority-expansion) | Replay before rollout and before authority expansion | 3 | `external-effect` | medium |

## E: Evidence & Evolution

Can we see, stop, and improve behavior? Full entries: [E.md](E.md).

| ID | Title | Level | Applies when | Failure severity |
| --- | --- | --- | --- | --- |
| [E-01](E.md#e-01-decision-and-effect-audit-trail) | Decision and effect audit trail | 1 | `tools` | high |
| [E-02](E.md#e-02-audit-custody-and-audit-before-effect) | Audit custody and audit-before-effect | 1 | `external-effect` | high |
| [E-03](E.md#e-03-forensic-context-manifest) | Forensic context manifest | 2 | `untrusted-input` | medium |
| [E-04](E.md#e-04-baseline-security-signals-routed-to-an-owner) | Baseline security signals routed to an owner | 1 | `tools` | medium |
| [E-05](E.md#e-05-behavioral-detection-and-automatic-containment) | Behavioral detection and automatic containment | 2 | `external-effect` | medium |
| [E-06](E.md#e-06-stop-without-deploy) | Stop without deploy | 1 | `tools` | critical |
| [E-07](E.md#e-07-kill-switch-scopes-and-measured-revocation-latency) | Kill-switch scopes and measured revocation latency | 2 | `tools` | high |
| [E-08](E.md#e-08-quarantine-recovery-and-exercised-incident-response) | Quarantine, recovery and exercised incident response | 2 | `all` | medium |
| [E-09](E.md#e-09-governed-change-and-re-assessment) | Governed change and re-assessment | 1 | `all` | high |
| [E-10](E.md#e-10-tamper-evident-audit) | Tamper-evident audit | 3 | `external-effect` | medium |

## Critical-boundary set

Every Level 1 control whose failure severity is critical (32 controls). [conformance.md](../conformance.md) defines how the set gates readiness and conformance claims.

- R: none
- A: A-01, A-02, A-03, A-04, A-06, A-07, A-08, A-10, A-11, A-15, A-16, A-19, A-23, A-24, A-25
- I: I-01, I-02, I-05, I-06, I-08, I-09, I-10, I-11, I-12, I-13, I-14, I-15, I-17, I-19, I-23
- S: S-06
- E: E-06

## Routing by applicability tag

Controls whose applies_when names the tag. An entry such as `A-06 (+external-effect)` applies only when the listed tags also hold in the same agent context. Controls tagged `all` apply to every system in scope. Tags are defined in [profile-and-levels.md](../profile-and-levels.md).

| Tag | Level 1 | Level 2 | Level 3 |
| --- | --- | --- | --- |
| `all` | R-01, R-02, R-03, R-04, I-04, I-24, S-01, S-03, S-06, S-07, E-09 | E-08 | S-09 |
| `untrusted-input` | A-06 (+external-effect), A-07 (+external-effect), A-08 (+sensitive-data+external-effect), A-24 (+external-effect), I-01, I-13 (+rendered-output), S-04 (+external-effect) | I-03, I-16 (+code-execution), S-08, E-03 | - |
| `sensitive-data` | R-06, A-08 (+untrusted-input+external-effect), I-10 (+provider-routing or +mcp) | - | - |
| `external-effect` | R-05, A-05, A-06 (+untrusted-input or +separation-pattern), A-07 (+untrusted-input or +separation-pattern), A-08 (+untrusted-input+sensitive-data), A-10, A-24 (+untrusted-input or +separation-pattern or +shared-context or +triggered-runs), A-25 (+tools), I-08, S-04 (+untrusted-input or +separation-pattern), E-02 | E-05 | S-10, E-10 |
| `tools` | A-01, A-02, A-03, A-04, A-09, A-16, A-20, A-21, A-23, A-25 (+external-effect), I-05, I-14, S-02, S-05, E-01, E-04, E-06 | A-17, A-22, E-07 | A-18 |
| `retrieval` | I-06 | - | - |
| `memory` | I-07 | - | - |
| `delegation` | A-01, A-15, A-16, A-20, A-23 | I-22 | A-18 |
| `inter-agent` | A-15, I-18, I-21 | I-22 | - |
| `queued-work` | A-01, A-04, A-21 | I-22 | - |
| `triggered-runs` | A-19, A-24 (+external-effect) | - | - |
| `shared-context` | A-19, A-24 (+external-effect) | - | - |
| `multi-tenant` | I-27 (+code-execution) | - | - |
| `approvals` | A-11, A-12 | A-13 | A-14 |
| `code-execution` | I-05, I-15, I-27 (+multi-tenant) | I-16 (+untrusted-input) | - |
| `browser-agent` | A-12, I-05, I-17 | - | - |
| `coding-agent` | A-09, A-23, I-05, I-19, I-23 | - | - |
| `mcp` | A-01, A-02, A-09, A-16, I-05, I-10 (+sensitive-data), I-18, I-19, I-20 | - | A-18 |
| `provider-routing` | I-10 (+sensitive-data) | - | - |
| `provider-executed-tools` | I-11 | - | - |
| `client-conversation` | I-09 | - | - |
| `rendered-output` | I-13 (+untrusted-input or +separation-pattern), I-14 | I-26 | - |
| `network-egress` | I-12 | - | - |
| `model-artifacts` | I-25 | - | - |
| `separation-pattern` | A-06 (+external-effect), A-07 (+external-effect), A-24 (+external-effect), I-02, I-13 (+rendered-output), S-04 (+external-effect) | - | - |

## Routing by ASI category

Controls whose asi field names the category. The asi field shows which risks a control is designed to address, govern or verify; it is not a coverage claim. ASI identifiers and titles are from the OWASP Top 10 for Agentic Applications 2026 by the OWASP GenAI Security Project, used under CC BY-SA 4.0 (see [owasp-agentic-top-10.md](../owasp-agentic-top-10.md)).

Cross-cutting (every category): R-01, R-04, S-01, S-06. These governance and verification controls carry every ASI identifier and are not repeated in the rows below.

| ASI | Title | Level 1 | Level 2 | Level 3 |
| --- | --- | --- | --- | --- |
| ASI01 | Agent Goal Hijack | R-02, R-03, R-05, A-01, A-03, A-06, A-07, A-08, A-12, A-19, A-23, A-24, A-25, I-01, I-02, I-04, I-07, I-09, I-11, I-13, I-17, I-20, I-23, S-02, S-04, E-01, E-04, E-09 | I-03, S-08, E-03 | S-09 |
| ASI02 | Tool Misuse & Exploitation | R-02, R-03, R-05, R-06, A-01, A-02, A-04, A-05, A-06, A-07, A-08, A-09, A-10, A-20, A-24, I-02, I-10, I-11, I-12, I-13, I-14, I-17, I-18, S-02, S-03, S-04, E-01, E-04 | A-22, S-08, E-05 | S-09 |
| ASI03 | Identity & Privilege Abuse | R-02, R-03, R-06, A-01, A-02, A-03, A-04, A-09, A-11, A-15, A-16, A-19, A-21, A-23, A-24, A-25, I-04, I-05, I-06, I-07, I-09, I-15, I-17, I-21, I-23, I-27, S-02, S-05, E-01 | A-17, I-16, E-07 | A-14, A-18, S-09 |
| ASI04 | Agentic Supply Chain Vulnerabilities | I-10, I-11, I-18, I-19, I-23, I-24, I-25, S-07, E-04, E-06, E-09 | E-07, E-08 | S-10 |
| ASI05 | Unexpected Code Execution (RCE) | A-02, A-10, I-05, I-12, I-14, I-15, I-19, I-23, I-24, I-27, S-03 | I-16 | - |
| ASI06 | Memory & Context Poisoning | R-02, R-05, R-06, A-06, A-08, I-01, I-02, I-06, I-07, I-08, I-25, S-04, E-04 | I-03, I-22, S-08, E-03, E-08 | - |
| ASI07 | Insecure Inter-Agent Communication | A-01, A-15, A-16, I-01, I-12, I-18, I-21 | A-17, I-22 | - |
| ASI08 | Cascading Failures | R-02, A-01, A-04, A-05, A-15, A-20, A-21, I-01, I-08, I-20, S-05, S-07, E-01, E-02, E-04, E-06 | A-13, A-22, I-22, E-03, E-05, E-07, E-08 | S-10, E-10 |
| ASI09 | Human-Agent Trust Exploitation | R-05, A-06, A-11, A-12, A-19, A-25, I-08, I-09, I-14, I-17, I-20, S-02, S-04, E-01, E-04 | A-13, I-03, I-26, S-08, E-05 | A-14, S-09 |
| ASI10 | Rogue Agents | R-02, R-03, A-07, A-08, A-09, A-10, A-15, A-20, A-23, I-05, S-05, S-07, E-01, E-02, E-04, E-06, E-09 | A-17, E-03, E-05, E-07, E-08 | A-14, S-09, S-10, E-10 |

## Counts

| Pillar | Level 1 | Level 2 | Level 3 | Total | Critical boundary |
| --- | --- | --- | --- | --- | --- |
| R: Risk & Responsibility | 6 | 0 | 0 | 6 | 0 |
| A: Authority & Access | 20 | 3 | 2 | 25 | 15 |
| I: Isolation & Integrity | 23 | 4 | 0 | 27 | 15 |
| S: Security Verification | 7 | 1 | 2 | 10 | 1 |
| E: Evidence & Evolution | 5 | 4 | 1 | 10 | 1 |
| Total | 61 | 12 | 5 | 78 | 32 |

Default failure severity: critical 32, high 33, medium 13, low 0.
