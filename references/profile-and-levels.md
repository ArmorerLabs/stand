# Capability profile, levels and change triage

This file and [conformance.md](conformance.md) are the normative framework text around the control catalog. This file defines how to profile an agent application, which controls apply to it, which level it needs, how much security work a change requires, and how controls are identified. BCP 14 key words (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY and the others) are used as defined in [conformance.md](conformance.md). Control IDs such as A-06 refer to catalog entries listed in [controls/index.md](controls/index.md).

## The application

"The model proposes. The application enforces." is the principle every control implements.

"The application" means the deterministic controls the model cannot alter: application code, identity and policy services, sandboxes, network policy and infrastructure. Prompts, delimiters, filters and guard or classifier models are not enforcement in this sense. They can add signals, but they are never the only enforcement for any control (T-01).

## Terms

These terms are used across the catalog and these files. Each one is defined in the control statement named with it, and that statement is the operative text; this list collects the definitions so that they are applied the same way everywhere. A difference between this list and the control statement is a defect to report, and the control statement governs.

| Term | Meaning | Defined in |
|---|---|---|
| consequential operation | An operation that changes state, moves value, communicates externally or sends data to a model-chosen destination. Each one is registered in versioned trusted configuration. | S-05 |
| consequential argument | An argument of a consequential operation that decides its effect (recipient, URL, host, path, query target, payee, account, amount, repository or branch, command), registered with its trusted source. | S-05 |
| trusted source | A principal-entered value from the current task; the system of record, only for the field that the principal's task names for that argument (or, where the task names none, the one field the register fixes as the argument's only permitted value), and for an object identifier only within the principal's or case's scope; an allowlist bound to the resource; a value that application code computes deterministically from trusted sources only; for a response to the sender of a triggering event, that sender's authenticated origin; or, for a read-tool query argument, the output of a query composer. | S-05, A-19, A-06 |
| principal-entered | A value the principal typed or selected in a structured field of a trusted interface, or in a channel the application can show carries no pasted, uploaded or forwarded content. | S-05 |
| supplied, designated | Supplied content is what the principal typed, pasted, uploaded or forwarded in this task. Designated content is an item the principal named by identifier or link, or selected in a structured interface the application renders (never in server-supplied UI such as an MCP Apps view), in this task, and the direct results of a retrieval whose full query the principal wrote, or reviewed and submitted in a structured query field that no tainted context filled. The application records each designation before the item enters the context; a tainted context cannot designate anything, and an item whose arrival started a triggered run with no principal in session is not designated. | A-06 |
| free-text principal turn | A principal turn in free-text chat whose pasted, uploaded or forwarded spans the client does not mark. It can carry third-party text, so: it taints the context it enters (T-01); a value taken from it is untrusted-derived, never principal-entered (S-05, A-06); a query composer does not receive it (A-06); and the task scope derived from it is confirmed by the principal before the run acts, whether or not the context is tainted (A-07). A turn entered in a structured field, a turn from a channel the application can show carries no such content, and a turn with the client-marked spans removed are not free-text principal turns in this sense. | T-01, S-05, A-06, A-07 |
| query composer | A context that has not read untrusted content in this run and receives only trusted configuration and principal turns from a channel the application can show carries no pasted, uploaded or forwarded content (or with the spans its own client marked as such removed). Where that cannot be shown, its query goes to a structured query field for the principal to review and submit. | A-06 |
| untrusted content | Content not authored by the authenticated principal in the current task or by reviewed trusted configuration, including any free-text field another party authored (see the field rule under untrusted-input). | T-01 |
| tainted context | A context that untrusted content has entered. Its taint attaches to every proposal, summary, memory write and delegated message it emits, and summarizing, compacting, embedding, caching or forwarding never clears it. | T-01 |
| untrusted-derived | A value taken from untrusted content or from a reading context across a separation boundary, a value extracted from content the principal pasted, uploaded or forwarded or taken from free-text chat that can carry such content, or a value that merely equals a system-of-record field the principal did not select. A type check never makes it trusted. | A-06, T-02, S-05 |
| model-influenced process | A process that executes, interprets or loads model-chosen code, commands, modules or file contents, or whose control flow the model can direct beyond selecting a registered operation with schema-validated arguments. | T-05 |
| redirecting value | A stored value that decides where later communications, account recovery, credentials or funds go. | A-25 |
| bulk modification | One operation or plan that changes more objects than a count the register sets for it, or more than one object where the register sets none. | A-10 |
| requester | The principal on whose behalf the run proposes an effect, and any human who started or supervises the run. Neither may be one of the two approvers under dual control. | A-14 |
| step-up authentication | Fresh re-authentication of an approver at approval time, as A-12 defines it. | A-14, A-12 |
| fresh re-authentication | A user-verifying gesture an agent cannot perform, made for the action and values the person saw: a confirmation on a separately enrolled device that displays the action and each material value with provenance from server data, with number matching or entry of a value shown only on the application's surface; a WebAuthn variant that displays the transaction (for example Secure Payment Confirmation); or a WebAuthn assertion with userVerification required against a server-stored random challenge bound to the exact action and values, started only from the application's preview, with the residual risk recorded. Passwords and fillable or readable one-time codes do not count. | A-12 |
| impact threshold | The value, recorded in the register for each operation that moves funds or grants access, at or above which a confirmation needs fresh re-authentication where the principal's browser can be agent-driven; at Level 3 it is the A-14 dual-control threshold. | S-05, A-12, A-14 |

## Capability profile

S-02 requires a capability profile in the security record. The profile decides which controls apply and which level is required.

### Agent contexts

Profile each agent context separately, not the application as a whole. An agent context is one model context or session configuration, together with its tool set: an agent, subagent, planner, quarantined reader or triggered worker. The record also states the union across contexts.

### Capability properties

The three properties follow Meta's Agents Rule of Two and Simon Willison's lethal trifecta, which are related work, not part of the framework basis. Property names are words; U, D and X are abbreviations for tables and formulas, never control IDs. The property abbreviation D (sensitive-data) shares its letter with the Demonstrated Defenses pillar, but it never carries a hyphen and serial, so it cannot be read as a control ID such as D-01.

**untrusted-input (U).** The context can contain content not authored by the authenticated principal in the current task or by reviewed trusted configuration. Examples:

- retrieved documents, web pages and search results;
- inbound email, calendar items, tickets and chat from other people;
- uploads, and third-party text the principal pastes or forwards, including a free-text principal turn whose pasted spans the client does not mark (see Terms);
- images, audio, OCR output and transcripts;
- tool results, within the field rule below; MCP tool results, resources, prompts and sampling results from any server; and MCP or remote-agent descriptors (server instructions included) unless they are reviewed and pinned with T-18 implemented-and-verified for that server (see rule 4 below);
- peer-agent messages;
- memory written from a tainted context;
- client-supplied history and client-executed tool results;
- repository content from outside contributors;
- in multi-principal or multi-tenant systems, other principals' input.

Field rule. Any free-text field authored by a party other than the current principal is untrusted-input, wherever it enters a context, including free text inside system-of-record records (names, addresses, delivery notes, comments). A field that an application adapter reads from the application's own system of record is not untrusted-input when its type is closed: an identifier the application generated, a number, a boolean, a timestamp, or a member of a closed enumeration the application defines (a status, a payment-method type). Such a field does not taint the context whoever chose its value, because it cannot carry instructions; where another party chose the value (a customer's payment-method choice, a delivery date, a quantity), it is untrusted-derived when it feeds a consequential argument (S-05, A-06). Any string field another party chose (a display name, username, email address, external or invoice reference, SKU label) is free text whatever its format validation, and reaches a privileged context only by opaque reference. Results from MCP servers and other third-party tools remain untrusted-input in full. The rule is the one T-01 and T-02 state. A context that receives only such typed fields from an order lookup does not become untrusted-input through that lookup; a context that receives the order's delivery note does. A typed field is still the value the record holds: whether it is a trusted source for a consequential argument is decided by S-05 and A-06 (for example an order identifier matches only within the orders of the case requester).

In a multi-tenant system every principal is also a potential attacker against the other tenants, even where a principal's own input is not untrusted-input for that principal's own context; T-27 applies that to code execution.

**sensitive-data (D).** The context, or a tool it can invoke, can read, or receives in its input, data an attacker should not obtain, or can reach systems an attacker should not control. Examples: another principal's or tenant's data, confidential or regulated data, secrets, payments, identity, production infrastructure, internal networks and admin APIs. The principal's own conversation and task content count as sensitive-data unless the record shows that each of the following holds (S-02):

- the principal is anonymous;
- the conversation is not retained and no memory is written from it;
- no tool or retrieval the context can invoke reads non-public data;
- the context receives no data of other principals.

**external-effect (X).** The context can change state or send information beyond the session. Examples:

- writes, sends, payments, publication, provisioning, and code execution with side effects;
- pull request, issue and comment creation;
- any request whose URL, host, path or query the model chooses, including search and fetch, unless every request goes to a fixed URL or to a host-and-path entry that a trusted operator set in configuration, T-12 is implemented-and-verified in allowlist mode, and no allowed entry is an open redirect, a content proxy, a user-content or shared-hosting domain (for example a private suffix on the Public Suffix List), an endpoint whose GET requests change state, or a host that accepts writes under a credential the request supplies, unless T-12 confines it to the operator's account or to read-only methods. A path or query segment the model chooses always makes the request external-effect, because it can carry data;
- a client that renders model output and auto-loads remote content or unfurls links, unless T-13 is implemented-and-verified.

The last two exceptions reward the cheap fixes: a retrieval chat with verified inert rendering does not count as external-effect through its renderer.

### Autonomy scope

The four scopes paraphrase the AWS Agentic AI Security Scoping Matrix (November 2025), which is related work, not part of the framework basis.

In this table, a consequential action is a call to an operation registered as consequential under S-05, or any call that makes the context external-effect (for example a search or fetch whose query or URL the model chooses). A read that is neither, such as a lookup by identifier in the application's own data, is not a consequential action.

| Scope | Name | Meaning |
|---|---|---|
| 1 | No agency | A human starts a fixed workflow. The model only produces content that a human acts on, and proposes no tool call. |
| 2 | Prescribed agency | The model gathers information and selects among predefined actions. Every consequential action runs only after explicit human approval of that action. |
| 3 | Supervised agency | A principal starts an interactive run. At least one consequential action runs without per-action approval, the run ends within a maximum duration recorded in trusted configuration, and the principal can stop it while it runs (N-06). |
| 4 | Full agency | Runs start from events, schedules or monitoring; or a run continues after the principal's session ends or beyond its recorded maximum duration; or no human can stop it while it runs. Every context with the triggered-runs tag is scope 4. |

A context whose actions fall under different scopes takes the highest of them. Cases that are easy to misclassify:

| Situation | Scope |
|---|---|
| Chat over retrieval the application performs; the model calls no tool | 1 |
| The model calls read-only lookups over the application's own data without approval, and every consequential action needs per-action approval | 2 |
| The model composes web search queries without approval | 3 or 4 (a model-chosen query is a consequential action here) |
| A principal starts a run that works for hours with a stop control, within its recorded maximum duration | 3 |
| The same run continues after the principal closes the session, or has no recorded maximum duration | 4 |

### Evaluation rules

1. Fail-safe. A property whose presence is unknown MUST be recorded as present. Treat an unknown feature tag the same way, and record the highest autonomy scope that cannot be ruled out.
2. Propagation. A context that consumes output of an untrusted-input context MUST be recorded as untrusted-input. Summaries, memory, embeddings and delegation do not remove the property. The only exception is output that crosses a separation boundary verified under T-02 as typed, validated values or opaque references; those values stay untrusted-derived, carry their provenance to the dispatcher, and A-06 and A-07 check every consequential argument derived from them. Content passed by opaque reference stays untrusted wherever it is dereferenced: an effect that carries it, or a renderer that shows it, applies A-24, T-13 and T-14 as for a tainted context (T-02). Likewise, a context that receives in its input data an attacker should not obtain (a summary of order data, recalled memory, a delegated message) MUST be recorded as sensitive-data, even when none of its own tools can read that data, so a context that reads untrusted input and sensitive data cannot hand a summary to an effect-only context recorded with two properties.
3. Separation credit. A property counts as removed from a context only when T-02 is implemented-and-verified for that context. Unverified separation earns nothing.
4. Descriptor trust. Reviewed, hash-pinned MCP and remote-agent descriptors are trusted configuration, and so do not by themselves make a context untrusted-input, only while T-18 is implemented-and-verified for that server or agent. Otherwise they are untrusted content (T-01). Results from every server stay untrusted in either case.
5. Absence. A property is absent only when the capability is architecturally absent, or removed under rule 3. Filters, guard models, prompts and approvals are controls; they never make a property absent.
6. Feature tags from the applicability vocabulary are recorded per context, with the profile.

Derived values per context: n is the number of U, D and X present after separation credit, and the context is a trifecta context when n is 3. A trifecta context MUST satisfy A-08 at Level 1.

### Profile record

The record holds one row per context, followed by a union line and a level line. Each property cell says present or absent, with the source, tool or renderer that justifies it. Example (worked example 2 below):

| Context | untrusted-input (U) and source | sensitive-data (D) and source | external-effect (X) and source | Separation pattern, removed property, T-02 status | Autonomy scope (1-4) | Feature tags | n | A-08 option, if n is 3 | Computed level |
|---|---|---|---|---|---|---|---|---|---|
| support-agent | present: ticket thread, help-center search | present: order lookup across tenants | present: refund, send_email, helpdesk renderer | none | 3 | tools, retrieval, approvals, multi-tenant, rendered-output, provider-routing | 3 | (a) per-refund confirmation | 3 |

Union: U, D, X; tags as above. Levels: computed 3, declared none, selected 3.

The record template, [agent-security-record.md](../assets/agent-security-record.md), carries this table with the same columns.

### Missing facts

Ask only for facts that change a consequential design decision: tenancy, identity source, which operations change state, move value or send externally, approval thresholds, data classes and approved providers, and the owner. Continue independent work while waiting. Without an answer (as in a non-interactive run), apply these fail-safe defaults and record each as an assumption in the register's assumption table:

- unknown properties are present, and unknown data takes the most restrictive class;
- deny by default;
- identity and tenant come only from the authenticated session;
- retrieval is filtered per tenant, with a system-of-record recheck;
- no egress beyond destinations fixed in trusted configuration;
- only providers approved for the data class, with synthetic data until the data policy is confirmed;
- readiness is at most confined-prototype.

Keep bounded operations within the caller's authority working: confirm only where A-06, A-07, A-08 or A-10 require it, and deny, confine or confirm an operation whose rule depends on an unknown fact.

## Applicability

### Vocabulary

`applies_when` uses a closed vocabulary. No other token is valid.

| Token | Matches when |
|---|---|
| all | Always: every agent or LLM application in scope. |
| untrusted-input, sensitive-data, external-effect | The capability property holds in the context, as defined above. |
| tools | The model proposes calls that the application executes. |
| retrieval | Indexed, searched or stored content enters model context, or a stored model response is served in place of a model call (a response, prompt or semantic cache). |
| memory | State persists across turns or sessions and is recalled into context. |
| delegation | An agent invokes subagents or workers inside the system. |
| inter-agent | Messages cross a process, network or trust boundary to other agents (for example A2A). |
| queued-work | Asynchronous jobs, schedules, retries, callbacks or resumable workflows. |
| triggered-runs | Runs start from events or senders rather than an authenticated principal in session. |
| shared-context | More than one principal participates in or can view a conversation, channel or thread. |
| multi-tenant | One deployment serves more than one tenant data boundary. |
| approvals | A human approval or confirmation gates some actions. |
| code-execution | Model-generated or untrusted code, commands, notebooks or dependency installs run. |
| browser-agent | The agent operates a browser or computer-use environment. |
| coding-agent | The agent reads or writes repositories, runs in CI, or executes developer commands. |
| mcp | The system acts as an MCP client, host, server or proxy. Which properties and other tags an MCP integration adds is described in [mcp.md](mcp.md#profiling-an-mcp-integration). |
| provider-routing | Data is sent to any external inference, embedding, reranking, evaluation, telemetry, tracing or crash-reporting service, or to a remote tool server outside the application (a remote MCP server, a remote agent, or a third-party API that receives tool arguments). |
| provider-executed-tools | Tools run on the model provider's infrastructure (hosted search, fetch, code execution, remote MCP connectors, managed runtimes). |
| client-conversation | A client submits or holds conversation state, or executes tools. |
| rendered-output | Model output is rendered in a UI, chat platform, console, report or export. |
| network-egress | Network requests are made whose scheme, host, port or path the model can choose, or that a model-influenced process makes (fetch, browse, webhooks, callbacks, sandbox network, calls to remote MCP servers or remote agents, and fetches of URLs a server supplies). An adapter that calls a fixed host and path set in trusted configuration, with model-chosen body fields, query parameters or other arguments (an email, payment or search API, for example), is provider-routing, not network-egress; its payload falls under A-24 and its recipients and other arguments under S-05 and A-06. |
| model-artifacts | The system loads self-hosted weights or adapters, or fine-tunes models. |
| separation-pattern | The design claims that separation removes a capability property from some context. |

### Grammar

```text
applies_when = alternative *( "," alternative )   ; list items are alternatives (OR)
alternative  = token *( "+" token )                ; all tokens hold in the same context (AND)
token        = an entry of the vocabulary above
```

For example, `["rendered-output", "tools"]` matches a context with either tag, and `untrusted-input+external-effect` matches only a context that holds both properties.

- A control is applicable to the system when at least one of its alternatives matches at least one agent context in the stated scope, using the profile after separation credit.
- Applicability comes from the profile alone; the selected level then decides which applicable controls are required (Levels 1 through N). Many Level 1 controls are conditional on capability properties (for example A-06, A-07, A-08 and D-04); they bind whenever their condition holds, whatever level is claimed.
- A control whose `applies_when` matches no context is recorded as not-applicable-with-reason, and the reason names the absent capability ([conformance.md](conformance.md)).

## Levels

### Semantics

- Every control has exactly one level: 1, 2 or 3.
- Level N requires every applicable control of Levels 1 through N.
- Higher levels only add controls. No level removes or relaxes a lower-level control, so every level includes the applicable critical-boundary controls listed in [conformance.md](conformance.md).

### Selection rule

Compute a level for each agent context from its n and autonomy scope, after separation credit:

1. Level 3 if n is 3, or if autonomy scope is 4 and external-effect is present.
2. Otherwise Level 2 if n is 2, or if autonomy scope is 3 or 4.
3. Otherwise Level 1.

Then:

- The system's computed level is the maximum over all contexts in the stated scope.
- The selected level is the higher of the computed level and the owner-declared level. An owner may declare a higher level, never a lower one.
- A claim below the computed level is invalid. There is no "required level not met" wording.

The rule rewards injection-resistant architecture: a verified T-02 separation that keeps every context at two properties or fewer lowers the computed level (example 3 below).

### What each level adds

Level 1, the enforcement baseline (61 controls, most of them conditional):

- accountable scope, profile, Least Agency, threat model, consequential operations register and data policy: S-01 to S-06;
- one dispatch path, deny by default, authority from trusted context at the moment of effect, idempotency, tool profiles and the destructive-operation guard: A-01 to A-05, A-09, A-10;
- untrusted content and consequential choices (provenance-aware values, task-scope binding, Rule of Two gating, outbound payload checks, verified changes to redirecting values, taint, enforced separation, system of record): A-06, A-07, A-08, A-24, A-25, T-01, T-02, T-08;
- approval binding and presentation integrity: A-11, A-12;
- delegation, tokens, principals and triggers, budgets, deadlines and no self-modification: A-15, A-16, A-19, A-20, A-21, A-23;
- disclosure boundaries for prompts, retrieval, memory, conversation state and providers: T-04, T-06, T-07, T-09, T-10, T-11;
- execution, egress and rendering boundaries, including per-tenant kernel isolation for code execution: T-05, T-12, T-13, T-14, T-15, T-17, T-27;
- MCP, inter-agent, coding-agent and supply-chain boundaries: T-18 to T-21, T-23, T-24, T-25;
- verification discipline and the release gate: D-01 to D-07;
- audit, baseline signals, stop without deploy and governed change: N-01, N-02, N-04, N-06, N-09.

Most agents that read web content compute to Level 3 (worked example 4). An agent that reads search results or web pages (untrusted-input), holds the principal's conversation (sensitive-data unless the record shows the four conditions above) and chooses its own search or fetch queries (external-effect) has all three properties. That follows from the lethal trifecta and is deliberate. The ways to a lower level are architectural: a separation verified under T-02, fetches limited to fixed destinations behind a verified egress boundary (T-12 in allowlist mode), or a conversation that meets the four conditions for non-sensitive content. Such an agent still works without a confirmation for every read: under any A-08 option, a read-tool request that A-06 allows without confirmation (a URL that satisfies A-06 conditions (i) to (iii), or a query or URL that matches a trusted source, such as a principal-entered value or a query composer's output) is not a consequential effect, so it needs no confirmation within the caps A-06 sets, and under option (b) an unattended agent can make it without a fixed destination. A confirmation never authorizes a value that A-06 denies, so a query or URL that a tainted context composed or modified is not sent on confirmation.

Level 2 adds depth for systems with two risky properties or supervised autonomy (12 controls):

- approval anomaly cues and fatigue management: A-13;
- workload identity and token exchange: A-17;
- principal, tenant and provider quotas: A-22;
- hidden-text normalization: T-03;
- strong isolation tier: T-16;
- fault-propagation containment: T-22;
- agent-to-human communication integrity: T-26;
- live-model adversarial evaluation: D-08;
- forensic context manifest, behavioral detection, kill-switch scopes with measured latency, quarantine and exercised recovery: N-03, N-05, N-07, N-08.

Level 3 adds, for trifecta or fully autonomous effectful systems (5 controls):

- step-up and dual control: A-14;
- sender-constrained tokens: A-18;
- independent adversarial review with adaptive attacks: D-09;
- replay before rollout and before authority expansion: D-10;
- tamper-evident audit: N-10.

Counts in catalog v0.1:

| Pillar | Level 1 | Level 2 | Level 3 | Total |
|---|---|---|---|---|
| S Scope & Stewardship | 6 | 0 | 0 | 6 |
| T Trust & Isolation | 23 | 4 | 0 | 27 |
| A Authority & Access | 20 | 3 | 2 | 25 |
| N Notice & Neutralize | 5 | 4 | 1 | 10 |
| D Demonstrated Defenses | 7 | 1 | 2 | 10 |
| Total | 61 | 12 | 5 | 78 |

### Worked examples

The counts below are computed from catalog v0.1 for the stated contexts and tags. Different tags give different counts; recompute them for a real system.

**1. Public product-docs assistant.** One context.

- U present: retrieval over public documentation, counted conservatively.
- D absent: no accounts, secrets or other principals' data are reachable, and the record shows the four conditions for a non-sensitive conversation: the principal is anonymous, conversations are not retained and write no memory, the retrieval reads only public documentation, and the context receives no other principal's data (otherwise D is present, n is 2, the computed level is Level 2, and S-06 and T-10 apply).
- X absent: there are no tools, and the client renders output inertly, with T-13 implemented-and-verified.
- Autonomy scope 1. Tags: retrieval, rendered-output, provider-routing.
- n is 1, so the computed level is Level 1, with 15 applicable controls: S-01 to S-04, T-01, T-04, T-06, T-13, T-14, T-24, D-01, D-03, D-06, D-07, N-09.
- If T-13 were not yet implemented-and-verified and the client auto-loaded images, the renderer would count as external-effect, n would be 2, and the computed level would be Level 2.

**2. Multi-tenant support agent.** One context. A support representative starts the agent on a ticket. It reads the ticket thread and help-center search results, looks up orders, issues refunds and sends customer emails; refunds above a threshold need the representative's approval. Help-center queries come from the ticket's intent (an enumeration the application maps to a query) or from a query composer that receives only the representative's turns from a structured field or paste-marked channel (A-06); a query the tainted context composes is denied (A-06). The ticket the representative opens is designated (A-06), so values in it are confirmed with their origin, never matched. Customer emails go to the case requester's verified address on record, which the email adapter fills (S-05).

This example illustrates profiling only; its design must still satisfy A-08 and A-10. With the representative present, A-08 option (a) means each refund the agent proposes after reading the ticket, below the threshold too, is confirmed by the representative (one plan-level confirmation may cover several fully bound refunds). Unattended refunds below a threshold need option (c), as in example 3, or option (b): the refund operation, payee and amount are fixed by trusted configuration (for example a rule that refunds exactly the system-of-record order total to the original payment method), and the order is selected by a trusted link outside the model's control (the case record, not an order named in the ticket text). An amount merely bounded by the order total is not fixed. A-10 is met by the dry-run approval, or by its option (c) rule where that option is allowed. At Level 3, refunds at or above the A-14 impact threshold also need dual control: step-up approvals by two distinct authorized humans, neither of them the representative who started the run, who is the requester.

- U present (ticket thread, search results), D present (order data across tenants), X present (refunds, emails, helpdesk renderer). It is a trifecta context, so A-08 binds.
- Autonomy scope 3. Tags: tools, retrieval, approvals, multi-tenant, rendered-output, provider-routing.
- n is 3, so the computed level is Level 3: 45 applicable controls at Level 1, 55 through Level 2 and 60 through Level 3.
- The other 18 controls are not applicable because their tags are absent: A-15, A-19, T-02, T-07, T-09, T-11, T-12, T-15, T-16, T-17, T-18, T-19, T-20, T-21, T-22, T-23, T-25, T-27.
- The email API and the payment provider are fixed hosts set in trusted configuration that receive model-chosen arguments, so they are provider-routing, not network-egress, and T-12 is not applicable. The recipients and amounts the agent chooses are consequential arguments under S-05 and A-06, and the email bodies pass A-24.

**3. The same support agent with enforced separation.** Two contexts, using a plan-then-execute or dual-model pattern under T-02 (option (c) of A-08).

- Ticket reader: the application places the ticket thread and help-center results in its context. It has no tools and returns only typed, validated values (an order ID, an intent from a fixed list, an opaque reference to the ticket text). U present, D present (the ticket can hold personal data), X absent. Tags: retrieval, multi-tenant, provider-routing, separation-pattern.
- Planner: receives only those values and trusted configuration, looks up orders, issues refunds and sends emails. Its order lookup is an application adapter over the application's own system of record that returns typed, application-validated fields only: the order ID, status, order total, refundable balance, payment-method type and timestamps. The order's free-text fields (customer name, shipping address, delivery notes, comments) never reach the planner's context; where an email needs them, the email adapter fills its template from the system of record, and the planner handles at most an opaque reference to the field (T-02/C7). The adapter also fills the recipient from the case requester's verified address on record, because a customer-chosen email address is free text under the field rule. Under the field rule above, these closed-type fields do not make the planner untrusted-input, even though the customer chose the payment-method type and customer actions set some statuses and timestamps; such a value is untrusted-derived only where it feeds a consequential argument (A-06). D and X present; U absent by separation credit, because T-02 is implemented-and-verified. Tags: tools, approvals, multi-tenant, rendered-output, provider-routing, separation-pattern.
- Both contexts are autonomy scope 3 with n of 2, so the computed level is Level 2: 45 applicable controls at Level 1 and 55 through Level 2.
- The level depends on the lookup staying typed. If the planner's order lookup returned the delivery note or any other free text a customer wrote, or if the planner called an MCP server or another third-party tool, the planner would be untrusted-input, n would be 3, A-08 would bind and the computed level would return to Level 3.
- A-08 no longer applies, because no context holds all three properties. A-06 and A-07 still apply, per value, through their `separation-pattern+external-effect` alternative: the order ID is still the ticket author's choice, so a ticket naming another customer's order is caught at dispatch, where the value arrives labelled untrusted-derived and is denied or confirmed with its origin shown. It matches the system of record only among the case requester's orders (S-05); that the order exists is not a match.
- A-24, T-13 and D-04 also still apply, through their `separation-pattern` alternatives. The planner never reads the ticket text, but it places the reader's opaque reference in customer emails and helpdesk replies, so that text reaches a recipient and a renderer: the payload check treats it as untrusted content with the reader's data classes, the helpdesk renderer stays inert, and the injection fixtures cover the reader's channels.
- T-02 now applies, and the level rests on it: if T-02 is not implemented-and-verified, the planner is untrusted-input by taint propagation and the system returns to Level 3.

**4. Open-web research agent.** One context. A signed-in user asks questions in free-text chat; the agent searches the web through a search API, fetches pages, keeps a per-user memory of past research and answers with citations. It sends nothing and buys nothing.

- U present: search results and fetched pages, and every free-text chat turn whose pasted spans the client does not mark (see Terms). D present: the principal's conversation and memory, because conversations are retained and memory is written, so the four conditions for a non-sensitive conversation do not hold. X present: the agent chooses its search queries and the URLs it fetches.
- Autonomy scope 3: the principal starts each run, searches and fetches run without per-action approval within a recorded maximum duration, and the principal can stop the run (N-06).
- Tags: tools, retrieval (search results and fetched pages enter the context), rendered-output, provider-routing (the search API is a fixed host set in trusted configuration that receives a model-chosen query, so it is provider-routing, not network-egress; see the network-egress row in the vocabulary), network-egress (the fetch tool requests model-chosen URLs), memory.
- n is 3, so the computed level is Level 3: 45 applicable controls at Level 1, 54 through Level 2 and 58 through Level 3.
- The other 20 controls are not applicable because their tags are absent: T-02, T-09, T-11, T-15, T-16, T-17, T-18, T-19, T-20, T-21, T-22, T-23, T-25, T-27, A-11, A-12, A-13, A-14, A-15, A-19.
- A-08 binds. The only effects are reads that A-06 allows without confirmation (a URL from a public result within the caps, a principal-entered URL, a query composer's query), which are not consequential effects under any option ("What each level adds" above), so the record names option (b): no other effect is reachable. The agent offers no confirmations: a URL that occurs only in content the principal pasted is denied rather than confirmed, so the context has no approvals tag. Offering confirmations would add that tag, and with it A-11, A-12 and, at Level 2, A-13.
- Queries: the tainted context never writes one. Follow-up searches come from a query composer that receives trusted configuration and the principal's turns with the client-marked pasted spans removed; where the client cannot mark them, the composed query waits in a structured query field for the principal to submit (A-06).
- T-12 mode per tool: the search tool is provider-routing to a fixed host, governed by T-10, A-06 and A-24 rather than T-12; the fetch tool runs in public-internet mode, and because the context holds sensitive-data, the proxy admits only a URL the dispatcher authorized for that request.
- A-06 exemption in the record: L of 8 links per retrieved item, a per-run cap of 3 and a daily cap of 30 give a per-run bound of 3 x log2(9), about 9.5 bits, under an owner ceiling of 10 bits set below the lowest-entropy secret class the data policy lists for conversations (a six-digit one-time code, about 19.9 bits). The daily bound (about 95 bits) and the total over the conversation retention period are recorded as residual risk the owner accepts (S-01).
- T-06 applies through the retrieval tag. Its cases run against the per-user memory index and any response, prompt or semantic cache; a case whose subject is absent is recorded not applicable with the verifiable absence.

### Levels in other frameworks

OWASP AISVS 1.0 also has Levels 1 to 3, with a different meaning: there, a level is an assurance depth the organization selects, and AISVS Level N assumes ASVS Level N in parallel. Here, the level is computed from the capability profile and is a minimum. The scales are not interchangeable. For example, approval binding (A-11) is Level 1 here, while the AISVS requirement it partly corresponds to, v1.0-C9.2.8, is Level 3 in AISVS. A level claim therefore always names the catalog and its version ("Level 2 of STAND v0.1"), never a bare "Level 2".

## Change triage

N-09 requires changes to be triaged; this section defines the tiers. Its instructions apply to whoever makes the change, human or coding agent.

Classify every task before doing security work, from the task-owned diff rather than the wording of the request. Record the tier and a one-line reason in the final report.

- A tie between two tiers resolves to the higher tier.
- Escalation only goes upward. If the work reveals a profile change, reclassify upward, say so in the report and continue at the new tier; in an interactive session, tell the user before expanding the work.

### Trigger locations

A trigger location is code or configuration that implements or feeds a control:

- tool dispatcher, tool registry or schemas;
- consequential operations register, consequential-argument validation and destination policy (allowlists), including code that computes a consequential fact or argument the register relies on (a price, refund eligibility, limit, payee or recipient);
- authorization, policy or identity code;
- credential broker, secret configuration and token handling (issuance, exchange, storage, logging);
- effect adapters, including the content they send;
- outbound message, comment and document content;
- timeout, retry or idempotency handling;
- approval store or approval UI;
- retrieval filters, indexes or caches;
- memory store;
- prompt assembly and system prompts;
- client conversation API, and rendering of model output (UI, consoles, exports, chat integrations);
- model, provider, routing, telemetry or tracing configuration;
- provider-executed tool settings;
- agent-framework version;
- sandbox or code runner;
- egress proxy, network policy or URL fetch;
- separation-pattern boundaries (reader and planner contexts and the typed values and references between them);
- MCP or A2A configuration;
- subagent, queue, trigger or webhook entry points;
- browser runtime;
- CI workflows, and instruction or rules files used by coding agents;
- audit, monitoring, stop and revocation mechanisms;
- budgets and quotas;
- dependency manifests, skills, plugins and model artifacts;
- security tests and policy files.

Prompt, model, provider and agent-framework version changes are always trigger locations, never NONE.

### NONE

The diff touches no trigger location. Examples: copy (user-facing text in static pages and UI labels that never enters model context and is not the content of a message, email, comment or document an effect sends), styling, static documentation, comments, non-security tests and unrelated business logic. Business logic is unrelated only when it is not reachable from a tool handler, effect adapter, retrieval, prompt assembly or rendering path, and is not a source of a consequential fact or argument that the S-05 register names. Tool descriptions, schemas, prompts and outbound templates are not copy. Documentation that is also a retrieval source is still NONE when only its text changes: retrieved content is already untrusted input. A change to what is indexed, how it is filtered or who may retrieve it touches a trigger location.

- Do not load the catalog, write a record or add security tests.
- The only obligation is not to weaken an existing control or test.
- If the diff turns out to touch a trigger location, upgrade the tier.

### SCOPED

The diff touches one or more trigger locations, and the capability profile is unchanged: no new property in any context, no change in which contexts are trifecta contexts, no autonomy increase, no new feature tag (for example a first MCP server, browser, code execution, triggered runs or provider-executed tools) and no new entry point.

- Select controls with the routing table in [SKILL.md](../SKILL.md): touched locations to control IDs, filtered by `applies_when` and the selected level. Select rows by the concern the diff changes, not by the file it is in: a timeout change inside an effect adapter uses only the timeouts row. For the MCP row, route the IDs whose concern in the [mcp.md control map](mcp.md#control-map) the diff touches, always keeping the row's critical-boundary IDs.
- A control is touched when the diff changes the code or configuration that enforces it. Always include any touched critical-boundary control.
- In a context with untrusted-input and external-effect, add T-01, A-06, A-07 and D-04 (and A-08 in a trifecta context) only when the diff changes consequential arguments or destinations, prompt assembly, an untrusted-input channel or the dispatcher. Changes confined to timeouts, retries, budgets, audit or stop mechanisms do not add them.
- A diff that adds or alters an operation setting a redirecting value (A-25), through a tool, an effect adapter or an MCP server, also routes the "Consequential arguments or destination policy" row, whether or not code enforcing A-25 exists yet.
- A wording-only change to prompt, tool-description or outbound-template text (no change to inputs, offered tools, arguments, recipients or assembly) does not add the untrusted-input and external-effect set above. It keeps its row's controls, plus T-01 and T-04 for prompt and tool-description text, verifies the row's critical-boundary controls by re-running their existing cases, and lists D-10 as a release prerequisite where it applies. Where those controls have no existing cases, a wording-only change builds no test harness: record each one as implemented-but-unverified (or failing, if the baseline records it failing), name the cases that did not run, and report the missing cases on a "Finding:" line.
- Drop a routed control whose subject the touched operation lacks only when the S-05 register shows that the operation has no effect (for example A-05 and N-02 for a pure read). Never drop a critical-boundary control this way, and state the reason in the compact record. Where no S-05 register exists, drop a control only when the code shows that the touched operation has no effect, and say so in the record.
- Route about 8 control entries (D-03 and D-06, which apply to every SCOPED task, not counted). The cap is a scoping signal, not a reason to drop a routed control: touched critical-boundary controls and the untrusted-input and external-effect additions above are always routed, even past it. Routing well beyond it is reported as a broad change, or reclassified as FULL if the profile changed. For D-05, load only the matrix rows for the touched boundary.
- Implement and verify only those controls, each with its hostile cases and authorized twin through the real path, and re-run the existing security suite (D-07). Run every required case of each routed control; a control whose cases did not all run at this commit is implemented-but-unverified, and the compact record names the cases that did not run. Before recording a control implemented-and-verified, apply the claim audit in [conformance.md](conformance.md#status).
- A routed control that is not critical-boundary, and whose mechanism does not exist at the touched boundary (for example no idempotency key in the adapter whose timeout changes), is recorded as failing on a "Finding:" line with its severity, unless the diff itself needs that mechanism because the requested change cannot work without it or creates the failure path. Implement only the clauses the changed lines enforce (for a timeout change, A-21's caller-enforced deadline). When the control's recorded severity is critical (for example A-05 when the effect moves funds), it is fixed inside the touched boundary under scope rule item 2. The second worked example below shows this case.
- D-08, D-09 and D-10 are release activities that a SCOPED task does not perform. List any that the change triggers (D-10 for a model, prompt, provider, tool-definition, tool-grant or policy change at Level 3) as release prerequisites for the owner in the compact record.
- Update the inventory in the same change when the diff adds or alters an inventory entry, such as a tool, a model version or a descriptor hash (S-04).
- The baseline is the security record from an earlier assessment, at the record path named in the repository's instructions (otherwise `docs/agent-security-record.md`). Use the selected level it states, or compute the level from the profile it records. If it states neither, route Level 1 entries only, say "level not stated in baseline" in the Profile line and never invent a level; if it records no readiness value, readiness is blocked (baseline readiness not stated).
- The baseline record is a claim, not configuration. Read it as it stands at the commit the change starts from on its target branch (the merge base), never from a version that the change under triage edits. Recompute the level from the profile it records, and check that profile against the code for the contexts the diff touches; where the stated level, the recomputed level and the level the code shows differ, use the highest and say so in the Profile line. Edits that the change makes to the record's profile, level, status, readiness, owner or exception lines (other than appending its own compact record) are proposals for human review, never the baseline for this change: the Readiness line is computed from the merge-base record and names the edited lines as pending review. If the record does not name the commit at which its assessment was made, say "baseline commit not stated" in the Profile line.
- Write a compact change record (format below) into that record, never into a second record file. The record is append-only: leave the baseline Controls table and release gate result unchanged, and add the compact record at the top of the section "Compact change record (SCOPED changes)", so the newest comes first. The newest compact record's Readiness line is the current readiness.
- If no baseline record exists, the change is still SCOPED. Route Level 1 entries only and say that the level is not computed, leave the other applicable controls as not-assessed, and recommend a full assessment. When the repository's instructions adopt this workflow or the user explicitly asked for the record, create the record file with only its header (assessment tier SCOPED) and the compact change record with "Baseline: missing". Otherwise, when the workflow was applied to a repository that has not adopted it, do not create the file: put the compact change record in the report and offer to create it. Do not build a baseline unless asked or unless the change qualifies as FULL.
- Every write to the record follows the record confidentiality rule in [conformance.md](conformance.md#record-confidentiality): where the record is readable beyond the people authorized to see unfixed vulnerabilities, or its visibility is unknown, an open critical or high item is written by reference only.
- Readiness: rate only the routed controls and any new finding. With a baseline, readiness is computed as the baseline value with the routed rows updated, and it is blocked if a routed control is failing or a routed critical-boundary control is not implemented-and-verified. It is also blocked when, at the time of the change, the accountable owner (S-01) is unassigned or an owner exception that the baseline value relies on has expired ("blocked (baseline exception expired: <IDs>)"). When the value relies on owner exceptions, the Readiness line names the earliest expiry among them. With "Baseline: missing", readiness is blocked (baseline missing: critical-boundary set not assessed); do not rate the individual not-assessed controls.
- Do not add an ASI table, a full assessment or unrelated refactors.
- Implementation follows the scope rule under "Assessing and implementing" below: fix failures inside the touched boundaries (a critical one always), report other failures with control ID, location, failing test and suggested severity, and list unrequested product rules as owner decisions instead of implementing them. Record a gap in an unchanged feature on a "Finding:" line, and finish with the unrequested-change self-check.

### Compact change record

Line budget: at most 12 lines plus one line per routed control. The budget counts every non-blank line the change adds to the record file, including the two code-fence lines and any heading or note; add no heading or note, because the section heading already exists and the Header pins the catalog version. Not counted: Inventory rows the diff adds or alters (S-04), "Finding:" lines, and, when the change creates the record file or the section, its Header and the section heading. If an existing record lacks this section, add its heading at the end of the file; that heading is not counted.

Each routed control takes one line, including a control dropped with its reason; the touched D-05 rows share one line, and controls with the same status and evidence scope may share one. D-03 and D-06 take no line of their own: the "Tests run" and "Readiness" lines record them. The other lines, with the two fences, fit in the 12:

- "Change:" with the change ID (the pull request, ticket or commit reference, or "none") and a one-line description;
- "Tier: SCOPED" with the reason, then "locations:" with the trigger locations touched, on the same line;
- "Profile: unchanged" with the reason, followed on the same line by "Baseline: missing (full assessment recommended)" only when there is no baseline;
- "Tests run:" with the tests actually run and their results;
- "Residual risk:" with new or changed residual risks, severity and owner or "unassigned", or "none new";
- "Finding:" only for a gap found in a pre-existing, unchanged feature (scope rule item 2), one line each with control ID, status, severity, location, failing test or "none" and suggested fix; where record confidentiality applies to an open critical or high finding, the private reference replaces the location, failing test and suggested fix; these lines are outside the budget, so a finding is never compressed or dropped to fit;
- "Release prerequisites:" only when the change triggers D-08, D-09 or D-10;
- "Owner decisions:" only when product rules, flows or thresholds are proposed and not implemented, or a minimal mechanism was built for a critical boundary;
- "Readiness:" with one value of the readiness enum and its basis, including the earliest owner-exception expiry it relies on, if any;
- "Approver:" with the name a human provided, or "unassigned" (N-09);
- the literal line "Other controls: not re-assessed (outside change scope)".

### FULL

FULL applies to:

- a new agent application or a new agent context;
- a new entry point (a request route, job, queue consumer, callback or trigger that starts or resumes runs), even when the capability profile is unchanged;
- any capability-profile change;
- an increase in computed level;
- a new principal type or tenant model;
- replacement of an enforcement component (dispatcher, policy engine, identity provider, approval service, sandbox technology);
- a change that adds external-effect when no baseline exists;
- an explicit request for an assessment.

Action: compute the profile and level (S-02), complete S-01 to S-06 where they apply, evaluate every applicable control at Levels 1 to N, build the ASI applicability table with architectural reasons for exclusions (S-04), and apply the release gate (D-06).

On an existing system, a FULL change assesses every applicable control but implements only within the scope rule below: it implements and verifies the controls whose enforcement boundary the change adds or alters and the critical-boundary controls whose enforcement path the new feature's calls traverse, re-runs the cases of carried-over rows, and records every other applicable control by inspection with its status and severity. Adding a first MCP server as a client, for example, implements T-18, T-19, T-20 and the dispatcher, credential and egress controls on the MCP call path (exposing one implements the controls in [mcp.md](mcp.md#exposing-an-mcp-server) "Exposing an MCP server" instead), and makes the new server and its tools disableable without a deploy (N-06) where a disable or stop path exists or can be added minimally; a missing system-wide kill switch is recorded as an open item rather than built.

A profile change re-assesses the whole system, not only the new feature, because a new property or tag can change which contexts are trifecta contexts and which controls bind, and the whole claim lapses when a FULL change lands without a new assessment ([conformance.md](conformance.md)). Re-assessing means recomputing every context's profile and level, re-running the cases of every carried-over row, and recording every other applicable control by inspection with its status and severity; implementation still follows the scope rule. A FULL change that adds an entry point but no property, tag or higher level verifies the new path and the carried-over cases on it, not the whole system. When the work expands well beyond the request, say so in the report and, in an interactive session, tell the user before re-assessing beyond the requested feature; in a non-interactive run, continue and report it. The whole-system re-assessment a profile change requires is part of the task, not an unrelated audit.

A scan, assessment, review or threat model without requested changes uses [scan-only execution](#scan-only-execution). The implementation and record-update rules in this section do not apply to that mode.

- When a record already exists, update it by control ID rather than starting a second one. A carried-over row keeps implemented-and-verified only if all its required cases re-ran and passed at the new commit at or above the minimum evidence scope. Isolated-runtime or deployed evidence that was not re-run becomes implemented-but-unverified. A newly applicable control enforced at a boundary this change adds or alters is implemented and verified in this change; any other newly applicable control is assessed by inspection and recorded as planned, failing or implemented-but-unverified, with its severity.
- Build order: the critical-boundary set first, then the remaining Level 1 controls, then Level 2 and Level 3. Controls that need people, production data, unapproved model spend or infrastructure the repository lacks follow the rule in "Assessing and implementing" below, in this tier as in SCOPED.

### Assessing and implementing

Assessing and implementing are different obligations. FULL assesses every applicable control and SCOPED every routed one; in both tiers, implementation stays inside the requested feature and the boundaries it creates or changes. This rule applies at the moment of implementation (Step 3 of [SKILL.md](../SKILL.md)):

1. Implement and verify the routed controls at the boundaries the change creates or changes, and the critical-boundary controls on the requested feature's call path. A mechanism such a control's MUST requires there (for example an A-20 budget or an A-21 deadline on a call the change adds) is not a product rule; take its values from existing configuration, otherwise use a documented placeholder recorded as an owner decision to confirm.
2. A gap in a pre-existing, unchanged feature is a finding, not a task. Record it (status failing or not-assessed, severity per the rubric in [conformance.md](conformance.md), location, failing test if any, suggested fix) and report it. Fix it only when the user asked, when the new feature makes it reachable, or when it is critical and inside a touched boundary. A routed control that is not critical-boundary and whose mechanism is missing at a touched boundary is handled the same way, unless the diff itself needs that mechanism (see SCOPED above).
3. The requested behavior, plus the smallest change needed to deliver it, is the task. Beyond that and the mechanisms item 1 puts in scope (an N-06 disable switch for a new tool, a T-24 version reference for a model the change adds), new user-facing flows, endpoints, confirmations, limits, caps, timeouts, circuit breakers, fail-fast paths, configuration switches, choosing or changing a model version, API or constructor changes, and behavior changes to existing features that the request did not ask for are product decisions. Build the minimal mechanism only when a critical-boundary control for the requested feature cannot otherwise be met, choosing the option that changes existing behavior least (for A-08, an existing approval step or option (b) before a new confirmation flow), and flag it as an owner decision. Otherwise list it as an owner decision and leave the gap open.
4. The release gate (D-06) then reports "blocked" honestly, naming the open IDs. Rewriting the application to pass the gate, or refactoring unrelated code, is out of scope.
5. In both tiers, controls whose evidence needs people, production data or unapproved model spend (D-08 live-model trials without an approved budget, the D-09 review, N-08 exercises, the D-10 replay corpus) are implemented as far as code allows and otherwise recorded as planned with the owner action needed; a coding agent never simulates a human reviewer or an exercise. Controls whose enforcement needs infrastructure the repository lacks (for example A-17 workload identity with token exchange, A-18 sender-constrained tokens, N-07 measured kill-switch scopes, N-10 tamper-evident audit storage) are implemented on the application side, behind an interface where code allows, and otherwise recorded as planned with the owner action needed; never provision infrastructure nobody asked for.

The scope rule does not authorize mechanisms because a control mentions them. Each of the following is out of scope unless the request names it or item 1 requires it on the requested call path, and is listed as an owner decision instead:

- a system-wide kill switch, global rate limiter or circuit breaker added while building a feature that needs only its own N-06 disable path;
- a deadline, retry policy or idempotency layer added to an existing call the change does not touch (record an A-21 or A-05 finding instead);
- a product rule the request did not state, such as a refund cap, eligibility window, approval threshold or allowed-domain list, chosen by the implementer;
- rerouting an existing workflow, for example moving the existing inline refunds behind a new queue, or replacing an existing lookup tool with a new one;
- disabling or removing an existing feature to close a gap (record the gap and its severity instead);
- a model, provider or framework version change, or a constructor or API signature change, that delivering the request does not need.

Unrequested-change self-check. Before verification, and again before finishing if the diff changed, list every behavior change in the diff that the request did not name. For each, cite the MUST clause and control ID that requires it on the requested feature's call path under item 1, or the critical-boundary control that item 3 builds a minimal mechanism for; anything else is reverted and listed as an owner decision. Report the list, including "none", in the final report.

For example, a request to queue refunds that are paid by a worker implements A-11 approval binding and A-04 time-of-effect checks on the new queued path. It does not add a customer confirmation endpoint, rewrite the existing lookup tool or change the existing inline refund path; the worker's new call to the payment provider gets an A-21 deadline, because the change adds that call, while a missing deadline on the existing inline call is recorded as an A-21 finding with its severity and a suggested fix.

### Invariants in every tier

1. Never weaken or remove an existing control, security test or CI security check without recording the reason and the affected control ID.
2. Never claim readiness or verification beyond the evidence actually produced.
3. Never fabricate owner acceptance.
4. A touched critical-boundary control is always in scope.

### Worked example: narrow timeout

Changing one adapter's timeout is SCOPED: it touches timeout and retry handling (inside the payments adapter) and leaves the profile unchanged. Only the timeouts row applies, so the adapter's other controls are not routed.

- Routing selects A-21 (caller-enforced deadline, bounded retries), A-05 (same idempotency key on retry, reconcile after an ambiguous timeout) and the D-05 rows "transport ignores its timeout" and "timeout after possible commit".
- The output is the deadline fix, every required case of the two routed controls (for A-21, a stalled-transport hostile test, the denial-retry case, the end-to-end deadline case and the transient-error twin; for A-05, the duplicate-delivery, timeout-after-commit and split-amount cases and the twin), and this record, 14 counted lines (12 field lines and two fences) against a budget of 15 for three routed controls:

```text
Change: CH-142, payments adapter timeout 30s to 10s
Tier: SCOPED (timeout and retry handling only); locations: timeouts and retries (payments adapter)
Profile: unchanged (no new tool, data source, renderer or autonomy)
A-21: implemented-and-verified, integration, A-21/C1 stalled transport abandoned at 10s, A-21/C2 denial not retried via fallback, A-21/C3 end-to-end deadline held, A-21/C4 twin pass
A-05: implemented-and-verified, integration, A-05/C1 duplicate delivery one effect, A-05/C2 timeout-after-commit reconciled, A-05/C3 split amount capped, A-05/C4 twin pass
D-05 (touched rows): implemented-and-verified, integration, "transport ignores its timeout" A-21/C1 and A-21/C3, "timeout after possible commit" A-05/C2
Tests run: pytest tests/security -k "A-21 or A-05": 8 passed
Residual risk: none new
Owner decisions: retry cap 3 to 2 proposed (not implemented)
Readiness: ready-within-scope (baseline value; routed rows re-verified, no new finding)
Approver: unassigned
Other controls: not re-assessed (outside change scope)
```

The baseline in this example has no open high, so the Readiness line names no exception expiry.

### Worked example: narrow timeout, no idempotency in the adapter

The same change in a helpdesk adapter that posts ticket replies and retries once on timeout, but sends no idempotency key and does not reconcile after a timeout. A-05 is routed, is not critical-boundary, and its mechanism does not exist at the touched boundary. The timeout change does not need it: the duplicate-reply path exists today, and a shorter timeout makes it more frequent, not new. The change therefore implements only A-21's caller-enforced deadline, runs every required case of both routed controls, and records A-05 as failing with a "Finding:" line rather than building an idempotency store. Because no funds move, A-05 keeps its default high severity; for a payments adapter its critical floor would apply, and the gap would be fixed inside the touched boundary. The repository is private, so the Finding line carries its details. This record has 13 counted lines against a budget of 15; the Finding line is outside the budget:

```text
Change: CH-311, helpdesk adapter timeout 30s to 10s
Tier: SCOPED (timeout and retry handling only); locations: timeouts and retries (helpdesk adapter)
Profile: unchanged (no new tool, data source, renderer or autonomy)
A-21: implemented-and-verified, integration, A-21/C1 stalled transport abandoned at 10s, A-21/C2 denial not retried via fallback, A-21/C3 end-to-end deadline held, A-21/C4 twin pass
A-05: failing, integration, A-05/C1 and A-05/C2 fail, A-05/C3: not applicable (a reply carries no amount), A-05/C4 twin pass; see Finding
D-05 (touched rows): "transport ignores its timeout" implemented-and-verified (A-21/C1, A-21/C3); "timeout after possible commit" failing (A-05/C2)
Finding: A-05, failing, high (default; duplicate ticket reply, no funds moved), helpdesk adapter post_reply sends no idempotency key and retries without reconciling, A-05/C1 and A-05/C2, suggested fix: durable idempotency key and reconcile-before-retry in the adapter
Tests run: pytest tests/security -k "A-21 or A-05": 5 passed, 2 failed (A-05/C1, A-05/C2)
Residual risk: duplicate ticket replies on timeout (A-05, high), owner unassigned
Readiness: blocked (routed A-05 failing, high)
Approver: unassigned
Other controls: not re-assessed (outside change scope)
```

## Control identifiers

### Form

An ID is a pillar letter, a hyphen and a two-digit serial: `^(S|T|A|N|D)-[0-9]{2}$`, for example A-06, T-13 or N-06. The letter is the pillar: S Scope & Stewardship, T Trust & Isolation, A Authority & Access, N Notice & Neutralize, D Demonstrated Defenses. Serials are assigned in creation order within a pillar and encode no topic, so regrouping never changes an ID. The pillar letters spell the framework name, but in an ID they are identifiers, not abbreviations: if the framework or a pillar is ever renamed, every ID keeps its letter and serial (rule 7 below). Only the uppercase letter, the hyphen and exactly two digits form a valid ID; lowercase, unhyphenated and one-digit variants are invalid.

The form is chosen so it cannot be read as another scheme's identifier: it always has a hyphen, exactly two digits and no dot. OWASP Top 10 identifiers (ASI01, LLM01, AST01, and the web Top 10's colon-year form), AIUC-1 identifiers (A003, B006.1), ISO/IEC 42001 Annex A references (A.x.y), AISVS requirements (v1.0-C9.2.8) and NIST AI RMF and AI 600-1 references (MAP 3.5, GV-6.1-007) all differ in shape, as do identifiers from catalogs outside the framework basis, such as NIST SP 800-53 controls (AC-3). In mapping tables, foreign identifiers always sit in separately labeled columns, never in the ID column.

### Citation forms

| Form | Example | Use |
|---|---|---|
| Bare ID | A-06 | This framework's own files, and records and change records whose header states the catalog version |
| Version-pinned | A-06@0.1 | Conformance claims, external mappings, and any record or document that does not state the catalog version |
| Test fixture | A-06/C1, pinned A-06@0.1/C1 | Hostile cases and authorized twins; the slash avoids the dotted suffix AIUC-1 controls use |
| Local test | A-06/L1 | A case that guidance or an adopter adds and the catalog does not have, in its own namespace per control |
| Mixed documents | STAND v0.1 A-06 | Prose that also cites other frameworks always qualifies the bare ID |
| Fully qualified | STAND:A-06@0.1 | Machine-readable mappings and claims that combine identifiers from several catalogs |

The version in a citation is the catalog MAJOR.MINOR; PATCH releases are editorial and are never cited. The namespace token is `STAND`, recorded as `namespace` in the catalog metadata (`catalog/controls.json`); it is the prefix of the fully qualified form. In templates, `<catalog name>` is filled with the name recorded in the catalog metadata.

### Stability, lifecycle and versioning

1. An ID is never reused or renumbered. `catalog/ledger.json` in the source repository lists every ID ever assigned. The same holds for catalog case numbers (`<ID>/C<n>`), even before the first release: a removed case keeps its number as `(C<n>: retired)`, and a new case takes the next number. Local cases use their own labels (`<ID>/L<n>`), so a catalog case added later never changes what a local label means.
2. An editorial change keeps the ID and is listed in `CHANGELOG.md`.
3. A normative change that keeps the control's intent keeps the ID, for example tightening the statement, changing `applies_when` or the level, or adding a hostile case. It is listed under "Normative changes" in `CHANGELOG.md` against the catalog version.
4. A change of subject, a split or a merge deprecates the old IDs and issues new ones in the same release, with `superseded_by` (the successor IDs) on each deprecated entry; withdrawal follows no earlier than the next minor release (rule 5). A withdrawn control stays in `catalog/controls.json` as a tombstone with `lifecycle: withdrawn`, `withdrawn_in` (the catalog version that withdrew it) and `superseded_by` (its successor IDs); a deprecated control has `lifecycle: deprecated`, and `superseded_by` when successors exist; a control without the field is active. The ledger entry's status mirrors the catalog lifecycle. Lifecycle states (active, deprecated, withdrawn) are catalog attributes, never record statuses.
5. An ID is deprecated for at least one minor release before it is withdrawn, so that claims can be restated against the new version. This applies to splits and merges too: no ID moves from active to withdrawn in one release.
6. Versioning:
   - before 1.0, every normative change bumps MINOR;
   - from 1.0, a change that can invalidate an existing claim bumps MAJOR (a new applicable control, a broader `applies_when`, a lower level, a stricter statement), other normative changes bump MINOR, and editorial fixes bump PATCH;
   - a claim against a superseded version stays valid until its re-establish date and names its version, unless a security advisory in `CHANGELOG.md` names that version and control (see Lapse in [conformance.md](conformance.md)); it is migrated to the new version, with a new assessment of any newly applicable control, before it cites that version.
7. A rename of the framework or of a pillar changes no ID: every ID keeps its letter and serial, because the letters are identifiers, not abbreviations of the name.

### Catalog changes

- Normative changes need maintainer review before release.
- From 1.0, normative changes also need a public comment period of at least 14 days.
- Errata that correct a factual source error ship as a PATCH release with an advisory in `CHANGELOG.md`.
- A report that a control's guidance leads to an exploitable design goes through the source repository's private security reporting process, not a public issue. A confirmed defect is fixed in a new catalog version and announced by a security advisory in `CHANGELOG.md` that names the affected catalog versions and controls; claims lapse for those controls until reassessed against the fixed version ([conformance.md](conformance.md)).

The source of truth is `catalog/controls.json` with `catalog/ledger.json` in the source repository. The files under [controls/](controls/index.md) are generated from it and are never edited by hand. Machine-readable schemas for the catalog, the record and the claim are planned for a later version.


## Scan-only execution

Scan-only is an execution mode within FULL. Keep the existing profile, level, applicability, control-status and evidence-scope rules.

Use Steps 1 and 2 to assess every applicable control by source inspection. Do not follow subsequent implementation, execution, rerun or record-update instructions, including those in references or templates. Return the [scan report](../assets/agent-security-record.md#scan-only-report) in the response, or write it only to the user-named report path. Apply the Step 5 confidentiality rule and Step 6 severity and readiness restrictions to that report.

Read the [status and evidence rules](conformance.md) before assessment. Read each selected control entry in full, with its metadata, statement and required verification. Check actual returned output for truncation or omitted sections. Recover missing source and reference text with bounded reads of the missing sections. Requested paths, listed IDs and retained terminal text outside the returned output do not prove retrieval. If gaps remain, return a partial report with the missing IDs, sources or sections, and next inspection steps.

- Use read-only source inspection tools to trace entry points, enforcement paths and retained evidence within the requested target.
- Do not change code, tests or configuration. Do not run builds, tests, experiments, live calls or the target application.
- Write no files except a report at the exact path the user names. Without that path, return the report in the response.
- Skip implementation, rerun and record-update instructions throughout the workflow and its references. Do not update an existing security record unless it is the user-named report path.
- Distinguish fresh source inspection from retained evidence. Cite retained results with their original snapshot, date, scope and known limits. Do not present them as fresh execution or carry verified status to the current snapshot without the required current-case evidence.
- Describe suggested checks only as proposed verification, never as actual results. Mark unavailable evidence and unknown reachability explicitly.

Use the [scan report format](../assets/agent-security-record.md#scan-only-report). Apply the existing confidentiality and severity rules. Inspection alone cannot establish readiness where applicable controls require stronger evidence. Keep those controls unverified and apply the existing readiness gate. A scan grants no implementation or release authority.
