<!-- Generated from catalog/controls.json in the source repository by scripts/render_catalog.py. Do not edit; propose changes upstream. -->
<!-- License: CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/). SPDX-License-Identifier: CC-BY-SA-4.0 -->

# D: Demonstrated Defenses

**Can we show that the controls work?**

Catalog version 0.1.0 (draft). This pillar has 10 controls: 7 at Level 1, 1 at Level 2, 2 at Level 3. Routing tables, the critical-boundary set and counts are in [index.md](index.md).

"Applies when" lists alternatives; `+` joins tags that must all hold in the same agent context ([profile-and-levels.md](../profile-and-levels.md)). Statuses, evidence scopes and severities are defined in [conformance.md](../conformance.md), and mapping relations in [mappings.md](../mappings.md).

## Level 1

### D-01 Enforcement-path tests

- **Level:** 1
- **Applies when:** `all`
- **Failure severity:** high
- **Minimum evidence scope:** integration
- **Critical boundary:** no
- **ASI:** ASI01, ASI02, ASI03, ASI04, ASI05, ASI06, ASI07, ASI08, ASI09, ASI10

**Statement:** Security tests for each applicable control MUST drive the public request, job, callback or message entry point through the real policy and dispatcher into a controlled adapter or destination that records protected reads, outbound traffic, state changes and audit events. A unit test of a policy helper MUST be accompanied by a test of the integration path that could bypass it.

**Rationale:** A test of an unused helper proves nothing about the running application. A mutation check keeps tests from being decorative. An unverified critical-boundary control is rated under D-06.

**Verification:** Inspection: the harness enters through public entry points named in S-04 and asserts downstream observations. Mutation check: disable the policy call in the dispatcher in a test build; the control's hostile tests fail (D-01/C1).

**Evidence:**

- Test harness reference
- Mutation run result

**Mappings:**

- AIUC-1: C002.1 (partial), D004.1 (supports)
- NIST: MEASURE 2.3 (partial), MEASURE 2.7 (partial), MEASURE 2.1 (supports), MP-2.1-002 (supports), MS-2.7-009 (supports)
- AISVS: none

### D-02 Hostile proposals with authorized twins

- **Level:** 1
- **Applies when:** `tools`
- **Failure severity:** medium
- **Minimum evidence scope:** integration
- **Critical boundary:** no
- **ASI:** ASI01, ASI02, ASI03, ASI09

**Statement:** Tests MUST inject crafted model proposals directly, independent of current model behavior. Each denial test MUST have an authorized-success twin of the same shape through the same path, and MUST assert that no downstream read, egress or effect occurred and that no weaker path was retried.

**Rationale:** Dangerous actions must be tested whether or not today's model chooses them, and the twin proves the application still works, so a control that blocks everything cannot pass.

**Verification:** Inspection: the test inventory pairs every hostile case with a twin, keyed `<ID>/C<n>`, and controlled adapters record zero calls for hostile cases and exactly one for twins.

**Evidence:**

- Test inventory keyed by control ID
- Controlled adapter call logs

**Mappings:**

- AIUC-1: C002.1 (supports), B001.1 (supports)
- NIST: MEASURE 2.7 (partial), MEASURE 2.6 (supports), MS-2.6-007 (supports)
- AISVS: none

### D-03 Evidence scope, runtime boundaries and record integrity

- **Level:** 1
- **Applies when:** `all`
- **Failure severity:** high
- **Minimum evidence scope:** inspection
- **Critical boundary:** no
- **ASI:** ASI02, ASI05

**Statement:** Every record entry MUST state its evidence scope from the closed enum (inspection, unit, simulation, integration, isolated-runtime, deployed). Each implemented-and-verified entry MUST cite a test or review that ran at the recorded commit at or above the control's minimum evidence scope; an unrun test MUST NOT be recorded as passed. Controls whose minimum evidence scope is isolated-runtime (A-12, A-14, A-17, A-18, A-23, T-05, T-11, T-12, T-13, T-15, T-16, T-17, T-19, T-23, T-26, T-27, D-08, D-10, N-10) MUST NOT be recorded as implemented-and-verified on weaker evidence; they remain implemented-but-unverified. Alternative evidence MAY replace a listed verification procedure only if it exercises the same boundary at the same or a stronger scope and the record states the substitution.

**Rationale:** A mock proves only the boundary it exercises, and simulated outputs cannot establish sandbox, egress, rendering or provider properties. One status enum and one evidence-scope enum make records lintable.

**Verification:** Record lint: every row has a scope and a status from the closed enums; rows for those controls with evidence below isolated-runtime are not implemented-and-verified; implemented-and-verified rows cite a run at the recorded commit. Hostile: a row marked implemented-and-verified that cites only a simulated sandbox run is rejected (D-03/C1).

**Evidence:**

- Record status and evidence-scope columns
- Record linter output

**Mappings:**

- AIUC-1: C002.1 (supports)
- NIST: MEASURE 2.1 (partial), MEASURE 1.1 (supports), MEASURE 2.3 (supports), MEASURE 2.13 (supports), MS-2.5-001 (supports), MS-1.1-009 (supports)
- AISVS: none

### D-04 Injection channel coverage with within-authority payloads

- **Level:** 1
- **Applies when:** `untrusted-input+external-effect` or `separation-pattern+external-effect`
- **Failure severity:** high
- **Minimum evidence scope:** integration
- **Critical boundary:** no
- **ASI:** ASI01, ASI02, ASI06, ASI09

**Statement:** For each untrusted channel in the profile (retrieved documents, web pages, inbound email and calendar items, uploads and pasted content, images, tool results, tool descriptors, peer-agent messages, memory, client-supplied history, repository files) and each consequential capability reachable from it, the suite MUST include at least one injection fixture driven through the real path, including at least one payload per channel whose requested action is within the principal's permissions but outside the task. In a separation pattern (T-02), the channels of the reading context count, and a capability is reachable from them when a value or reference that crosses the boundary can reach it.

**Rationale:** Attacks arrive through the channel nobody fixtured: EchoLeak arrived by email, ASI01's goal-drift example by calendar invite, and tool poisoning through descriptors. A forbidden-action test alone misses steering within authority.

**Verification:** Generate the channel-by-capability matrix from S-02 and S-04 and assert that each cell maps to a fixture ID that ran at the recorded commit, with at least one within-authority payload per channel.

**Evidence:**

- Channel-by-capability coverage matrix
- Fixture set
- Test run results

**Mappings:**

- AIUC-1: B001.1 (partial), C002.1 (supports)
- NIST: MEASURE 2.7 (partial), MEASURE 2.3 (supports), MP-2.3-005 (partial), MS-2.7-007 (supports), MS-2.6-007 (supports)
- AISVS: v1.0-C11.1.3 (supports)

### D-05 Failure, revocation and concurrency test matrix

- **Level:** 1
- **Applies when:** `tools`
- **Failure severity:** high
- **Minimum evidence scope:** integration
- **Critical boundary:** no
- **ASI:** ASI03, ASI08, ASI10

**Statement:** For each enforcement component and effect path in scope, tests MUST cover: failure of the policy service, credential service, audit sink and adapter; a timeout after a possible commit; a transport that ignores its timeout; cancellation while work is queued and while it is running; revocation of the principal, the approval and the parent run; and concurrent duplicate delivery. Each test MUST assert that no new effect starts after the defined point, and in-flight limits MUST be recorded. A scoped change MUST run only the rows for the boundaries it touches.

**Rationale:** Most bypasses in agent systems appear on failure and timing paths, not on the happy path. Routing only the touched rows keeps narrow changes narrow.

**Verification:** Inspection: each applicable row has a test that ran at the recorded commit, with its observed result; a missing row leaves the related control implemented-but-unverified.

**Evidence:**

- Test IDs per matrix row
- Record in-flight limits

**Mappings:**

- AIUC-1: C002.1 (supports)
- NIST: MEASURE 2.6 (partial), MEASURE 2.7 (supports), MS-2.6-005 (supports), MP-5.1-005 (supports)
- AISVS: none

### D-06 Severity-rated release gate

- **Level:** 1
- **Applies when:** `all`
- **Failure severity:** critical
- **Minimum evidence scope:** inspection
- **Critical boundary:** yes
- **ASI:** ASI01, ASI02, ASI03, ASI04, ASI05, ASI06, ASI07, ASI08, ASI09, ASI10

**Statement:** Every applicable control that is failing, implemented-but-unverified, planned or not-assessed MUST be rated with the catalog severity rubric, with a recorded rationale, before any readiness claim. A readiness or conformance claim MUST NOT be made while any critical finding is open or any applicable critical-boundary control is not implemented-and-verified. A high finding MUST carry an exception under S-01 for release, and exceptions never count toward conformance. The coding agent MUST NOT record acceptance, or suppress or weaken a failing check.

**Rationale:** The go or no-go decision is the most consequential output, and 'critical' must not be left to judgment under delivery pressure. A readiness claim contradicted by evidence is itself critical.

**Verification:** Record lint: severity and rationale exist for every non-passing row. Hostile: a record that claims ready while a critical-boundary control is implemented-but-unverified (D-06/C1), or with a high finding lacking owner, date or expiry (C2), is rejected by the linter or reviewer. Twin: a record with only verified or not-applicable rows passes (C3).

**Evidence:**

- Record severity column
- Readiness value
- Record linter output

**Mappings:**

- AIUC-1: C002.1 (partial), C001.1 (supports), C002.2 (supports)
- NIST: MANAGE 1.1 (partial), MANAGE 1.2 (partial), MANAGE 1.3 (supports), MANAGE 1.4 (supports), MEASURE 2.6 (supports), GV-1.3-002 (partial), GV-1.3-007 (supports), MG-1.3-001 (supports), MS-2.3-003 (supports)
- AISVS: v1.0-AC.4.3 (supports)

### D-07 Security regressions as required checks

- **Level:** 1
- **Applies when:** `all`
- **Failure severity:** high
- **Minimum evidence scope:** inspection
- **Critical boundary:** no
- **ASI:** ASI04, ASI08, ASI10

**Statement:** Security tests MUST be committed with the change, keyed by control ID, and runnable non-interactively by a documented command. Where the repository's CI is in scope, they MUST run on changes to the locations they protect, including model, prompt, provider, descriptor and agent-framework version changes, and SHOULD be required merge checks. Changes to security tests and policy files SHOULD require code-owner review. Each confirmed incident or bypass MUST add a regression fixture. The record MUST state whether required-check enforcement was inspected.

**Rationale:** Controls regress silently: model and framework upgrades change prompt-dependent behavior or add native tool paths, and agents 'fix' failing builds by weakening tests. A skill alone cannot enforce CI, so the record states what was inspected.

**Verification:** Inspection: the documented command runs every test ID cited in the record; CI path filters map to the protected locations; the record states whether required-check enforcement was inspected. Hostile: in a branch, change the model version and a tool descriptor; the security suite runs (D-07/C1). Twin: a documentation-only change does not trigger it (C2).

**Evidence:**

- CI configuration reference
- Documented test command
- Record CI field

**Mappings:**

- AIUC-1: C002.2 (partial), B001.1 (supports)
- NIST: MEASURE 1.2 (partial), MEASURE 2.7 (supports), MANAGE 4.2 (supports), MS-2.7-009 (partial), MG-4.2-002 (supports), MS-2.7-006 (supports)
- AISVS: v1.0-C11.1.2 (supports), v1.0-C3.2.3 (partial), v1.0-AC.6.4 (supports)

## Level 2

### D-08 Live-model adversarial evaluation

- **Level:** 2
- **Applies when:** `untrusted-input`
- **Failure severity:** medium
- **Minimum evidence scope:** isolated-runtime
- **Critical boundary:** no
- **ASI:** ASI01, ASI02, ASI06, ASI09

**Statement:** Before a release at Level 2 or above, the delivered application MUST be evaluated with its pinned live model configuration against injected content in each untrusted channel and in multi-turn flows, using repeated trials. The report MUST state trial counts, attempted versus executed harmful effects, attack success rate, clean task success, task success under attack, and false refusals of authorized tasks. Results supplement deterministic controls and MUST NOT be the sole evidence for any control.

**Rationale:** Deterministic tests force proposals; only live runs show how often the model is steered and what the defenses cost in utility.

**Verification:** Inspection of the evaluation report: pinned model, prompts, tools and corpus; channels covered; trial counts and metrics; stated limits; and no deterministic control recorded as verified on the evaluation alone.

**Evidence:**

- Evaluation configuration
- Evaluation report with trial counts

**Mappings:**

- AIUC-1: B001.1 (partial), D004.1 (supports), C012.1 (supports)
- NIST: MEASURE 2.7 (partial), MEASURE 2.3 (partial), MEASURE 2.1 (supports), MS-2.7-007 (partial), MP-2.3-005 (supports), MS-2.5-001 (supports), MS-4.2-002 (supports), MS-4.2-001 (supports), MS-2.10-001 (supports)
- AISVS: v1.0-C11.1.3 (partial), v1.0-C6.1.4 (supports), v1.0-AC.2.3 (supports)

## Level 3

### D-09 Independent adversarial review with adaptive attacks

- **Level:** 3
- **Applies when:** `all`
- **Failure severity:** high
- **Minimum evidence scope:** inspection
- **Critical boundary:** no
- **ASI:** ASI01, ASI02, ASI03, ASI09, ASI10

**Statement:** Before a Level 3 release, a human reviewer independent of the implementer MUST attempt to bypass every applicable critical-boundary control through the real execution path, including adaptive attacks that iterate against the deployed prompts and tools. Automated attack tools MAY assist. Findings MUST be recorded with severity, and each bypass found MUST become a D-07 regression fixture.

**Rationale:** At the trifecta or full-autonomy level, self-verification is insufficient, and static attack sets overstate robustness. An implementing agent, or a pipeline it configured, is not independent.

**Verification:** Inspection: the review record names the reviewer and their independence basis, the date and scope, the adaptive attack method, the attack success and utility metrics with trial counts, and every finding with its disposition and regression fixture.

**Evidence:**

- Independent review record
- New regression fixtures

**Mappings:**

- AIUC-1: B001.1 (partial), D004.1 (partial), B004.3 (supports)
- NIST: MEASURE 1.3 (partial), MEASURE 2.7 (partial), MS-1.3-003 (supports), MS-2.7-007 (partial), GV-3.2-001 (supports)
- AISVS: v1.0-AC.6.3 (supports)

### D-10 Replay before rollout and before authority expansion

- **Level:** 3
- **Applies when:** `external-effect`
- **Failure severity:** medium
- **Minimum evidence scope:** isolated-runtime
- **Critical boundary:** no
- **ASI:** ASI04, ASI08, ASI10

**Statement:** Before a change to model version, prompts, tool definitions or grants, or policy reaches production, and before tools, permissions, autonomy or fan-out limits are expanded, recorded runs (redacted traces or a maintained regression corpus that includes past incidents) MUST be replayed against the changed configuration in an isolated clone of the environment. Differences in proposed and executed consequential actions MUST be reviewed by an accountable human, and an expansion MUST be blocked if replay exceeds the recorded blast-radius caps.

**Rationale:** ASI08 lists digital-twin replay and policy gating among its mitigations (mitigation 9, p. 32); otherwise behavioral drift from a model or policy change is first found in production.

**Verification:** Hostile: propose an expansion that would let a recorded faulty plan fan out beyond the cap; the replay gate blocks it (D-10/C1). For a sample of changes, confirm a replay run, a diff of consequential actions and a named reviewer. Twin: an expansion within the caps passes (C2).

**Evidence:**

- Replay corpus manifest
- Replay diff reports
- Reviewer record

**Mappings:**

- AIUC-1: C002.1 (partial), E004.1 (supports)
- NIST: MEASURE 2.3 (partial), MANAGE 4.1 (supports), MANAGE 3.2 (supports), MG-3.1-003 (supports), MS-2.5-006 (supports)
- AISVS: v1.0-C3.2.3 (partial), v1.0-C3.3.1 (supports)
