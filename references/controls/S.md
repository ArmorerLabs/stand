<!-- Generated from catalog/controls.json in the source repository by scripts/render_catalog.py. Do not edit; propose changes upstream. -->
<!-- License: CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/). SPDX-License-Identifier: CC-BY-SA-4.0 -->

# S: Scope & Stewardship

**What could go wrong, and who owns it?**

Catalog version 0.1.0 (draft). This pillar has 6 controls: 6 at Level 1. Routing tables, the critical-boundary set and counts are in [index.md](index.md).

"Applies when" lists alternatives; `+` joins tags that must all hold in the same agent context ([profile-and-levels.md](../profile-and-levels.md)). Statuses, evidence scopes and severities are defined in [conformance.md](../conformance.md), and mapping relations in [mappings.md](../mappings.md).

## Level 1

### S-01 Accountable scope, owner and risk acceptance

- **Level:** 1
- **Applies when:** `all`
- **Failure severity:** high
- **Minimum evidence scope:** inspection
- **Critical boundary:** no
- **ASI:** ASI01, ASI02, ASI03, ASI04, ASI05, ASI06, ASI07, ASI08, ASI09, ASI10

**Statement:** The security record MUST state the claimed scope (agents, entry points, deployments and environments), intended use, forbidden outcomes, affected principals and one accountable human owner. Acceptance of a residual risk or an exception MUST be recorded by that owner, or by a delegate the owner named, with severity, scope, compensating controls and an expiry no more than 90 days after acceptance. A coding agent or model MUST NOT enter an owner, an acceptance or an exception that a human has not provided; it MUST write "unassigned" instead, and an unassigned owner blocks any readiness claim. A coding agent MAY draft a conformance or progress statement marked as pending owner review, but MUST NOT publish one or record one as published; only the owner, or a delegate the owner named, publishes it. A failure of this control MUST be rated critical when the record shows an acceptance or exception that no human gave (D-06).

**Rationale:** Conformance claims, exceptions and incident routing need a bounded scope and a real decision maker. Fabricated or implied acceptance is the most damaging false assurance a coding agent can produce, and unowned risk is never accepted risk.

**Verification:** Record lint: the scope fields are present; every exception names an owner, a severity, a compensating control and an expiry within 90 days; each acceptance links to an artifact authored by that human (message, ticket or signed commit). Hostile: an acceptance that appears only in an agent-authored commit with no linked human decision (S-01/C1), and an expired exception (C2), are both rejected and reported as open. Twin: a record with owner-authored, unexpired exceptions passes (C3). Hostile: a record in which a coding agent marked a conformance statement as published, with no human review or owner publication cited, is rejected and the statement reported as a draft (C4).

**Evidence:**

- Record section 'Scope and owner' with owner source reference
- Record table 'Residual risks and exceptions'

**Mappings:**

- AIUC-1: E004.1 (partial), C002.1 (partial), E008.1 (supports)
- NIST: GOVERN 2.1 (partial), MAP 1.1 (supports), MAP 3.3 (partial), MANAGE 1.3 (partial), MANAGE 1.4 (supports), GOVERN 3.2 (supports), MG-1.3-001 (supports), MP-1.1-002 (supports)
- AISVS: none

### S-02 Capability profile and required level

- **Level:** 1
- **Applies when:** `all`
- **Failure severity:** high
- **Minimum evidence scope:** inspection
- **Critical boundary:** no
- **ASI:** ASI01, ASI02, ASI03, ASI06, ASI08, ASI10

**Statement:** The record MUST list each agent context in scope with: untrusted-input, sensitive-data and external-effect, each marked present or absent with a reason; autonomy scope 1 to 4; feature tags from the closed vocabulary; and the Level computed by the selection rule. A property whose presence is unknown MUST be recorded as present. The principal's own conversation and task content MUST be recorded as sensitive-data unless the record shows that each of the following holds: the principal is anonymous; the conversation is not retained and no memory is written from it; no tool or retrieval the context can invoke reads non-public data; and the context receives no data of other principals. A context that consumes output of an untrusted-input context MUST be recorded as untrusted-input unless that output crossed a separation boundary verified under T-02. A context that receives in its input data an attacker should not obtain (for example a summary of order data written by another context, memory or a delegated message) MUST be recorded as sensitive-data, even when none of its own tools can read that data. A property MAY be recorded as absent because of separation only when T-02 is implemented-and-verified for that context. The profile MUST be recomputed in the same change that adds a tool, data source, trigger, renderer, delegate or autonomy, and SHOULD be checked by an automated test that derives the properties from the running tool registry and configuration. A failure of this control MUST be rated critical when the understated profile hides a context that holds all three properties (D-06).

**Rationale:** Applicability and depth must be deterministic, not delegated to an undefined product risk policy. Per-context propagation of untrusted-input and sensitive-data stops a design from hiding the lethal trifecta behind a summarizer, or splitting it so that one context reads the data and another sends it, and separation credit only for verified separation rewards injection-resistant architecture without allowing it to be claimed on paper. A free-text reason that a conversation holds nothing worth taking is the easiest way to understate a profile, so that exemption is a closed list of facts a reviewer can check.

**Verification:** Inspection: for each context, derive the three properties from code (input sources, data scopes, tool effects, renderers) and recompute the level; any mismatch fails. Hostile: register an effectful tool, or enable auto-loading of markdown images, in a context recorded without external-effect (S-02/C1); record a planner that reads a summarizer's output as trusted (C2); record a summarizer that holds untrusted-input and sensitive-data feeding a sender that holds only external-effect tools as n=2 without sensitive-data (C3). The reviewer or the automated consistency test rejects all three. Twin: a context fed only principal input and trusted configuration is correctly recorded without untrusted-input (C4). Hostile: a profile recomputed from the running tool registry and configuration differs from the recorded profile because a tool was added after the record; readiness is blocked until the record is updated (C5). A record marks the principal's conversation as not sensitive-data while the context writes memory from it; the reviewer or the consistency test rejects it (C6).

**Evidence:**

- Record table 'Capability profile': context, properties with reasons, separation claimed and T-02 status, autonomy scope, tags, computed and declared level
- Optional profile-consistency test output

**Mappings:**

- AIUC-1: C001.1 (supports), E017.1 (supports)
- NIST: GOVERN 1.3 (partial), MAP 3.3 (supports), MAP 3.5 (supports), GV-1.3-001 (supports), MP-1.1-001 (supports), MP-4.1-008 (supports)
- AISVS: none

### S-03 Least Agency

- **Level:** 1
- **Applies when:** `all`
- **Failure severity:** medium
- **Minimum evidence scope:** integration
- **Critical boundary:** no
- **ASI:** ASI01, ASI02, ASI03, ASI10

**Statement:** Each tool, autonomous step, trigger and delegate MUST have a recorded task need tied to the intended use, and a capability without one MUST NOT be enabled. Where a deterministic workflow or a lower autonomy scope meets the need, the design MUST use it, and for each tool, trigger or delegate that runs at autonomy scope 3 or 4 the record MUST state why a deterministic workflow or a lower scope does not meet the need. A failure of this control MUST be rated at least high when the unneeded capability is an external effect (D-06).

**Rationale:** The Least Agency principle of the OWASP Top 10 for Agentic Applications 2026 (p. 7): autonomy that adds no value expands the attack surface. Removing a capability is the cheapest control available, and it can remove a Rule of Two property entirely.

**Verification:** Inspection: compare the registered tools, triggers and delegates of each context with their recorded needs; any capability without a need fails, and so does a scope 3 or 4 tool, trigger or delegate with no recorded reason against a deterministic workflow or lower scope. Hostile: inject into an order-lookup context an instruction to issue a refund and script that proposal; dispatch reports an unknown tool for the context and no adapter runs (S-03/C1). Twin: the needed lookup succeeds, and the authorized task suite still passes with every unjustified tool removed (C2).

**Evidence:**

- Record column 'task need' per tool, trigger and delegate
- Per-context tool registry export

**Mappings:**

- AIUC-1: B006.1 (partial; Automation only), A003.1 (supports), D003.5 (supports; Automation only), A003.3 (supports)
- NIST: MANAGE 2.1 (partial), MAP 3.3 (supports), MP-1.1-001 (supports)
- AISVS: none

### S-04 Threat model: inventory, boundary trace and ASI applicability

- **Level:** 1
- **Applies when:** `all`
- **Failure severity:** high
- **Minimum evidence scope:** inspection
- **Critical boundary:** no
- **ASI:** ASI01, ASI02, ASI03, ASI04, ASI05, ASI06, ASI07, ASI08, ASI09, ASI10

**Statement:** The record MUST inventory: models with exact versions; inference, embedding, evaluation, telemetry and tracing recipients with accounts; tools, including provider-executed tools; MCP servers and remote agents with descriptor hashes; skills, prompts and policies with versions; and egress destination classes. It MUST trace every entry point (interactive, job, callback, webhook, schedule, MCP server, CLI) through these components and mark each boundary where data becomes instruction, identity, permission, executable input, destination or persistent state. It MUST list every principal a run touches (initiating user, trigger sender, data owner, output viewers). Each ASI category MUST either map to control IDs and at least one abuse case that stays within granted authority, or carry a not-applicable reason that names a verifiable architectural absence. The inventory MUST be updated in the same change that adds or alters an entry.

**Rationale:** Controls can only be placed on boundaries that have been found, and components that are not inventoried cannot be pinned, revoked or re-assessed. ASI01, ASI02, ASI06, ASI08, ASI09 and ASI10 often do harm within granted authority, so an assessment that only asks whether authority can be exceeded misses them. Reliance on a library or vendor is not an architectural absence. The default severity is high because an untraced entry point can reach an effect with no control on its path.

**Verification:** Inspection: enumerate entry points and outbound clients from code and configuration (routes, job handlers, webhooks, schedulers, MCP client configuration, provider tool flags, HTTP clients) and confirm each appears in the record; confirm each not-applicable ASI row names an absent capability. Hostile: add a queue consumer that reaches an adapter, or an MCP server entry, without updating the record; the review or the CI inventory diff fails (S-04/C1). Twin: the same queue consumer added together with its inventory and trace update passes the inventory diff (C2).

**Evidence:**

- Record sections 'Inventory', 'Trace' and 'Principals'
- Record table 'ASI applicability' keyed to control IDs

**Mappings:**

- AIUC-1: E017.1 (partial), C001.1 (supports), E011.1 (supports), B006.1 (supports; Automation only), C002.2 (supports)
- NIST: MAP 4.1 (partial), MAP 4.2 (partial), GOVERN 1.6 (supports), MAP 5.1 (supports), GV-3.2-005 (partial), GV-1.6-003 (partial), GV-6.1-007 (supports), GV-4.2-003 (supports), MP-2.2-001 (supports), MP-5.1-006 (supports), MS-2.7-001 (supports)
- AISVS: v1.0-C3.1.1 (partial), v1.0-AC.2.1 (supports)

### S-05 Consequential operations register and trusted sources

- **Level:** 1
- **Applies when:** `external-effect`
- **Failure severity:** high
- **Minimum evidence scope:** integration
- **Critical boundary:** no
- **ASI:** ASI01, ASI02, ASI06, ASI09

**Statement:** Every operation that changes state, moves value, communicates externally or sends data to a model-chosen destination MUST be registered in versioned trusted configuration. Each entry records: the consequence class (sensitive read, reversible write, irreversible or financial effect, external communication); allowed resources and destinations; each consequential argument (recipient, URL, host, path, query target, payee, account, amount, repository or branch, command) with its trusted source; value and rate limits; for every operation that moves funds or grants access, an impact threshold with its rationale (at Level 3, the A-14 threshold), which A-12 uses; reversibility; approval policy; and the system of record for each fact the operation relies on. A trusted source is a principal-entered value from the current task, the system of record, an allowlist bound to the resource, a value that application code computes deterministically from trusted sources only (for example a percentage the principal entered, applied to the system-of-record order total and capped by the refundable balance), for a response to the sender of a triggering event, that sender's authenticated origin as A-19 establishes it; or, for a read-tool query argument, the output of a query composer as A-06 defines it. A system-of-record value is the trusted source for an argument only for the field that the principal's task (A-07) names for that argument, or, where the task names no field for it, for a field that the register fixes as the argument's only permitted value, so that the model does not choose it. Where the register allows several fields or a range for the argument, only the field the task names matches. The verified contact address on record of a case's requester is a trusted source only for a reply to that requester on that case, filled by the effect adapter from the system of record. A system-of-record source for an object identifier (an order, account, ticket, document or customer) MUST be scoped to the principal or case on whose behalf the run acts, for example the orders of the case requester; that a record with the identifier exists is not enough. A principal-entered value is one the principal typed or selected in a structured field of a trusted interface (for example a recipient field, contact picker or payee selector), or in a channel the application can show carries no pasted, uploaded or forwarded content. Values extracted from content the principal pasted, uploaded or forwarded are not trusted sources, and a value taken from free-text chat that can carry such content is untrusted-derived. Message, comment, document and payload bodies of external communication are checked as outbound content under A-24. Tool registration MUST fail for an effectful tool whose consequential arguments lack a declared trusted source. The dispatcher MUST read its policy for these operations from the register, and the model MUST NOT set or lower an operation's class. When a required fact is unknown, the implementation MUST choose a fail-safe default (deny, confine or require confirmation) and record the assumption. It SHOULD NOT add approval prompts for operations already within the caller's authority unless A-06, A-07, A-08 or A-10 require them.

**Rationale:** Provenance-aware destination policy (A-06), destructive-operation guards (A-10) and system-of-record reads (T-08) all need an explicit per-operation definition. Without one, approval defaults to everything (approval fatigue) or to nothing, and undeclared arguments such as bcc or callback_url escape destination policy. A user who pastes an attacker's email would otherwise give an attacker-chosen recipient the appearance of user input. Likewise, an attacker who writes another customer's order number into a ticket names a record that exists, so a match against the whole system of record would pass a value the attacker chose, and a value that equals a field the principal never asked for (the full refundable balance) carries the attacker's choice of field. A value computed from trusted inputs carries no attacker choice, so it needs no confirmation, while the same computation over an input taken from a document does.

**Verification:** Registration test: load the registry and fail if any consequential argument of an effectful tool lacks a source annotation; adding an unannotated bcc or callback_url argument to a send tool must fail registration (S-05/C1). Hostile: a proposal that claims a lower class for an irreversible operation is evaluated under the registered class (C2). An object identifier that exists in the system of record but belongs to another requester or tenant does not match its trusted source (C3). Change a limit in the register and observe the dispatcher enforce the new value (C4). Twin: a fully annotated tool registers, and a low-consequence operation within the caller's authority proceeds without an extra prompt (C5). Twin: the principal enters 50 percent in a structured refund field; the amount the application computes from the system-of-record order total, capped by the refundable balance, matches its trusted source and refunds once without an extra prompt (C6). Hostile: a document in context asks for a 100 percent refund and the model supplies 100 as the percentage; the computed amount has an untrusted-derived input, so it is not a trusted source, and the refund is denied or confirmed with the document shown as its origin (C7). Twin: a search tool whose query argument declares the query composer as its trusted source registers (C8). Registration test: an operation that moves funds or grants access with no recorded impact threshold fails registration (C9).

**Evidence:**

- Machine-readable register referenced by dispatcher policy
- Registration test output
- Record 'Assumptions' section

**Mappings:**

- AIUC-1: D003.1 (partial; Automation only), D003.2 (partial; Automation only), D003.4 (partial; Automation only), C007.1 (supports)
- NIST: MAP 3.5 (supports), MAP 5.1 (supports), MEASURE 2.6 (supports), MP-2.2-001 (supports), MAP 4.2 (supports)
- AISVS: v1.0-C9.2.3 (partial), v1.0-C9.2.4 (partial), v1.0-C9.3.3 (supports)

### S-06 Data classification and disclosure policy

- **Level:** 1
- **Applies when:** `sensitive-data`
- **Failure severity:** high
- **Minimum evidence scope:** integration
- **Critical boundary:** no
- **ASI:** ASI02, ASI03, ASI06

**Statement:** Each data class that can enter a model context MUST have a policy in trusted configuration naming the providers, destinations, memory stores, logs, telemetry sinks and output audiences that may receive it, with its retention and deletion obligations. Provider routing (T-10), egress and rendering (T-12, T-13), outbound payload checks at effect adapters (A-24), shared-context disclosure (A-19), memory (T-07) and audit minimization (N-01) MUST read this policy rather than separate lists. Data of unknown class MUST be treated as the most restrictive class present in the context. Each class whose disclosure of a single value is the harm (a credential, a one-time code, an account or health identifier, a confidential fact) is a secret class: the policy MUST record its entropy in bits (how many bits an attacker must learn to obtain one value of it) and its retention period, and the record lists the secret classes each context can hold, so that residual channels such as the read-tool selection channel of A-06 are compared against them.

**Rationale:** Provider routing, exfiltration-channel control, shared-context disclosure and log minimization all need the same answer to what may go where. One policy prevents divergent hardcoded lists, and its deletion obligations keep memory, indexes and forensic records consistent with deletion requests and tenant offboarding.

**Verification:** Inspection: each listed enforcement point references the policy, not its own list, and each secret class records its entropy in bits and its retention period. Hostile: add a provider or destination that the policy does not list in a test fixture; every enforcement point denies it by default (S-06/C1). Twin: a listed destination receives its permitted class (C2).

**Evidence:**

- Data policy configuration
- Record list of data classes with policy reference

**Mappings:**

- AIUC-1: A001.1 (partial), A001.2 (supports), A003.1 (supports), E011.1 (supports), A006.1 (supports), E005.1 (supports)
- NIST: MEASURE 2.10 (supports), GOVERN 1.1 (supports), GOVERN 6.1 (supports), GV-6.1-001 (supports), GV-6.1-007 (supports), MP-4.1-005 (supports)
- AISVS: v1.0-C5.2.7 (supports)
