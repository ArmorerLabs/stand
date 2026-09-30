# Runtime controls

These are implementation recommendations for this skill. Select the sections that match the application's capabilities. The framework sources classify risk and provide governance context; they do not prescribe this exact architecture.

## Authority and tool dispatch

Keep the authenticated user, tenant, workload identity, permission scopes, and run ID in trusted execution context. Model arguments may identify a requested object, but they cannot establish ownership or authority. Resolve the object and check current access in the service that owns it. A broad service credential must never substitute for the caller's permission.

Use a single logical enforcement path for all entry points, including jobs, fallback models, subagents, callbacks, and retries. A framework's tool allowlist is insufficient if another endpoint can call the adapter directly. Independently validate:

1. The authenticated identity and any constrained delegation.
2. The registered tool, accepted schema, and semantic constraints on arguments.
3. Current authorization for the action, object, tenant, and destination.
4. Policy limits, resource state, revocation, and required approval.
5. The transaction or idempotency state before initiating the effect.

The final adapter uses only the validated canonical request. It must not reread mutable model arguments after validation. Reject unknown tools and unrecognized fields where ambiguity could change authority. Validate types, ranges, content length, amount and currency, identifiers, and allowed state transitions. Use parameterized database operations and structured process arguments. Never assemble a shell command or query by concatenating model output.

Authorization checks and effects need an appropriate transaction, version precondition, or destination-side check to prevent a race. Use database constraints, atomic reservations, or a durable operation ledger for concurrent requests. If an external call times out after possible success, reconcile the operation before retrying. Process-local deduplication does not establish correctness across workers or restarts.

## Approval integrity and human oversight

Define risk and autonomy policy outside the model. Permit bounded operations covered by existing user authorization. Require additional review when scope changes or the approved policy requires it because of impact, irreversibility, or uncertainty. A read can still disclose highly sensitive data.

Render action previews from canonical server data. Show the action, target, recipient, data to be disclosed, consequences, and applicable limits. Render model explanations as untrusted text; an explanation cannot alter the approval record or impersonate a trusted control.

Bind approval to the authenticated approver, tenant, exact normalized action, target, arguments, policy version, relevant resource version, and expiry. Keep proof in trusted storage or a cryptographically authenticated artifact. An approval ID is a reference, not proof of permission. Recheck the approver's authority and current revocation at execution. Changes to approved material fields invalidate the approval. Enforce single use or an explicitly bounded reuse policy with replay protection.

Do not accept a model's `approved: true`, quoted user consent from retrieved text, a claimed administrator role, or a tool's free-text success message as approval. Model confidence cannot lower the action's risk class. Step-up authentication and independent review are appropriate when required by the product's consequential-action policy.

## Untrusted input, retrieval, and memory

Keep trusted instructions and policy separate from retrieved content, browser pages, emails, documents, images, code, tool descriptions, and tool results. Label provenance and trust throughout transformations. Delimiters, filters, and a second model are useful signals; application permissions must still hold if those signals fail.

Enforce tenant and document access before retrieval results enter model context, including caches, embeddings, rerankers, summaries, exports, and debug views. Recheck access when references are reused after revocation. A prompt asking the model to ignore unauthorized documents cannot repair disclosure that already occurred.

Separate working memory from approved configuration and authorization state. Bound memory by principal, tenant, purpose, size, and retention. Give persistent entries a source, writer identity, trust classification, timestamp, and version. Validate writes, resolve conflicting updates, and support deletion and quarantine. A model must not promote its own speculative summary into trusted policy, system instructions, or another tenant's facts.

Where tampering matters, enforce write access and verify integrity using established authenticated mechanisms. A checksum of attacker-controlled data only detects accidental corruption; it does not establish authenticity. Test reindexing, compaction, and summarization paths because they can erase provenance or reintroduce removed content.

## Credentials, egress, and execution isolation

Keep credentials outside prompts, tool responses, memory, and user-visible logs. Broker short-lived credentials with restricted audience, operation, resource, and lifetime. Protect token renewal and revocation. Do not forward a caller's token to arbitrary tools or accept an unverified identity supplied by a model or another agent.

Before sending protected data to inference, embedding, reranking, evaluation, or telemetry services, enforce the approved provider, account, endpoint, model, and data-class policy. Include configured restrictions on retention, training use, processing location, and prompt caches where applicable. A caller's permission to read a record does not establish permission to disclose it to an external provider. Keep routing under trusted configuration. Fallbacks and debug tracing must preserve the same constraints; if no approved route is available, stop that transmission. Verify provider configuration and commitments as well as application behavior, and record anything that cannot be independently tested.

Represent external destinations as approved resources where possible. For necessary arbitrary URL access, restrict schemes, hosts, ports, and resolved addresses; account for redirects, alternate address representations, DNS changes, and proxy behavior. Block access to cloud metadata and internal services unless explicitly required and independently authorized. Validate at connection time and enforce network policy as a second boundary. Restrict file paths against traversal, symlink escape, and mount boundaries using the platform's supported safe APIs.

Prevent outbound tools from sending data to unauthorized recipients even when the tool itself is permitted. Apply data classification, destination authorization, and payload limits to browser requests, uploads, notifications, and agent messages. Pattern-based redaction cannot reliably identify every encoded secret. Minimize the data and network access available to the agent first.

Run untrusted generated code, dependencies, and notebooks in disposable isolation with no ambient production credentials, host sockets, or broad writable mounts. Restrict privileges, filesystem access, network access, CPU, memory, processes, output size, and duration. An application-level timeout alone does not stop an escaped process. Containers require a justified isolation configuration; higher-risk execution may need a stronger boundary. Pin the execution image and enforce termination outside the worker.

Treat rendered output as untrusted at its destination: escape HTML, validate links and attachments, restrict active content, and sanitize structured output before downstream interpretation. A JSON schema checks structure; it does not establish permission or safe business semantics.

## Delegation, queues, and resource budgets

Authenticate agent and service peers, encrypt transport for protected data, validate message schemas, and constrain delegation to the intersection of caller authority, agent policy, and task need. Carry tenant, initiating actor, task/run ID, allowed actions/resources, audience, expiry, and correlation data through a trusted transport or verified envelope. Identity establishes who sent a message; it does not make every claim inside the message true.

Do not permit a worker to mint broader authority, delegate indefinitely, or switch to a more privileged route after denial. Protect against duplicate, expired, reordered, or cross-run messages where they could cause effects. Revalidate current permissions when queued work runs. Revoking the parent task must prevent new effects by its descendants.

Enforce cumulative budgets across the full run and its descendants: elapsed time, iterations, tool calls, model tokens or cost, retries, parallel workers, and expensive external operations. Use trusted shared accounting when work spans processes. Child budgets consume the parent allocation; spawning a child cannot reset it. A model upgrade or fallback must preserve the same authority and limits.

Make retries bounded and distinguish transient errors from policy denials. Use backpressure and circuit breakers to contain dependency failure. Stop safely when permission, policy, or required approval cannot be verified. Define what happens when audit storage or dependencies fail before a consequential effect. Prefer a durable local audit/outbox mechanism over silently losing the event; operations requiring an audit record must not proceed without one.

## Supply chain and operations

Inventory models and versions, orchestration code, tools, MCP servers, skill packages, prompts, policies, evaluation data, and deployment artifacts. Pin reviewed dependencies and preserve provenance. Compare requested permissions and exposed tool schemas on upgrades. A remote tool description or signed package can still contain unsafe behavior. Do not let dynamic discovery silently expand permissions or execute install hooks.

Record structured events for requests, policy decisions, approvals, dispatch, verified results, and failures. Include actor, tenant, run, tool/version, policy version, target reference, reason code, and correlation ID as appropriate. Store only the necessary redacted parameters or protected references. Restrict and retain logs according to their sensitivity. Avoid raw secrets and private model reasoning. Do not let the agent erase or falsify the authoritative audit record.

Implement suspension, token revocation, queue cancellation, and rollback or compensating actions where supported. State which external effects are irreversible. Keep a tested recovery path for polluted memory or indexes. Reassess the affected controls after changes to models, prompts, tools, permissions, retrieval, or deployment boundaries. Set monitoring thresholds and review frequency according to impact and observed failures.
