# Framework basis, mappings and related work

Source snapshot checked **2026-10-03**. The catalog's controls are an engineering synthesis informed by the sources in this file. They do not reproduce any standard, and they establish no certification, no conformance to a source framework and no guarantee of complete threat prevention. A mapped requirement is not evidence that an application's control works. What a claim against the catalog means is defined in [conformance.md](conformance.md).

## Source snapshot

| Source | Edition pinned | Status at check (2026-10-03) | Recheck when |
| --- | --- | --- | --- |
| [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) | Version 2026, December 2025 | Current edition | A new edition is published |
| [AIUC-1](https://standard.aiuc-1.com/changelog/) | Release of July 15, 2026 | Still the most recent release; the changelog announces the next release for October 15, 2026 | Every release, using the AIUC-1 recheck protocol below |
| [NIST AI RMF 1.0, NIST AI 100-1](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf) | January 2023 | NIST states that AI RMF 1.0 is being revised as part of the White House AI Action Plan; no revised draft was posted on the [AI RMF page](https://www.nist.gov/itl/ai-risk-management-framework) | A revised AI RMF is published |
| [Generative AI Profile, NIST AI 600-1](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf) | July 2024 | Current edition | A revision is published, or a revised AI RMF renumbers the subcategories its action IDs follow |
| [ISO/IEC 42001:2023](https://www.iso.org/standard/42001) | Edition 1, published 2023-12-18 | Current edition per the [IEC webstore listing](https://webstore.iec.ch/en/publication/90574) | An amendment or a new edition is published |
| [OWASP AISVS](https://github.com/OWASP/AISVS) | 1.0, June 2026, read from the locked `1.0/en` folder at commit 94fbad5 | Current release; the project states that identifiers in the locked folder will not change | A later AISVS release |
| Related OWASP projects and NIST work | Versions and dates in the tables below | Each item checked on 2026-10-03 | A new version of the item |

Record every recheck, with its date and result, in the repository changelog, and update this table. Protocol versions that controls depend on, such as the Model Context Protocol specification, are pinned in [mcp.md](mcp.md).

## Basis and related work

The basis is fixed. The OWASP Top 10 for Agentic Applications 2026 is the risk taxonomy. AIUC-1, NIST AI RMF 1.0 with NIST AI 600-1 as supporting guidance, and ISO/IEC 42001 themes are the supporting sources. Related work informs controls and is cross-referenced, but it does not extend the basis.

| Group | Source | Role | Where it appears |
| --- | --- | --- | --- |
| Basis | OWASP Top 10 for Agentic Applications 2026 (ASI01-ASI10) | Risk taxonomy. Each control lists the ASI risks it is designed to address. | `asi` field; [owasp-agentic-top-10.md](owasp-agentic-top-10.md); [controls/index.md](controls/index.md) |
| Basis | AIUC-1 | Requirements and evidence expectations for agent security | `aiuc1` field, cited at control level (for example B006.1) |
| Basis | NIST AI RMF 1.0, with NIST AI 600-1 as supporting guidance | Risk-management outcomes and suggested actions | `nist` field: subcategories (for example MANAGE 2.4) and suggested actions (for example MG-2.4-002) |
| Basis | ISO/IEC 42001:2023 | Management-system themes only | This file; no field, no clause or Annex references |
| Related OWASP | OWASP AISVS 1.0 | Verification requirements, cross-referenced by identifier | `aisvs` field (for example v1.0-C9.2.8) |
| Related OWASP | Agent Control Standard, Securing Agentic Applications Guide, Agentic AI Threats and Mitigations, AI Testing Guide, AIVSS, Agentic Skills Top 10, GenAI Security Industry Framework Crosswalk, Cheat Sheet Series | Design, testing, scoring and runtime-hook guidance | Listed in this file; not mapped per control |
| Related NIST | Agent-security research and projects from NIST and its Center for AI Standards and Innovation (CAISI) | Further reading | Listed in this file; not mapped |
| Related work | [Meta's Agents Rule of Two](https://ai.meta.com/blog/practical-ai-agent-security/), [Willison's lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/), [AWS Agentic AI Security Scoping Matrix](https://aws.amazon.com/blogs/security/the-agentic-ai-security-scoping-matrix-a-framework-for-securing-autonomous-ai-systems/), [Design Patterns for Securing LLM Agents against Prompt Injections](https://arxiv.org/abs/2506.08837), [CaMeL](https://arxiv.org/abs/2503.18813) | Capability and autonomy scoping, and injection-resistant separation patterns | [profile-and-levels.md](profile-and-levels.md), [runtime-controls.md](runtime-controls.md) and control rationale (R-02, A-08, I-02) |
| Related work | [CSA MAESTRO](https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro) (Cloud Security Alliance, February 2025; checked 2026-10-03) | Agentic threat-modeling method; related work, not mapped | Listed in this file only |

## How mappings work

Fields. Every catalog control carries an `asi` field and a `mappings` object with three lists, `aiuc1`, `nist` and `aisvs`, whose entries hold a `ref` and a `relation`:

- `asi`: the ASI risks the control is designed to address. These identifiers place the control in the risk taxonomy; they do not claim that the control fully covers a risk.
- `aiuc1`: AIUC-1 control IDs (for example B006.1) rather than bare requirement IDs, because core and supplemental controls carry different weight.
- `nist`: AI RMF 1.0 subcategories (for example MANAGE 2.4) and NIST AI 600-1 suggested-action IDs (for example MG-2.4-002).
- `aisvs`: OWASP AISVS 1.0 requirement IDs in the version-prefixed form the AISVS project recommends (for example v1.0-C9.2.8). Items from AISVS Appendix C (AI-Assisted Secure Coding) are cited as v1.0-AC.x.y.

ISO/IEC 42001 has no field (see the ISO/IEC 42001 section).

Relations. Each `aiuc1`, `nist` and `aisvs` entry states how closely the cited external requirement corresponds to the control:

- **direct**: the external requirement covers essentially the same obligation as the control.
- **partial**: the external requirement covers part of the control, or the same obligation in a narrower scope (for example MCP only, code-generating products only, or organization level).
- **supports**: the external requirement helps implement or evidence the control but is not equivalent to it.

No mapping in catalog 0.1.0 is direct. AI RMF subcategories are never marked direct, because each one includes organization-level outcomes that no single control meets, and no AI 600-1 action is marked direct either. A direct relation does not carry over the source's own conditions: AIUC-1 scoping, frequencies, third-party testing and auditor judgment still apply.

Other rules:

- Mappings are many to many. A control can cite several items, and one item can appear under several controls. A mapping never merges or restates a source requirement.
- An empty list means that no counterpart more specific than a generic anchor was found, not that the control matters less. Only I-04 has no AIUC-1 counterpart. AISVS has no counterpart for, among others, task-scope binding (A-07) and the system of record for consequential facts (I-08).
- [mappings.md](mappings.md) lists every control's mappings and relations. It is generated from the catalog by the repository's render script and is never edited by hand.
- In the source repository, `catalog/mappings.json` holds the justification for each mapping entry, its source URL and the source version checked. It is not part of the installed skill. Justifications paraphrase the sources and reproduce no AIUC-1 text.
- Control citations use the bare catalog ID (A-06). Records, claims and external mappings use the version-pinned form described in [profile-and-levels.md](profile-and-levels.md). Foreign identifiers sit in their own labeled columns, never in a control ID column.
- Catalog levels are computed from the capability profile, while AISVS levels are assurance depths an organization selects, so the scales are not interchangeable. Approval binding (A-11) is Level 1 here, while v1.0-C9.2.8, which partly corresponds to it, is AISVS Level 3 ([profile-and-levels.md](profile-and-levels.md)).

## AIUC-1

### Snapshot and structure

The mapping pins the AIUC-1 release of July 15, 2026, per the [official changelog](https://standard.aiuc-1.com/changelog/). On 2026-10-03 it was still the most recent release, and the changelog announced the next release for October 15, 2026.

How AIUC-1 is structured ([scoping](https://standard.aiuc-1.com/scoping), [January 15, 2026 changelog](https://standard.aiuc-1.com/changelog/2026-01-15)):

- AIUC-1 requirements are mandatory or optional, and a requirement becomes optional when the agent lacks the capability it addresses. Each requirement carries capability tags, for example Universal, Automation, Code-generation or External-facing.
- Each requirement lists core controls ("Should include") and supplemental controls ("May include"); auditors may accept alternative evidence that meets the requirement. Organizations opt into supplemental controls where they are relevant; supplemental controls are not needed to pass.
- Scoping ends in a Statement of Applicability signed off by the auditor. A mandatory requirement can be scoped out only with a documented, legitimate business reason that the auditor accepts.
- Frequency is an attribute of the requirement: every 3, 6 or 12 months. A 12-month frequency does not mean the controls behind it run once a year; access checks still run on every request.
- The certificate is valid for 12 months, and evaluations are needed at least every 3 months to keep it valid ([FAQ](https://standard.aiuc-1.com/faq)). B001 and D004 call for testing by expert third parties every 3 months, as do D002, C010 and C011 (hallucination, harmful-output and out-of-scope-output testing, outside this skill's scope) and C012 (customer-defined risks). Internal tests run with this skill do not satisfy these requirements. They produce a test corpus, reproducible results and remediation records that an assessor can use.

This skill's approval, containment, and logging recommendations may be stricter than a particular AIUC-1 control. They are not universal mandates attributed to AIUC-1.

### Requirement-level orientation

This table covers the requirements most relevant to agent security engineering. It is a selective mapping, not the full standard. Its Application column records whether a requirement is mandatory or optional, and the sentence after the table does so for the other cited requirements; mapping justifications do not repeat it. Topics are this project's short descriptions, not AIUC-1 titles; the linked page gives the current title. The ASI column comes from AIUC's [hosted OWASP mapping](https://standard.aiuc-1.com/crosswalks/owasp-agentic-top-10) (last updated May 27, 2026). The catalog column lists controls with a direct or partial relation, grouped by the AIUC-1 control they cite; [mappings.md](mappings.md) also lists supporting relations.

| Requirement | Topic | Application; capability; frequency | ASI (AIUC mapping) | Catalog controls (direct or partial) | Notes |
| --- | --- | --- | --- | --- | --- |
| [A003](https://standard.aiuc-1.com/data-and-privacy/implement-contextual-data-safeguards) | Task-scoped data access | Mandatory; Universal; 12 months | ASI02, ASI06 | A-03, I-06 (A003.1); A-17 (A003.2); A-15 (A003.3) | Core A003.1: data access scoped to the task and enforced in code before context construction and tool execution. Supplemental: per-agent identity (A003.2) and narrowly scoped, non-inherited agent permissions (A003.3). |
| [A005](https://standard.aiuc-1.com/data-and-privacy/prevent-cross-customer-data-exposure) | Isolation between customers | Mandatory; Universal; 12 months | ASI06 | I-06, I-07 (A005.2) | Core A005.2: tenant isolation in retrieval, memory, caches and output, with isolation tests. Core A005.1 (customer consent for combined data use) is contractual work outside this skill. |
| [A008](https://standard.aiuc-1.com/data-and-privacy/prevent-secrets-leakage) | Secrets in code-generating products | Mandatory; Code-generation; 12 months | Not in the AIUC mapping (added July 2026) | None; supports only (I-05, I-23, E-01) | Applies only to products that generate code for their users: secrets detection in user inputs (A008.1) and in generated code (A008.2), and credential storage from which credentials are fetched only at tool invocation (A008.3). For other agents, AIUC-1 has no direct equivalent of A008.3; record credential scoping and rotation under A003.3 (supplemental) and B008.2 (core). |
| [B001](https://standard.aiuc-1.com/security/test-adversarial-robustness) | Independent adversarial testing | Mandatory; Universal; 3 months | ASI01, ASI06 | S-04, S-08, S-09 (B001.1) | A test corpus, reproducible results, and remediation records that support independent assessment. Internal tests do not satisfy the third-party requirement. The B001.1 report states the risk taxonomy tested (C001). |
| [B002](https://standard.aiuc-1.com/security/detect-adversarial-input) | Detecting attack inputs | Optional; Universal; 3 months | ASI01, ASI06 | None; supports only (I-01, I-03, E-04, E-08) | Detectors are recorded as signals routed to an owner (E-04), never as the boundary that stops an attack (I-01). |
| [B006](https://standard.aiuc-1.com/security/enforce-contextual-access-controls) | Limits on agent actions and reach | Mandatory; Automation; 12 months | ASI01, ASI02, ASI03, ASI05, ASI07, ASI10 | R-03, A-09, I-11, I-12, I-18 (B006.1); E-04, E-05 (B006.2); A-01, I-05, I-15, I-18, I-19, I-23 (B006.3) | Core: limits on the services, endpoints and tool servers an agent can reach (B006.1), and monitoring with alerts on unauthorized actions (B006.2). Denial tests prove enforcement; B006.2 also needs production logging and alerting on boundary violations. Supplemental B006.3 covers execution-level safeguards such as sandboxing, tool-definition change monitoring and pre-execution authorization hooks. Where the application itself loads skills, hooks or MCP tool definitions at runtime, I-18 and I-24 evidence supports B006.3. Checks a developer's coding agent applies to its own workspace are not B006.3 evidence; I-23 applies when the assessed application runs coding or CI agents. |
| [B007](https://standard.aiuc-1.com/security/enforce-ai-access-privileges) | Access to AI configuration, tools and logs | Mandatory; Universal; 3 months | ASI02, ASI03 | A-23 (B007.1) | Core: role- or attribute-based access to model configuration, tool-calling capabilities and prompt logs (B007.1), and periodic access reviews (B007.2), which are organizational. A-23 adds that agent credentials cannot change the agent's own policy, tool grants, budgets or audit configuration. |
| [B008](https://standard.aiuc-1.com/security/protect-model-deployment-environment) | Deployment environment and agent interfaces | Mandatory; Universal; 12 months | ASI03, ASI04, ASI05, ASI07, ASI10 | A-16, I-21 (B008.1); I-21 (B008.2); A-02, I-21 (B008.3); I-25 (B008.5) | Core: caller authentication, including token validation and scoping for MCP connections and mutual authentication between agents (B008.1), and transport security with credential rotation (B008.2). Supplemental: message integrity for agent interfaces (B008.3), model hosting hardening (B008.4) and model integrity checks (B008.5). |
| [B010](https://standard.aiuc-1.com/security/promote-secure-code-patterns) | Secure defaults in code a product generates | Mandatory; Code-generation; 12 months | Not in the AIUC mapping (added July 2026) | None; supports only (I-24) | Applies only when the assessed product generates code for its users. Evidence: secure-pattern guidance in the product's prompts or scaffolding and sample generations (B010.1-B010.3). Code that a developer's coding agent writes while building the application is not B010 evidence. |
| [C001](https://standard.aiuc-1.com/safety/define-ai-risk-taxonomy) | Organizational risk taxonomy | Mandatory; Universal; 12 months | Not in the AIUC mapping | None; supports only (R-02, R-04, S-06) | The threat model (R-04), severity ratings (S-06) and ASI applicability feed the organization's AI risk taxonomy. The taxonomy itself is an organizational artifact. B001.1 and D004.1 reports must state the taxonomy tested. |
| [C002](https://standard.aiuc-1.com/safety/conduct-pre-deployment-testing) | Testing and sign-off before release | Mandatory; Universal; 12 months | Not in the AIUC mapping | R-01, S-01, S-06, S-10, E-09 (C002.1); S-07 (C002.2) | Core C002.1: risk-based tests and a scoped readiness decision with an accountable sign-off. Supplemental: testing built into the development lifecycle (C002.2) and vulnerability scans (C002.3). |
| [C006](https://standard.aiuc-1.com/safety/prevent-output-vulnerabilities) | Unsafe output handling | Mandatory; Code-, Text- and Voice-generation; 3 months | ASI05 | I-13, I-14 (C006.1); A-12, I-01 (C006.2) | Core: sink-safe output handling and validated structured output (C006.1), and distinct handling and labelling of untrusted content (C006.2). Supplemental: detection of attack patterns in output (C006.3). |
| [C007](https://standard.aiuc-1.com/safety/flag-high-risk-recommendations) | Human review of high-risk outputs | Optional; Universal; 12 months | ASI09 | None; supports only (A-13) | High-risk action and output criteria drawn from the risk taxonomy (C007.1) and automated detection that routes them to review (C007.2). Supplemental: reviewer assignment, escalation and queue records (C007.3). The catalog's enforced approval path (A-10, A-11, A-12) goes further than C007. |
| [C008](https://standard.aiuc-1.com/safety/monitor-ai-risk-categories) | Monitoring across AI risk categories | Optional; Universal; 12 months | Not in the AIUC mapping | None; supports only (E-04) | Core C008.1: ongoing monitoring of AI output and behavior across the risk taxonomy's categories. Supplemental C008.3: sending AI monitoring data and alerts into existing security tooling, which E-04 supports. |
| [C009](https://standard.aiuc-1.com/safety/collect-real-time-feedback) | User intervention and feedback | Optional; Universal; 3 months | ASI01, ASI09 | E-06 (C009.1) | Stop and revoke mechanisms and their tests. Supplemental C009.2: review of feedback and intervention patterns. |
| [D003](https://standard.aiuc-1.com/reliability/restrict-unsafe-tool-calls) | Tool-call validation, limits and logs | Mandatory; Automation; 12 months | ASI01, ASI02, ASI03, ASI05, ASI08, ASI10 | R-05, A-01, A-02, A-03, A-04, A-09 (D003.1); R-05, A-09, A-20, I-22 (D003.2); E-01, E-04 (D003.3); R-05, A-08, A-10, A-11 (D003.4) | Core: tool allowlists, argument validation and authorization before execution (D003.1); rate limits, transaction caps and circuit breakers (D003.2); tool-call logs (D003.3). Supplemental: human approval for sensitive operations (D003.4) and log review (D003.5). |
| [D004](https://standard.aiuc-1.com/reliability/3rd-party-testing-of-tool-calls) | Independent tool-call testing | Mandatory; Automation; 3 months | ASI02, ASI05, ASI10 | S-09 (D004.1) | Requires a report from expert third parties (D004.1) that states the risk taxonomy tested, the method and findings, and improvement tracking. Internal tests do not satisfy it. The skill produces material an assessor can use: a tool-abuse taxonomy aligned with the organization's AI risk taxonomy (C001), hostile cases with authorized twins (S-02) and a reproducible harness (S-01). |
| [E001](https://standard.aiuc-1.com/accountability/ai-failure-plan-for-security-breaches) | Security breach response plan | Mandatory; Universal; 12 months | ASI08, ASI10 | E-08 (E001.1) | Suspension, revocation and evidence preservation (E-06, E-07, E-08). Breach notification procedures (customer, regulator, vendor) are organizational work outside this skill. |
| [E004](https://standard.aiuc-1.com/accountability/assign-accountability) | Accountable approval of system changes | Mandatory; Universal; 12 months | Not in the AIUC mapping; the OWASP crosswalk (v1.0) maps it to ASI09 as Secondary | R-01, E-09 (E004.1) | List the changes the catalog governs (tool registrations, permission scopes, approval thresholds, destination allowlists, budgets, sandbox and egress policy, system prompts and model versions) among the changes that need an accountable approver, and keep the approval records (E004.1). Supplemental: code signing (E004.2). |
| [E006](https://standard.aiuc-1.com/accountability/conduct-vendor-due-diligence) | Model provider due diligence | Mandatory; Universal; 12 months | ASI04 | I-10 (E006.1) | Due diligence records for each foundation or upstream model provider: data handling, retention and training use, PII controls, security and compliance, and the approval decision (E006.1). E006 is scoped to model providers. Evidence for other tools, MCP servers, skills and packages fits better under B006.1, B006.3 (supplemental), E009 and C002.3 (supplemental). |
| [E009](https://standard.aiuc-1.com/accountability/monitor-3rd-party-access) | Monitoring third-party connections | Mandatory; Universal; 12 months | ASI02, ASI03, ASI04, ASI07 | I-11 (E009.1) | Logs of third-party API, tool and MCP connections and sessions with identity, timestamps, resources and usage (E009.1). Supplemental: alerting on anomalous access, routed to an owner (E009.2; E-04 and E-05 support it). |
| [E013](https://standard.aiuc-1.com/accountability/implement-quality-management-system) | Quality management system | Optional; Universal; 12 months | Not in the AIUC mapping | None; supports only (E-09) | Core E013.2: change management and approval procedures, which AIUC-1 lets E004 evidence fulfill. E-09 records feed it. |
| [E015](https://standard.aiuc-1.com/accountability/log-model-activity) | Activity and agent execution logs | Mandatory; Universal; 12 months | ASI06, ASI07, ASI08, ASI10 | E-01 (E015.1, E015.2); E-02 (E015.3, E015.4); E-03 (E015.2); E-10 (E015.4) | Core: protected, minimized records of authorization, actions, outcomes and failures (E015.1), and log storage with retention, access control and sanitization (E015.3). Supplemental: agent execution logging such as tool calls, sub-agent actions and provenance (E015.2), and tamper-evident logs (E015.4). |
| [E017](https://standard.aiuc-1.com/accountability/document-system-transparency-policy) | System transparency documentation | Optional; Universal; 12 months | Not in the AIUC mapping | R-04 (E017.1) | Core E017.1: transparency documentation such as a model card or AI bill of materials, including AI components beyond the model; the R-04 inventory feeds it, and R-02, I-24 and I-25 support it. Supplemental E017.3: the split of security duties between platform and deployer, which I-11 supports. |

Retention evidence has two anchors: the input data policy, including retention periods (A001, cited by R-06), and log storage retention (E015.3, cited by E-02). The catalog also cites controls of A001, A004, A006, B004, C012, E005, E008 and E011, all mandatory requirements; see [mappings.md](mappings.md).

### Where the catalog goes beyond AIUC-1 core

These controls go beyond AIUC-1 core controls; where the OWASP crosswalk names a related gap, it is cited:

- Cumulative budgets across a run and all its descendants (A-20; crosswalk Gaps 4 and 7). D003.2 covers per-tool rate limits, transaction caps and circuit breakers, so circuit breakers do have a core home; budgets shared across descendants do not.
- Approval binding to the approver, the exact normalized action and arguments, target, policy and resource version, and expiry, consumed with the effect (A-11). AIUC-1's human approval for tool calls (D003.4) is supplemental and does not specify binding.
- Delegation bounded to the intersection of the delegating context's ceiling, the initiating principal's authority, the delegate's policy and the task's need, with re-authorization by the receiver (A-15; related to crosswalk Gap 2, which lists autonomy escalation and identity substitution, and Gap 1 on agent-to-agent authorization). Only supplemental A003.3 touches this.

### Published crosswalks with the OWASP list

An official OWASP crosswalk, [AIUC-1: Crosswalks OWASP Top 10 For Agentic Applications](https://genai.owasp.org/resource/aiuc-1-crosswalks-owasp-top-10-for-agentic-applications/) (Version 1.0, May 2026), maps requirements in both directions and identifies eight areas where AIUC-1 may need new or expanded requirements, including agent identity, runtime containment and monitoring, supply chain attestation, cascading failure containment, and schema controls. These are gaps in AIUC-1, not in the OWASP list or in this catalog.

Both that crosswalk and the AIUC-1 [hosted mapping](https://standard.aiuc-1.com/crosswalks/owasp-agentic-top-10) (last updated May 27, 2026) predate the July 15, 2026 AIUC-1 release. The crosswalk also cites retired and pre-2026 identifiers and titles (for example E007, retired January 2026). Some of the gaps it describes have since narrowed: the April 15, 2026 release split agent identity and agent permission management into separate controls (now A003.2 and A003.3), added execution-level safeguards (B006.3) and agent execution logging (E015.2), and extended caller authentication to MCP and agent-to-agent interfaces (now B008.1). All of these except B008.1 are supplemental controls.

### Older mappings, retired identifiers and renumbering

- Retired: E007 was merged into E004, and E014 into E017, at the January 15, 2026 release, as shown in the [accountability requirements](https://standard.aiuc-1.com/accountability/). The catalog cites neither.
- Renamed: older mappings may use earlier titles for A003 (framed around data collection, now data access), B006 (framed around system access, now unauthorized agent actions) and E015 (framed around model activity, now AI system activity). The page URLs keep the older names, for example `implement-contextual-data-safeguards` for A003.
- Renumbered by the July 15, 2026 release: the agent identity and agent permission controls became A003.2 and A003.3 (A003.3 and A003.4 in the April 15, 2026 release); B008 controls were renumbered B008.1-B008.5 after a core control was retired; C008.4 became C008.3; and a core control of A006 was retired. A control ID cited against an older release can therefore point at a different control today.

### Recheck protocol

AIUC-1 states that it releases quarterly, on January 15, April 15, July 15 and October 15 ([re-certification guidance](https://standard.aiuc-1.com/re-certification-maintaining-aiuc-1)). Earlier releases fell on other dates (July 22, 2025 and October 1, 2025), so follow the changelog rather than the calendar. After each release, and before any formal assessment or external submission:

1. Read the [changelog](https://standard.aiuc-1.com/changelog/) and the side-by-side comparison in [AIUC-1-Changelog](https://github.com/aiunderwriting/AIUC-1-Changelog).
2. For every `aiuc1` entry in the catalog, confirm that the control ID still exists with the same subject, core or supplemental status and capability tags. Update renumbered IDs and replace retired ones in the same change.
3. Recheck the application, capability, frequency and ASI columns of the table above, and the renumbering notes.
4. Regenerate [mappings.md](mappings.md), update the snapshot date in this file, and record the recheck in the repository changelog.

The October 15, 2026 release falls after this snapshot. Recheck every row against it before relying on this mapping for an assessment. Recheck the current scoped requirements before a formal assessment.

### Reuse boundary

For AIUC-1, cite identifiers and links only; do not paste requirement descriptions, control activities or evidence text. AIUC-1 publications are not included in or relicensed by this project ([third-party notices](../THIRD_PARTY_NOTICES.md)). This skill concentrates on security engineering and does not claim coverage of every AIUC-1 safety, reliability, accountability, data, or societal risk requirement.

## NIST

### Basis documents

- [AI RMF 1.0, NIST AI 100-1](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf) ([doi:10.6028/NIST.AI.100-1](https://doi.org/10.6028/NIST.AI.100-1)), released January 26, 2023: the GOVERN, MAP, MEASURE and MANAGE functions and their subcategories.
- [Generative AI Profile, NIST AI 600-1](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf) ([doi:10.6028/NIST.AI.600-1](https://doi.org/10.6028/NIST.AI.600-1)), released July 26, 2024, as supporting guidance. Its suggested actions are keyed to AI RMF subcategories (for example GV-1.3-002 sits under GOVERN 1.3).
- Revision note: NIST states that AI RMF 1.0 is being revised as part of the White House AI Action Plan ([AI RMF page](https://www.nist.gov/itl/ai-risk-management-framework), checked 2026-10-03). No revised draft was posted there at check. Recheck every `nist` entry when a revision is published, because AI 600-1 action IDs follow AI RMF 1.0 subcategory numbering.

### Pillar-to-NIST orientation

Rows group catalog controls by pillar and theme. The per-control list in [mappings.md](mappings.md) is authoritative; this table summarizes it.

| Pillar and theme | Catalog controls | AI RMF 1.0 subcategories | AI 600-1 suggested actions |
| --- | --- | --- | --- |
| R: scope, owner, intended use and risk acceptance | R-01, R-02, R-03 | GOVERN 2.1 (roles documented), MAP 1.1 (intended purpose and context), MAP 3.3 (application scope), MANAGE 1.3 (risk responses, including acceptance), MANAGE 1.4 (residual risks documented) | MP-1.1-002 (context of use), MG-1.3-001 (trade-offs for risks within tolerance) |
| R: inventory, threat model and consequential operations | R-04, R-05 | GOVERN 1.6 (the per-system inventory feeds the organization's AI system inventory), MAP 4.1, MAP 4.2 (component risks and internal controls), MAP 5.1 (likelihood and magnitude of impacts) | GV-1.6-003 (inventory details such as model versions, known issues from sources like CVE and AVID, oversight roles and access modes), GV-3.2-005 (threat modeling), MS-2.7-001 (security threats, including compromised dependencies and autonomous agents) |
| A: authority, approvals and human oversight | A-06 to A-14, A-19, A-25 | MAP 3.5 (human oversight processes), GOVERN 3.2 (human-AI configuration roles) | MP-3.4-001 (users understand content origin), MP-3.4-005 (monitor human-AI configuration outcomes) |
| A and E: budgets, stop and deactivation | A-20, A-23, E-05, E-06, E-07 | MANAGE 2.4 (supersede, disengage or deactivate) | MG-2.4-002 (escalation when deactivation criteria are met), MG-2.4-004 (deactivation criteria) |
| I: providers, provider-executed tools, MCP servers and other components | I-10, I-11, I-18, I-19, I-24, I-25, with R-04, E-08 and E-09 | GOVERN 6.1 (third-party risk policies), GOVERN 6.2 (contingency for third-party failures), MAP 4.1, MANAGE 3.1 (third-party risks monitored), MANAGE 3.2 (pre-trained models monitored) | GV-6.1-007 (third-party inventory and approved provider lists), GV-6.1-009 (third-party libraries, tools and APIs), GV-4.2-003 (third-party plugins in impact documentation), GV-6.2-006 (fallback technologies), MG-3.1-002 (value chain risks), MG-3.1-003 (re-assessment after changes such as retrieval-augmented generation) |
| I: untrusted content, retrieval and disclosure | I-01, I-02, I-06, I-07, I-10, I-13, R-06 | MEASURE 2.10 (privacy risk examined) | MP-2.1-002 (test and evaluate data and content flows) |
| I: generated and executed code | I-14, I-15, I-23 | None more specific than the generic anchors | MS-2.6-004 (review generated code) |
| S: verification and the release gate | S-01 to S-10 | MEASURE 1.2 (control effectiveness assessed), MEASURE 1.3 (independent assessors), MEASURE 2.1 (test sets, metrics and tools documented), MEASURE 2.3 (deployment-like conditions), MEASURE 2.7 (security and resilience evaluated), MANAGE 1.1 (go or no-go determination), MANAGE 1.2 (risk treatment prioritized) | GV-1.3-002 (go/no-go thresholds), MS-1.3-003 (feedback-exercise participants independent of model development), MS-2.7-007 (red-teaming, including prompt injection), MS-2.7-009 (verify that security measures remain effective and uncompromised) |
| E: audit, monitoring and detection | E-01 to E-05, E-10 | MEASURE 2.4 (production monitoring), MEASURE 2.8 (transparency and accountability risks), MANAGE 4.1 (post-deployment monitoring plans) | MS-2.7-004 (security metrics such as unauthorized access attempts), MG-4.1-002 (post-deployment monitoring processes), MS-2.6-005 (monitor, recover from and repair errors after security anomalies) |
| E: incident response, recovery and governed change | E-08, E-09 | GOVERN 1.5 (periodic review), MEASURE 1.2, MANAGE 4.3 (incident tracking, response and recovery) | MG-4.3-001 (after-action assessment of incidents) |

GOVERN 1.7 covers decommissioning and phasing out whole AI systems. It is not used for stopping a run or revoking a credential, which map to MANAGE 2.4, and no catalog control covers system retirement. Some runtime mechanisms have no subcategory or action more specific than the generic anchors, so their `nist` lists are empty: A-03, A-04, A-05, A-15, A-18, A-22, I-05, I-09, I-16 and I-27.

These frameworks guide risk management and outcomes. The table is this skill's selective mapping, not a NIST endorsement or prescribed application architecture.

### Generative AI risk categories

AI 600-1 section 2 describes 12 risks that generative AI creates or makes worse. This framework's principle is: The model proposes. The application enforces. Section 2.9 describes the threat behind it: "Indirect prompt injection attacks occur when adversaries remotely (i.e., without a direct interface) exploit LLM-integrated applications by injecting prompts into data likely to be retrieved." Any retrieved content can carry instructions, so enforcement cannot depend on the model's judgment.

- Addressed by catalog controls:
  - 2.9 Information Security, including indirect prompt injection and data poisoning: I-01, A-06, A-08, S-04.
  - 2.12 Value Chain and Component Integration: I-18, I-24, I-25.
  - 2.7 Human-AI Configuration, including automation bias in approvals: A-12, A-13.
  - 2.4 Data Privacy, as disclosure boundaries and provider data routing: R-06, I-06, I-10.
- Partly addressed: 2.2 Confabulation, only where a confabulated value could drive a consequential action. Consequential values come from trusted sources and the system of record (R-05, A-06, I-08).
- Outside this skill's scope, and needing separate treatment: 2.1 CBRN Information or Capabilities; 2.3 Dangerous, Violent, or Hateful Content; 2.5 Environmental Impacts; 2.6 Harmful Bias and Homogenization; 2.8 Information Integrity; 2.10 Intellectual Property; 2.11 Obscene, Degrading, and/or Abusive Content.

### Related NIST work (further reading, not part of the basis)

Each item was checked on 2026-10-03. None changes the basis or the catalog's NIST mappings.

- [NIST AI 100-2e2025](https://doi.org/10.6028/NIST.AI.100-2e2025), Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations (March 2025). Section 3.5, Security of Agents, covers attacks that lead agents to execute arbitrary code or exfiltrate data, and cites the AgentDojo evaluation framework.
- CAISI, [Technical Blog: Strengthening AI Agent Hijacking Evaluations](https://www.nist.gov/news-events/news/2025/01/technical-blog-strengthening-ai-agent-hijacking-evaluations) (January 17, 2025). With repeated attempts, average attack success rose from 57% to 80%, which supports repeated trials in live-model evaluation (S-08).
- CAISI, [Insights into AI Agent Security from a Large-Scale Red-Teaming Competition](https://www.nist.gov/blogs/caisi-research-blog/insights-ai-agent-security-large-scale-red-teaming-competition) (March 23, 2026). At least one successful attack was found against every target frontier model.
- CAISI, [AI Agent Standards Initiative](https://www.nist.gov/caisi/ai-agent-standards-initiative). It lists CAISI's [request for information on securing AI agent systems](https://www.nist.gov/news-events/news/2026/01/caisi-issues-request-information-about-securing-ai-agent-systems) (January 12, 2026; docket NIST-2025-0035; comments closed March 9, 2026) and an NCCoE concept paper, Accelerating the Adoption of Software and AI Agent Identity and Authorization.
- [SP 800-53 Control Overlays for Securing AI Systems (COSAiS)](https://csrc.nist.gov/Projects/cosais). The project lists single-agent and multi-agent use cases. No agent overlay had been published at check; the latest deliverable was an annotated outline for predictive AI (January 8, 2026).

## ISO/IEC 42001

Use the official public description of [ISO/IEC 42001:2023](https://www.iso.org/standard/42001): Edition 1, published 2023-12-18 by ISO/IEC JTC 1/SC 42, as confirmed on the [IEC webstore listing](https://webstore.iec.ch/en/publication/90574) (checked 2026-10-03). It specifies requirements and guidance for establishing, implementing, maintaining and continually improving an AI management system within an organization, so it applies at organization level.

The catalog uses its themes only. Records produced with this skill can feed these themes:

- context and intended use: R-01, R-02;
- roles, responsibilities and accountable decisions: R-01, E-09;
- risk assessment and treatment, including residual-risk acceptance by an owner: R-04, R-05, S-06;
- suppliers and third-party components: I-10, I-24;
- operation, monitoring and incident response: E-04, E-06, E-08;
- change control and continual improvement: E-09, S-07.

A record produced with this skill becomes management-system evidence only if the organization adopts it within its AI management system's scope and processes. The catalog has no ISO/IEC 42001 mapping field and cites no clause or Annex A control.

Public summaries do not establish detailed clause or Annex conformity. A formal assessment needs the licensed standard, the organization's defined management system, and evidence beyond application code. This skill therefore uses management themes without claiming clause-level compliance or certification.

## OWASP

### Basis: OWASP Top 10 for Agentic Applications 2026

- The [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/), by the OWASP GenAI Security Project's Agentic Security Initiative (Version 2026, December 2025, CC BY-SA 4.0), defines ASI01 through ASI10.
- [owasp-agentic-top-10.md](owasp-agentic-top-10.md) preserves its identifiers and titles, with attribution, and gives target outcomes and adversarial evidence for each risk. [controls/index.md](controls/index.md) lists the controls for each ASI risk.
- The ASI entries cross-reference the 2025 edition of the OWASP Top 10 for LLM Applications (for example LLM01:2025 Prompt Injection and LLM06:2025 Excessive Agency). OWASP published a [2026 edition of the LLM Top 10](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/) on August 3, 2026. The catalog is not mapped to either edition, and neither is part of the basis.
- Appendix A of the ASI document cross-maps each entry to the LLM Top 10 (2025), to threat identifiers in Agentic AI Threats and Mitigations and to AIVSS core risks.

### How this framework relates to other OWASP work

This framework applies the OWASP Top 10 for Agentic Applications 2026 as its risk taxonomy inside a coding agent's build workflow: the catalog's controls name the ASI risks they are designed to address, and each control is enforced outside the model, tested adversarially through the real execution path and recorded as evidence, without claiming that any risk is fully covered. Every control names a hostile case, an authorized twin, a minimum evidence scope and a record artifact, and levels are computed from what each agent context can do. That workflow is what this framework adds. It complements the OWASP projects below: AISVS for component verification requirements, the Agent Control Standard for runtime hook interfaces, the Securing Agentic Applications Guide for design guidance, and the Agentic Skills Top 10 for risks in skills. Where a control corresponds to an AISVS requirement, the catalog cites the AISVS identifier instead of restating it. Related projects do not extend the framework basis, and listing a project here does not imply endorsement in either direction.

### Related OWASP projects

Versions and dates were checked on 2026-10-03.

| Project | Version and date | Relationship to this framework |
| --- | --- | --- |
| [OWASP AISVS](https://github.com/OWASP/AISVS) ([documentation](https://owasp.github.io/www-project-artificial-intelligence-security-verification-standard-aisvs-docs/)) | 1.0, released June 2026 at OWASP Global AppSec in Vienna; 191 requirements at Levels 1-3; CC BY-SA 4.0 | Cross-referenced by version-prefixed requirement ID in the `aisvs` field wherever a requirement corresponds: mainly C9 (Orchestration & Agentic Security) and C10 (Model Context Protocol (MCP) Security), plus C5 (access control and identity), C6 (supply chain) and C12 (monitoring and logging). |
| [Agent Control Standard (ACS)](https://genai.owasp.org/resource/agent-control-standard-acs/) ([repository](https://github.com/GenAI-Security-Project/agent-control-standard)) | Resource published September 1, 2026; specification v0.1.0, with no 1.0 date set; documentation CC BY-SA 4.0, code Apache-2.0 | Defines how agent platforms expose middleware hooks through which a separate guardian can permit, deny or modify an action before it runs. Where a platform implements ACS hooks, the catalog's authorization and stop tests (A-01, A-04, E-06, S-01) should exercise those enforcement points through the real path. A hook enforces under this framework's principle only when its decision comes from deterministic policy the model cannot alter; a model's judgment at the hook is a detection signal. |
| [Securing Agentic Applications Guide 1.0](https://genai.owasp.org/resource/securing-agentic-applications-guide-1-0/) | July 27, 2025 | Guidance for designing, developing and deploying secure agentic applications; design reading alongside [runtime-controls.md](runtime-controls.md). |
| [Agentic AI - Threats and Mitigations](https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/) | v1.0, February 17, 2025, on its resource page; the ASI document also cites a version 1.1 | The ASI list's foundational threat taxonomy. Appendix A of the ASI document maps each ASI entry to its threat identifiers. |
| [OWASP AI Testing Guide](https://owasp.org/www-project-ai-testing-guide/) | v1, released November 26, 2025; Incubator project | Testing methodology for the trustworthiness of AI systems; complements the method in [verification.md](verification.md). |
| [OWASP AIVSS](https://aivss.owasp.org/) | v0.8; the site announces a v1.0 launch | Scoring system the ASI entries cite for prioritization. Teams may record an AIVSS score and its version beside the catalog's severity rating; it never changes the release gate ([conformance.md](conformance.md)). |
| [OWASP Agentic Skills Top 10 (AST10)](https://owasp.org/projects/agentic-skills-top-10) | Incubator project; the project page lists version 1.0-2026 | Related OWASP guidance (Incubator) on risks in agent skills themselves. Use it when the application loads skills at runtime (I-24) and when reviewing any skill, including this one, before installation. |
| [GenAI Security Industry Framework Crosswalk](https://genai.owasp.org/resource/genai-security-industry-framework-crosswalk/) ([data](https://genai-security-project.github.io/crosswalk/)) | Resource published September 1, 2026; 26 frameworks at check; CC BY-SA 4.0 | Community mapping of OWASP GenAI risk lists, including ASI01-ASI10, to industry frameworks. Its site states that every mapping is unreviewed until a named reviewer signs it, and its AIUC-1 entry was last synced on April 10, 2026, before the July 15, 2026 AIUC-1 release. Use primary AIUC-1 sources for requirement status. The catalog's mappings are not reconciled against it. |

### OWASP Cheat Sheet Series

Related official implementation references, read when needed:

- [AI Agent Security](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html): tool permissions, independent action checks, human oversight, and evaluation.
- [MCP Security](https://cheatsheetseries.owasp.org/cheatsheets/MCP_Security_Cheat_Sheet.html): tool and server trust and identity boundaries; see also [mcp.md](mcp.md).
- [RAG Security](https://cheatsheetseries.owasp.org/cheatsheets/RAG_Security_Cheat_Sheet.html): authorized retrieval and provenance.
- [Secure Coding with AI](https://cheatsheetseries.owasp.org/cheatsheets/Secure_Coding_with_AI_Cheat_Sheet.html): risks introduced through coding assistants and generated changes.
- [LLM Prompt Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html): prompt injection attack types and defenses. ASI01 routes inputs through the prompt-injection safeguards of LLM01:2025.
- [Verifying Third Party Agent Execution Evidence](https://cheatsheetseries.owasp.org/cheatsheets/Verifying_Third_Party_Agent_Execution_Evidence_Cheat_Sheet.html): assessing execution records supplied by agents, MCP servers or services you do not control.
