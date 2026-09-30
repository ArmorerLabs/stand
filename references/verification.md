# Verification and release evidence

Choose tests based on the application's reachable boundaries and the task's changes. Use the repository's language and test runner. Do not call live targets, incur substantial model costs, or use real secrets as part of an unapproved test.

## Test the enforcement path

Drive the public request or job entry point through the real application policy and dispatcher into a controlled adapter. Record whether protected data was read, outbound traffic occurred, state changed, and an audit event was produced. When isolating policy logic in a unit test, also cover the integration path that could bypass it. A test of an unused helper provides no evidence about the running application.

Supply crafted model proposals directly so dangerous actions are tested regardless of whether today's model chooses them. For every meaningful denial, include an authorized success case that proves the application still works. Check that denied requests cause no downstream read or effect. Verify error handling does not retry through a weaker path.

Use the OWASP matrix to select cases. Frequently important combinations include:

- A retrieved document or tool response asks for a forbidden action, including after memory summarization or agent delegation.
- A valid user requests another tenant's object, or a cached/retrieved record survives permission revocation.
- An authorized read is routed to an unapproved inference, embedding, reranking, fallback, or telemetry endpoint. Observe that the endpoint receives no protected payload while an approved route still works.
- Arguments contain forged roles, approval flags, an unregistered tool, extra fields, unsafe amounts, or a destination outside scope.
- An approved action is changed, replayed concurrently, resumed after expiry, or executed after user/parent-task revocation.
- The policy service, credential service, audit sink, or external adapter fails; a timeout occurs after the external effect may have committed.
- A child agent exceeds delegated permissions, reuses an old message, or tries to reset the shared budget.
- Cancellation arrives while work is queued or running; assert no new effects begin after revocation takes effect and document in-flight limits.
- Poisoned memory, a changed tool schema, or an unreviewed dependency update crosses a previously trusted boundary.

Simulated outputs cannot establish actual sandbox isolation or egress filtering. Test those properties using the configured runtime and controlled network/file targets, or mark them unverified. Browser approval UX needs appropriate integration or browser evidence when the task changes it; a model transcript cannot establish UI security.

## Evaluate model behavior separately

When useful, run a bounded adversarial evaluation against representative user inputs, documents, tool results, and multi-turn workflows. Pin model and configuration, tool set, prompt/policy versions, corpus, and environment. Record the number of cases and repeated trials. Distinguish intent, attempted tool use, allowed execution, and harmful effect.

A fake tool transcript demonstrates behavior in that simulation. A controlled real adapter demonstrates only the configured boundary. Neither establishes a production attack rate. Report failures, uncertainty, unsupported attack surfaces, and false refusals of authorized actions. Evaluate fallback models and changed capabilities when their behavior affects risk.

## Record the result and gate the release

Use a case record with: threat and precondition, controlled input, expected invariant, actual observation, execution command, environment/configuration, result, and evidence location. Redact secrets and identify unavailable infrastructure. Mark controls as implemented-and-verified, implemented-but-unverified, planned, not-applicable-with-reason, or failing. Record organizational work separately when it cannot be completed by a code change.

Block readiness claims for unresolved critical failures such as unauthorized protected data access, privilege escalation, unapproved consequential effects, or escape from an intended execution boundary. Establish other acceptance criteria according to the application's consequence and exposure before evaluating it. Passing a control matrix or a scanner is not a universal security score.

Use existing CI to run deterministic security regressions whenever their protected boundary changes. For new consequential capabilities, include the relevant tests in the required merge/release checks where authorized. Test configuration and required-check enforcement are separate facts. Report whether repository enforcement was actually inspected or configured. Protect test and policy modifications through the repository's normal review permissions.

Record the accountable owner, remaining risks, compensating controls, expiry of any exception, and conditions that trigger another review. The coding agent may propose these fields; it must not invent owner acceptance. Continue authorized implementation and report a concrete remaining dependency when verification or a release decision needs an external party.
