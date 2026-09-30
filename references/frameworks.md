# Framework basis and source snapshot

Checked **2026-09-30**. This skill is informed by selected framework requirements and public guidance. Its implementation recommendations are an engineering synthesis. They do not reproduce a complete standard or establish certification, full conformance, or complete threat prevention.

NIST basis: **AI RMF 1.0**, with its Generative AI Profile as supporting guidance.

## OWASP

Use [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) for ASI01 through ASI10. The [coverage matrix](owasp-agentic-top-10.md) preserves its identifiers and titles and supplies application-level test designs.

An official [OWASP and AIUC-1 crosswalk](https://genai.owasp.org/resource/aiuc-1-crosswalks-owasp-top-10-for-agentic-applications/) already exists, dated May 2026. It identifies gaps involving agent identity, runtime containment, monitoring, supply chain assurance, and schemas. The [AIUC-1 hosted mapping](https://standard.aiuc-1.com/crosswalks/owasp-agentic-top-10) is useful for requirement tracing. It predates the July AIUC-1 additions. A mapped requirement is not evidence that an application's control works.

Related official implementation references, read when needed:

- [AI Agent Security](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html): tool permissions, independent action checks, human oversight, and evaluation.
- [MCP Security](https://cheatsheetseries.owasp.org/cheatsheets/MCP_Security_Cheat_Sheet.html): tool/server trust and identity boundaries.
- [RAG Security](https://cheatsheetseries.owasp.org/cheatsheets/RAG_Security_Cheat_Sheet.html): authorized retrieval and provenance.
- [Secure Coding with AI](https://cheatsheetseries.owasp.org/cheatsheets/Secure_Coding_with_AI_Cheat_Sheet.html): risks introduced through coding assistants and generated changes.

## AIUC-1

Snapshot: **Q3 2026, July 15, 2026**, per the [official changelog](https://standard.aiuc-1.com/changelog/). Requirements and evidence depend on [capability scoping](https://standard.aiuc-1.com/scoping). The following is a selective implementation mapping, not the full standard:

| Requirement and primary source | Evidence this skill helps developers produce |
| --- | --- |
| [A003](https://standard.aiuc-1.com/data-and-privacy/implement-contextual-data-safeguards) | Task-scoped data permissions enforced before model context construction and tool execution. |
| [A005](https://standard.aiuc-1.com/data-and-privacy/prevent-cross-customer-data-exposure) | Tenant isolation tests for retrieval, memory, caches, and output. |
| [A008](https://standard.aiuc-1.com/data-and-privacy/prevent-secrets-leakage) | Credential isolation and review of generated artifacts and telemetry; relevant to code generation. |
| [B001](https://standard.aiuc-1.com/security/test-adversarial-robustness) | A test corpus, reproducible results, and remediation records that support independent assessment. Internal tests do not satisfy the third-party requirement. |
| [B006](https://standard.aiuc-1.com/security/enforce-contextual-access-controls) | Trusted execution policy, scoped tool authority, and observed denial of unauthorized actions. |
| [B010](https://standard.aiuc-1.com/security/promote-secure-code-patterns/) | Secure defaults and review of code produced by coding agents. |
| [C002](https://standard.aiuc-1.com/safety/conduct-pre-deployment-testing) | Risk-based tests and a scoped readiness decision for the change. |
| [C006](https://standard.aiuc-1.com/safety/prevent-output-vulnerabilities) | Safe rendering, validated structured output, and tested downstream interpretation. |
| [D003](https://standard.aiuc-1.com/reliability/restrict-unsafe-tool-calls) | Argument validation, authorization, bounded transactions, and action records. |
| [D004](https://standard.aiuc-1.com/reliability/) | Testable tool abuse cases and evidence suitable for independent evaluation. |
| [E004](https://standard.aiuc-1.com/accountability/assign-accountability) | Named control and risk owners with actual decision evidence. |
| [E006](https://standard.aiuc-1.com/accountability/conduct-vendor-due-diligence) | Provider/dependency inventory and relevant security and data handling evidence. |
| [E015](https://standard.aiuc-1.com/accountability/log-model-activity) | Protected, minimized records of authorization, actions, outcomes, and failures. |

The current standard distinguishes mandatory requirements, supplemental requirements, and supplementary evidence. This skill's approval, containment, and logging recommendations may be stricter than a particular evidence item. They are not universal mandates attributed to AIUC-1. B001 and D004 call for independent testing at least every three months; an organization's certification program needs that separate work. Annual assessment frequencies on some controls do not mean access checks run only annually.

Retired identifiers can appear in older mappings: E007 was consolidated into E004 and E014 into E017, as shown in the [accountability requirements](https://standard.aiuc-1.com/accountability/). Recheck the current scoped requirements before a formal assessment. This skill concentrates on security engineering and does not claim coverage of every AIUC-1 safety, reliability, accountability, data, or societal risk requirement.

## NIST

| Framework | Role and selective mapping to developer evidence |
| --- | --- |
| [AI RMF 1.0, NIST AI 100-1](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf), January 2023 | GOVERN: inventory and accountable roles. MAP: use context, boundaries, and oversight. MEASURE: representative testing and security/resilience evidence. MANAGE: treatment, monitoring, recovery, and deactivation. Relevant anchors include GOVERN 1.6 and 2.1, MAP 1.1 and 3.5, MEASURE 2.3 and 2.7, and MANAGE 2.4 and 4.1. |
| [Generative AI Profile, NIST AI 600-1](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf), July 2024 | Adds suggested actions for generative systems: measurable release criteria (GV-1.3-002), version/provenance inventory (GV-1.6-003), adversarial evaluation (MS-2.7-007), recurring validation (MS-2.7-009), and monitoring (MG-4.1-002). These support the skill's threat tests and evidence record. |

These frameworks guide risk management and outcomes. The table is this skill's selective mapping, not a NIST endorsement or prescribed application architecture.

## ISO/IEC 42001

Use the official public description of [ISO/IEC 42001:2023](https://www.iso.org/standard/42001), Edition 1, December 2023. It concerns an organization's AI management system and continual improvement. The skill supports that work through documented intended use, responsibilities, risk decisions, control evidence, and operational review.

Public summaries do not establish detailed clause or Annex conformity. A formal assessment needs the licensed standard, the organization's defined management system, and evidence beyond application code. This skill therefore uses management themes without claiming clause-level compliance or certification.
