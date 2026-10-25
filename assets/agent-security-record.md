# Agent security record

## Scan-only report

For FULL scan-only execution, use this report format instead of the implementation template below. Follow [the scan-only rules](../references/profile-and-levels.md#scan-only-execution). Return the report in the response unless the user names a report path. Preserve the confidentiality rule below, including private references for open critical or high details.

- **Target and snapshot:** repository or source target, commit, inspection date, dirty paths or source identities, and snapshot limits.
- **Scope:** requested boundaries, entry points, exclusions and unavailable sources.
- **Profiles and coverage:** per-context properties, tags, levels, applicable controls, assessed IDs, not-applicable reasons and not-assessed IDs.
- **Evidence:** fresh inspection references, separate retained receipts with their original snapshot and scope, and gaps that prevent current verification.
- **Findings:** control ID, status, severity and rubric rationale, source file and function or line, failure path, smallest fix, proposed verification, and owner or unassigned. Do not invent an owner or exception.
- **Unknowns and exclusions:** missing facts, unverified assumptions, external boundaries and checks that did not run.
- **Gate:** readiness under the existing rubric, residual risks and required owner decisions. Do not claim execution results for proposed checks.

If any required source, reference or applicable control remains unassessed, label the report partial in Scope and the final conclusion. In Unknowns and exclusions, list each affected control ID, missing source or section, and next inspection step.

In Profiles and coverage, give the total unique IDs considered and the applicable and not-applicable counts. Give the assessed and not-assessed applicable counts. Give counts for every control status, even zero. Reconcile these counts with the IDs in the Controls rows and grouped exclusions. Assessed plus not-assessed equals applicable. Applicable plus not-applicable equals total considered.

Apply the [status definitions](../references/conformance.md#status) to each row. Support each `failing` row with a failed required case or a source-proven bypass. Missing or unrun verification alone does not establish `failing`. For implemented statuses, cite the actual mechanism and identify documentation-only evidence. Do not invent implementation for absent or unknown mechanisms.

Keep source conclusions within the inspected boundary. An unavailable host source does not prove an absent capability for a not-applicable reason. Apply the [unknown-property rules](../references/profile-and-levels.md#evaluation-rules) when architectural absence is unknown.

Use complete local source to show when a required guard is absent. Record an external mechanism with no available source as unknown. Keep a source-proven bypass if host behavior is unknown.

End Findings with a brief prioritized repair sequence for actual findings. Link actual findings to their smallest fixes, dependencies and proposed checks. Separate evidence acquisition and owner decisions from code repairs.

For each finding, compare the proposed repair with all applicable requirements in the control statement and required verification. Include required clauses missing from the source outside the observed path. Record a repair as partial if it closes only that path with other required clauses open.

Use the existing status and evidence-scope enums below. Include one Controls row per applicable control with the existing column names. Group not-applicable IDs by reason. In the test column, label proposed checks as proposed and retained results as retained. Source inspection does not establish a fresh test result.

The rest of this template applies to implementation records. In scan-only mode, skip its execution and update instructions.

> Template instructions. Remove these quoted blocks after adapting the record.
>
> - **Format.** Adapt the record to the project's existing evidence format, but keep the control IDs, the column names of the control table, and the enum values exactly as written here.
> - **Control IDs.** IDs refer to the catalog version in the header. Outside this record, cite a control as `A-06@0.1` and a test as `A-06@0.1/C1`.
> - **SCOPED changes.** Write only the "Compact change record (SCOPED changes)" section at the end, plus any Inventory entry the diff adds or alters (S-04); its rules and line budget are stated there.
> - **Length (FULL).** Budget about 120 lines for the template's fixed structure, plus one per applicable control and one per Inventory entry, register operation, assumption, signal or residual risk beyond the template's placeholder rows, counting non-blank lines once these quoted instructions are removed: a system with about 40 applicable controls and about 20 such entries fits in roughly 180 lines. One Controls row per applicable control; one row per not-applicable reason, listing all its IDs; cells cite files, functions and test IDs instead of describing code; no prose that repeats a table, the catalog or the code. One line per Inventory entry; omit the empty Deviations table (write "Deviations: none") and, below the selected level, the Level 2 and 3 rows and bullets. Never drop a required field to meet the budget; a record far beyond it usually duplicates code or the catalog.
> - **Unknowns.** Write "unknown", "unassigned" or not-assessed rather than inventing evidence, owners or approval. Keep an unrun test distinct from a passed test.
> - **Owner fields.** A coding agent never enters an owner, an acceptance or an exception that a human has not provided (S-01).
> - **Confidentiality.** This record maps open, located weaknesses. Where it is readable beyond the people authorized to see unfixed vulnerabilities (a public repository, or visibility unknown), write each open critical or high item by reference only, as `<ID>: open, details in <private tracker reference>`, and keep its location, failing test and suggested fix in the project's private vulnerability channel (its SECURITY.md process or a private advisory). Set "Record visibility" in the Header accordingly.
> - **Integrity.** The record is a claim, not configuration. Name the commit each assessment was made at, and change the profile, level, status or readiness lines only through the repository's review for security-relevant paths. A later task recomputes the level from the recorded profile and uses the higher value if they differ.
> - **Claim audit.** Before recording implemented-and-verified, list every required case of the control by label with its result at the recorded commit. A case not run or not passing keeps the status implemented-but-unverified or failing.
> - **Status** (exactly one per control): implemented-and-verified, implemented-but-unverified, planned, not-applicable-with-reason, failing, not-assessed.
> - **Evidence scope** (weakest to strongest): inspection, unit, simulation, integration, isolated-runtime, deployed.
> - **Where definitions live:**
>   - the profile, applicability tokens, levels and triage are in the skill's references/profile-and-levels.md;
>   - status, evidence scope, the severity rubric, the release gate and statements are in references/conformance.md;
>   - control text is in references/controls/;
>   - test design is in references/verification.md.

## Header

| Field | Value |
| --- | --- |
| Catalog version | 0.1.0 |
| Skill version and commit (the STAND bundle used; a bundle manifest SHA-256 if one is shipped) | 0.1.0; |
| System, version and assessment commit (D-03) | |
| Record visibility (private, or public with open critical and high details redacted); location of redacted details | |
| Scope (agents, entry points, deployments, environments) and enforcement-path components in scope (dispatcher, policy engine, adapters, credential broker, sandbox, egress proxy, approval UI, audit store) | |
| Intended use; forbidden outcomes | |
| Affected principals | |
| Accountable owner (S-01); owner source reference (a human-authored message, ticket or signed commit) | unassigned |
| Record date; prepared by (a person, or a coding agent named as such) | |
| Assessment tier; selected level | FULL; |
| Re-establish date (no later than 12 months after any claim) | |
| Progress (FULL, while incomplete): last completed control ID; next planned control ID; commit | |

## Capability profile (S-02)

> Add one row per agent context: an agent, subagent, planner, quarantined reader or triggered worker, together with its tool set. Rules:
>
> - A property whose presence is unknown counts as present.
> - A context that consumes output of an untrusted-input context is untrusted-input, unless that output crossed a separation boundary verified under T-02; values that cross it stay untrusted-derived and are checked under A-06 and A-07.
> - A context that receives sensitive data in its input (a summary, recalled memory, a delegated message) is sensitive-data, even when its own tools cannot read that data.
> - Filters, guard models, prompts and approvals never make a property absent.
> - Take feature tags from the closed vocabulary, and compute each level with the selection rule in references/profile-and-levels.md.

| Context | untrusted-input (U) and source | sensitive-data (D) and source | external-effect (X) and source | Separation pattern, removed property, T-02 status | Autonomy scope (1-4) | Feature tags | n | A-08 option, if n is 3 | Computed level |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | | | |

- Union across contexts (U, D, X and tags); computed level (the maximum over contexts):
- Owner-declared level (or none); selected level (the higher of the two; a claim below the computed level is invalid):
- Principal browser agent-capable (A-12; an agentic browser or an extension can drive it): yes | no | unknown (unknown counts as yes)

## Inventory (S-04)

> One bullet per entry, starting with its label, with the fields in the order shown and separated by semicolons; repeat the label for each further entry. List the labels with no entries on the "None" line instead of leaving them empty.

- None: <labels with no entries, for example MCP server or remote agent; provider-executed tool>
- Agent: <context>; <workload identity and owner>; <models with exact versions (primary, fallback, guard, embedding)>; <prompt and policy versions>; <agent framework and skill versions>
- Tool: <fully qualified name>; <context>; <executed by the application or the provider>; <task need (S-03)>; <register entry (S-05)>; <runs without approval (A-09): yes or no>
- MCP server or remote agent: <name>; <transport and protocol version>; <endpoint, or exact launch command (T-19)>; <pinned descriptor hash (T-18)>; <credential audience (A-16)>; <sandbox>; <reviewed on>
- Provider-executed tool (T-11): <tool>; <provider and account>; <domain or tool allowlist>; <approval mode>; <data classes that can be in context>; <where call records are logged>
- Model or data recipient (T-10): <inference, embedding, reranking, evaluation, telemetry, tracing or crash reporting>; <provider, account, endpoint, region>; <model and version>; <approved data classes (S-06)>; <retention, training and logging terms>; <fallback order>
- Egress destination (T-12, T-13): <destination class>; <mode (allowlist or public-internet) and tool>; <allowed hosts or allowlist reference>; <contexts>; <enforced at (proxy, network policy, renderer allowlist, provider setting)>
- Read-tool exemption (A-06): <context>; <L>; <per-run cap>; <daily cap>; <per-run bound in bits (per-run cap x log2(L+1))>; <ceiling in bits, below the lowest-entropy secret class, and its rationale>; <daily bound and retention-period total, accepted as residual risk (S-01)>
- Browser context (T-17): <context>; <navigation rule (allowlist, exempt links in a profile with no delegated session, or unrestricted in an isolated logged-out profile)>; <delegated sessions and expiry>; <input to pages outside the allowlist (none, or page requests blocked after input)>
- Data class (S-06): <class>; <policy reference>; <secret class: entropy in bits, or no>; <permitted providers, destinations, stores, logs and audiences>; <retention and deletion>
- Store: <index, memory, cache, export, log or audit store>; <data classes>; <partitioning (tenant, principal, purpose)>; <writers>
- Component (T-24, T-25): <dependency, plugin, sandbox image or model artifact>; <version or hash>; <provenance>; <advisories checked (for example CVE, AVID)>
- Entry point (S-04, A-19): <interactive, job, callback, webhook, schedule, MCP server or CLI>; <principals (initiating user, trigger sender, data owner, output viewers)>; <path through components>; <boundaries where data becomes instruction, identity, permission, executable input, destination or persistent state>
- Trigger policy (A-19), per trigger type for unattended runs: <policy>
- External enforcement component: <component owned by another team, repository or vendor>; <owner>; <evidence reference (another record of this catalog at a named commit, or a listed vendor attestation) and the adopter-side test that exercised it>

## Consequential operations register (S-05)

> Summarize the machine-readable register that the dispatcher reads, and link to it; do not keep a second hand-maintained copy. The consequence class is one of: sensitive read, reversible write, irreversible or financial effect, external communication.

| Operation | Consequence class | Allowed resources and destinations | Consequential arguments and trusted source | Value and rate limits; impact threshold (funds or access) | Reversibility | Approval policy | System of record for each fact relied on |
| --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | |

| Assumption (a required fact that is unknown) | Fail-safe default chosen (deny, confine or require confirmation) | Owner decision needed |
| --- | --- | --- |
| | | |

## ASI applicability (S-04)

> Titles follow references/owasp-agentic-top-10.md (OWASP Top 10 for Agentic Applications 2026). For each category:
>
> - If it applies, list the control IDs (from each control's ASI field in references/controls/) and at least one abuse case that stays within granted authority.
> - If it does not, give a reason that names a verifiable architectural absence: the capability that is absent. Reliance on a library, vendor or provider is not a reason.

| ASI | Title | Applicable | Control IDs | Abuse case within granted authority | Not-applicable reason |
| --- | --- | --- | --- | --- | --- |
| ASI01 | Agent Goal Hijack | | | | |
| ASI02 | Tool Misuse & Exploitation | | | | |
| ASI03 | Identity & Privilege Abuse | | | | |
| ASI04 | Agentic Supply Chain Vulnerabilities | | | | |
| ASI05 | Unexpected Code Execution (RCE) | | | | |
| ASI06 | Memory & Context Poisoning | | | | |
| ASI07 | Insecure Inter-Agent Communication | | | | |
| ASI08 | Cascading Failures | | | | |
| ASI09 | Human-Agent Trust Exploitation | | | | |
| ASI10 | Rogue Agents | | | | |

## Controls

> **Rows.** Add one row for each control whose applies_when matches any context in scope, at Level 1 through the selected level. Group the controls excluded as not applicable into one row per reason, with every ID it covers in the Control ID cell (for example `T-15, T-16, T-27` with "no code execution in any context"). Conditional Level 1 controls bind whenever their condition holds, whatever level is claimed.
>
> **Cells.** Cite the enforcing file and function, and the test IDs with their observed results; do not describe the code or restate the control. A gap in a pre-existing feature that this change did not implement is still a row: status failing or not-assessed, severity, location and suggested fix (by reference only where the confidentiality rule above applies).
>
> **Pillars:** S Scope & Stewardship, T Trust & Isolation, A Authority & Access, N Notice & Neutralize, D Demonstrated Defenses.
>
> **Hostile test, twin and evidence scope.** Give test IDs as `<ID>/C<n>` with each observed result, and the scope that evidence achieved. A row with no evidence states the control's minimum evidence scope as its target and cites no test. A required case whose subject is architecturally absent from every context in scope (for example a stdio launch command when only remote MCP servers are used) is written `<ID>/C<n>: not applicable (<verifiable absence>)`; it does not block implemented-and-verified when the other required cases passed (references/conformance.md).
>
> **Severity and rationale.**
>
> - For a row that is failing, implemented-but-unverified, planned or not-assessed, give the severity, the rubric cell (harm class and reachability) and a rationale.
> - Write "none open" for a row that is implemented-and-verified or not-applicable-with-reason.
> - Start from the control's default failure severity. Lower it only with a recorded precondition that makes the attack unreachable, never because of current model behavior, detector coverage, prompt instructions or unverified provider claims.
>
> **Owner or exception.** Give the owning team or role, or the exception reference for a high finding. A coding agent writes "unassigned".
>
> The first row is an example; replace it.

| Control ID | Pillar | Applicable or not-applicable reason | Status | Implementation reference | Hostile test, twin and evidence scope | Severity and rationale | Owner or exception |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T-13 | T | Applicable: the support-chat context is rendered-output+untrusted-input (ticket text reaches the web chat renderer) | implemented-but-unverified | `web/chat/render.ts` blocks remote images and renders non-allowlisted links inert; unfurling disabled in `integrations/chat.yaml` | Unit (sanitizer only): T-13/C1 image node for `https://attacker.example/?d=<canary>` removed from the sanitizer output; T-13/C2 link to the same URL rendered as inert text; T-13/C6 twin: allowlisted image node kept; C3 to C5 not run. No real-client run at isolated-runtime, so no request log exists | Critical: H-breach (disclosure through rendering), reachable (anyone can file a ticket). Critical-boundary control, so readiness is blocked | unassigned; a critical cannot be excepted |
| | | | | | | | |

### Deviations (SHOULD clauses)

> A SHOULD clause is satisfied by implementation or by a deviation recorded here. A deviation does not change the control's status, which follows its MUST clauses and required cases (references/conformance.md). A coding agent may draft a row but writes "unassigned" for an owner a human has not named. A row whose owner is unassigned does not satisfy the clause: it stays an open item rated with the severity rubric.

| Control ID | Clause | Reason | Compensating measure | Owner | Test or review reference |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

## Verification record (D-01 to D-10)

- Documented test command (D-07); commands actually run, with commit, environment and configuration:
- Mutation check result (D-01); test inventory pairing each hostile case with its twin (D-02):
- Channel-by-capability matrix reference (D-04); failure, revocation and concurrency rows run, and rows not run (D-05):
- Positive behavior preserved (twins and the existing suite):
- Live-model evaluation at Level 2 and above (D-08): pins; channels covered; trial counts; attack success, attempted and executed; clean task success; task success under attack; false refusals; stated limits.
- Independent adversarial review at Level 3 (D-09): reviewer and independence basis; date and scope; adaptive method; findings and the regression fixtures added.
- Replay at Level 3 (D-10): corpus, diff report, reviewer.
- CI (D-07): protected paths covered; required merge checks; whether required-check enforcement was inspected (yes or no, with evidence).
- Runtime boundaries still needing isolated-runtime or deployed evidence:

## Signals (N-04)

> Detection supplements enforcement. A signal never counts as the implementation of an enforcement control. At Level 2, add approval-fatigue signals (A-13) and behavioral detection with its false-positive rate (N-05).

| Signal | Condition | Emitted by | Routed to (owner, or unassigned) | Response target | Test ID |
| --- | --- | --- | --- | --- | --- |
| Consequential action denied | | | | | |
| Provenance or task-scope denial from a tainted context | | | | | |
| Budget or quota stop | | | | | |
| Descriptor or component drift | | | | | |
| Audit-write failure | | | | | |
| Kill-switch activation | | | | | |
| User report of suspicious agent behavior | | | | | |

## Stop and revocation (N-06, N-07)

> Derive each latency target from token lifetimes, authorization-cache TTLs and queue leases on paths that do not check revocation directly. In-flight limits name what can still complete after a stop takes effect, such as an external call already sent.

| Scope | Mechanism, working without a deploy | Who may trigger it | Latency target and derivation | Measured value and test ID | In-flight limits | Compensating action |
| --- | --- | --- | --- | --- | --- | --- |
| Run and all descendants (N-06) | | | | | | |
| Tool, component or model version (N-06) | | | | | | |
| Agent (N-06) | | | | | | |
| Tenant (N-07, Level 2) | | | | | | |
| Global (N-07, Level 2) | | | | | | |

- Incident owner, containment, evidence preservation and memory or index cleanup (N-08, Level 2):
- Irreversible effects, with any compensating actions:
- Last incident exercise, with date and outcome:

## Residual risks and exceptions (S-01, D-06)

> A coding agent may draft rows but leaves the owner and the acceptance reference as "unassigned". A critical finding cannot be excepted, and exceptions never count toward conformance.

| Finding or control ID | Severity and rubric cell | Scope | Compensating control | Owner | Acceptance reference (human-authored) | Expiry (at most 90 days after acceptance) | State |
| --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | |

## Release gate result (D-06)

- Selected level; applicable controls at Level 1 through it; counts implemented-and-verified and not-applicable-with-reason:
- Open critical, including applicable critical-boundary controls that are not implemented-and-verified (IDs; details by reference where the record is not private):
- Open high, each with its exception reference or "no exception" (IDs):
- Medium and low, each with owner and target date (IDs):
- Accountable owner assigned (yes or no; an unassigned owner blocks ready-within-scope); readiness (exactly one: ready-within-scope, confined-prototype, blocked):
- Gate applied on (date) by (person, or coding agent named as such); owner decision reference, or "pending"; next review (the re-establish date, and the N-09 triggers that require re-assessment):

## Conformance or progress statement

> Use the conformance statement only when every validity condition in references/conformance.md holds. Otherwise use the progress statement, which never uses the word "meets". Replace each placeholder in angle brackets: `<catalog name>` is the name recorded in the catalog metadata, and `v<X.Y>` is the catalog MAJOR.MINOR. A coding agent may prepare the text; only the accountable owner self-declares it.

Conformance statement:

```text
<System and version> at <commit>, for the stated scope <agents, entry points, deployments, environments>, meets Level <N> of <catalog name> v<X.Y> (computed level <M> from profile <summary>), self-declared on <date> by <accountable owner>; to be re-established by <date>.
```

Progress statement:

```text
Adopting <catalog name> v<X.Y>: <k> of <m> applicable Level 1 controls implemented-and-verified; critical-boundary controls outstanding: <IDs>.
```

- Statement reviewed by (a human, never a coding agent; review date, commit and reference, as validity condition 8 requires); published by (the accountable owner or a named delegate), or "draft, pending owner review":

Either statement is a self-declared engineering statement about this catalog's controls only. It is not a certification, an audit opinion, an attestation or a guarantee of security. It is not a statement of conformance to, or certification against, the OWASP Top 10 for Agentic Applications 2026 or any other OWASP project, AIUC-1, NIST AI RMF 1.0 or its Generative AI Profile (NIST AI 600-1), or ISO/IEC 42001.

## Compact change record (SCOPED changes)

> Rules for a SCOPED change (defined in the change triage of references/profile-and-levels.md):
>
> - **Placement.** Add each record at the top of this section, newest first, as a fenced `text` block. The record is append-only: leave the baseline Controls table and release gate result unchanged. The newest record's Readiness line is the current readiness. In the same change, update any Inventory entry the diff adds or alters (S-04). Add no ASI table, full assessment or other section.
> - **No record file.** Create this file at the path the repository's instructions name, otherwise `docs/agent-security-record.md`, with only the Header and this section: fill in the Catalog version so bare IDs stay pinned, set Assessment tier to SCOPED, Selected level to "not computed (no baseline)" and Accountable owner to "unassigned" unless a human named one, and leave the other fields empty. When the repository has no record and no instruction adopting this workflow, and the user did not explicitly ask for the record, put the compact record in the report and offer to create the file instead.
> - **Line budget: at most 12 lines plus one per routed control.** Count every non-blank line the change adds to the record file: the two fence lines, every field line, and any heading or note. Add no heading or note; this heading already exists and the Header pins the catalog version. Not counted: Inventory rows the diff requires (S-04), "Finding:" lines, and, when the change creates the file or this section, its Header and this heading. If an existing record lacks this section, add this heading at the end of the file; that heading is not counted.
> - **Control lines.** One line per routed control, including a control dropped with its reason; the touched D-05 rows share one line, and controls with the same status and evidence scope may share one. D-03 and D-06 take no line: the "Tests run" and "Readiness" lines record them. A control whose required cases did not all run at this commit is implemented-but-unverified.
> - **Fixed and conditional lines.** The skeleton's other lines fill the 12 with the fences. Lines marked "only if" are left out otherwise. With no baseline record, append "Baseline: missing (full assessment recommended)" to the Profile line, leave the other applicable controls not-assessed and record readiness as blocked (baseline missing: critical-boundary set not assessed). "Release prerequisites:" lists the D-08, D-09 or D-10 activities the change triggers. "Owner decisions:" lists proposed product rules, flows and thresholds, marked not implemented, or a minimal mechanism built for a critical boundary. A gap found in a pre-existing, unchanged feature (scope rule item 2) takes one "Finding:" line each, outside the budget, so it is never compressed or dropped to fit; where the confidentiality rule applies, a critical or high finding gives the control ID, status, severity and private reference only.

```text
Change: <PR, ticket or commit reference, or none>, <one-line description>
Tier: SCOPED (<reason>); locations: <trigger locations touched>
Profile: unchanged (<reason>)[; Baseline: missing (full assessment recommended), only if no baseline record exists]
<Control ID>: <status>, <evidence scope>, <test IDs and observed results, or the reason it was dropped>   <- one line per routed control
Tests run: <command>: <result>
Residual risk: <none new, or risk with severity and owner or "unassigned">
Finding: <control ID>, <status>, <severity>, <location>, <failing test or none>, <suggested fix>   <- only if a gap in an unchanged feature was found; one per finding; not counted
Release prerequisites: <D-08, D-09 or D-10 activities the change triggers>   <- only if any
Owner decisions: <proposed product rules, flows or thresholds: not implemented, or minimal mechanism built>   <- only if any
Readiness: <ready-within-scope, confined-prototype or blocked> (<basis>)
Approver: <name a human provided, or unassigned>
Other controls: not re-assessed (outside change scope)
```

A filled example, 14 counted lines for three routed controls, is the narrow-timeout worked example in the skill's references/profile-and-levels.md.

## Framework context (optional)

- Source editions consulted (see the skill's references/frameworks.md):
- NIST AI RMF subcategories or GAI Profile actions supported, with the record rows that evidence them (optional):
- AIUC-1 requirements this record supports, by identifier only (optional):
- OWASP AIVSS scores, with version, recorded alongside as related scoring; they never change the gate (optional):

All framework references are engineering mappings. This record is an engineering assessment, distinct from certification or organization-wide conformance.
