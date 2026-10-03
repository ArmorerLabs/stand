# Licensing and third-party notices

This project is independent. Citing a standard, publication or project does not imply affiliation with, endorsement by or certification from OWASP, AIUC, ISO, IEC, NIST or any coding-agent or model provider. Mappings to other frameworks are this project's engineering mappings, not certification or conformance claims.

## Licensing summary

| Path | License |
| --- | --- |
| Documentation and data: `SKILL.md`, `README.md` and the other Markdown files at the repository root, `references/`, `assets/`, `agents/`, `docs/` (including the infographic SVG and PNG), `catalog/`, and the text and data in `evals/` | Creative Commons Attribution-ShareAlike 4.0 International ([CC BY-SA 4.0](LICENSES/CC-BY-SA-4.0.txt)) |
| `references/owasp-agentic-top-10.md` | CC BY-SA 4.0, as an adaptation of an OWASP publication (see [OWASP Top 10 for Agentic Applications 2026](#owasp-top-10-for-agentic-applications-2026)) |
| Code: `scripts/`, `tests/`, `.github/` and repository configuration files such as `.gitattributes` and `.gitignore` | [MIT](LICENSE) |
| `LICENSE` and `LICENSES/` | The license texts, under their own terms |
| The Developer Certificate of Origin 1.1 text quoted in `CONTRIBUTING.md` | Reproduced verbatim under its own terms, not CC BY-SA 4.0 |

- Copyright in this project's original material belongs to its contributors, as recorded in [LICENSE](LICENSE). Contributions are accepted under the license of the path they change.
- Documentation and data: Copyright (c) 2026 the project contributors. Licensed under CC BY-SA 4.0.
- Suggested credit: "STAND by its contributors, https://github.com/ArmorerLabs/raise, licensed under CC BY-SA 4.0". If the project or repository is renamed, use the name and URL given here at the time of the copy.
- `references/controls/` and `references/mappings.md` are generated from `catalog/` and are licensed under CC BY-SA 4.0, like their source.
- A file that states its own license follows that statement. A new path that this table does not cover gets its license recorded here before it is merged.
- The installed skill bundle (`SKILL.md`, `references/`, `assets/`, `agents/`, `LICENSE`, `LICENSES/` and this file) contains only CC BY-SA 4.0 material and license texts.

### Sharing copies and adaptations

When you share a copy or an adaptation of CC BY-SA 4.0 material from this project, for example an edited `SKILL.md` or reference file:

- keep `LICENSE`, `LICENSES/` and this file with it;
- credit the project's contributors and link to the source repository, for example with the suggested credit above;
- state that you changed the material, and how;
- license your adaptation under CC BY-SA 4.0 or a license that Creative Commons has approved as compatible with it.

The license text governs. This summary is not legal advice.

## OWASP Top 10 for Agentic Applications 2026

[references/owasp-agentic-top-10.md](references/owasp-agentic-top-10.md) adapts the following work:

- Title: OWASP Top 10 for Agentic Applications 2026 (Version 2026, December 2025).
- Author: OWASP GenAI Security Project, Agentic Security Initiative (OWASP Foundation).
- Source: [publication page](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/).
- License: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). The legal code is in [LICENSES/CC-BY-SA-4.0.txt](LICENSES/CC-BY-SA-4.0.txt).
- Copyright: Copyright © 2025 OWASP Foundation, Inc., per the genai.owasp.org site notice; the publication is licensed under CC BY-SA 4.0 and the site states it is provided without warranty of service or accuracy.
- Taken from the source: the ten risk identifiers and titles, with page references. The target outcomes, adversarial evidence, detection signals and control mappings are this project's adaptation, informed by the publication's examples and mitigations.
- Changes: first adapted on September 30, 2026, and revised on October 3, 2026 for catalog version 0.1.0. The file's own header lists what changed.

The ASI identifiers, and in places their titles, also appear in `catalog/`, the generated control references and other documentation, where they identify the publication's risk categories. Those files are CC BY-SA 4.0 as well, and this attribution covers that use. It does not suggest that OWASP endorses this project or any use of it.

## Other OWASP projects

The catalog cross-references the OWASP Artificial Intelligence Security Verification Standard (AISVS) 1.0 (June 2026) as a related project. It cites AISVS by version-prefixed requirement identifiers only, for example `v1.0-C10.2.7`, and describes each correspondence in this project's own words. AISVS is Copyright © 2025-2026 The AISVS Project and is licensed under CC BY-SA 4.0 ([repository](https://github.com/OWASP/AISVS)). It is not part of this framework's basis, and this repository does not bundle it.

The [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/) is cited as further reading. This repository does not bundle its articles or example code. Preserve the applicable attribution and license if adding an adaptation from those sources.

Other OWASP GenAI Security Project resources, such as the Agent Control Standard, the Securing Agentic Applications Guide and the GenAI Security Industry Framework Crosswalk, are cited by title and link as related work. This repository does not bundle them.

## AIUC-1

AIUC-1 is published by the Artificial Intelligence Underwriting Company (AIUC). Its [terms of use](https://standard.aiuc-1.com/legal/terms) restrict copying, distributing and creating derivative works from site content. This project therefore cites AIUC-1 by requirement and control identifiers (for example `E004.1`) and links only. Mapping justifications describe each relationship in this project's own words and do not reproduce AIUC-1 requirement descriptions, control activities or evidence text; report any passage that does in a public issue, so it can be removed. AIUC-1 publications are not included in or relicensed by this repository. The mapped AIUC-1 release and the date it was checked are recorded in `catalog/mappings.json` and [references/frameworks.md](references/frameworks.md). A mapping is not AIUC-1 certification or audit evidence.

## ISO/IEC 42001

The ISO/IEC 42001 reference uses its [public description](https://www.iso.org/standard/42001) and maps management themes only. This repository contains no standard clauses, Annex text, or licensed copy of the standard. See [ISO's copyright guidance](https://www.iso.org/copyright.html). A link or thematic mapping does not grant rights to redistribute the standard.

## NIST

The catalog maps controls to subcategories of NIST AI 100-1 (Artificial Intelligence Risk Management Framework, AI RMF 1.0, January 2023) and to suggested actions of NIST AI 600-1 (Generative Artificial Intelligence Profile, July 2024). Mapping justifications quote short phrases from those publications in quotation marks, with a table or page reference. NIST's statement for its technical series says that works authored by NIST employees are not subject to copyright protection within the United States, that foreign rights are reserved, and that, to the extent NIST holds rights abroad, the public may reprint them worldwide. See [NIST's copyright, fair use, and licensing statements](https://www.nist.gov/open/copyright-fair-use-and-licensing-statements-srd-data-software-and-technical-series-publications) for the exact terms and for works written by third parties. NIST publications are not bundled. The mappings are this project's interpretation, not a NIST conformance claim.

## Other sources

Other publications cited in the documentation, such as the Model Context Protocol specification, research papers and provider documentation, are referenced by title and link. This repository does not bundle them, and they keep their own terms.

The infographic in `docs/` names the Geist and IBM Plex Mono typefaces, which are licensed under the SIL Open Font License 1.1. The fonts are not included in this repository.

## Trademarks

The OWASP® Word Mark and OWASP & Design™ Logo are registered or unregistered service marks of OWASP Foundation, Inc. in the United States and other countries. This project uses no OWASP logo and uses the OWASP name only to identify OWASP publications and projects. That use is referential and implies no affiliation, sponsorship or endorsement. The AIUC-1, ISO, IEC and NIST names likewise identify the referenced publications only. Names of coding agents, model providers and other products belong to their respective owners and are used only to identify those products.
