# Conformance, evidence and the release gate

This file defines the normative language, the evidence-scope and status enums, the severity rubric and release gate, the critical-boundary set, the confidentiality and integrity of the security record, and what a conformance or progress statement may claim. [profile-and-levels.md](profile-and-levels.md) defines the capability profile, applicability, levels and change triage that this file relies on. Control IDs refer to catalog entries listed in [controls/index.md](controls/index.md).

## Normative language

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in the normative sources are to be interpreted as described in BCP 14 (RFC 2119 and RFC 8174) when, and only when, they appear in all capitals, as shown here. Definitions, enum meanings, the conditions of the conformance statement and the release gate table are normative as written; a lowercase "may" describes a permitted option.

- A SHOULD clause is satisfied either by implementation or by a recorded deviation that states the reason and the compensating measure. A recorded deviation does not make the control failing. Status follows the control's MUST clauses and required cases: a control whose MUST clauses are implemented and whose required cases passed is implemented-and-verified even while one of its SHOULD clauses carries a recorded deviation. Each deviation is listed in the record's deviations section with the clause, reason, compensating measure, owner and test or review reference. A deviation counts only when the accountable owner (S-01), or a delegate the owner named, has recorded it. A deviation whose owner is unassigned leaves the SHOULD clause unsatisfied: it is an open item rated with the severity rubric, and no conformance statement can be published while it remains.
- MAY clauses describe permitted options and impose no obligation.
- Rationale text is informative.
- Each control's verification text is normative as to its intent: the hostile cases and the authorized twin it names are required cases, run at or above the control's minimum evidence scope. Tooling and harness details are informative.
- A required case whose subject is architecturally absent from every context in scope (for example a stdio launch command when the system uses only remote MCP servers, or a proxy consent flow when the application operates no proxy) is recorded as `<ID>/C<n>: not applicable (<verifiable absence>)`. It does not count against implemented-and-verified when every remaining required case ran and passed. Role-conditional cases are labelled in the verification text (for example "Server role:" or "stdio servers"). The absence MUST be verifiable in code or configuration, as for not-applicable-with-reason.
- Equivalent alternative evidence is acceptable when it exercises the same boundary at the same or a stronger evidence scope and the record names the substitution (D-03).

### Normative sources

- The control catalog: each control's statement, `applies_when`, level, default failure severity, minimum evidence scope and required verification cases. Its source is `catalog/controls.json` in the source repository; the installed skill carries the rendered views under [controls/](controls/index.md).
- This file and [profile-and-levels.md](profile-and-levels.md).
- The routing table in Step 2 of [SKILL.md](../SKILL.md), which the SCOPED rules in profile-and-levels.md adopt by reference, as to which control IDs each trigger location routes to. The rest of SKILL.md is not normative.

Other files, including the rest of SKILL.md, the guidance under references/ and the record template, explain, route or apply these sources. Where any of them differs from a normative source, the normative source governs and the difference is a defect to report.

## Evidence scope

Every record entry states an evidence scope from this closed enum. The order runs from weakest to strongest, and "at or above" uses this order.

| Scope | Definition |
|---|---|
| inspection | Review of code, configuration, records or documents without executing the control. |
| unit | An isolated function or module executed with test doubles. |
| simulation | An end-to-end run in which the boundary under test is itself simulated or mocked, including scripted model turns against mocks, replayed sessions and tabletop exercises. |
| integration | The real entry point, policy and dispatcher driving a controlled adapter or destination. |
| isolated-runtime | The configured boundary itself (real sandbox, proxy or network policy, real browser or client renderer, real identity or authorization server, provider test account) in a non-production environment. |
| deployed | The production or production-equivalent deployment. |

Rules:

- A mock proves only the boundary it exercises. Simulated outputs cannot establish sandbox, egress, rendering or provider properties.
- Each control names a minimum evidence scope. Evidence below it cannot make the control implemented-and-verified.
- The controls whose minimum is isolated-runtime remain implemented-but-unverified on any weaker evidence (D-03): T-05, T-11, T-12, T-13, T-15, T-16, T-17, T-19, T-23, T-26, T-27, A-12, A-14, A-17, A-18, A-23, N-10, D-08, D-10.
- An entry that cites evidence states the scope of that evidence. An entry that cites none (planned, not-assessed, or implemented-but-unverified with nothing run) states the control's minimum evidence scope as its target and cites no test; the status shows that the evidence is missing.
- Label simulated, sandboxed and deployed evidence accurately. An unrun test is never recorded as passed.

## Status

Every record entry has exactly one status from this closed enum.

| Status | Meaning |
|---|---|
| implemented-and-verified | The control is implemented, and its required hostile cases and authorized twin ran and passed at the recorded commit, through the real execution path (D-01, D-02), at or above its minimum evidence scope (D-03). |
| implemented-but-unverified | The control is implemented, but its required verification is missing, did not run at the recorded commit, or ran below the minimum evidence scope. |
| planned | The control is not implemented at the recorded commit; the record names the intended implementation and its location. A planned control is not an implemented control. |
| not-applicable-with-reason | The control's `applies_when` matches no agent context in scope, or it matches but the subject of every required case is architecturally absent from every context in scope (see "Normative language"). The reason names the architecturally absent capability so that a reviewer can verify it in code or configuration. Reliance on a library, vendor or provider is not a reason. |
| failing | A required hostile case or authorized twin fails at the recorded commit, or examination shows that the boundary the control protects is bypassable. A demonstrated bypass is recorded as failing even when a plan exists. |
| not-assessed | The control was not examined for this record: outside a SCOPED change, before a baseline exists, or not yet reached in a brownfield adoption. |

- Lifecycle states of catalog entries (active, deprecated, withdrawn) are never record statuses.
- Claim audit. Before an entry is recorded implemented-and-verified, the record lists every required case of the control by label (`<ID>/C<n>`, the authorized twin included; a case shown as `(C<n>: retired)` is not required), each with its result at the recorded commit and the evidence scope it ran at; a case recorded not applicable states its verifiable absence. A case that did not run, or ran below the control's minimum evidence scope, keeps the status implemented-but-unverified, and a case that failed makes it failing. A count of passing tests without case labels does not satisfy the audit.
- Use one exclusion phrase: a verifiable architectural absence.
- Every status other than implemented-and-verified and not-applicable-with-reason is open and is rated with the severity rubric below.

## Severity rubric

Apply the rubric to every applicable control that is failing, implemented-but-unverified, planned or not-assessed, and to every open finding and failed adversarial case. Record the severity, the matrix cell used and a rationale in the record's "Severity and rationale" column (D-06).

### Step 1, harm class

**H-breach**, any of the following:

- disclosure of protected data to an unauthorized principal, tenant, provider or channel (rendering, URL arguments, DNS, logs and telemetry included);
- privilege, identity or tenant escalation;
- an unapproved consequential or irreversible effect, including one within the caller's authority whose destination, payee, amount, target or operation was chosen by untrusted content;
- execution outside the intended boundary (host execution, sandbox or browser-profile escape, ambient-credential use);
- acceptance of a forged or replayed approval;
- an agent able to write its own security policy;
- loss of the ability to stop or revoke the agent and its descendants;
- a readiness claim contradicted by evidence.

**H-degrade**, any of the following:

- a missing audit or detection record for a consequential effect;
- unbounded cost or resource use;
- poisoned facts or memory that reach a consequential decision without an effect;
- an unenforced inventory or pinning control;
- revocation slower than its stated target.

**H-depth**: a defense-in-depth or hygiene gap while the enforcing control holds.

### Step 2, reachability

- **Reachable**: an attacker can trigger it through normal product use, including by placing content the agent will read (a document, email, web page, tool result, descriptor or peer message), or as any principal acting within normal permissions.
- **Constrained**: it needs a privileged insider, a non-default configuration, or a second independent control failure.
- Unknown reachability is rated reachable.

### Step 3, severity

| Harm class | Reachable | Constrained |
|---|---|---|
| H-breach | Critical | High |
| H-degrade | High | Medium |
| H-depth | Medium | Low |

### Default severities

- Each control has a default failure severity, carried in the catalog field `failure_severity`, which is normative. A control statement can also set a floor for a stated failure ("A failure of this control MUST be rated critical when ..."), which is normative too. Rationale text may explain either but is informative and never lowers a severity.
- The recorded severity is the highest of the default, any floor the statement sets for the failure found, and the rubric cell (D-06). The rubric can raise a severity above the default; it never lowers one.
- For a control that is implemented-but-unverified, planned or not-assessed, no failure has been found, so a floor applies when the profile or register shows the floor's precondition: T-07 in a multi-tenant context with memory, A-05 where a registered operation moves funds, A-09 where an auto-run tool can reach the network, A-12 where a context that holds all three properties relies on A-08 option (a), T-26 where the application collects credentials, MFA codes or payment details, and A-22 where the record shows no provider spend cap, or no per-principal and per-tenant limit, so that cost is unbounded. A floor whose condition is the failure itself (S-01, S-02, S-03, T-04) applies when that failure is found (D-06). Every control whose statement sets a floor is in one of these two lists; the validator checks this against the catalog.
- A rater may raise a severity freely.
- A precondition that only constrains the attack (Constrained in Step 2) does not lower the default or a floor. Lowering below them requires a recorded precondition that makes the attack unreachable in this system; the record states the precondition, how it was verified and the resulting severity.
- Severity MUST NOT be lowered on the basis of current model behavior ("the model refuses today"), detector or classifier coverage, prompt instructions, or unverified provider claims.

Examples:

- N-01 (default high) is failing because effects through a legacy batch path that only an administrator can enable write no audit record. The rubric gives H-degrade and Constrained, which is Medium. The recorded severity is High, the default, because the precondition constrains the attack but does not make it unreachable.
- N-04 (default medium) is failing because no signal reaches an owner when the dispatcher denies a burst of proposals, in a system where any user can trigger such a burst. The rubric gives H-degrade and Reachable, which is High, so the recorded severity is High.
- A-05 (default high) is failing in a payments adapter. The statement's floor applies because the effect moves funds, so the recorded severity is Critical whatever the rubric cell.

## Critical-boundary set

The critical-boundary set is every Level 1 control whose default failure severity is critical and that is not withdrawn. It is derived from the catalog, not chosen, and changes only when a control's level, default severity or lifecycle changes. [SKILL.md](../SKILL.md) lists the same set as its always-on invariants.

<!-- critical-boundary:start -->
T-01, T-02, T-05, T-06, T-08, T-09, T-10, T-11, T-12, T-13, T-14, T-15, T-17, T-19, T-23, A-01, A-02, A-03, A-04, A-06, A-07, A-08, A-10, A-11, A-15, A-16, A-19, A-23, A-24, A-25, N-06, D-06
<!-- critical-boundary:end -->

- The set holds the enforcement boundaries plus the release gate itself (D-06), because a readiness claim contradicted by evidence is an H-breach harm.
- An applicable control from this set whose status is implemented-but-unverified, planned or not-assessed counts as an open critical.
- An applicable control from this set that is failing is rated with the rubric, and it blocks every readiness and conformance claim whatever its rating (D-06).
- Do not describe a release as ready while an applicable critical boundary is bypassable or its required verification is missing.
- For partial adoption, the set is implemented and verified first (see "Progress statement" below).

## Release gate

The gate (D-06) turns open items into a readiness value. It applies before any readiness claim and before any conformance statement.

| Severity | Effect |
|---|---|
| Critical | Blocks every readiness and conformance claim; no exception converts it into a pass. The readiness value is blocked, or confined-prototype when the system runs only with synthetic data and no production credentials. |
| High | Release requires an exception under S-01 from the accountable owner, naming a compensating control, with an expiry no more than 90 days after acceptance. Highs never count toward conformance. |
| Medium | Tracked with an owner and a target date. Does not block. |
| Low | Tracked. |

Readiness values (closed enum):

| Value | Meaning |
|---|---|
| ready-within-scope | The accountable owner is recorded (S-01); every applicable critical-boundary control is implemented-and-verified; S-02, S-05 where it applies, and A-12 for every confirmation surface that an applicable critical-boundary control relies on are implemented-and-verified; no critical is open; every open high carries an owner exception that has not expired at the time of the claim; every open item has a severity and rationale. Ready applies only to the stated scope and is not a conformance claim. |
| confined-prototype | The system runs only with synthetic data and no production credentials. Open criticals are listed by ID. |
| blocked | Any other state. The record lists the open IDs that block. |

A readiness claim means the value ready-within-scope. confined-prototype and blocked are recorded states, not claims.

A SCOPED change rates only its routed controls and any new finding. With a baseline record, readiness is computed as the baseline value with the routed rows updated (the record itself is append-only: the baseline Controls table stays unchanged and the compact change record carries the routed rows), and it is blocked if a routed control is failing or a routed critical-boundary control is not implemented-and-verified. The baseline value is rechecked at the time of the change: it is blocked when the accountable owner is unassigned or an owner exception it relies on has expired, and the compact Readiness line names the earliest exception expiry it relies on. The baseline is read as a claim, at the commit the change starts from, never from a version the change edits (see "Record and catalog integrity" below). With "Baseline: missing", readiness is blocked (baseline missing: critical-boundary set not assessed), and the individual not-assessed controls are not rated.

- A human may still choose to deploy a blocked system. The record then states "blocked" with the open IDs, and the coding agent does not describe the release as ready.
- The coding agent may draft an exception, but it MUST NOT record acceptance, enter an owner who has not been provided, or suppress or weaken a failing check. Where the owner is unknown it writes "unassigned", and an unassigned owner blocks ready-within-scope (S-01).
- The coding agent may draft a conformance or progress statement, marked as pending owner review, but it MUST NOT publish one or record one as published.
- OWASP AIVSS scores (v0.8, pre-1.0) may be recorded alongside as related scoring. They never change the gate.

## The security record

The record ([agent-security-record.md](../assets/agent-security-record.md)) holds the profile, the control statuses, the severities and the readiness value. Two rules protect it.

### Record confidentiality

The record locates and rates weaknesses, so a record that others can read can disclose unfixed vulnerabilities.

- Where the record is readable beyond the people authorized to see unfixed vulnerabilities (for example in a public repository or a widely shared wiki), it MUST NOT carry the details of an open item rated critical or high: its location, failing test or reproduction, attack path or suggested fix. Unknown visibility counts as readable beyond them.
- Such an item appears by reference only, as `<ID>: open, details in <private reference>`, with its status and severity in the usual columns. Its details go to the project's private vulnerability channel: the process its SECURITY.md names, a private security advisory or a private tracker.
- A coding agent that cannot write to that channel returns the details in its response, tells the user where they belong, and never commits them to a readable location.
- The ID, status and severity stay in the record, so redaction never hides an open item from the release gate or from a reader of the readiness value. Open medium and low items, closed items and the profile MAY be recorded in full.
- The record states its visibility: `Record visibility: private` or `Record visibility: public (details redacted)`.
- An assessor who verifies a claim needs the private details; the record names who holds them. After the fix is released, the details MAY be added to the record.

### Record and catalog integrity

The record is a claim about the system, so the framework treats it like any other claim and never as configuration that can lower a requirement.

- The record names the commit at which each assessment was made, and each compact change record names its change.
- Changes to the record's profile, level, status, severity, readiness, owner and exception lines MUST go through the repository's human review for security-relevant paths (for example a code-owner rule that covers the record path). A change that a coding agent makes to those lines is a proposal until a human has reviewed it.
- A later change reads the baseline record as a claim: at the commit the change starts from, with the level recomputed from the recorded profile and checked against the code, using the highest level found ([profile-and-levels.md](profile-and-levels.md#scoped)).
- A conformance or progress statement names a published catalog version. Controls, routing rules or the critical-boundary set edited in an installed copy of the skill or the catalog are not that version, and a statement made with an edited copy is invalid. Changes to an installed copy go through the same review as the record.

## Conformance statement

A system that satisfies every condition below may publish this statement:

```text
<System and version> at <commit>, for the stated scope <agents, entry points, deployments, environments>, meets Level <N> of <catalog name> v<X.Y> (computed level <M> from profile <summary>), self-declared on <date> by <accountable owner>; to be re-established by <date>.
```

`<catalog name>` is the name recorded in the catalog metadata (STAND), and `v<X.Y>` is the catalog MAJOR.MINOR. The statement is valid only when all of the following hold:

1. **Scope.** The scope names the system, components, environments and commit. It includes every component on the enforcement path that in-scope agents rely on (dispatcher, policy engine, adapters, credential broker, sandbox, egress proxy, approval UI, audit store). A claim cannot exclude a component it depends on; a component that another team or a vendor operates is covered as "Shared responsibility" below describes.
2. **Profile.** S-02 records the profile of every context in scope, and N is at least the computed level M. A claim below M is invalid.
3. **Controls.** Every control of Levels 1 through N has status implemented-and-verified, or not-applicable-with-reason because its `applies_when` matches no agent context in scope or the subject of every required case is architecturally absent (see "Status"). The reason is a verifiable architectural absence; reliance on a library, vendor or provider is not a reason.
4. **Excluded statuses.** No applicable control is failing, implemented-but-unverified, planned or not-assessed, and no SHOULD clause rests on an unaccepted deviation. Owner exceptions are release decisions under D-06 and never count toward conformance.
5. **Evidence.** Each implemented-and-verified entry cites a test or review that ran at the claimed commit, at or above the control's minimum evidence scope (D-03). It drives the real execution path (D-01) and pairs each denial with an authorized twin (D-02).
6. **Findings.** No finding rated critical or high is open within the scope.
7. **Metadata.** The record names the catalog version, the accountable owner (S-01) and a re-establish date no later than 12 months after the claim.
8. **Review.** A human reviewed the profile, the not-applicable reasons, and the hostile-case and twin inventory for the critical-boundary set, and the record cites that review (reviewer, date and commit); a review by a coding agent does not count. The accountable owner, or a delegate the owner named, publishes the statement; a coding agent may draft it but MUST NOT publish it.

The statement and its record live in the security record ([agent-security-record.md](../assets/agent-security-record.md)). A SCOPED change record can state that the changed controls were re-verified. It cannot support a level claim unless the baseline record satisfies conditions 1 to 8.

### Shared responsibility

Condition 1 keeps every enforcement component that an in-scope agent relies on inside the claim, whoever operates it. A component owned by another team or a vendor (a policy engine in another repository, a hosted agent platform's tool runtime, a managed egress proxy) is in scope when the record cites both of the following:

1. Evidence from the component's owner: another record against this catalog that covers the component at a named commit, with the relevant entries implemented-and-verified, or a vendor attestation, listed as an attestation with its date and scope.
2. The adopter's own hostile cases and authorized twins for the control, driving the component through the adopter's real entry point (D-01, D-02).

Rules:

- The control counts at the evidence scope that the adopter's own cases exercised. A cited record or attestation does not raise it.
- A cited record or vendor attestation alone never makes a control implemented-and-verified, and reliance on it is never a not-applicable reason (see "Status").
- The record lists each such component under "External enforcement components", with the component, its owner, and the evidence reference with its commit or date.
- A new version of an external component is a change to the enforcement path: the controls it enforces lapse until the adopter's cases pass again (see "Lapse"). Where the owner does not announce versions, the record states how often the adopter's cases re-run.

### Lapse

- A conformance statement names one commit. It MAY be carried forward to a later commit only if every change since that commit was triaged NONE or SCOPED, and for each SCOPED change the routed controls' required cases re-ran and passed at the later commit. The record then names the later commit and the commit range since the claimed commit, references the compact change record of each SCOPED change in that range, and states that the rest of the diff over the range touches no trigger location, so that an assessor can re-triage the range. NONE changes still write no record of their own. A FULL change cannot be carried forward this way.
- The claim lapses for a control when a SCOPED or FULL change touches that control's boundary, until the control's required cases pass at the new commit. While any applicable control has lapsed, the statement MUST NOT be published or relied on for that commit.
- The whole claim lapses when a FULL change lands without a new assessment, or when the re-establish date passes.
- A security advisory in `CHANGELOG.md` that names a catalog version and a control, because the control's guidance in that version leads to an exploitable design, makes every claim against that version lapse for that control from the advisory's date, until the control is reassessed against the fixed version. While it has lapsed, the statement MUST NOT be published or relied on.
- A claim is valid against the catalog version it names until its re-establish date, even after a newer catalog version is published, unless a security advisory names that version and control (see the previous item). Before a claim cites a newer version, it MUST be migrated: every control the new version adds or changes for the claimed profile and level is assessed, and the statement names the new version.
- Assessors verify a claim by sampling record entries and re-running the cited tests at the cited commit.

## Progress statement

A system that does not yet conform may publish a progress statement instead:

```text
Adopting <catalog name> v<X.Y>: <k> of <m> applicable Level 1 controls implemented-and-verified; critical-boundary controls outstanding: <IDs>.
```

- A progress statement MUST NOT use the word "meets".
- Recommended order: the critical-boundary set first, then the remaining Level 1 controls, then Level 2 and Level 3.
- Controls not yet examined are recorded as not-assessed, and the release gate applies to them as to any other open item.

## Nature of the claim

- A conformance statement is a self-declared engineering conformance statement about this catalog's controls only.
- Much of its evidence can be produced by the same coding agent that wrote the code. Such evidence shows that the cited cases ran and passed; it does not show that they are the right cases or that the profile is right. Condition 8 is the minimum human check on that; Level 3 adds independent adversarial review (D-09).
- It is not a certification, an audit opinion, an attestation or a guarantee of security. Zero observed failures is not a guarantee.
- It is not a statement of conformance to, or certification against, any of the following: the OWASP Top 10 for Agentic Applications 2026, OWASP AISVS or any other OWASP project; AIUC-1; NIST AI RMF 1.0 or its Generative AI Profile (NIST AI 600-1); ISO/IEC 42001.
- ASI identifiers on a control show which OWASP risks it is designed to address, govern or verify; controls tagged with every category are cross-cutting governance or verification controls. All references to those sources, including [mappings.md](mappings.md), are engineering mappings and do not claim coverage.
