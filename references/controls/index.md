<!-- Generated from catalog/controls.json in the source repository by scripts/render_catalog.py. Do not edit; propose changes upstream. -->
<!-- License: CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/). SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Control catalog index

Catalog version 0.1.0 (draft). 78 controls in 5 pillars. Control IDs are stable: they are never reused or renumbered. Framework mappings are listed in [mappings.md](../mappings.md).

How to use the catalog:

1. Compute the capability profile and level, then select every control whose applies_when matches at or below that level, as defined in [profile-and-levels.md](../profile-and-levels.md).
2. Record each selected control's status and evidence by ID and apply the release gate defined in [conformance.md](../conformance.md).

## S: Scope & Stewardship

What could go wrong, and who owns it? Full entries: [S.md](S.md).

| ID | Title | Level | Applies when | Failure severity |
| --- | --- | --- | --- | --- |
| [S-01](S.md#s-01-accountable-scope-owner-and-risk-acceptance) | Accountable scope, owner and risk acceptance | 1 | `all` | high |
| [S-02](S.md#s-02-capability-profile-and-required-level) | Capability profile and required level | 1 | `all` | high |
| [S-03](S.md#s-03-least-agency) | Least Agency | 1 | `all` | medium |
| [S-04](S.md#s-04-threat-model-inventory-boundary-trace-and-asi-applicability) | Threat model: inventory, boundary trace and ASI applicability | 1 | `all` | high |
| [S-05](S.md#s-05-consequential-operations-register-and-trusted-sources) | Consequential operations register and trusted sources | 1 | `external-effect` | high |
| [S-06](S.md#s-06-data-classification-and-disclosure-policy) | Data classification and disclosure policy | 1 | `sensitive-data` | high |

## T: Trust & Isolation

What must stay separate and trustworthy? Full entries: [T.md](T.md).

| ID | Title | Level | Applies when | Failure severity |
| --- | --- | --- | --- | --- |
| [T-01](T.md#t-01-untrusted-content-stays-data-and-taints-its-context) | Untrusted content stays data and taints its context | 1 | `untrusted-input` | critical |
| [T-02](T.md#t-02-enforced-separation-patterns) | Enforced separation patterns | 1 | `separation-pattern` | critical |
| [T-03](T.md#t-03-hidden-text-normalization-and-reviewer-view) | Hidden-text normalization and reviewer view | 2 | `untrusted-input` | medium |
| [T-04](T.md#t-04-system-prompts-hold-no-secrets-or-enforcement) | System prompts hold no secrets or enforcement | 1 | `all` | high |
| [T-05](T.md#t-05-no-ambient-credentials-or-enforcement-access-in-model-influenced-processes) | No ambient credentials or enforcement access in model-influenced processes | 1 | `tools` or `code-execution` or `browser-agent` or `mcp` or `coding-agent` | critical |
| [T-06](T.md#t-06-retrieval-authorization-before-context) | Retrieval authorization before context | 1 | `retrieval` or `multi-tenant` | critical |
| [T-07](T.md#t-07-memory-provenance-scope-expiry-and-revocation) | Memory provenance, scope, expiry and revocation | 1 | `memory` | high |
| [T-08](T.md#t-08-system-of-record-for-consequential-facts) | System of record for consequential facts | 1 | `external-effect` | critical |
| [T-09](T.md#t-09-server-held-conversation-state) | Server-held conversation state | 1 | `client-conversation` | critical |
| [T-10](T.md#t-10-provider-data-routing) | Provider data routing | 1 | `sensitive-data+provider-routing` or `sensitive-data+mcp` | critical |
| [T-11](T.md#t-11-provider-executed-tools) | Provider-executed tools | 1 | `provider-executed-tools` | critical |
| [T-12](T.md#t-12-network-egress-boundary) | Network egress boundary | 1 | `network-egress` | critical |
| [T-13](T.md#t-13-rendered-output-exfiltration-channels) | Rendered-output exfiltration channels | 1 | `rendered-output+untrusted-input` or `rendered-output+separation-pattern` | critical |
| [T-14](T.md#t-14-sink-safe-output-handling-and-no-implicit-execution) | Sink-safe output handling and no implicit execution | 1 | `rendered-output` or `tools` | critical |
| [T-15](T.md#t-15-code-execution-sandbox-baseline) | Code-execution sandbox baseline | 1 | `code-execution` | critical |
| [T-16](T.md#t-16-strong-isolation-tier) | Strong isolation tier | 2 | `code-execution+untrusted-input` | high |
| [T-17](T.md#t-17-browser-and-computer-use-containment) | Browser and computer-use containment | 1 | `browser-agent` | critical |
| [T-18](T.md#t-18-pinned-descriptors-and-fully-qualified-tool-identity) | Pinned descriptors and fully qualified tool identity | 1 | `mcp` or `inter-agent` | high |
| [T-19](T.md#t-19-local-tool-and-third-party-component-confinement) | Local tool and third-party component confinement | 1 | `mcp` or `coding-agent` | critical |
| [T-20](T.md#t-20-mcp-sampling-and-elicitation) | MCP sampling and elicitation | 1 | `mcp` | high |
| [T-21](T.md#t-21-inter-agent-message-integrity) | Inter-agent message integrity | 1 | `inter-agent` | high |
| [T-22](T.md#t-22-fault-propagation-containment) | Fault propagation containment | 2 | `delegation` or `inter-agent` or `queued-work` | high |
| [T-23](T.md#t-23-coding-and-ci-agent-boundaries) | Coding and CI agent boundaries | 1 | `coding-agent` | critical |
| [T-24](T.md#t-24-component-pinning-and-intake) | Component pinning and intake | 1 | `all` | high |
| [T-25](T.md#t-25-model-artifact-integrity) | Model artifact integrity | 1 | `model-artifacts` | high |
| [T-26](T.md#t-26-agent-to-human-communication-integrity) | Agent-to-human communication integrity | 2 | `rendered-output` | medium |
| [T-27](T.md#t-27-per-tenant-kernel-isolation-for-code-execution) | Per-tenant kernel isolation for code execution | 1 | `code-execution+multi-tenant` | high |

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

## N: Notice & Neutralize

Can we see, stop, and improve behavior? Full entries: [N.md](N.md).

| ID | Title | Level | Applies when | Failure severity |
| --- | --- | --- | --- | --- |
| [N-01](N.md#n-01-decision-and-effect-audit-trail) | Decision and effect audit trail | 1 | `tools` | high |
| [N-02](N.md#n-02-audit-custody-and-audit-before-effect) | Audit custody and audit-before-effect | 1 | `external-effect` | high |
| [N-03](N.md#n-03-forensic-context-manifest) | Forensic context manifest | 2 | `untrusted-input` | medium |
| [N-04](N.md#n-04-baseline-security-signals-routed-to-an-owner) | Baseline security signals routed to an owner | 1 | `tools` | medium |
| [N-05](N.md#n-05-behavioral-detection-and-automatic-containment) | Behavioral detection and automatic containment | 2 | `external-effect` | medium |
| [N-06](N.md#n-06-stop-without-deploy) | Stop without deploy | 1 | `tools` | critical |
| [N-07](N.md#n-07-kill-switch-scopes-and-measured-revocation-latency) | Kill-switch scopes and measured revocation latency | 2 | `tools` | high |
| [N-08](N.md#n-08-quarantine-recovery-and-exercised-incident-response) | Quarantine, recovery and exercised incident response | 2 | `all` | medium |
| [N-09](N.md#n-09-governed-change-and-re-assessment) | Governed change and re-assessment | 1 | `all` | high |
| [N-10](N.md#n-10-tamper-evident-audit) | Tamper-evident audit | 3 | `external-effect` | medium |

## D: Demonstrated Defenses

Can we show that the controls work? Full entries: [D.md](D.md).

| ID | Title | Level | Applies when | Failure severity |
| --- | --- | --- | --- | --- |
| [D-01](D.md#d-01-enforcement-path-tests) | Enforcement-path tests | 1 | `all` | high |
| [D-02](D.md#d-02-hostile-proposals-with-authorized-twins) | Hostile proposals with authorized twins | 1 | `tools` | medium |
| [D-03](D.md#d-03-evidence-scope-runtime-boundaries-and-record-integrity) | Evidence scope, runtime boundaries and record integrity | 1 | `all` | high |
| [D-04](D.md#d-04-injection-channel-coverage-with-within-authority-payloads) | Injection channel coverage with within-authority payloads | 1 | `untrusted-input+external-effect` or `separation-pattern+external-effect` | high |
| [D-05](D.md#d-05-failure-revocation-and-concurrency-test-matrix) | Failure, revocation and concurrency test matrix | 1 | `tools` | high |
| [D-06](D.md#d-06-severity-rated-release-gate) | Severity-rated release gate | 1 | `all` | critical |
| [D-07](D.md#d-07-security-regressions-as-required-checks) | Security regressions as required checks | 1 | `all` | high |
| [D-08](D.md#d-08-live-model-adversarial-evaluation) | Live-model adversarial evaluation | 2 | `untrusted-input` | medium |
| [D-09](D.md#d-09-independent-adversarial-review-with-adaptive-attacks) | Independent adversarial review with adaptive attacks | 3 | `all` | high |
| [D-10](D.md#d-10-replay-before-rollout-and-before-authority-expansion) | Replay before rollout and before authority expansion | 3 | `external-effect` | medium |

## Critical-boundary set

Every Level 1 control whose failure severity is critical (32 controls). [conformance.md](../conformance.md) defines how the set gates readiness and conformance claims.

- S: none
- T: T-01, T-02, T-05, T-06, T-08, T-09, T-10, T-11, T-12, T-13, T-14, T-15, T-17, T-19, T-23
- A: A-01, A-02, A-03, A-04, A-06, A-07, A-08, A-10, A-11, A-15, A-16, A-19, A-23, A-24, A-25
- N: N-06
- D: D-06

## Routing by applicability tag

Controls whose applies_when names the tag. An entry such as `T-13 (+rendered-output)` applies only when the listed tags also hold in the same agent context. Controls tagged `all` apply to every system in scope. Tags are defined in [profile-and-levels.md](../profile-and-levels.md).

| Tag | Level 1 | Level 2 | Level 3 |
| --- | --- | --- | --- |
| `all` | S-01, S-02, S-03, S-04, T-04, T-24, N-09, D-01, D-03, D-06, D-07 | N-08 | D-09 |
| `untrusted-input` | T-01, T-13 (+rendered-output), A-06 (+external-effect), A-07 (+external-effect), A-08 (+sensitive-data+external-effect), A-24 (+external-effect), D-04 (+external-effect) | T-03, T-16 (+code-execution), N-03, D-08 | - |
| `sensitive-data` | S-06, T-10 (+provider-routing or +mcp), A-08 (+untrusted-input+external-effect) | - | - |
| `external-effect` | S-05, T-08, A-05, A-06 (+untrusted-input or +separation-pattern), A-07 (+untrusted-input or +separation-pattern), A-08 (+untrusted-input+sensitive-data), A-10, A-24 (+untrusted-input or +separation-pattern or +shared-context or +triggered-runs), A-25 (+tools), N-02, D-04 (+untrusted-input or +separation-pattern) | N-05 | N-10, D-10 |
| `tools` | T-05, T-14, A-01, A-02, A-03, A-04, A-09, A-16, A-20, A-21, A-23, A-25 (+external-effect), N-01, N-04, N-06, D-02, D-05 | A-17, A-22, N-07 | A-18 |
| `retrieval` | T-06 | - | - |
| `memory` | T-07 | - | - |
| `delegation` | A-01, A-15, A-16, A-20, A-23 | T-22 | A-18 |
| `inter-agent` | T-18, T-21, A-15 | T-22 | - |
| `queued-work` | A-01, A-04, A-21 | T-22 | - |
| `triggered-runs` | A-19, A-24 (+external-effect) | - | - |
| `shared-context` | A-19, A-24 (+external-effect) | - | - |
| `multi-tenant` | T-06, T-27 (+code-execution) | - | - |
| `approvals` | A-11, A-12 | A-13 | A-14 |
| `code-execution` | T-05, T-15, T-27 (+multi-tenant) | T-16 (+untrusted-input) | - |
| `browser-agent` | T-05, T-17, A-12 | - | - |
| `coding-agent` | T-05, T-19, T-23, A-09, A-23 | - | - |
| `mcp` | T-05, T-10 (+sensitive-data), T-18, T-19, T-20, A-01, A-02, A-09, A-16 | - | A-18 |
| `provider-routing` | T-10 (+sensitive-data) | - | - |
| `provider-executed-tools` | T-11 | - | - |
| `client-conversation` | T-09 | - | - |
| `rendered-output` | T-13 (+untrusted-input or +separation-pattern), T-14 | T-26 | - |
| `network-egress` | T-12 | - | - |
| `model-artifacts` | T-25 | - | - |
| `separation-pattern` | T-02, T-13 (+rendered-output), A-06 (+external-effect), A-07 (+external-effect), A-24 (+external-effect), D-04 (+external-effect) | - | - |

## Routing by ASI category

Controls whose asi field names the category. The asi field shows which risks a control is designed to address, govern or verify; it is not a coverage claim. ASI identifiers and titles are from the OWASP Top 10 for Agentic Applications 2026 by the OWASP GenAI Security Project, used under CC BY-SA 4.0 (see [owasp-agentic-top-10.md](../owasp-agentic-top-10.md)).

Cross-cutting (every category): S-01, S-04, N-04, D-01, D-06. These controls carry every ASI identifier and are not repeated in the rows below.

| ASI | Title | Level 1 | Level 2 | Level 3 |
| --- | --- | --- | --- | --- |
| ASI01 | Agent Goal Hijack | S-02, S-03, S-05, T-01, T-02, T-04, T-07, T-09, T-11, T-13, T-17, T-20, T-23, A-01, A-03, A-06, A-07, A-08, A-12, A-19, A-23, A-24, A-25, N-01, N-09, D-02, D-04 | T-03, T-26, N-03, D-08 | D-09 |
| ASI02 | Tool Misuse & Exploitation | S-02, S-03, S-05, S-06, T-02, T-10, T-11, T-12, T-13, T-14, T-17, T-18, A-01, A-02, A-04, A-05, A-06, A-07, A-08, A-09, A-10, A-20, A-24, N-01, D-02, D-03, D-04 | A-22, N-05, D-08 | D-09 |
| ASI03 | Identity & Privilege Abuse | S-02, S-03, S-06, T-04, T-05, T-06, T-07, T-09, T-15, T-17, T-21, T-23, T-27, A-01, A-02, A-03, A-04, A-09, A-11, A-15, A-16, A-19, A-21, A-23, A-24, A-25, N-01, D-02, D-05 | T-16, A-17, N-07 | A-14, A-18, D-09 |
| ASI04 | Agentic Supply Chain Vulnerabilities | T-10, T-11, T-18, T-19, T-23, T-24, T-25, N-06, N-09, D-07 | N-07, N-08 | D-10 |
| ASI05 | Unexpected Code Execution (RCE) | T-05, T-12, T-14, T-15, T-19, T-23, T-24, T-27, A-02, A-10, D-03 | T-16 | - |
| ASI06 | Memory & Context Poisoning | S-02, S-05, S-06, T-01, T-02, T-06, T-07, T-08, T-25, A-06, A-08, D-04 | T-03, T-22, N-03, N-05, N-08, D-08 | - |
| ASI07 | Insecure Inter-Agent Communication | T-01, T-12, T-18, T-21, A-01, A-15, A-16 | T-22, A-17 | - |
| ASI08 | Cascading Failures | S-02, T-01, T-08, T-20, A-01, A-04, A-05, A-15, A-20, A-21, N-01, N-02, N-06, D-05, D-07 | T-22, A-13, A-22, N-03, N-05, N-07, N-08 | N-10, D-10 |
| ASI09 | Human-Agent Trust Exploitation | S-05, T-08, T-09, T-14, T-17, T-20, A-06, A-11, A-12, A-19, A-25, N-01, D-02, D-04 | T-03, T-26, A-13, N-05, D-08 | A-14, D-09 |
| ASI10 | Rogue Agents | S-02, S-03, T-05, A-07, A-08, A-09, A-10, A-15, A-20, A-23, N-01, N-02, N-06, N-09, D-05, D-07 | A-17, N-03, N-05, N-07, N-08 | A-14, N-10, D-09, D-10 |

## Counts

| Pillar | Level 1 | Level 2 | Level 3 | Total | Critical boundary |
| --- | --- | --- | --- | --- | --- |
| S: Scope & Stewardship | 6 | 0 | 0 | 6 | 0 |
| T: Trust & Isolation | 23 | 4 | 0 | 27 | 15 |
| A: Authority & Access | 20 | 3 | 2 | 25 | 15 |
| N: Notice & Neutralize | 5 | 4 | 1 | 10 | 1 |
| D: Demonstrated Defenses | 7 | 1 | 2 | 10 | 1 |
| Total | 61 | 12 | 5 | 78 | 32 |

Default failure severity: critical 32, high 33, medium 13, low 0.
