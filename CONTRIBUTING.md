# Contributing

Keep this skill useful across applications, coding agents, programming languages, and model providers. Prefer guidance that changes an implementation decision or provides an observable verification outcome.

## Propose a change

Explain the concrete failure or missing capability, the affected boundary, and the intended behavior after the change. Keep routine contributions focused. A wording change does not require a new application evaluation; a changed permission rule, workflow, or trigger needs an appropriate behavioral check.

For framework claims, cite primary sources and record the edition or snapshot date. Distinguish source requirements from this project's recommendations. Keep the NIST mapping focused on AI RMF and its Generative AI Profile. Do not invent ISO clauses, certify an application through a checklist, or equate a model refusal with runtime authorization.

Use relative links for bundled resources. Keep personal paths, private project names, account details, credentials, production data, and raw customer traces out of the repository. Use synthetic fixtures for examples. Do not introduce external actions as a side effect of merely loading the skill.

Keep the main workflow concise. Put conditional detail in the relevant reference and link to it from the entry point. Preserve the distinction between a full initial application assessment and a focused change. Support explicit file loading without assuming every host has automatic skill discovery or honors the same instruction filename.

## Verify the change

Run:

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

The validator deliberately supports this repository's simple, single-line frontmatter fields and inline Markdown links. If a contribution needs another syntax, extend the parser and its failure tests together. Do not weaken a check to hide a broken package.

For behavior changes, choose a relevant case from [evals/README.md](evals/README.md). Give an independent coding agent the task, skill, and raw fixture in an isolated workspace. Review its actual changes and tests. Record model/configuration, skill revision, commands, results, limits, and unexpected behavior. Do not give the evaluator a prewritten solution. Never publish unsupported aggregate pass rates or results without their method and evidence scope.

External model calls and services require the evaluator's configured credentials and authorization. The default CI runs offline repository checks and makes no model calls. Keep application or model benchmark infrastructure outside the skill unless a concrete maintenance need justifies adding it.

## Attribution and releases

Original contributions use the repository's MIT license. Changes to the OWASP coverage reference follow that file's CC BY-SA 4.0 license. Preserve source attribution, license links, and modification notices. Do not copy framework PDFs, standard text, diagrams, or example code without suitable redistribution terms.

Before a release, inspect the complete diff for private content, run the checks, verify any updated primary sources, review the relevant behavioral evidence, and test installation into an empty skill directory. Use a version tag and concise release notes describing changed behavior and evidence. Publishing a release and configuring repository protection are explicit maintainer operations.
