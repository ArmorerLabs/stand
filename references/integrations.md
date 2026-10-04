# Integrations: framework loops, hosted platforms and components elsewhere

Informative guidance for three common situations:

- an agent framework runs the tool loop and calls tools itself;
- a hosted agent platform runs the agent and executes its tools;
- an enforcement component that in-scope agents rely on (policy engine, credential broker, egress proxy, approval service, audit store) lives in another repository or service, or belongs to another team or a vendor.

The normative statements are in the catalog ([controls/index.md](controls/index.md)); where this page and a control statement differ, the control statement governs. Conformance rules are in [conformance.md](conformance.md), and the generic enforcement points are in [runtime-controls.md](runtime-controls.md) and [patterns.md](patterns.md). Load this page only when one of the three situations applies. Product names below are examples, checked on 2026-10-04; check the current documentation of whatever you use.

The model proposes. The application enforces. The catalog does not care where the enforcement code lives. It cares about three things: the code sits on the only path the model's proposals can take, the model cannot alter it, and a test through the public entry point shows that it holds.

## Framework-owned agent loops

Many frameworks own the loop: the model returns a tool call, and the framework looks up a function and runs it. Wrapping one tool function in a check enforces nothing for the next tool, the framework's MCP client, a handoff or a fallback model. Place each enforcement point as follows.

| Enforcement point | Where it goes in a framework-owned loop | Controls |
| --- | --- | --- |
| Dispatcher | Every tool the framework sees is a stub whose only body calls `dispatch(proposal, ctx)`, with `ctx` built from server-side state, never from framework or model fields. Adapters and their credentials are constructed only inside the dispatcher module. A framework MCP client is registered the same way, as stubs for pinned tools, never connected straight to the model ([mcp.md](mcp.md)). | A-01, A-02, A-03, T-05 |
| Approval interrupt | Use the framework's pause and resume mechanism only to pause. The approval itself lives in the application's approval service, bound under A-11 and shown on the application's surface under A-12. On resume, the stub calls `execute` with the stored request, never the model's re-proposal. | A-11, A-12 |
| Taint and provenance | Framework message lists and state do not carry taint. Keep the taint flag, data classes and source references in `ctx`, set by context assembly whenever a tool result, retrieval, recalled memory or handed-off message enters, and pass them to `dispatch`. Framework guardrails and classifier hooks add signals; they are never the enforcement. | T-01, A-06, A-24, T-07 |
| Handoffs and subagents | A handoff or subagent call is delegation: it goes through the orchestrator's envelope with the intersected authority, taint, data classes and source references, and the receiver dispatches every proposal itself. A handoff that passes the whole conversation passes its taint too. | A-15, T-21 |
| Model calls | Wrap the framework's model client, fallback models included, in the `model_call` wrapper, so every turn spends the run budget under a caller-enforced deadline. | A-20, A-21 |
| Memory and checkpoints | A framework memory store is memory under T-07. A checkpointer or serialized run state is server-held conversation state: key it to the authenticated session and tenant, and never accept it from a client. | T-07, T-09 |
| Stop | The dispatcher checks the stop flags before every effect, and the stop also cancels the framework run and its children. | N-06 |
| Version | A framework version change is a trigger location: re-run the routed security tests before it reaches production. | N-09, D-07 |

Two examples of pause mechanisms, checked on 2026-10-04:

- LangGraph pauses a graph with `interrupt()`, saves state through a checkpointer keyed by a thread ID, and resumes with `Command(resume=...)`. Its documentation warns that the node re-runs on resume, so side effects before the interrupt must be idempotent. Call no adapter before the interrupt, and let the step's idempotency key (A-05) absorb any repeat.
- The OpenAI Agents SDK marks a tool with `needs_approval`, surfaces pending calls in `RunResult.interruptions`, and resumes from a `RunState` after `approve` or `reject`. Its documentation notes that serialized run state carries approval decisions and belongs in trusted server storage. Treat the SDK's `approve` call as the signal to resume, not as the approval proof: the stub still finds and consumes the bound approval in `execute`.

Testing. Replace only the framework's model client with a scripted client that implements the same interface (pattern 6 in [patterns.md](patterns.md)), and keep the framework, graph, stubs, dispatcher, policy and adapters real. Drive each hostile case and its twin through the application's public entry points and through the framework's own run API, since both are entry points (A-01, D-01, D-02). If the framework cannot take a scripted client, serve scripted responses from a fake provider endpoint at the HTTP boundary. Add a static test that no tool body or framework callback references an adapter or a credential, and run the mutation check: with the policy call disabled, every hostile case must fail.

## Hosted agent platforms

When a hosted platform runs the loop and executes the tools (a provider-hosted agent, a managed agent runtime, a low-code agent builder), the platform is the dispatcher for those tools, and a test of your own dispatcher proves nothing about them (T-11). There are two ways to build on one.

1. Keep every consequential effect behind your own boundary. Expose each consequential operation as an endpoint you operate, such as an MCP server or an API, whose handler runs your dispatcher with the principal taken from a token issued for that endpoint (A-16). The platform then only proposes, and the dispatcher, provenance, approval and budget controls are yours and testable like any other. Your endpoint cannot see the platform's context, so it cannot tell whether untrusted content entered it or whether a value was principal-entered: treat every proposal as coming from a context that holds untrusted-input and sensitive-data, with every argument untrusted-derived unless it arrives through a structured field your own interface captured and bound to the call, and profile the platform context that way (S-02). A-06, A-07 and A-08 then apply at the endpoint. Prefer this for anything that moves money, sends externally, changes access or writes the system of record.
2. Rely on a platform control. Then you configure it, record it, and test it yourself through the platform's public entry point.

| Control area | What the platform must provide if you rely on it | What stays with you |
| --- | --- | --- |
| Tool path (A-01, A-02) | Only configured tools run, with schema validation and no fallback to unregistered tools | Registering only tools that point at endpoints you control or have reviewed |
| Identity and authority (A-03, A-16) | A verified end-user identity, or a token issued for your endpoint's audience | Resolving objects and checking access at your endpoint on every call |
| Provenance, task scope, Rule of Two (A-06, A-07, A-08) | Rarely available: the platform does not know your register | Enforcing them at your endpoints; routing any per-call approval the platform offers to your own approval surface (A-11, A-12) |
| Egress and provider-executed tools (T-11, T-12) | Network and domain allowlists, and per-call approval for connectors | Configuring them, and testing them with a canary in a platform test account |
| Credentials (T-05) | Secret storage the agent's code cannot read | Narrow scopes and short lifetimes |
| Rendering (T-13, T-26) | Inert rendering, if the platform renders the chat | Inert rendering wherever you render agent output |
| Provider routing and retention (T-10) | Retention, training-use and location settings | Choosing them, recording them, and checking provider terms |
| Stop (N-06) | An API that cancels a run, its background work and its connector calls | Wiring the stop to that API, and revoking the credentials you issued |
| Audit (N-01, N-02) | An export of call records with run and principal identifiers | Storing them where no agent identity can modify them |

Testing through the platform. Drive hostile content through the platform's public entry point into your controlled endpoints and canary hosts, and record what reached them. Where the platform does not let you script the model's proposals, two kinds of evidence still hold up: crafted proposals sent straight to your own endpoint, which is integration evidence for the controls that endpoint enforces; and canary tests in a platform test account, which are isolated-runtime evidence for the platform settings they exercise. Live-model runs that try to elicit the attack are evaluation evidence (D-08), not a deterministic test. A hostile case the model never attempted did not run; it is not a passed case.

Conformance. A claim cannot exclude a component it depends on, and reliance on a vendor is never a reason for not-applicable ([conformance.md](conformance.md)). A platform control is therefore in scope like any other. It counts at the evidence scope your own test actually exercised, at the recorded commit (D-03). A vendor's statement or attestation can be cited beside that evidence, but on its own it is not a run at the recorded commit, so it leaves the control implemented-but-unverified, and it never makes a critical-boundary control implemented-and-verified.

## Enforcement components in other repositories or services

Real systems split the enforcement path across services and repositories: a shared policy engine, a credential broker run by the platform team, an egress proxy run by networking, an approval service shared by several products. The scope of a claim still includes every component on the enforcement path that in-scope agents rely on ([conformance.md](conformance.md)), so the record has to reach them.

- Name each one. For every enforcement component outside the repository under review, record the component, its owner, and the evidence reference with the commit or version deployed, for example `egress proxy; network platform team; STAND record in infra/egress at commit 4f2c1e0, T-12 rows`.
- Cite evidence from where it lives. The best evidence is that component's own STAND record at the commit that is deployed, whose rows cover the controls you rely on. Pair it with your own hostile case and twin through your public entry point that reaches the deployed component, for example A-06/C1 or T-12/C1 run against the policy service or proxy version in your environment. The control counts at the scope your own test exercised.
- Pin what you depend on. Pin the versions of shared policy bundles, client libraries and service contracts in your repository, so a change on their side reaches you as a change in your repository: a trigger location that re-runs the routed tests (N-09, D-07). Where you cannot pin (a shared service deployed on its own schedule), ask the owning team to run your hostile cases as contract tests in their pipeline, and record that arrangement.
- Fail closed across the boundary. An unreachable policy service, credential broker or approval store, or one that answers with an unknown version, is a denial (A-02). Cover these in the failure matrix (D-05), because the network hop between repositories is where such failures happen.
- Keep shared configuration out of the agent's reach. A register, policy bundle or allowlist that lives in another repository is still configuration the agent must not change without review (A-23). Check the agent's credentials against that repository too.
- In a monorepo, the same rules apply to directories: give each component's path a code owner, and set CI path filters so a change to a shared enforcement path runs the security tests of every application that depends on it (D-07).

## Sources

Checked 2026-10-04:

- LangGraph, interrupts: https://docs.langchain.com/oss/python/langgraph/interrupts
- OpenAI Agents SDK, human in the loop: https://openai.github.io/openai-agents-python/human_in_the_loop/
