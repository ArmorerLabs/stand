# MCP guidance

Informative guidance for applications that act as a Model Context Protocol (MCP) host or client, server, or proxy (feature tag `mcp`). It is keyed by control ID; the normative statements are in the catalog ([controls/index.md](controls/index.md)), and where this page and a control statement differ, the control statement governs. Generic rules for dispatch, egress, sandboxes and credentials are in [runtime-controls.md](runtime-controls.md); this page adds only what MCP changes. Pseudocode is in [patterns.md](patterns.md).

Pinned version: MCP specification 2025-11-25 and its security best practices page. Every specification statement below was checked against modelcontextprotocol.io on 2026-10-03, and each section links the page it relies on. On that date the MCP versioning page lists 2026-07-28 as the current revision; see [Version note](#version-note) before relying on mechanism-level details.

The specification is explicit that "MCP itself cannot enforce these security principles at the protocol level" ([overview, Security and Trust & Safety](https://modelcontextprotocol.io/specification/2025-11-25)). Consent, authorization and confinement are the application's job, which is what the controls below require.

Scope: this page covers MCP in the application under review. The coding agent's own MCP servers and skills are a development-time trust decision covered by the workspace rules in [SKILL.md](../SKILL.md).

## How to read this page

- "Spec: required" marks a statement the specification makes with its capitalized requirement keywords; "spec: recommended" marks a recommendation-level statement. Read the linked page for the exact wording and conditions.
- The catalog is sometimes stricter than the specification. Where it is, the section says so.
- Server, client and proxy duties differ. Where it matters, the text names the role (client, server or proxy) a statement applies to.

## Control map

| Control | MCP concern | Section |
|---|---|---|
| A-01, A-02, A-09, A-21 | Framework-native MCP clients bypass the dispatcher; fully qualified tool names; strict schemas; per-context tool exposure; timeouts | [Route every MCP call through the dispatcher](#route-every-mcp-call-through-the-dispatcher) |
| I-18, I-01, I-03, R-04, E-04 | Tool poisoning, hidden characters, rug pulls, cross-server shadowing, `notifications/tools/list_changed`, untrusted annotations | [Descriptors: pinning, rug pulls and shadowing](#descriptors-pinning-rug-pulls-and-shadowing) |
| A-16, A-17, A-18, I-05 | Token passthrough, audience binding, per-client consent at proxies, session IDs, stdio credentials | [Tokens, authorization and sessions](#tokens-authorization-and-sessions) |
| I-12, I-14, A-16 | SSRF during OAuth metadata discovery, authorization URL handling, DNS rebinding of local servers | [Discovery, URLs and transports](#discovery-urls-and-transports) |
| I-19, I-05, A-23 | Local (stdio) server commands, sandboxing, roots, configuration writes | [Local (stdio) servers](#local-stdio-servers) |
| I-20, A-20, A-22, A-12, I-26 | Sampling and elicitation | [Sampling and elicitation](#sampling-and-elicitation) |
| R-02, I-10, I-12 | Which capability properties and feature tags an MCP integration adds | [Profiling an MCP integration](#profiling-an-mcp-integration) |
| I-10, A-06, A-24, I-11, R-06 | Remote servers as data recipients; tool arguments as an exfiltration channel; provider-hosted connectors | [Remote servers as data recipients](#remote-servers-as-data-recipients) |
| A-01, A-03, A-04, A-16, A-20, A-22, I-12 | The application as an MCP server, including its authorization server | [Exposing an MCP server](#exposing-an-mcp-server) |

## Profiling an MCP integration

Implements R-02 for MCP. Adding a first MCP server adds the `mcp` tag, so it is a profile change and a FULL change ([profile-and-levels.md](profile-and-levels.md)). Record the properties and tags it adds per context with these rules:

- untrusted-input: tool results, resources, prompts and sampling results from every server are untrusted content (I-01), and so are descriptors until I-18 is implemented-and-verified for that server. A context that calls an MCP tool is untrusted-input from its first result.
- external-effect: a tool that writes, sends or executes is external-effect. A read-only tool on a server outside the application's trust boundary (a remote server, or a local server that forwards requests to a third party) is external-effect too when the model chooses any of its arguments, because the arguments send information beyond the session; the only exception is the one for fixed destinations in the external-effect definition (every argument fixed by trusted configuration, with I-12 implemented-and-verified).
- network-egress: a remote server, a local server that makes network requests, or any fetch of a URL a server supplied (OAuth discovery, resource links, elicitation URLs) makes the context network-egress, so I-12 applies.
- provider-routing: a remote server or remote agent that receives data from the context is a data recipient, so the context carries `provider-routing`, and I-10 applies whenever the context is sensitive-data (it also applies through its `sensitive-data+mcp` alternative).
- sensitive-data: a server tool that can read data an attacker should not obtain makes the context sensitive-data, as any tool does.

Record the negotiated protocol revision of each server in the MCP inventory (R-04), together with its identity and descriptor hash.

## Route every MCP call through the dispatcher

Implements A-01, A-02, A-09, A-21.

Many agent frameworks ship an MCP client that lists a server's tools and lets the model call them directly. That path skips every dispatcher check: identity, schema, authorization, provenance, approval and budget. Instead, adapt each pinned MCP tool into the application's own tool registry, so a call runs model proposal, then dispatcher, then the MCP client as the adapter. The MCP client session and its credentials are adapter internals that nothing else can reach (A-01).

- Register MCP tools under a fully qualified name that includes the server identity, for example `billing-server.create_refund`. The specification recommends that tool names be unique within a server, so names can and do collide across servers. Resolve only fully qualified names, and fail closed on ambiguous or look-alike names (A-02, I-18). ([Tools: Tool Names](https://modelcontextprotocol.io/specification/2025-11-25/server/tools))
- Validate arguments against the pinned, reviewed input schema and the register's semantic constraints. A server's `inputSchema` describes shape, not permission (A-02).
- Expose to each agent context only the MCP tools its task needs (A-09, R-03). Every tool description you expose enters the model's context, so an unneeded server is both attack surface and injection surface.
- Decide auto-run and approval from the register's consequence class and the parsed arguments, never from annotations such as `readOnlyHint` or `destructiveHint`. The specification requires clients to consider tool annotations untrusted unless they come from trusted servers (spec: required). The catalog goes further: annotations never relax policy or approval requirements, even from a trusted server (I-18). ([Tools: Data Types](https://modelcontextprotocol.io/specification/2025-11-25/server/tools))
- The tools page recommends a human in the loop who can deny tool invocations, UI that shows which tools are exposed, and that clients "Show tool inputs to the user before calling the server, to avoid malicious or accidental data exfiltration" (spec: recommended). In this framework, confirmation is targeted (A-06, A-07, A-08, A-10) rather than required for every call, and the tool inputs appear in the server-rendered approval preview (A-12). The overview's key principles go further (hosts must obtain explicit user consent before invoking any tool). This page reads that as consent when the principal enables a server and its tools for a context, plus the targeted confirmations; per-call prompts for routine operations recreate the approval fatigue that A-13 measures.
- The tools page recommends client timeouts for tool calls (spec: recommended). Enforce the deadline in the caller, independently of the transport (A-21).
- The tools page recommends logging tool usage for audit (spec: recommended). Include the server identity and descriptor hash in the dispatcher's events (E-01).

## Descriptors: pinning, rug pulls and shadowing

Implements I-18, I-01, I-03, R-04, E-04.

Three attacks target the descriptions a client loads, as described by [Invariant Labs](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks):

- Tool poisoning: instructions hidden in a tool description that the model reads and the user does not see.
- Rug pull: the server changes a description after the user or reviewer approved it.
- Cross-server shadowing: a malicious server's description changes how the agent uses a different, trusted server's tool, for example telling it to send every email through the trusted email tool to an attacker's address.

The specification's overview says that descriptions of tool behavior such as annotations "should be considered untrusted, unless obtained from a trusted server" ([overview](https://modelcontextprotocol.io/specification/2025-11-25)). Treat tool results, resource contents, prompt templates and sampling results from any server, trusted or not, as untrusted content that taints the context (I-01). Treat descriptions, annotations and server instructions the same way until they are reviewed and hash-pinned (I-18): instructions from a server that is not pinned never go in system or developer position. A reviewed, pinned descriptor is trusted configuration: it goes in the provider's tool-definition field, does not taint the context, and any change to it disables the tool until re-review. That trust holds only while I-18 is implemented-and-verified for the server, including its drift-disabling test; until then its descriptors are untrusted content and taint the context (I-01). This follows the specification's distinction between trusted and other servers; the catalog adds that trust in a server is established by review and pinning, never by the server's own claims.

Review has to see what the model will see. Poisoned descriptors hide their instructions in Unicode tag characters, bidirectional controls and zero-width text, or past the point where a client UI truncates a description. I-18 therefore requires review of the full descriptor after the hidden-text normalization described under I-03, with invisible and control characters shown and nothing truncated, and pinning fails on tag characters, bidirectional controls or zero-width characters the reviewer has not explained. This applies at every level, as part of I-18, even though I-03 itself is a Level 2 control; only a descriptor that passed this review becomes trusted configuration.

- Pin each server by identity (URL, or package, version and exact command for stdio) and by a hash over every server-supplied field that reaches model context or the reviewer: the server name, version and `instructions` (returned at initialization in 2025-11-25, and placed in the system prompt by many hosts); tool names, titles, descriptions, input and output schemas, annotations and any `_meta` content exposed to the model; and prompt, resource and resource-template names and descriptions. Hash only the `_meta` fields that reach the model or the reviewer, because servers may put volatile data there. Record both in the inventory (R-04). Refuse to load a server or tool that is not pinned (I-18).
- A change to a server-level field such as `instructions` disables all of that server's tools until re-review, so a rug pull that edits only the instructions cannot pass with every tool hash intact (I-18).
- Servers that declared `listChanged` are recommended to send `notifications/tools/list_changed` when their tools change (spec: recommended). On that notification, disable the affected tools, re-list, diff against the pin and hold them for re-review. Do not rely on the notification: a hostile server can change silently, so re-hash on every `tools/list` and on reconnection, and emit a drift signal on any mismatch (E-04). ([Tools: List Changed Notification](https://modelcontextprotocol.io/specification/2025-11-25/server/tools))
- The 2025-11-25 security best practices describe a session-hijack path in which an injected `notifications/tools/list_changed` leaves a client "with tools that they were not aware were enabled". Disabling on drift closes that path as well. ([Security best practices: Session Hijacking](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices#session-hijacking))
- Where several servers of different trust share one context, any one server's text can steer calls to the others. Split contexts by trust level where the task allows, and keep high-consequence tools out of contexts that load descriptions from servers you do not control.
- A valid signature on a package or descriptor identifies the publisher; it does not make the descriptor safe (I-18).

## Tokens, authorization and sessions

Implements A-16, A-17, A-18, I-05.

Token passthrough is the anti-pattern in which a server accepts a token that was not issued to it and forwards it to a downstream API. The specification forbids it because it bypasses audience-dependent controls such as rate limiting and request validation, breaks audit attribution, and lets a stolen token use the server as a proxy. ([Security best practices: Token Passthrough](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices#token-passthrough); [Authorization: Token Handling](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization))

As an MCP client:

- Use a token issued for that server's audience, never the end user's token for some other service. Clients include the RFC 8707 `resource` parameter identifying the MCP server in authorization and token requests, and send the server only tokens issued by its authorization server (spec: required).
- Request a minimal initial scope set and elevate on specific challenges, rather than everything in `scopes_supported` (spec security best practices: Scope Minimization). Wildcard or omnibus scopes widen the blast radius of a leaked token.
- Send tokens only in the `Authorization` header, never in a query string (spec: required), which also keeps them out of URL logs.

As an MCP server:

- Validate every access token and reject any token not issued for this server as its audience (spec: required). Accept or transit no other tokens (spec: required).
- When the server calls upstream APIs, it acts as an OAuth client with a separate token issued by the upstream authorization server; it never passes through the token it received (spec: required). At Level 2, use token exchange or an on-behalf-of flow that records subject and actor (A-17).
- Do not treat claimed scopes as sufficient on their own. The best practices list "treating claimed scopes in token as sufficient without server-side authorization logic" as a common mistake; the server still resolves the object and checks the principal's access at the moment of effect (A-03, A-04).

As an MCP proxy that uses a static client ID toward a third-party authorization server:

- Implement per-client consent before the third-party flow (spec: required): keep a per-user registry of approved `client_id` values and check it first; show an MCP-server-owned consent page that names the client, the third-party scopes and the registered `redirect_uri`, with CSRF protection and anti-framing; bind consent cookies to the specific `client_id`; match `redirect_uri` exactly; and generate a single-use, short-lived `state` value that is stored only after consent is approved. ([Security best practices: Confused Deputy Problem](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices#confused-deputy-problem))

Sessions and other server-held state:

- Servers that implement authorization verify every inbound request, and no server uses sessions for authentication (spec: required). Use secure, non-deterministic session IDs (spec: required) from a secure random number generator, and bind them to the authenticated user, for example by keying stored state as `<user_id>:<session_id>` with the user ID taken from the verified token (spec: recommended). The draft and the 2026-07-28 revision rename this attack state handle hijacking. ([Security best practices: Session Hijacking](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices#session-hijacking))
- Tasks are experimental in 2025-11-25. When an authorization context exists, bind each task to it and reject `tasks/get`, `tasks/result` and `tasks/cancel` from other contexts (spec: required). ([Tasks: Security Considerations](https://modelcontextprotocol.io/specification/2025-11-25/basic/utilities/tasks))
- Servers that implement elicitation never associate its state with session IDs alone, and derive user identity from the credentials obtained through MCP authorization where possible (spec: required). ([Elicitation: Statefulness](https://modelcontextprotocol.io/specification/2025-11-25/client/elicitation))

Credentials for stdio servers. The authorization specification recommends that stdio implementations not follow it and instead "retrieve credentials from the environment" ([Authorization: Protocol Requirements](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization)). This is where I-05 matters: give a stdio server only the narrowly scoped credential it needs, injected into its sandbox, never the host's environment, home directory, cloud configuration or SSH agent. At Level 3, sender-constrain tokens that could surface in context, logs or a model-influenced process (A-18).

## Discovery, URLs and transports

Implements I-12, I-14, A-16.

A malicious server chooses the URLs a client fetches during OAuth metadata discovery: the `resource_metadata` URL in the `WWW-Authenticate` header, the `authorization_servers` in the protected resource metadata, and the token and authorization endpoints in the authorization server metadata. Pointing them at `169.254.169.254`, internal services or localhost turns the client into an SSRF proxy. Clients deployed to a server are required to consider SSRF here (spec: required), and the best practices recommend HTTPS, blocking private and reserved ranges (including `169.254.0.0/16`), validating redirect targets and using an egress proxy, and warn: "Avoid implementing IP validation manually." ([Security best practices: Server-Side Request Forgery](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices#server-side-request-forgery-ssrf))

- Route every discovery and metadata fetch through the egress boundary (I-12), with redirect hops validated and DNS resolved by a controlled resolver. The catalog requires this (A-16), not just recommends it.
- Authorization URLs from a server: accept only `https` (and `http` only for loopback during development), reject `javascript:`, `data:`, `file:`, `vbscript:` and other dangerous schemes, never open a URL through a shell command, and sanitize every URL received from a server (spec: required). Web-based clients are recommended to set a Content Security Policy (spec: recommended). ([Security best practices: OAuth Authorization URL Validation](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices#oauth-authorization-url-validation))
- URLs inside tool results, resource links and elicitation requests are untrusted render targets; apply the rendering and link rules in [runtime-controls.md](runtime-controls.md#egress-and-exfiltration-channels) (I-13, I-14).
- Streamable HTTP servers validate the `Origin` header on all incoming connections to prevent DNS rebinding (spec: required). Servers running locally are recommended to bind only to localhost, and all servers to authenticate every connection (spec: recommended). ([Transports: Security Warning](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports))

## Local (stdio) servers

Implements I-19, I-05, A-23.

A local server is arbitrary code running on the user's or the application's host, with the client's privileges unless you confine it. The best practices list malicious startup commands in client configuration, malicious payloads inside the server, and insecure local servers reached through DNS rebinding. ([Security best practices: Local MCP Server Compromise](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices#local-mcp-server-compromise))

- Clients that offer one-click local configuration must, before running anything, "Show the exact command that will be executed, without truncation", identify it as code execution, require explicit approval and allow cancellation (spec: required for one-click configuration). The catalog applies this to every configuration path and requires re-approval whenever the command or its arguments change (I-19).
- The best practices recommend executing server commands in a sandbox with minimal default privileges, restricted file system and network access, and explicit grants for anything more (spec: recommended). The catalog requires it: each server sees only its declared files, network destinations and secrets (I-19), and holds no ambient credentials (I-05).
- Roots are advisory. Clients expose roots, and servers are recommended to "Respect root boundaries during operations" (spec: recommended). A malicious server ignores them, so enforce file confinement in the sandbox, not through roots. ([Roots: Security Considerations](https://modelcontextprotocol.io/specification/2025-11-25/client/roots))
- Files that define MCP servers, tools, skills or agent rules, and approval or auto-run settings, are not writable by the agent wherever the write takes effect without human review, so an injected instruction cannot install a new command or switch on auto-approval (I-19, A-23). In a local working tree, the files the client loads or reloads (MCP configuration, rules files, workspace editor settings) are active configuration; a change the agent proposes on a branch for review is not.
- Where a local proxy spawns stdio servers on request, a cross-site scripting bug in the client can become arbitrary command execution through the proxy. The best practices recommend sandboxing spawned processes, restricting their file system access, logging stdio usage and requiring extra authorization for dangerous commands (spec: recommended). ([Security best practices: stdio Transport Security in Proxy Scenarios](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices#stdio-transport-security-in-proxy-scenarios))
- Servers meant to run locally are recommended to use stdio, or to require an authorization token or a restricted IPC channel if they use HTTP (spec: recommended).

## Sampling and elicitation

Implements I-20, A-20, A-22, A-12, I-26.

Both features are server-originated, so both are untrusted.

Sampling lets a server ask the client's model to generate, which means a server can drive your model and spend your budget. The overview says users must explicitly approve any sampling request, and should control whether sampling occurs, the prompt that is sent and what results the server can see ([overview](https://modelcontextprotocol.io/specification/2025-11-25)). The sampling page recommends a human who can deny requests, review of prompts and generated responses, rate limiting, and iteration limits for tool loops (spec: recommended). ([Sampling](https://modelcontextprotocol.io/specification/2025-11-25/client/sampling))

- Deny sampling by default; allow it per server by policy (I-20).
- Include only the context the request needs. The `includeContext` values `thisServer` and `allServers` are soft-deprecated; never send other servers' context or the user's conversation to a server.
- Count every sampling request and its tokens against the run budget and the principal's quotas (A-20, A-22).
- Treat sampling results as untrusted content wherever the client reuses them (I-01).
- With sampling with tools, added in 2025-11-25, the server supplies tool definitions and executes the resulting tool uses itself. Those effects happen at the server, outside your dispatcher; present the proposed tool calls for review as the specification's flow shows, and decide whether that server may cause them at all.

Elicitation lets a server ask the user for input in the middle of an operation, which a hostile server can style as the application's own login or payment screen. ([Elicitation](https://modelcontextprotocol.io/specification/2025-11-25/client/elicitation))

- Clients make clear which server is requesting information, offer decline and cancel, and in form mode let the user review responses before sending (spec: required). Render elicitation outside the application's trusted approval and login surfaces, labeled with the server's identity (A-12, I-20).
- Servers do not use form mode for passwords, API keys, access tokens or payment credentials (spec: required). Do not rely on the server: block or warn on form requests that ask for secrets (I-20, I-26).
- URL mode, added in 2025-11-25, keeps secrets out of the client and the model. Clients do not pre-fetch the URL or its metadata, do not open it without consent, show the full URL before consent, and open it in a way that does not let the client or the model inspect the content or the user's input (spec: required). They are recommended to highlight the domain and warn on ambiguous URLs such as Punycode (spec: recommended). The catalog requires the domain highlighting as well, and requires the page to open outside any surface the model can read or actuate (I-20).
- Servers bind elicitation requests to the client and user identity, and verify the identity of the user who opens a URL-mode link before accepting information (spec: required).

## Remote servers as data recipients

Implements I-10, A-06, A-24, I-11, R-06.

- Everything sent to a remote server (tool arguments, resource requests, sampling results) is a disclosure to that server's operator. Add each remote server to the data-classification policy as a recipient and send only the classes it may receive (I-10, R-06). The overview says hosts must obtain explicit user consent before exposing user data to servers ([overview](https://modelcontextprotocol.io/specification/2025-11-25)).
- Tool arguments are an exfiltration channel, which is why the tools page recommends showing inputs before calls. When the context is tainted and also holds sensitive data, URL, host, path and query arguments to remote tools are consequential values under A-06: they match a trusted source or are confirmed with their provenance, except a public web result's URL followed unchanged within the per-run cap that A-06 sets. Free-text arguments cannot match a trusted source, so govern them as disclosures, tainted or not: the data classes they can carry, determined from what the context read as in A-24, must be ones the data policy allows for that server. I-10 requires this for remote tool servers, and A-24 covers free-text arguments that reach a party outside the application. Otherwise deny the call, route it to a server approved for those classes, or confirm it with the content shown. This keeps confirmations targeted rather than per call (A-13).
- When the model provider's API calls a remote MCP server for you (a provider-hosted connector), the call never reaches your dispatcher. Govern it as a provider-executed tool: allowlists, approval kept on for servers that receive protected data or cause effects, and logged call records (I-11, [runtime-controls.md](runtime-controls.md#provider-routing-and-provider-executed-tools)).

## Exposing an MCP server

Implements A-01, A-03, A-04, A-16, A-20, A-22, I-12.

When the application is the server, the calling client and its model are untrusted proposers, and your tool handlers are effect adapters.

- Put tool handlers behind your own dispatcher and policy. Authorize each call against the principal from the validated token, at the moment of effect, never against tool arguments, session identifiers or identity claims in the request (A-03, A-04). The elicitation page states the same rule for user identification: servers do not rely on client-provided identification without server verification (spec: required).
- The tools page requires servers to validate all tool inputs, implement proper access controls, rate limit tool invocations and sanitize tool outputs (spec: required). The resources page requires servers to validate all resource URIs, and the prompts page requires implementations to validate prompt inputs and outputs (spec: required). Rate limits per principal and tenant are budgets in this framework (A-20, A-22).
- Validate audience on every token and never pass a received token upstream ([Tokens, authorization and sessions](#tokens-authorization-and-sessions)).
- Your tool descriptions are someone else's untrusted content. Keep them factual, free of instructions to the model, and stable; a description change is a breaking change for clients that pin hashes.
- If the application runs the authorization server for its MCP server and accepts Client ID Metadata Documents (in 2025-11-25, authorization servers and clients are recommended to support them), the authorization server fetches a URL that an unknown client supplies as its `client_id`. Authorization servers are required to consider the security implications in the Client ID Metadata Document draft's security considerations (spec: required) and are recommended to consider SSRF and to cache documents respecting HTTP cache headers (spec: recommended). Fetch the document through the egress boundary (I-12) or an equivalently SSRF-hardened fetcher, with a size limit. Validate that the document's `client_id` matches its URL exactly and that the redirect URI in each authorization request matches the document (spec: required). On the authorization screen, clearly display the redirect URI hostname (spec: required), and warn on redirect URIs that are only `localhost`, because an attacker can present a legitimate client's metadata URL with its own `localhost` listener (spec: recommended). ([Authorization: Client ID Metadata Documents](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization))

## Verification pointers

Each control's hostile cases and authorized twin are in the catalog; [verification.md](verification.md) explains the method. The MCP-specific cases, all driven through the real client or server path into a controlled test server or destination:

- I-18: change a tool description on a test server to include hidden instructions and send `notifications/tools/list_changed`; the tool is disabled and a drift signal fires. Change only the server's `instructions` and reconnect; all of its tools are disabled and a drift signal fires. Register a colliding or look-alike name on a second server; resolution fails closed. Mark a destructive tool `readOnlyHint: true` on an untrusted server; approval policy is unchanged. Add an unpinned server to configuration; it is not loaded. Submit a descriptor whose instruction is written in Unicode tag characters; pinning fails.
- A-16: as a client, capture outbound calls; each carries a token issued for its audience. Server role: forward the user's upstream token to the server; it rejects it on audience, and another user's session identifier is rejected. Point `resource_metadata` at `169.254.169.254`; the fetch is blocked at the egress boundary. Cases for a role the application does not have are recorded as not applicable with the absence named ([conformance.md](conformance.md)).
- I-19: for stdio servers, alter the configured command's arguments; the server does not start, and a canary outside the server's declared scope cannot be read or sent. For every system, through injected content, ask the agent to edit its MCP configuration or to set a workspace setting that auto-approves tool calls; neither takes effect without review.
- I-20: issue looping sampling requests and one that asks for the conversation history; the budget stops the loop and no client context is included. Send an elicitation styled as an application login that asks for an API key; it is blocked or shown with the server's identity and a warning. Send a URL-mode request whose URL is a Punycode look-alike; the full URL is shown with the domain highlighted and a warning, and nothing is fetched before consent.
- A-01: drive a forbidden proposal through the framework's native MCP client path; it is denied at the dispatcher and no server call occurs.

Pair every case with an authorized twin of the same shape (a pinned, unchanged tool works by its fully qualified name; a correctly issued token is accepted).

## Version note

This page is pinned to MCP specification 2025-11-25. On 2026-10-03 the [MCP versioning page](https://modelcontextprotocol.io/docs/2026-07-28/learn/versioning) lists 2026-07-28 as the current revision. Its [changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog) includes changes that affect mechanisms named on this page:

- protocol-level sessions and the `Mcp-Session-Id` header are removed; servers that need state mint explicit handles passed as tool arguments, and the security best practices call the corresponding attack state handle hijacking;
- the `initialize` handshake is removed, and each request carries its protocol version and client capabilities;
- list-changed notifications move to an opt-in `subscriptions/listen` stream;
- server-initiated requests such as `roots/list`, `sampling/createMessage` and `elicitation/create` are replaced by multi round-trip requests, in which a server returns an input-required result and the client retries with the requested input.

The control intents carry over unchanged: possession of a session ID or state handle is never authentication (A-16), descriptor drift disables tools whatever the notification mechanism (I-18), and server-originated requests for model output or user input are untrusted and budgeted (I-20). The mechanism-level guidance on this page has not been rechecked against 2026-07-28; recheck it before moving the pin.

When an SDK negotiates 2026-07-28 or later:

- record the negotiated revision or revisions of each server in the MCP inventory (R-04);
- apply the intents above to the replacement mechanisms: run the session-ID cases of A-16 against state handles, hash server-supplied fields wherever the revision delivers them (I-18), and budget and review multi round-trip input requests as sampling and elicitation (I-20);
- record a case whose mechanism the revision removed as `<ID>/T<n>: not applicable (removed in protocol <revision>; earlier revisions not accepted)` only when the implementation rejects every earlier revision that has the mechanism, which is the verifiable absence [conformance.md](conformance.md) requires; while it still negotiates an earlier revision, run the case against that revision.

## Sources

MCP specification 2025-11-25 (checked 2026-10-03):

- Overview, Security and Trust & Safety: https://modelcontextprotocol.io/specification/2025-11-25
- Security best practices: https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices (the specification path https://modelcontextprotocol.io/specification/2025-11-25/basic/security_best_practices redirects here)
- Authorization: https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization
- Transports: https://modelcontextprotocol.io/specification/2025-11-25/basic/transports
- Tools: https://modelcontextprotocol.io/specification/2025-11-25/server/tools
- Resources: https://modelcontextprotocol.io/specification/2025-11-25/server/resources
- Prompts: https://modelcontextprotocol.io/specification/2025-11-25/server/prompts
- Roots: https://modelcontextprotocol.io/specification/2025-11-25/client/roots
- Sampling: https://modelcontextprotocol.io/specification/2025-11-25/client/sampling
- Elicitation: https://modelcontextprotocol.io/specification/2025-11-25/client/elicitation
- Tasks (experimental): https://modelcontextprotocol.io/specification/2025-11-25/basic/utilities/tasks

Later revision, for the version note:

- Versioning: https://modelcontextprotocol.io/docs/2026-07-28/learn/versioning
- 2026-07-28 changelog: https://modelcontextprotocol.io/specification/2026-07-28/changelog
- 2026-07-28 security best practices (State Handle Hijacking): https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices

Related reading:

- Invariant Labs, MCP Security Notification: Tool Poisoning Attacks: https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks
- OWASP MCP Security Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/MCP_Security_Cheat_Sheet.html
- Resource Indicators for OAuth 2.0, RFC 8707: https://www.rfc-editor.org/rfc/rfc8707
