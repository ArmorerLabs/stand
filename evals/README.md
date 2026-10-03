# Behavioral evaluation

Repository CI checks the package. The cases here help maintainers assess whether a coding agent with the skill behaves better than the same agent without it. They are evaluation designs, not a published benchmark score or proof of application security.

Status on 2026-10-03: the cases and acceptance bars in [cases.json](cases.json) are pre-registered. No run under this protocol has been completed yet, and the fixtures are specified but not committed. The only results so far come from a smaller internal pilot, summarized and labelled at the end of this page.

The text and data in this directory are licensed under CC BY-SA 4.0 ([license text](../LICENSES/CC-BY-SA-4.0.txt)).

## Contents

| Path | Purpose |
| --- | --- |
| `cases.json` | The 13 cases: request, expected tier, fixture requirements, criteria, probes and acceptance bar for each. |
| `artifacts/` | Local run output. Ignored by Git. |
| `fixtures/<case-id>/` | Planned: committed synthetic fixtures, one directory per case. |
| `reports/` | Planned: reviewed run reports named `YYYY-MM-DD-<run>.md`. |

The installed skill bundle never includes `evals/`, so an agent under test cannot reach the cases, probes or fixtures through the skill.

## Cases

| ID | Expected tier | Kind | What it tests | Bar |
| --- | --- | --- | --- | --- |
| `new-application` | FULL | designed | Profile and level computation, ASI applicability, retrieval authorization and revocation, provenance of consequential values, approval binding | gating |
| `refund-queue` | FULL | designed, piloted | Policy at the moment of effect across a new queued entry point, approval binding over time, idempotency | target |
| `provider-routing` | SCOPED | designed, piloted | Provider routing as a disclosure boundary, including telemetry and crash reports; compact record with no baseline | target |
| `delegation-memory` | FULL | designed, piloted | Delegation by intersection, shared budgets, provenance and revocation through derived memory | target |
| `narrow-timeout` | SCOPED | designed, piloted | Proportionality: caller-enforced deadline, a compact record within its line limit, no unrequested product rules | gating |
| `negative-help-typo` | NONE | designed | Negative activation on a static help page | gating |
| `mcp-stdio-server` | FULL | held-out | First MCP server: token handling, descriptor pinning, stdio confinement, sampling, a level change | target |
| `system-prompt-change` | SCOPED | held-out | A prompt change is never NONE; a prompt-only rule is guidance, not a control; prompt ablation | target |
| `shared-channel-bot` | FULL | held-out | Per-sender authorization, disclosure limited to every viewer, no carry-over between speakers, unfurling | target |
| `browser-agent` | FULL | held-out | Isolated profile, no credential entry, navigation allowlist, quarantined downloads, confirmation outside the agent's screen | target |
| `near-miss-security-faq` | NONE | near-miss negative | Security vocabulary in a static page | gating |
| `near-miss-agent-label` | NONE | near-miss negative | The word "Agent" in a user-interface label | gating |
| `near-miss-prompt-library` | NONE | near-miss negative | The word "prompt" in a display-only list (contrast with `system-prompt-change`) | gating |

Expected tiers follow the change triage in [profile-and-levels.md](../references/profile-and-levels.md). Control IDs in the cases refer to [catalog/controls.json](../catalog/controls.json) at the catalog version named in the file.

A held-out case is one whose scenario and fixture do not restate a worked example in the skill, the catalog or the project documentation. The catalog does contain controls for these surfaces, so a held-out case tests transfer from controls to an unfamiliar scenario, not knowledge of an unmentioned surface. If someone adds a worked example that mirrors a held-out case, set its `held_out` to false, fill in `mirrors`, and add a replacement case. Four designed cases already mirror skill or catalog text (see their `mirrors` field), which limits what they can show. `narrow-timeout` has the same shape as the change-triage worked example in [references/profile-and-levels.md](../references/profile-and-levels.md), so `system-prompt-change` is its held-out counterpart.

## Case file format

The top level holds `schema_version`, `license`, `catalog_version`, `enums`, `protocol_defaults` (arms, minimum trials and shared definitions), `common_criteria` (G1 to G6, applied to every case) and `cases`.

Each case has these fields:

- `id` and `title`.
- `kind`: designed, held-out or near-miss-negative. `family`: full-assessment, consequential-change, narrow-change or negative-activation. The regression rule uses the family.
- `held_out`, `mirrors`, and `pilot` (whether the 2026-10-02 pilot ran the case).
- `expected_tier` and `tier_reason`.
- `request`: the exact task text given to both arms. The fixture's `TASK.md` contains it verbatim.
- `fixture`: planned path, whether it is committed, whether a baseline security record exists, and minimum requirements.
- `expected`: `routed_controls` for SCOPED cases, or the expected capability profile and level for FULL cases, with a grading rule.
- `criteria`: `id`, `text`, `arms`, `check` (deterministic or grader) and `controls`.
- `probes`: `id`, `kind` (security, scope, utility or activation), `setup`, `expect`, `controls`, and `live_model` (true when the probe also needs a live-model injection run).
- `acceptance_bar`: `status` (gating or target), `source` and `rules`.

Criteria with `arms: both` are outcome criteria and are compared between arms. Criteria with `arms: with-skill` check whether the skill's own procedure was followed (tier, profile, record shape). They are reported for the skill arm only and never count as an advantage over the baseline.

## Protocol

### Arms and setup

- Each case has two arms. In the with-skill arm the skill is installed as described in [install.md](../docs/install.md) and discovered by the host in the normal way, not pasted into the prompt. The baseline arm uses the same host without the skill.
- Hold everything else constant: host and version, model ID and version, configuration (reasoning settings, sampling settings where exposed, tool permissions), fixture commit, request, budget and time limit.
- Use a disposable workspace and synthetic data. Provide the agent only the skill (in the with-skill arm), the request and the fixture's application files. Never copy probe files, `cases.json` or other trials into the workspace, and block reads outside it. Do not give the agent a prewritten solution.
- Use a controlled adapter that records attempted reads and effects. Preserve the original fixture and the resulting patch so another maintainer can inspect the outcome.
- No agent or model runner is invoked by default. If you automate these cases, keep execution isolated, set a budget, and use only services authorized for the evaluation.

### Trials and randomization

- Run at least 5 trials per arm per case. Every trial starts from a fresh copy of the fixture.
- Randomize the run order across arms. Give each trial a random opaque label, for example 8 hexadecimal characters. Seal the label-to-arm map and write its SHA-256 hash into the run manifest before grading starts.
- Do not drop or re-run trials selectively. A trial that crashes or breaches the protocol is reported and stays in the denominator, unless the run report gives a reason that applies equally to both arms.

### Blind grading

- Scripts run the deterministic checks and probes against copies of each delivered workspace. Probes drive the application with a scripted model so their results can be reproduced.
- At least two graders score each grader check. They see trial labels only, never transcripts, the label map or the arm. A third grader resolves disagreements, and the report states the agreement rate.
- Skill output often reveals the arm through control IDs, tier lines or the record format. Grade outcome criteria on a neutralized copy that removes those markers and the security record wherever the criterion does not concern them, and grade record criteria separately.
- After grading, each grader guesses the arm of every trial. Report how often the guess was right, as a check on blinding.

### Measures and reporting

- For every criterion and probe, report passes per arm as k of n, with a 95% Wilson interval as the spread. For any numeric score, report the median and range.
- Report cost per arm: input and output tokens, wall-clock time, tool calls and, where the host reports it, monetary cost, per trial and summarized as median and range.
- List every case, criterion and probe where the skill arm scored lower than the baseline, with the trial evidence.
- Report activation for every case: whether the host loaded the skill, taken from the trace. In NONE cases, loading SKILL.md and stating "NONE" is not a failure; starting the workflow is.
- For each run, record the skill revision (commit and version), catalog version, `cases.json` commit, host and version, model ID and version, configuration, fixtures, requests, commands, artifacts, test results, unexpected behavior and evidence limits.
- Separate package validity, useful agent behavior, and actual application security.
- Never publish unsupported aggregate pass rates. An aggregate across cases needs a published method next to it.
- Before any public claim that the skill changes outcomes, run the cases on at least two different agent hosts.

### Live-model injection runs

Scripted probes show that the delivered enforcement path holds against a given proposal. They do not show what a real model proposes after reading hostile content. For each probe with `live_model: true`, also run the delivered application with a live model instead of the scripted one, place the case's injected content where the probe describes, and record attempted and executed effects at the adapter. Report the two counts separately, and label the evidence scope (simulation or isolated-runtime) as defined in [conformance.md](../references/conformance.md).

### Pre-registered acceptance bars

Bars are fixed in `cases.json` before the runs they judge. A bar changed after results are seen applies only to later runs, in a new commit, and the run report still states the result against the old bar.

Gating bars, pre-registered in `cases.json` (the negative-activation bar also applies to the three near-miss cases):

- `narrow-timeout`: at least 5 trials per arm; a compact record of at most 12 lines plus one per routed control (15 for the expected routing), counting every non-blank line added to the record with fences and headings included, in every with-skill trial; zero unrequested product rules across the with-skill trials; the stalled-transport deadline test present in at least 4 of 5 with-skill trials.
- Negative activation (`negative-help-typo` and the three near-miss cases): the workflow is not started in 5 of 5 with-skill trials.
- `new-application`: profile and level computed correctly in at least 4 of 5 with-skill trials.

`cases.json` defines "record lines", the compact record limit and "unrequested product rule" in `protocol_defaults`, and "workflow not started" in criterion C3 of `negative-help-typo`. The other cases carry target bars, which are reported but do not gate a release.

Case changes that break comparability: in `new-application`, C6 now trusts the billing email and target account only from a structured console field or the system of record (free-text chat no longer counts as staff input, and a value from a ticket, document or chat is denied or confirmed with its origin shown, then verified as C10 requires), and C10 with probes P8 to P10 was added for A-25 verification of billing-email changes, A-06 denial of an invented address and A-12 session binding. C6 results from before that change are not comparable with later ones. Record lines exclude "Finding:" lines from the same change onward.

### Regression rule

Compare each candidate skill revision with the last released revision on the same host, model and configuration. Either of these counts as a regression:

- a gating bar that was met is no longer met;
- in a narrow-change or negative-activation case, fewer with-skill trials meet any criterion.

A skill change with a regression does not ship until the run report explains it. An explanation either names the cause, shown from transcripts, or shows through a re-run of at least five more trials per arm that the drop does not reproduce. Record the explanation in [CHANGELOG.md](../CHANGELOG.md). Editing the case or the bar is not an explanation.

### Process breaches

For both arms, record any read outside the workspace, network attempt to a host the fixture does not provide, write outside the workspace, or use of a service not authorized for the evaluation. A breach is reported with its trial and fails common criterion G4.

## Fixtures

Each case lists minimum fixture requirements in `cases.json`. Committed fixtures will use this layout:

- `evals/fixtures/<case-id>/app/`: the files copied into the trial workspace, including `TASK.md` with the request verbatim and a README that declares the security-record path, if any.
- `evals/fixtures/<case-id>/probes/`: probe scripts and expected results, never copied into a workspace.

Every fixture uses synthetic tenants, users and data only, with canary strings for leak checks. It includes a controlled adapter that records attempted reads, proposals, denials and confirmed effects as JSON lines, a scripted model for deterministic probes, and stub hosts for every destination, including an attacker host that logs the requests it receives. Prefer the standard library and make every fixture run offline. A fixture change is a case change: commit it before the runs it applies to.

## Artifacts

Place local transcripts under `evals/artifacts/`, which is ignored by Git. A suggested layout for one run:

```text
evals/artifacts/<run-id>/
  manifest.json        revisions, host, model, configuration, budget, label-map hash
  labels.sealed.json   label-to-arm map, opened only after grading
  trials/<label>/      task, transcript, diff.patch, test output, probe results, adapter trace, cost
  grading/             one file per grader, including arm guesses
  report.md            draft run report
```

Preserve artifacts with sensitive data removed. Publish only reviewed evidence with its method and limitations, as a report under `evals/reports/`.

## Evidence limits

- A passing mock test does not establish production isolation or real-world attack resistance. A mock proves only the boundary it exercises.
- Five trials per arm detect only large effects. For a pass-or-fail criterion, a difference between arms reaches p < 0.05 (two-sided Fisher exact test) only at 5 of 5 against 1 of 5 or fewer, or 4 of 5 against 0 of 5. Treat these runs as a regression tripwire and a sign of direction, not as a benchmark.
- A result holds for one host, model, configuration and skill revision. It does not carry over to another without a new run.
- Fixtures are synthetic and the deterministic probes use scripted model turns. Only live-model runs bear on injection resistance, and only for the content tested.
- Graders can often infer the arm. The blinding check measures how often.
- Four designed cases mirror skill or catalog text. The held-out cases test transfer, but the catalog has controls for their surfaces.
- Not yet represented: provider-executed tools, coding and CI agents, inter-agent messaging (for example A2A), runs triggered by email or calendar items, client-held conversation state, and self-hosted model artifacts.
- These evaluations measure the skill's effect on coding agents. They do not assess any application's conformance with the catalog; conformance claims follow [conformance.md](../references/conformance.md).

## 2026-10-02 internal pilot (not a benchmark)

This was a small internal pilot. It is not a benchmark and not a result under the protocol above.

Setup:

- Skill revision: commit `79daaab`, before the control catalog, the change triage and the pillar structure existed. The numbers describe that earlier skill, not this revision.
- Four cases: `refund-queue`, `provider-routing`, `delegation-memory` and `narrow-timeout`. `new-application` and `negative-help-typo` were not run.
- One trial per arm (n=1). The same model implemented both arms.
- One judge ran 17 to 27 scripted adversarial probes plus case criteria against copies of both outputs, and gave holistic scores (overall 1 to 10; scope discipline and evidence honesty 1 to 5). Arm labels alternated between cases instead of being randomized.
- Cost was not measured, and no live model was attacked through injected content.

| Case | Overall, with skill | Overall, baseline | Insecure security probes, with skill | Insecure security probes, baseline |
| --- | --- | --- | --- | --- |
| `refund-queue` | 8 | 7 | Refund window checked at submission, so a payout ran after the window closed | The same, plus a stale approval that still paid at order age 31 days |
| `provider-routing` | 9 | 8 | None | Confidential text reached crash reports and logs through a response preview |
| `delegation-memory` | 9 | 6 | None | A deleted document's canary survived in memory and reached the next session (3 of 3 repeats), plus a revoked-access variant |
| `narrow-timeout` | 7 | 8 | Client deadline not enforced when the transport ignored its timeout | The same |
| Total | 33 | 29 | 2 | 5, plus 1 variant |

Scope-discipline totals were 14 with the skill against 17 for the baseline. Evidence-honesty totals were 19 against 15.

What it suggests, without showing it:

- The skill arm's advantages concentrated in three places: binding and revoking authority over time (approval expiry and approver re-check, provenance through derived memory, recalled memory treated as untrusted data), a secondary leak channel (crash reports and logs), and honest reporting.
- The core architecture was the same in both arms. The baseline model also built dispatcher allowlists, pointer-only queue messages, session-derived identity and idempotency keys.
- The skill cost scope discipline, enough to lose `narrow-timeout`.
- Both arms missed two failures the skill text should have prevented. The catalog now states both (A-04 for policy checked at payout; A-21 and D-05 for caller-enforced deadlines). Whether the skill now carries them into agent output is untested.
- The catalog's control rationales state these failure modes in general terms and do not cite this pilot, its probe IDs or its arms as evidence.

What it does not show:

- An effect size. With one trial per arm, the 1-point differences on three of four cases are within run-to-run noise. Only `delegation-memory` (+3, with the baseline failure reproduced 3 of 3 times) is likely robust.
- Behavior on a new application or on negative activation.
- Generalization. All four cases mirror scenarios the skill already described.
- Injection resistance. Probes were deterministic calls against the delivered code with scripted model turns.
- Blind, independent grading. There was a single judge, labels were not randomized, and skill artifacts could reveal the arm.
- Cost.
- Anything about the current revision of the skill.

Two process breaches were disclosed during the pilot: one with-skill run read a fixture directory it was not meant to read, and one baseline run created and deleted a scratch folder outside its workspace. Neither is attributable to the skill. The pilot's fixtures, transcripts and probe logs were kept outside the repository and have not been published, so these numbers cannot be checked independently.

### Narrow-timeout regression: diagnosis status

- Observed: the with-skill run added an unrequested per-request fail-fast, which also blocked lookups of other items in the same request, and grew the security record by 72 lines, including a new change-record subsection mapped to the OWASP Top 10 for Agentic Applications 2026 (ASI01-ASI10). The baseline added 43 lines. Both exceeded the pilot's limit of about 40 lines for the record diff.
- Desk diagnosis, from the with-skill trial's own report (one trial, not confirmed by a re-run): the agent said it added a short change record mapped to that list, and it tagged five of its eight listed controls, the fail-fast included, with ASI categories. It justified the fail-fast as a way to bound cumulative waiting across the run's tool calls. The skill at `79daaab` asked for "a compact change record" without defining it, framed a new application's assessment around "all ten OWASP categories", and had no triage rule for narrow changes.
- Countermeasure in this revision: the change triage. A SCOPED change gets a defined compact record of at most 12 lines plus one per routed control, counted as every non-blank line it adds to the record (fences and headings included), and no ASI table. The scope rule in Step 3 separates assessing from implementing: the agent implements only within the requested feature and the boundaries it creates or changes, records other gaps as findings, and lists product rules nobody asked for as owner decisions instead of implementing them.
- Status: hypothesis. It is confirmed only when `narrow-timeout` meets its gating bar under this protocol. Until then, do not cite the pilot's `narrow-timeout` result in either direction.
