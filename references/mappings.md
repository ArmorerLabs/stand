<!-- Generated from catalog/controls.json in the source repository by scripts/render_catalog.py, with catalog/mappings.json. Do not edit; propose changes upstream. -->
<!-- License: CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/). SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Framework mappings

**Disclaimer.** These are engineering mappings between this catalog's controls and external frameworks, written in this project's own words. They are not certification, attestation or an audit opinion, and they do not claim conformance to, or coverage of, AIUC-1, NIST AI RMF 1.0, NIST AI 600-1, OWASP AISVS or any other framework. A mapped requirement is not evidence that an application's control works, and implementing a control does not by itself satisfy the mapped requirement.

Catalog version 0.1.0 (draft); mappings checked 2026-10-03. This file lists identifiers and relations. The justification for every mapping is recorded in `catalog/mappings.json` in the source repository. Control entries are listed in [controls/index.md](controls/index.md).

Relations:

- **direct:** The external requirement covers essentially the same obligation as the control.
- **partial:** The external requirement covers part of the control, or the same obligation in a narrower scope.
- **supports:** The external requirement helps implement or evidence the control but is not equivalent to it.

## Source versions

| Framework | Source version | Source |
| --- | --- | --- |
| AIUC-1 | AIUC-1 release of July 15, 2026 | https://standard.aiuc-1.com/ |
| NIST AI RMF 1.0 (NIST AI 100-1) with NIST AI 600-1 | NIST AI 100-1, AI RMF 1.0, January 2023 (doi:10.6028/NIST.AI.100-1); NIST AI 600-1, Generative Artificial Intelligence Profile, July 2024 (doi:10.6028/NIST.AI.600-1) | https://www.nist.gov/itl/ai-risk-management-framework |
| OWASP AISVS 1.0 | OWASP AISVS 1.0 (June 2026), locked 1.0/en folder at commit 94fbad5acee4e4716bff263a4c455dfd780e53a7 | https://github.com/OWASP/AISVS/tree/94fbad5acee4e4716bff263a4c455dfd780e53a7/1.0/en |

## Summary

| Framework | References | Direct | Partial | Supports | Controls mapped | Controls unmapped |
| --- | --- | --- | --- | --- | --- | --- |
| AIUC-1 | 203 | 0 | 72 | 131 | 77 | 1 |
| NIST AI RMF 1.0 (NIST AI 100-1) with NIST AI 600-1 | 232 | 0 | 49 | 183 | 68 | 10 |
| OWASP AISVS 1.0 | 186 | 0 | 91 | 95 | 64 | 14 |

## By pillar

Distinct AIUC-1 requirements, AI RMF 1.0 subcategories and AISVS chapters, and the number of distinct AI 600-1 actions, that each pillar's controls map to with any relation. Per-control details are in the tables below.

| Pillar | AIUC-1 requirements | AI RMF 1.0 subcategories | AI 600-1 actions | AISVS chapters |
| --- | --- | --- | --- | --- |
| S: Scope & Stewardship | A001, A003, A006, B006, C001, C002, D003, E004, E005, E008, E011, E017 | GOVERN 1.1, GOVERN 1.3, GOVERN 1.6, GOVERN 2.1, GOVERN 3.2, GOVERN 6.1, MAP 1.1, MAP 3.3, MAP 3.5, MAP 4.1, MAP 4.2, MAP 5.1, MEASURE 2.6, MEASURE 2.10, MANAGE 1.3, MANAGE 1.4, MANAGE 2.1 | 14 | C3, C5, C9, Appendix C |
| T: Trust & Isolation | A001, A003, A004, A005, A006, A008, B002, B006, B007, B008, B010, C002, C006, C009, D003, E004, E006, E009, E011, E015, E017 | GOVERN 6.1, MAP 3.5, MAP 4.1, MAP 4.2, MEASURE 2.6, MEASURE 2.10, MEASURE 3.3, MANAGE 2.4, MANAGE 3.1, MANAGE 3.2, MANAGE 4.1 | 20 | C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C12, Appendix C |
| A: Authority & Access | A003, A005, B004, B006, B007, B008, C006, C007, D003, E015 | GOVERN 1.6, GOVERN 3.2, MAP 3.4, MAP 3.5, MAP 4.2, MEASURE 2.6, MEASURE 2.10, MANAGE 2.4, MANAGE 3.1 | 3 | C2, C5, C7, C9, C10, C11, C12, Appendix C |
| N: Notice & Neutralize | A006, A008, B002, B004, B006, C002, C008, C009, D003, E001, E004, E008, E009, E013, E015 | GOVERN 1.5, GOVERN 2.1, GOVERN 6.2, MEASURE 1.2, MEASURE 2.4, MEASURE 2.6, MEASURE 2.8, MEASURE 2.9, MEASURE 3.1, MEASURE 3.3, MANAGE 2.3, MANAGE 2.4, MANAGE 3.2, MANAGE 4.1, MANAGE 4.3 | 18 | C3, C8, C9, C12, Appendix C |
| D: Demonstrated Defenses | B001, B004, C001, C002, C012, D004, E004 | MEASURE 1.1, MEASURE 1.2, MEASURE 1.3, MEASURE 2.1, MEASURE 2.3, MEASURE 2.6, MEASURE 2.7, MEASURE 2.13, MANAGE 1.1, MANAGE 1.2, MANAGE 1.3, MANAGE 1.4, MANAGE 3.2, MANAGE 4.1, MANAGE 4.2 | 22 | C3, C6, C11, Appendix C |

## AIUC-1

Notes:

- Snapshot: the AIUC-1 release of July 15, 2026, which was still the most recent release when checked against the public changelog on 2026-10-03. The next release is announced for October 15, 2026. Recheck every identifier after each quarterly release, because releases can renumber controls (the July 2026 release renumbered controls under A003, A006, B008 and C008). Retired E007 and E014 are not cited.
- Structure: AIUC-1 requirements are mandatory or optional, and a requirement becomes optional when the agent lacks the capability it addresses. Each requirement lists core controls and supplemental controls. Each justification says whether the cited control is core or supplemental. Whether each cited requirement is mandatory or optional is recorded in the application map of catalog/mappings.json, which the validator checks against the Application column of the requirement table in references/frameworks.md; justifications do not repeat it. C008, E013 and E017, like B002, C007 and C009, are optional requirements.
- Capability scoping: D003, D004 and B006 carry the Automation capability. C006 applies to text-, voice- or code-generating products. A008 and B010 (Code-generation) apply only when the assessed product generates code for its users, so they are never evidence for a coding agent that builds the application. They appear only as capability-scoped supports: A008.3 on T-05 and T-23, A008.5 on N-01, and B010.3 on T-24.
- Relations: no AIUC-1 relation is direct. D003.1, B006.1 and B006.3 each cover parts of A-01, A-02 and S-05, but none requires one non-bypassable dispatcher, canonicalization or fail-closed behavior. B001, D004 and C012 require third-party testers while D-04 and D-08 do not, so those links are partial or supports.
- Gaps: T-04 has no AIUC-1 counterpart. A-05, A-18, A-21, T-02, T-08, T-09, T-20, N-07, D-03 and D-05 have only weak supports links. A-11 (approval binding), A-15 (delegation by intersection) and A-20 (cumulative budgets across descendants) go beyond AIUC-1 core controls, consistent with the gaps listed in the OWASP and AIUC-1 crosswalk. Owner risk acceptance under S-01 and D-06 has no AIUC-1 expiry analogue.
- Reuse boundary: justifications are written in this project's own words. No AIUC-1 requirement text, control activity or evidence text is reproduced; cite AIUC-1 by identifier and link only.

### AIUC-1 references

| AIUC-1 control | Catalog controls (relation) |
| --- | --- |
| [A001.1](https://standard.aiuc-1.com/data-and-privacy/establish-data-use-policy) | S-06 (partial), T-10 (supports) |
| [A001.2](https://standard.aiuc-1.com/data-and-privacy/establish-data-use-policy) | S-06 (supports), T-06 (supports), T-07 (supports) |
| [A003.1](https://standard.aiuc-1.com/data-and-privacy/implement-contextual-data-safeguards) | S-03 (supports), S-06 (supports), T-06 (partial), T-07 (supports), T-09 (supports), A-03 (partial), A-19 (supports) |
| [A003.2](https://standard.aiuc-1.com/data-and-privacy/implement-contextual-data-safeguards) | A-16 (supports), A-17 (partial) |
| [A003.3](https://standard.aiuc-1.com/data-and-privacy/implement-contextual-data-safeguards) | S-03 (supports), T-05 (supports), A-03 (supports), A-07 (supports), A-09 (supports), A-14 (supports), A-15 (partial), A-17 (supports) |
| [A004.2](https://standard.aiuc-1.com/data-and-privacy/protect-ip-trade-secrets) | T-10 (supports) |
| [A005.2](https://standard.aiuc-1.com/data-and-privacy/prevent-cross-customer-data-exposure) | T-06 (partial), T-07 (partial), T-27 (supports), A-19 (supports) |
| [A006.1](https://standard.aiuc-1.com/data-and-privacy/prevent-pii-leakage) | S-06 (supports), N-01 (supports) |
| [A006.2](https://standard.aiuc-1.com/data-and-privacy/prevent-pii-leakage) | T-10 (supports) |
| [A008.3](https://standard.aiuc-1.com/data-and-privacy/prevent-secrets-leakage) | T-05 (supports), T-23 (supports) |
| [A008.5](https://standard.aiuc-1.com/data-and-privacy/prevent-secrets-leakage) | N-01 (supports) |
| [B001.1](https://standard.aiuc-1.com/security/test-adversarial-robustness) | D-02 (supports), D-04 (partial), D-07 (supports), D-08 (partial), D-09 (partial) |
| [B002.2](https://standard.aiuc-1.com/security/detect-adversarial-input) | N-04 (supports), N-08 (supports) |
| [B002.4](https://standard.aiuc-1.com/security/detect-adversarial-input) | T-01 (supports), T-03 (supports) |
| [B004.1](https://standard.aiuc-1.com/security/prevent-ai-endpoint-scraping) | N-05 (supports) |
| [B004.2](https://standard.aiuc-1.com/security/prevent-ai-endpoint-scraping) | A-22 (partial) |
| [B004.3](https://standard.aiuc-1.com/security/prevent-ai-endpoint-scraping) | D-09 (supports) |
| [B006.1](https://standard.aiuc-1.com/security/enforce-contextual-access-controls) | S-03 (partial), S-04 (supports), T-11 (partial), T-12 (partial), T-17 (supports), T-18 (partial), A-01 (supports), A-07 (supports), A-08 (supports), A-09 (partial), A-23 (supports) |
| [B006.2](https://standard.aiuc-1.com/security/enforce-contextual-access-controls) | N-04 (partial), N-05 (partial) |
| [B006.3](https://standard.aiuc-1.com/security/enforce-contextual-access-controls) | T-05 (partial), T-12 (supports), T-15 (partial), T-16 (supports), T-17 (supports), T-18 (partial), T-19 (partial), T-23 (partial), T-24 (supports), T-27 (supports), A-01 (partial), A-04 (supports), A-23 (supports) |
| [B007.1](https://standard.aiuc-1.com/security/enforce-ai-access-privileges) | T-19 (supports), T-23 (supports), A-23 (partial) |
| [B008.1](https://standard.aiuc-1.com/security/protect-model-deployment-environment) | T-21 (partial), A-15 (supports), A-16 (partial), A-18 (supports) |
| [B008.2](https://standard.aiuc-1.com/security/protect-model-deployment-environment) | T-05 (supports), T-21 (partial), A-16 (supports), A-18 (supports) |
| [B008.3](https://standard.aiuc-1.com/security/protect-model-deployment-environment) | T-09 (supports), T-18 (supports), T-21 (partial), A-02 (partial) |
| [B008.4](https://standard.aiuc-1.com/security/protect-model-deployment-environment) | T-15 (supports), T-16 (supports), T-27 (supports) |
| [B008.5](https://standard.aiuc-1.com/security/protect-model-deployment-environment) | T-25 (partial) |
| [B010.3](https://standard.aiuc-1.com/security/promote-secure-code-patterns) | T-24 (supports) |
| [C001.1](https://standard.aiuc-1.com/safety/define-ai-risk-taxonomy) | S-02 (supports), S-04 (supports), D-06 (supports) |
| [C002.1](https://standard.aiuc-1.com/safety/conduct-pre-deployment-testing) | S-01 (partial), N-09 (partial), D-01 (partial), D-02 (supports), D-03 (supports), D-04 (supports), D-05 (supports), D-06 (partial), D-10 (partial) |
| [C002.2](https://standard.aiuc-1.com/safety/conduct-pre-deployment-testing) | S-04 (supports), T-23 (supports), D-06 (supports), D-07 (partial) |
| [C002.3](https://standard.aiuc-1.com/safety/conduct-pre-deployment-testing) | T-24 (supports) |
| [C006.1](https://standard.aiuc-1.com/safety/prevent-output-vulnerabilities) | T-13 (partial), T-14 (partial), A-02 (supports), A-24 (supports) |
| [C006.2](https://standard.aiuc-1.com/safety/prevent-output-vulnerabilities) | T-01 (partial), T-02 (supports), T-03 (supports), T-07 (supports), T-17 (supports), T-20 (supports), T-26 (supports), A-06 (supports), A-08 (supports), A-12 (partial), A-19 (supports) |
| [C006.3](https://standard.aiuc-1.com/safety/prevent-output-vulnerabilities) | T-14 (supports) |
| [C007.3](https://standard.aiuc-1.com/safety/flag-high-risk-recommendations) | A-13 (supports) |
| [C008.3](https://standard.aiuc-1.com/safety/monitor-ai-risk-categories) | N-04 (supports) |
| [C009.1](https://standard.aiuc-1.com/safety/collect-real-time-feedback) | T-26 (supports), N-04 (supports), N-06 (partial) |
| [C012.1](https://standard.aiuc-1.com/safety/3rd-party-testing-for-other-risk) | D-08 (supports) |
| [D003.1](https://standard.aiuc-1.com/reliability/restrict-unsafe-tool-calls) | S-05 (partial), T-08 (supports), T-18 (supports), A-01 (partial), A-02 (partial), A-03 (partial), A-04 (partial), A-06 (supports), A-07 (supports), A-09 (partial), A-24 (supports), A-25 (supports) |
| [D003.2](https://standard.aiuc-1.com/reliability/restrict-unsafe-tool-calls) | S-05 (partial), T-20 (supports), T-22 (partial), A-05 (supports), A-09 (partial), A-20 (partial), A-21 (supports), A-22 (supports) |
| [D003.3](https://standard.aiuc-1.com/reliability/restrict-unsafe-tool-calls) | T-11 (supports), N-01 (partial), N-04 (partial) |
| [D003.4](https://standard.aiuc-1.com/reliability/restrict-unsafe-tool-calls) | S-05 (partial), A-06 (supports), A-08 (partial), A-10 (partial), A-11 (partial), A-12 (supports), A-14 (supports), A-25 (supports) |
| [D003.5](https://standard.aiuc-1.com/reliability/restrict-unsafe-tool-calls) | S-03 (supports), A-13 (supports), N-05 (supports) |
| [D004.1](https://standard.aiuc-1.com/reliability/3rd-party-testing-of-tool-calls) | D-01 (supports), D-08 (supports), D-09 (partial) |
| [E001.1](https://standard.aiuc-1.com/accountability/ai-failure-plan-for-security-breaches) | N-06 (supports), N-07 (supports), N-08 (partial) |
| [E004.1](https://standard.aiuc-1.com/accountability/assign-accountability) | S-01 (partial), N-09 (partial), D-10 (supports) |
| [E004.2](https://standard.aiuc-1.com/accountability/assign-accountability) | T-24 (supports), T-25 (supports) |
| [E005.1](https://standard.aiuc-1.com/accountability/assess-cloud-vs-on-prem-processing) | S-06 (supports) |
| [E006.1](https://standard.aiuc-1.com/accountability/conduct-vendor-due-diligence) | T-10 (partial), T-11 (supports), T-24 (supports) |
| [E008.1](https://standard.aiuc-1.com/accountability/review-internal-processes) | S-01 (supports), N-09 (supports) |
| [E009.1](https://standard.aiuc-1.com/accountability/monitor-3rd-party-access) | T-11 (partial) |
| [E009.2](https://standard.aiuc-1.com/accountability/monitor-3rd-party-access) | N-04 (supports), N-05 (supports) |
| [E011.1](https://standard.aiuc-1.com/accountability/record-processing-locations) | S-04 (supports), S-06 (supports), T-10 (partial) |
| [E013.2](https://standard.aiuc-1.com/accountability/implement-quality-management-system) | N-09 (supports) |
| [E015.1](https://standard.aiuc-1.com/accountability/log-model-activity) | N-01 (partial), N-03 (supports) |
| [E015.2](https://standard.aiuc-1.com/accountability/log-model-activity) | T-22 (supports), A-11 (supports), A-15 (supports), N-01 (partial), N-03 (partial) |
| [E015.3](https://standard.aiuc-1.com/accountability/log-model-activity) | N-02 (partial) |
| [E015.4](https://standard.aiuc-1.com/accountability/log-model-activity) | N-02 (partial), N-10 (partial) |
| [E017.1](https://standard.aiuc-1.com/accountability/document-system-transparency-policy) | S-02 (supports), S-04 (partial), T-24 (supports), T-25 (supports) |
| [E017.3](https://standard.aiuc-1.com/accountability/document-system-transparency-policy) | T-11 (supports) |

### Controls with no AIUC-1 mapping

T-04.

### Controls mapped to AIUC-1 only through supports relations

S-02, T-02, T-03, T-08, T-09, T-16, T-17, T-20, T-24, T-26, T-27, A-05, A-06, A-07, A-13, A-14, A-18, A-19, A-21, A-24, A-25, N-07, D-02, D-03, D-05.

## NIST AI RMF 1.0 (NIST AI 100-1) with NIST AI 600-1

Notes:

- Sources: AI RMF 1.0 subcategories come from NIST AI 100-1 Tables 1 to 4, cited with the printed page where each subcategory ends. Suggested actions come from NIST AI 600-1 Section 3, cited with the printed page where each action starts. In the justifications in catalog/mappings.json, text in single quotes is quoted from the NIST publication, apart from whitespace, ligatures and dash normalization. NIST CSF is not used.
- Revision: NIST states that AI RMF 1.0 is being revised. Recheck these identifiers when a revision is published.
- Relations: no AI RMF subcategory and no AI 600-1 action is marked direct. Each subcategory includes organization-level outcomes that no single control meets, and the AI 600-1 actions cited are broader or differently scoped than the control.
- Generic anchors: every control recorded as implemented supports MAP 4.2 (internal risk controls identified and documented) and MANAGE 1.3 (risk responses documented). They are listed per control only where the control itself produces that documentation or response. Controls with no NIST reference are runtime authorization, credential, isolation and state mechanisms for which neither publication has a subcategory or action more specific than these anchors.
- Exclusions: GOVERN 1.7 (decommissioning) is not mapped, because stop and revocation map to MANAGE 2.4 with MG-2.4-002 and MG-2.4-004, and no control covers system retirement. MS-2.8-003 (tamper-proof content history) concerns digital content transparency, not audit logs, and is not used for N-02 or N-10. AI 600-1 Information Integrity actions about synthetic-content provenance are cited only where the wording fits data lineage (MP-2.1-001, MP-2.1-002, MG-2.2-007, MG-4.1-006, MP-3.4-001), and those justifications note the different framing.
- Context, not cited as references: AI 600-1 section 2.9 (Information Security) describes indirect prompt injection and is relevant to T-01, A-06, A-08 and D-04; section 2.7 (Human-AI Configuration) to A-13; section 2.12 (Value Chain and Component Integration) to T-18, T-24 and T-25; and section 2.4 (Data Privacy) to S-06 and T-10.
- Source quirks: AI 600-1 has no suggested actions for some subcategories used here (for example MAP 3.5, MAP 4.2, MEASURE 2.4, MANAGE 1.1 and MANAGE 1.4), so those carry only AI 100-1 references. AI 600-1 prints GV-4.3-001 as 'GV4.3--001'; that action is not used here.

### AI RMF 1.0 subcategories (NIST AI 100-1)

| Subcategory | Catalog controls (relation) |
| --- | --- |
| GOVERN 1.1 | S-06 (supports) |
| GOVERN 1.3 | S-02 (partial) |
| GOVERN 1.5 | N-09 (supports) |
| GOVERN 1.6 | S-04 (supports), A-17 (supports) |
| GOVERN 2.1 | S-01 (partial), N-04 (supports) |
| GOVERN 3.2 | S-01 (supports), A-14 (supports) |
| GOVERN 6.1 | S-06 (supports), T-10 (supports), T-11 (supports), T-18 (supports), T-19 (supports), T-24 (supports) |
| GOVERN 6.2 | N-08 (supports) |
| MAP 1.1 | S-01 (supports) |
| MAP 3.3 | S-01 (partial), S-02 (supports), S-03 (supports) |
| MAP 3.4 | A-13 (supports) |
| MAP 3.5 | S-02 (supports), S-05 (supports), T-03 (supports), T-17 (supports), T-23 (supports), A-06 (supports), A-07 (supports), A-08 (supports), A-09 (supports), A-10 (supports), A-11 (supports), A-12 (supports), A-13 (partial), A-14 (supports), A-19 (supports), A-23 (supports), A-25 (supports) |
| MAP 4.1 | S-04 (partial), T-11 (supports), T-18 (supports), T-24 (supports), T-25 (supports) |
| MAP 4.2 | S-04 (partial), S-05 (supports), T-04 (supports), A-01 (supports) |
| MAP 5.1 | S-04 (supports), S-05 (supports) |
| MEASURE 1.1 | D-03 (supports) |
| MEASURE 1.2 | N-05 (supports), N-09 (supports), D-07 (partial) |
| MEASURE 1.3 | D-09 (partial) |
| MEASURE 2.1 | D-01 (supports), D-03 (partial), D-08 (supports) |
| MEASURE 2.3 | D-01 (partial), D-03 (supports), D-04 (supports), D-08 (partial), D-10 (partial) |
| MEASURE 2.4 | N-01 (supports), N-04 (partial), N-05 (partial) |
| MEASURE 2.6 | S-05 (supports), T-22 (supports), A-02 (supports), A-21 (supports), N-07 (supports), D-02 (supports), D-05 (partial), D-06 (supports) |
| MEASURE 2.7 | D-01 (partial), D-02 (partial), D-04 (partial), D-05 (supports), D-07 (supports), D-08 (partial), D-09 (partial) |
| MEASURE 2.8 | N-01 (supports), N-02 (supports), N-03 (supports), N-10 (supports) |
| MEASURE 2.9 | N-03 (supports) |
| MEASURE 2.10 | S-06 (supports), T-06 (supports), T-07 (supports), T-10 (supports), T-13 (supports), A-19 (supports), A-24 (supports) |
| MEASURE 2.13 | D-03 (supports) |
| MEASURE 3.1 | N-04 (supports) |
| MEASURE 3.3 | T-26 (partial), N-04 (supports) |
| MANAGE 1.1 | D-06 (partial) |
| MANAGE 1.2 | D-06 (partial) |
| MANAGE 1.3 | S-01 (partial), D-06 (supports) |
| MANAGE 1.4 | S-01 (supports), D-06 (supports) |
| MANAGE 2.1 | S-03 (partial) |
| MANAGE 2.3 | N-08 (partial) |
| MANAGE 2.4 | T-22 (supports), A-20 (supports), A-23 (supports), N-05 (partial), N-06 (partial), N-07 (partial) |
| MANAGE 3.1 | T-10 (supports), T-11 (supports), T-18 (partial), T-19 (supports), T-20 (supports), T-24 (partial), A-16 (supports) |
| MANAGE 3.2 | T-24 (supports), T-25 (supports), N-09 (supports), D-10 (supports) |
| MANAGE 4.1 | T-26 (supports), N-04 (partial), N-08 (supports), N-09 (partial), D-10 (supports) |
| MANAGE 4.2 | D-07 (supports) |
| MANAGE 4.3 | N-03 (supports), N-08 (partial) |

### Generative AI Profile actions (NIST AI 600-1)

| Action | Catalog controls (relation) |
| --- | --- |
| GV-1.3-001 | S-02 (supports) |
| GV-1.3-002 | D-06 (partial) |
| GV-1.3-007 | D-06 (supports) |
| GV-1.5-002 | N-08 (supports) |
| GV-1.6-003 | S-04 (partial), T-24 (supports) |
| GV-3.2-001 | D-09 (supports) |
| GV-3.2-004 | T-26 (supports) |
| GV-3.2-005 | S-04 (partial) |
| GV-4.2-003 | S-04 (supports) |
| GV-6.1-001 | S-06 (supports) |
| GV-6.1-007 | S-04 (supports), S-06 (supports), T-10 (partial) |
| GV-6.1-009 | T-11 (supports), T-18 (supports), T-24 (supports) |
| GV-6.2-003 | N-08 (partial) |
| GV-6.2-004 | T-18 (supports) |
| GV-6.2-006 | T-10 (supports) |
| GV-6.2-007 | T-10 (supports) |
| MP-1.1-001 | S-02 (supports), S-03 (supports) |
| MP-1.1-002 | S-01 (supports) |
| MP-2.1-001 | T-01 (supports), T-03 (supports), T-07 (supports), T-22 (supports), N-03 (supports) |
| MP-2.1-002 | T-01 (supports), T-02 (supports), D-01 (supports) |
| MP-2.2-001 | S-04 (supports), S-05 (supports) |
| MP-2.2-002 | T-11 (supports), T-12 (supports), T-17 (supports) |
| MP-2.3-003 | T-08 (supports) |
| MP-2.3-005 | D-04 (partial), D-08 (supports) |
| MP-3.4-001 | A-12 (supports) |
| MP-3.4-005 | A-13 (partial) |
| MP-4.1-005 | S-06 (supports) |
| MP-4.1-008 | S-02 (supports) |
| MP-5.1-005 | D-05 (supports) |
| MP-5.1-006 | S-04 (supports) |
| MS-1.1-009 | D-03 (supports) |
| MS-1.3-003 | D-09 (supports) |
| MS-2.3-003 | D-06 (supports) |
| MS-2.5-001 | D-03 (supports), D-08 (supports) |
| MS-2.5-005 | T-25 (partial) |
| MS-2.5-006 | N-09 (supports), D-10 (supports) |
| MS-2.6-004 | T-14 (supports), T-15 (supports), T-23 (supports) |
| MS-2.6-005 | T-22 (supports), N-05 (partial), D-05 (supports) |
| MS-2.6-007 | D-02 (supports), D-04 (supports) |
| MS-2.7-001 | S-04 (supports), T-21 (supports) |
| MS-2.7-004 | N-01 (supports), N-04 (supports) |
| MS-2.7-006 | D-07 (supports) |
| MS-2.7-007 | D-04 (supports), D-08 (partial), D-09 (partial) |
| MS-2.7-008 | T-25 (supports) |
| MS-2.7-009 | N-10 (supports), D-01 (supports), D-07 (partial) |
| MS-2.10-001 | D-08 (supports) |
| MS-4.2-001 | D-08 (supports) |
| MS-4.2-002 | D-08 (supports) |
| MS-4.2-004 | A-13 (supports), N-01 (supports) |
| MG-1.3-001 | S-01 (supports), D-06 (supports) |
| MG-2.2-007 | T-07 (supports) |
| MG-2.3-001 | N-08 (partial) |
| MG-2.4-002 | N-06 (supports) |
| MG-2.4-003 | N-08 (supports) |
| MG-2.4-004 | N-05 (supports), N-06 (supports), N-07 (supports) |
| MG-3.1-002 | T-18 (supports), T-19 (supports), T-24 (supports), T-25 (partial) |
| MG-3.1-003 | N-09 (supports), D-10 (supports) |
| MG-3.2-004 | T-26 (supports) |
| MG-4.1-002 | N-04 (partial) |
| MG-4.1-006 | T-06 (supports), T-07 (supports), N-03 (supports) |
| MG-4.1-007 | N-04 (supports) |
| MG-4.2-002 | D-07 (supports) |
| MG-4.3-001 | N-08 (supports) |
| MG-4.3-002 | N-04 (supports) |

### Controls with no NIST mapping

T-05, T-09, T-16, T-27, A-03, A-04, A-05, A-15, A-18, A-22.

### Controls mapped to NIST only through supports relations

S-05, S-06, T-01, T-02, T-03, T-04, T-06, T-07, T-08, T-11, T-12, T-13, T-14, T-15, T-17, T-19, T-20, T-21, T-22, T-23, A-01, A-02, A-06, A-07, A-08, A-09, A-10, A-11, A-12, A-14, A-16, A-17, A-19, A-20, A-21, A-23, A-24, A-25, N-01, N-02, N-03, N-10.

## OWASP AISVS 1.0

Notes:

- Identifiers: AISVS requirements are cited in the version-prefixed form the AISVS README recommends, `v1.0-C<chapter>.<section>.<requirement>`. Appendix C (AI-assisted secure coding) items are cited by analogy as `v1.0-AC.<section>.<item>`; they are organizational controls for AI coding tools and are used mainly for coding-agent controls, otherwise only as supports.
- Levels: in catalog/mappings.json, each justification starts with the AISVS level of the requirement. Several Level 1 controls here map to AISVS requirements at a higher AISVS level, for example A-04, A-11, A-23, T-04, T-06, T-13, T-18 and T-19. AISVS levels are assurance depths an organization selects (AISVS level N assumes ASVS level N in parallel), while this catalog's levels are computed from a capability profile, so neither substitutes for the other.
- Unmapped on purpose: AISVS leaves governance, risk acceptance and risk management to ISO/IEC 42001 and NIST AI RMF (S-01 to S-03), does not define test-harness or evidence-scope methods (D-01, D-02, D-03, D-05), and leaves audit log custody to ASVS (N-02). No AISVS 1.0 requirement corresponds to idempotency, task-scope binding, approval fatigue, system-of-record reads, provider data routing or MCP sampling and elicitation (A-05, A-07, A-13, T-08, T-10, T-20).
- Taint propagation (T-01), argument provenance (A-06) and Rule of Two gating (A-08) have no AISVS equivalent beyond the instruction-hierarchy and separation requirements cited, so those mappings are partial or supports.
- Reuse boundary: justifications paraphrase AISVS in this project's own words; no AISVS requirement text is reproduced.

### OWASP AISVS 1.0 references

| Requirement | Catalog controls (relation) |
| --- | --- |
| v1.0-C1.1.2 | T-25 (partial) |
| v1.0-C1.3.1 | T-25 (partial) |
| v1.0-C2.1.1 | T-03 (partial) |
| v1.0-C2.1.2 | T-03 (partial) |
| v1.0-C2.1.3 | T-01 (supports), A-19 (supports) |
| v1.0-C2.1.6 | T-01 (supports) |
| v1.0-C2.1.7 | T-09 (supports) |
| v1.0-C2.2.3 | T-03 (supports) |
| v1.0-C3.1.1 | S-04 (partial), T-24 (partial) |
| v1.0-C3.1.3 | T-25 (supports) |
| v1.0-C3.2.3 | T-24 (supports), N-09 (partial), D-07 (partial), D-10 (partial) |
| v1.0-C3.3.1 | D-10 (supports) |
| v1.0-C3.3.2 | N-08 (supports) |
| v1.0-C4.1.2 | T-25 (partial) |
| v1.0-C5.1.1 | A-14 (supports) |
| v1.0-C5.1.2 | A-15 (supports), A-16 (supports) |
| v1.0-C5.2.1 | A-02 (supports) |
| v1.0-C5.2.2 | T-06 (partial) |
| v1.0-C5.2.4 | A-19 (supports) |
| v1.0-C5.2.5 | T-05 (partial), A-01 (supports) |
| v1.0-C5.2.7 | S-06 (supports), T-06 (supports) |
| v1.0-C5.3.1 | T-16 (supports), T-27 (supports) |
| v1.0-C5.3.2 | T-16 (supports), T-27 (supports) |
| v1.0-C6.1.2 | T-25 (partial) |
| v1.0-C6.1.3 | T-25 (partial) |
| v1.0-C6.1.4 | D-08 (supports) |
| v1.0-C7.1.1 | T-14 (supports), A-02 (partial) |
| v1.0-C7.3.3 | T-12 (supports), T-13 (partial), A-24 (supports) |
| v1.0-C7.3.4 | T-13 (supports), T-26 (supports), A-24 (supports) |
| v1.0-C8.1.1 | T-06 (supports), T-07 (supports) |
| v1.0-C8.1.2 | T-07 (supports) |
| v1.0-C8.1.3 | T-06 (partial) |
| v1.0-C8.2.3 | T-01 (supports), T-07 (partial) |
| v1.0-C8.3.1 | T-07 (partial) |
| v1.0-C8.3.2 | N-08 (partial) |
| v1.0-C8.3.3 | T-07 (supports), N-08 (supports) |
| v1.0-C9.1.1 | T-15 (partial), A-09 (partial), A-20 (supports), A-21 (partial) |
| v1.0-C9.1.2 | A-20 (partial) |
| v1.0-C9.1.3 | N-07 (partial) |
| v1.0-C9.2.1 | A-08 (partial), A-10 (partial), A-25 (supports) |
| v1.0-C9.2.2 | A-10 (partial), A-12 (partial) |
| v1.0-C9.2.3 | S-05 (partial), A-10 (supports) |
| v1.0-C9.2.4 | S-05 (partial), A-10 (supports) |
| v1.0-C9.2.5 | A-23 (partial) |
| v1.0-C9.2.8 | A-11 (partial) |
| v1.0-C9.2.9 | T-05 (supports), A-11 (supports), A-23 (supports) |
| v1.0-C9.2.10 | T-22 (supports) |
| v1.0-C9.3.1 | T-15 (partial), T-17 (supports), A-09 (supports) |
| v1.0-C9.3.3 | S-05 (supports) |
| v1.0-C9.3.4 | A-09 (supports) |
| v1.0-C9.3.5 | T-02 (partial), A-08 (partial) |
| v1.0-C9.3.6 | T-01 (supports), T-02 (partial) |
| v1.0-C9.3.7 | T-15 (supports), T-24 (partial), A-06 (supports) |
| v1.0-C9.3.8 | T-22 (supports), N-05 (partial), N-08 (supports) |
| v1.0-C9.4.1 | T-21 (supports), A-17 (partial) |
| v1.0-C9.4.2 | T-21 (supports), T-22 (partial) |
| v1.0-C9.4.4 | T-09 (supports) |
| v1.0-C9.5.1 | A-01 (partial), A-06 (supports), A-09 (partial) |
| v1.0-C9.5.2 | A-03 (partial), A-15 (partial), A-17 (partial) |
| v1.0-C9.5.3 | T-04 (partial), A-01 (partial), A-03 (partial) |
| v1.0-C9.5.4 | T-04 (partial), T-05 (partial) |
| v1.0-C9.5.5 | A-15 (partial) |
| v1.0-C9.5.6 | A-04 (partial) |
| v1.0-C9.6.1 | N-06 (partial) |
| v1.0-C9.6.2 | A-11 (supports) |
| v1.0-C9.6.3 | N-06 (supports), N-07 (supports) |
| v1.0-C10.1.1 | T-18 (supports), T-24 (partial) |
| v1.0-C10.1.2 | T-11 (supports), T-18 (partial) |
| v1.0-C10.1.3 | T-19 (partial) |
| v1.0-C10.2.1 | A-16 (partial) |
| v1.0-C10.2.2 | A-16 (partial) |
| v1.0-C10.2.4 | A-09 (supports) |
| v1.0-C10.2.5 | A-03 (partial) |
| v1.0-C10.2.7 | A-16 (partial) |
| v1.0-C10.3.1 | T-21 (partial) |
| v1.0-C10.3.2 | T-19 (supports) |
| v1.0-C10.3.4 | T-21 (partial) |
| v1.0-C10.3.5 | A-18 (partial) |
| v1.0-C10.4.1 | T-18 (supports) |
| v1.0-C10.4.2 | T-01 (supports) |
| v1.0-C10.4.3 | A-02 (partial) |
| v1.0-C10.4.4 | A-02 (partial) |
| v1.0-C10.4.6 | T-21 (partial) |
| v1.0-C10.4.7 | T-19 (partial) |
| v1.0-C10.4.8 | T-18 (partial) |
| v1.0-C11.1.2 | D-07 (supports) |
| v1.0-C11.1.3 | D-04 (supports), D-08 (partial) |
| v1.0-C11.2.2 | A-22 (partial) |
| v1.0-C12.1.1 | N-01 (partial) |
| v1.0-C12.1.2 | N-01 (supports) |
| v1.0-C12.1.3 | N-01 (supports), N-03 (supports) |
| v1.0-C12.1.4 | N-03 (partial) |
| v1.0-C12.2.1 | N-04 (supports) |
| v1.0-C12.2.2 | N-05 (partial) |
| v1.0-C12.2.5 | A-22 (supports) |
| v1.0-C12.3.4 | N-05 (supports) |
| v1.0-C12.4.1 | N-05 (supports) |
| v1.0-C12.4.2 | N-01 (partial) |
| v1.0-C12.4.3 | N-04 (partial) |
| v1.0-C12.5.3 | N-09 (supports), N-10 (supports) |
| v1.0-C12.5.4 | T-07 (partial) |
| v1.0-AC.2.1 | S-04 (supports) |
| v1.0-AC.2.3 | D-08 (supports) |
| v1.0-AC.3.3 | T-23 (partial) |
| v1.0-AC.4.1 | A-14 (supports) |
| v1.0-AC.4.3 | D-06 (supports) |
| v1.0-AC.4.4 | A-14 (supports) |
| v1.0-AC.5.1 | N-03 (supports) |
| v1.0-AC.5.3 | N-10 (partial) |
| v1.0-AC.6.1 | N-04 (supports) |
| v1.0-AC.6.3 | D-09 (supports) |
| v1.0-AC.6.4 | D-07 (supports) |
| v1.0-AC.7.4 | T-23 (supports) |
| v1.0-AC.8.1 | A-23 (supports) |
| v1.0-AC.8.2 | A-17 (supports) |
| v1.0-AC.8.3 | T-23 (partial), A-23 (supports) |
| v1.0-AC.11.1 | T-23 (partial) |
| v1.0-AC.11.2 | T-19 (supports), T-23 (partial), A-23 (supports) |
| v1.0-AC.11.3 | T-14 (partial) |
| v1.0-AC.11.4 | T-05 (supports), T-12 (partial) |
| v1.0-AC.11.5 | A-01 (supports) |
| v1.0-AC.11.6 | N-10 (partial) |
| v1.0-AC.11.7 | T-23 (partial) |
| v1.0-AC.12.1 | T-23 (partial) |
| v1.0-AC.12.2 | T-23 (supports) |
| v1.0-AC.12.3 | T-23 (partial) |
| v1.0-AC.12.5 | T-23 (partial) |
| v1.0-AC.13.3 | T-24 (supports) |
| v1.0-AC.14.1 | N-08 (partial) |
| v1.0-AC.14.3 | N-07 (partial) |
| v1.0-AC.14.5 | N-08 (supports) |

### Controls with no AISVS mapping

S-01, S-02, S-03, T-08, T-10, T-20, A-05, A-07, A-13, N-02, D-01, D-02, D-03, D-05.

### Controls mapped to AISVS only through supports relations

S-06, T-01, T-09, T-11, T-16, T-17, T-26, T-27, A-06, A-14, A-19, A-24, A-25, D-04, D-06, D-09.
