<!-- Generated from catalog/controls.json in the source repository by scripts/render_catalog.py. Do not edit; propose changes upstream. -->
<!-- License: CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/). SPDX-License-Identifier: CC-BY-SA-4.0 -->

# N: Notice & Neutralize

**Can we see, stop, and improve behavior?**

Catalog version 0.1.0 (draft). This pillar has 10 controls: 5 at Level 1, 4 at Level 2, 1 at Level 3. Routing tables, the critical-boundary set and counts are in [index.md](index.md).

"Applies when" lists alternatives; `+` joins tags that must all hold in the same agent context ([profile-and-levels.md](../profile-and-levels.md)). Statuses, evidence scopes and severities are defined in [conformance.md](../conformance.md), and mapping relations in [mappings.md](../mappings.md).

## Level 1

### N-01 Decision and effect audit trail

- **Level:** 1
- **Applies when:** `tools`
- **Failure severity:** high
- **Minimum evidence scope:** integration
- **Critical boundary:** no
- **ASI:** ASI01, ASI02, ASI03, ASI08, ASI09, ASI10

**Statement:** The system MUST emit a structured event for each proposal, policy decision with reason code, approval, dispatch attempt, denial, confirmed effect and failure, carrying actor, principal, tenant, run, lineage ID, tool and version, policy version, target reference, taint state and correlation ID. Proposed, attempted, denied and confirmed effects MUST be distinguishable. Events MUST minimize sensitive content according to S-06, MUST NOT contain secrets, and MUST NOT depend on hidden model reasoning.

**Rationale:** This preserves the evidence discipline: proposed, attempted, denied and confirmed are different facts. Misuse through chains of trusted tools is invisible to host monitoring (ASI02 example scenario 6), so only application-level events show it.

**Verification:** Test: a forced denied proposal emits proposed and denied events with a reason code (N-01/C1); an allowed one emits proposed, attempted and confirmed events (C2); a canary secret is absent from all events (C3).

**Evidence:**

- Audit event schema
- Audit tests and canary scan

**Mappings:**

- AIUC-1: E015.2 (partial), D003.3 (partial), E015.1 (partial), A006.1 (supports), A008.5 (supports)
- NIST: MEASURE 2.8 (supports), MEASURE 2.4 (supports), MS-2.7-004 (supports), MS-4.2-004 (supports)
- AISVS: v1.0-C12.1.2 (supports), v1.0-C12.4.2 (partial), v1.0-C12.1.1 (partial), v1.0-C12.1.3 (supports)

### N-02 Audit custody and audit-before-effect

- **Level:** 1
- **Applies when:** `external-effect`
- **Failure severity:** high
- **Minimum evidence scope:** integration
- **Critical boundary:** no
- **ASI:** ASI08, ASI10

**Statement:** Audit events MUST be written to a store that no agent identity can modify or delete. An operation whose policy requires an audit record MUST NOT start unless that record, or a durable outbox entry for it, has been written.

**Rationale:** A rogue or hijacked agent must not be able to erase its trail, and consequential effects must not outrun their evidence. ASI08's security-operations example has agents purging logs and reporting clean metrics.

**Verification:** Hostile: the agent's credentials attempt to delete or overwrite audit records and are denied by store permissions (N-02/C1); with the audit sink down, the consequential effect is blocked and the outbox keeps the event (C2). Twin: with a healthy sink, the effect and its record both exist (C3).

**Evidence:**

- Audit store permission configuration
- Sink-failure test

**Mappings:**

- AIUC-1: E015.4 (partial), E015.3 (partial)
- NIST: MEASURE 2.8 (supports)
- AISVS: none

### N-04 Baseline security signals routed to an owner

- **Level:** 1
- **Applies when:** `tools`
- **Failure severity:** medium
- **Minimum evidence scope:** integration
- **Critical boundary:** no
- **ASI:** ASI01, ASI02, ASI04, ASI06, ASI08, ASI09, ASI10

**Statement:** The system MUST emit signals for: denials of consequential actions; provenance and task-scope denials from tainted contexts; budget and quota stops; descriptor or component drift; audit-write failures; kill-switch activations; and user reports of suspicious agent behavior. Each signal MUST be routed to a named owner (or 'unassigned', which S-01 treats as blocking) with a recorded response target. Detection MUST supplement, never replace, enforcement.

**Rationale:** Every ASI entry lists monitoring or anomaly detection among its mitigations. Persistent and within-authority attacks first show up as repeated denials and drift that enforcement blocks but nobody notices.

**Verification:** For each signal type, trigger its condition in a test and assert that it is emitted and delivered to the owner's controlled channel (N-04/C1).

**Evidence:**

- Signal catalog with owners and targets
- Signal emission tests

**Mappings:**

- AIUC-1: B006.2 (partial), D003.3 (partial), B002.2 (supports), C009.1 (supports), C008.3 (supports), E009.2 (supports)
- NIST: MEASURE 2.4 (partial), MANAGE 4.1 (partial), MEASURE 3.1 (supports), GOVERN 2.1 (supports), MG-4.1-002 (partial), MS-2.7-004 (supports), MG-4.1-007 (supports), MEASURE 3.3 (supports), MG-4.3-002 (supports)
- AISVS: v1.0-C12.4.3 (partial), v1.0-C12.2.1 (supports), v1.0-AC.6.1 (supports)

### N-06 Stop without deploy

- **Level:** 1
- **Applies when:** `tools`
- **Failure severity:** critical
- **Minimum evidence scope:** integration
- **Critical boundary:** yes
- **ASI:** ASI04, ASI08, ASI10

**Statement:** Authorized operators MUST be able to stop a run together with all its descendants, and to disable a specific tool, component, model version or agent, without a deploy. After a stop takes effect, new effects MUST NOT start, and queued work MUST be cancelled or revalidated before execution.

**Rationale:** A prompt asking the agent to stop is not enforcement. A rogue-agent stop and a supply-chain kill switch need the same mechanism.

**Verification:** Hostile: stop a run while one child is queued and another is running; no new effects occur after the stop (recorder), and the queued job revalidates and aborts (N-06/C1). Disabling a tool flag makes dispatch deny it (C2). Twin: other runs are unaffected (C3).

**Evidence:**

- Stop and disable tests
- Operator runbook reference

**Mappings:**

- AIUC-1: C009.1 (partial), E001.1 (supports)
- NIST: MANAGE 2.4 (partial), MG-2.4-002 (supports), MG-2.4-004 (supports)
- AISVS: v1.0-C9.6.1 (partial), v1.0-C9.6.3 (supports)

### N-09 Governed change and re-assessment

- **Level:** 1
- **Applies when:** `all`
- **Failure severity:** high
- **Minimum evidence scope:** inspection
- **Critical boundary:** no
- **ASI:** ASI01, ASI04, ASI10

**Statement:** Tool registrations, permission scopes, approval thresholds, destination allowlists, budgets, sandbox and egress policy, agent configuration and system prompts MUST be versioned configuration. Changes to them, and to models, providers, retrieval sources or agent-framework versions, MUST be triaged (NONE, SCOPED or FULL), MUST re-run the tests of the controls mapped to the changed locations, MUST update the record, and MUST have an accountable human approver before production use. A capability-profile change MUST trigger a full assessment.

**Rationale:** Agent behavior changes with configuration as much as with code, and ungoverned changes silently invalidate verified controls. AIUC-1 E004 is change approval, and ASI01 mitigation 3 (p. 10) recommends locking system prompts and routing changes to goals or reward definitions through configuration management and human approval.

**Verification:** Inspection: a sample of recent changes of the listed kinds each shows a triage tier, re-run test IDs, a record update and a named approver; a profile change has a full record. Hostile: a configuration change merged without these is caught by review rules or the record linter (N-09/C1).

**Evidence:**

- Change records with triage tier
- CI path-filter mapping
- Approver references

**Mappings:**

- AIUC-1: E004.1 (partial), C002.1 (partial), E008.1 (supports), E013.2 (supports)
- NIST: MANAGE 4.1 (partial), MEASURE 1.2 (supports), GOVERN 1.5 (supports), MANAGE 3.2 (supports), MG-3.1-003 (supports), MS-2.5-006 (supports)
- AISVS: v1.0-C3.2.3 (partial), v1.0-C12.5.3 (supports)

## Level 2

### N-03 Forensic context manifest

- **Level:** 2
- **Applies when:** `untrusted-input`
- **Failure severity:** medium
- **Minimum evidence scope:** integration
- **Critical boundary:** no
- **ASI:** ASI01, ASI06, ASI08, ASI10

**Statement:** For each consequential proposal, the system MUST record a manifest of references (identifier and content hash) to the prompt, policy and model versions and to the documents, tool results, memory entries, descriptors and messages in context, correlated across agents and runs (for example using the OpenTelemetry GenAI semantic conventions, which are in Development status). Manifests MUST NOT contain secrets. Content capture MAY be enabled as an opt-in with retention limits, and deletion requests and tenant offboarding MUST remove captured content while leaving references that resolve to a deletion marker.

**Rationale:** Investigating an injection requires knowing what the model saw, and minimization applied literally discards exactly that. Retention and deletion rules keep forensic capture consistent with data-subject deletion.

**Verification:** Drill: run an injection fixture that triggers a denied or confirmed effect, then identify the planted source using only the stored manifest (N-03/C1). Hostile: the manifest contains no canary secret (C2), and after a deletion request captured content is gone while references remain (C3).

**Evidence:**

- Manifest schema
- Forensic drill record
- Retention configuration

**Mappings:**

- AIUC-1: E015.2 (partial), E015.1 (supports)
- NIST: MEASURE 2.8 (supports), MEASURE 2.9 (supports), MANAGE 4.3 (supports), MP-2.1-001 (supports), MG-4.1-006 (supports)
- AISVS: v1.0-C12.1.4 (partial), v1.0-C12.1.3 (supports), v1.0-AC.5.1 (supports)

### N-05 Behavioral detection and automatic containment

- **Level:** 2
- **Applies when:** `external-effect`
- **Failure severity:** medium
- **Minimum evidence scope:** simulation
- **Critical boundary:** no
- **ASI:** ASI02, ASI08, ASI09, ASI10

**Statement:** The system MUST baseline each agent's tool sequences, destinations, volumes and fan-out, MUST alert when recorded thresholds are crossed, and MUST automatically throttle or suspend the agent at the narrowest scope for high-risk patterns: a sensitive read followed by an external send to a new destination, a novel tool combination, activity that continues after its triggering source was removed, and spawning bursts. False-positive rates MUST be recorded.

**Rationale:** Within-authority abuse, poisoning, cascades and rogue behavior are often visible only as behavior (ASI10 examples include exfiltration that continues after the poisoned source is removed).

**Verification:** Replay recorded hostile sessions (an exfiltration-like sequence and a spawning burst); each detector fires, routes to the owner and suspends the agent at the right scope within the target (N-05/C1). Replay clean sessions and record the false-positive rate (C2).

**Evidence:**

- Detector configuration with thresholds
- Replay results

**Mappings:**

- AIUC-1: B006.2 (partial), B004.1 (supports), E009.2 (supports), D003.5 (supports)
- NIST: MEASURE 2.4 (partial), MANAGE 2.4 (partial), MEASURE 1.2 (supports), MS-2.6-005 (partial), MG-2.4-004 (supports)
- AISVS: v1.0-C12.2.2 (partial), v1.0-C9.3.8 (partial), v1.0-C12.3.4 (supports), v1.0-C12.4.1 (supports)

### N-07 Kill-switch scopes and measured revocation latency

- **Level:** 2
- **Applies when:** `tools`
- **Failure severity:** high
- **Minimum evidence scope:** integration
- **Critical boundary:** no
- **ASI:** ASI03, ASI04, ASI08, ASI10

**Statement:** Stop controls MUST also work at tenant and global scope, revoking credentials and cancelling queued and descendant work. The record MUST state a revocation latency target derived from token lifetimes, authorization-cache TTLs and queue leases, and a test MUST measure the time from revocation to the last possible new effect at each scope.

**Rationale:** 'After revocation takes effect' needs a bound, and the bound is set by TTLs and leases that otherwise go unexamined.

**Verification:** Test: revoke at tenant and global scope during a long run with children, queued jobs and an in-flight external call; the measured time to the last new effect is within target and unaffected scopes continue (N-07/C1). Inspection: TTL and lease values match the derivation.

**Evidence:**

- Latency target and derivation in the record
- Latency test output per scope

**Mappings:**

- AIUC-1: E001.1 (supports)
- NIST: MANAGE 2.4 (partial), MEASURE 2.6 (supports), MG-2.4-004 (supports)
- AISVS: v1.0-C9.1.3 (partial), v1.0-C9.6.3 (supports), v1.0-AC.14.3 (partial)

### N-08 Quarantine, recovery and exercised incident response

- **Level:** 2
- **Applies when:** `all`
- **Failure severity:** medium
- **Minimum evidence scope:** integration
- **Critical boundary:** no
- **ASI:** ASI04, ASI06, ASI08, ASI10

**Statement:** The system MUST be able to quarantine a suspect agent, MCP server, memory scope or index (revoke credentials, block memory writes and peer messaging, hold pending work, preserve evidence), purge derived content by source lineage, and restore from a trusted baseline. Reintegration MUST require re-verification of pinned versions and configuration hashes and an accountable human's approval. Irreversible effects MUST be listed in the record with any compensating actions. A documented incident procedure covering containment, evidence preservation, cleanup and owner notification MUST be exercised at least once per release cycle.

**Rationale:** Poisoning persists after its source is removed, ASI10 calls for quarantine and verified reintegration, and recovery fails if it is first attempted during an incident.

**Verification:** Drill: poison memory or an index with a canary, quarantine it, purge by lineage and confirm the canary is gone from retrieval and the next session (N-08/C1). Hostile: use of the quarantined component is denied (C2), and reintegration with a changed hash or without approval is refused (C3). Twin: restore from the trusted baseline works (C4). Record the incident exercise with its date and outcomes.

**Evidence:**

- Recovery and incident runbook
- Drill and exercise records
- Irreversible-effects list

**Mappings:**

- AIUC-1: E001.1 (partial), B002.2 (supports)
- NIST: MANAGE 2.3 (partial), MANAGE 4.3 (partial), MANAGE 4.1 (supports), GOVERN 6.2 (supports), MG-2.3-001 (partial), GV-6.2-003 (partial), GV-1.5-002 (supports), MG-4.3-001 (supports), MG-2.4-003 (supports)
- AISVS: v1.0-C8.3.2 (partial), v1.0-C8.3.3 (supports), v1.0-C3.3.2 (supports), v1.0-C9.3.8 (supports), v1.0-AC.14.1 (partial), v1.0-AC.14.5 (supports)

## Level 3

### N-10 Tamper-evident audit

- **Level:** 3
- **Applies when:** `external-effect`
- **Failure severity:** medium
- **Minimum evidence scope:** isolated-runtime
- **Critical boundary:** no
- **ASI:** ASI08, ASI10

**Statement:** Audit storage MUST be tamper-evident through cryptographic chaining or a write-once store, and its integrity MUST be checked on a schedule and before forensic use.

**Rationale:** At the highest level, investigators must be able to prove that the record was not altered, including by an insider or a compromised component. ASI08 mitigation 10 calls for tamper-evident, time-stamped logs (p. 32).

**Verification:** Hostile: alter or delete one stored event out of band; the integrity check detects it (N-10/C1). Twin: an untouched log verifies (C2).

**Evidence:**

- Integrity check output
- Store configuration

**Mappings:**

- AIUC-1: E015.4 (partial)
- NIST: MEASURE 2.8 (supports), MS-2.7-009 (supports)
- AISVS: v1.0-AC.5.3 (partial), v1.0-C12.5.3 (supports), v1.0-AC.11.6 (partial)
