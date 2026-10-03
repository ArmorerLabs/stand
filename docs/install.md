# Install the skill

This guide installs the skill into a coding-agent host, makes its workflow required in a project if you want that, and checks the result. Host paths were checked against each vendor's documentation on 2026-10-03; the [sources](#sources) are listed at the end. Hosts change their skill locations, so recheck the documentation for the version you use.

## What gets installed

The skill bundle is exactly these seven items:

```text
SKILL.md references assets agents LICENSE LICENSES THIRD_PARTY_NOTICES.md
```

The bundle is Markdown, YAML and license text. It ships no executable code and needs no network access, MCP server or application credentials. Everything else in the repository (`catalog/`, `docs/`, `evals/`, `scripts/`, `tests/`, `.github/`) is for maintainers and is not installed.

Do not clone this repository directly into a skills directory. A plain clone would place repository tooling, tests and evaluation material where agents look for skill content. Install only the bundle.

The folder that receives the bundle is named `stand`, matching `name: stand` in the SKILL.md frontmatter. The [Agent Skills specification](https://agentskills.io/specification) requires the name to match the parent directory.

## 1. Clone and pin a reviewed commit

```bash
git clone <repo-url> stand-src
cd stand-src
git checkout <reviewed-tag-or-commit>
git rev-parse HEAD
```

Replace `<repo-url>` with the repository's clone URL and `<reviewed-tag-or-commit>` with the commit you reviewed. No release is tagged yet, so pin a full commit hash and keep the output of `git rev-parse HEAD` as the installed revision. Once signed release tags exist, check the tag with `git verify-tag <tag>` before checking it out.

Optionally, run the repository checks from the checkout before installing (Python 3.10 or newer):

```bash
python3 scripts/render_catalog.py --check
python3 scripts/validate.py
```

## 2. Choose the destination

| Host | Scope | Destination | Invoke |
| --- | --- | --- | --- |
| Claude Code | Personal, all your projects | `~/.claude/skills/stand` | `/stand` |
| Claude Code | One project | `.claude/skills/stand` in the project | `/stand` |
| Codex | User, all your repositories | `$HOME/.agents/skills/stand` | `$stand` |
| Codex | One repository | `.agents/skills/stand` at the repository root | `$stand` |
| Other Agent Skills hosts | One repository | `.agents/skills/stand` in the repository | see below |

**Claude Code.** The [skills documentation](https://code.claude.com/docs/en/skills) lists personal skills at `~/.claude/skills/<skill-name>/SKILL.md` and project skills at `.claude/skills/<skill-name>/SKILL.md`, invoked as `/skill-name`. Claude Code watches these directories and picks up a new skill within the current session; if the top-level skills directory did not exist when the session started, run `/reload-skills`. `/skills` lists the available skills. The Claude Code documentation does not list `.agents/skills` as a skill location.

**Codex.** The [Codex skills documentation](https://learn.chatgpt.com/docs/build-skills) (the target of `developers.openai.com/codex/skills`) lists user skills at `$HOME/.agents/skills` and scans `.agents/skills` in every directory from the working directory up to the repository root. Skills are invoked as `$skill-name`, and `/skills` lists them. Codex detects skill changes automatically; if the skill does not appear, restart Codex. `agents/openai.yaml` in the bundle holds optional Codex display metadata and a default prompt.

Earlier versions of the README installed the skill under `${CODEX_HOME:-$HOME/.codex}/skills`, in a folder named after the framework's former working name, following an OpenAI blog post. The current Codex skills documentation does not list that location, and whether current Codex still loads it could not be verified. Use `$HOME/.agents/skills/stand` instead, and remove an old copy after the new one is verified.

**Other Agent Skills hosts.** These hosts also read `.agents/skills` in a repository:

- GitHub Copilot CLI reads `.github/skills`, `.claude/skills` or `.agents/skills` in the repository, and `~/.copilot/skills` or `~/.agents/skills` for personal skills. Mention `/stand` in a prompt to use the skill; `/skills list` lists skills ([documentation](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills)).
- Gemini CLI reads `.gemini/skills` or the `.agents/skills` alias in the workspace, and `~/.gemini/skills` or `~/.agents/skills` for the user. `/skills list` lists skills and `/skills reload` rescans them ([documentation](https://geminicli.com/docs/cli/using-agent-skills/)).
- Cursor reads `.agents/skills` and `.cursor/skills` in the project, and `~/.agents/skills` and `~/.cursor/skills` for the user. It also loads `.claude/skills` and `.codex/skills` for compatibility ([documentation](https://cursor.com/docs/skills)).

A team that uses Claude Code together with Codex or another `.agents/skills` host needs two project copies, `.claude/skills/stand` and `.agents/skills/stand`, installed from the same pinned commit and updated together.

**Hosts without skill discovery.** Load the skill explicitly. For any coding agent that can read local files, give it a concrete request such as:

```text
Read SKILL.md in the installed skill folder and apply it to this task.
Add a support agent that searches tenant documents and proposes account changes.
Implement the relevant controls, test the execution paths, and record remaining risks.
```

The Markdown workflow is portable; integrations must be verified for the agent and version you use.

## 3. Copy the bundle

Run this from the root of the reviewed checkout. Set `skill_destination` to one destination from the table. The command refuses to overwrite an existing installation, including a symbolic link at the destination:

```bash
skill_destination="$HOME/.claude/skills/stand"
if [ -e "$skill_destination" ] || [ -L "$skill_destination" ]; then
  printf '%s\n' "Already installed: $skill_destination. Review updates before replacing it."
else
  mkdir -p "$skill_destination" &&
  cp -R SKILL.md references assets agents LICENSE LICENSES THIRD_PARTY_NOTICES.md "$skill_destination/"
fi
```

Other destinations, for example:

```bash
skill_destination="$HOME/.agents/skills/stand"               # Codex, user
skill_destination="$project_root/.claude/skills/stand"       # Claude Code, project
skill_destination="$project_root/.agents/skills/stand"       # Codex and other hosts, repository
```

Set `project_root` to the root of the project that adopts the skill. For a project installation, commit the copied bundle to that project and name the source commit in the commit message, so every team member uses the same reviewed version.

## 4. Verify the installation

Check that the copy matches the reviewed checkout. Run this from the checkout, with `skill_destination` still set:

```bash
for item in SKILL.md references assets agents LICENSE LICENSES THIRD_PARTY_NOTICES.md; do
  diff -r "$item" "$skill_destination/$item" > /dev/null 2>&1 || printf '%s\n' "Missing or different: $item"
done
grep -m 1 '^name:' "$skill_destination/SKILL.md"
```

No "Missing or different" line should appear, and the last command prints `name: stand`.

The repository validator can also stage a fresh copy of the bundle and validate it on its own, including that every link inside the bundle resolves inside it and that the folder name matches the skill name. The stage directory has to be outside the repository and absent or empty. If it is not named `stand`, the bundle is staged in a `stand` subdirectory of it:

```bash
stage_dir="$(mktemp -d)/stand"
python3 scripts/validate.py --stage "$stage_dir"
```

The staged check covers the bundle in the reviewed checkout; the loop above confirms that your installed copy matches that checkout.

Then check the host:

1. Open the host in the target project, list its skills (`/skills` in Claude Code and Codex, `/skills list` in Copilot CLI and Gemini CLI), and confirm that `stand` appears with its description.
2. Invoke it on a small agentic task in a scratch repository, for example `/stand` in Claude Code or `$stand` in Codex followed by "Add a document-search agent with tenant isolation and scoped tools." The response names a triage tier (NONE, SCOPED or FULL), a capability profile with a computed level, and control IDs such as A-01 or I-06.
3. Ask for a cosmetic change, such as fixing a typo in a README. Either the skill is not activated, or it classifies the task as NONE; in both cases no security assessment starts.

A successful check shows only that the host loads the skill and follows its triage. Skill activation, passing this repository's checks, and enforced application security are separate properties.

## 5. Make the workflow required in a project

Adapt [assets/AGENTS-snippet.md](../assets/AGENTS-snippet.md) into the project's instructions. Keep the requirement scoped to changes affecting agentic behavior.

- **Codex** reads `AGENTS.md` files from the repository root down to the working directory before doing any work ([documentation](https://learn.chatgpt.com/docs/agent-configuration/agents-md)).
- **Claude Code** reads `AGENTS.md` only when there is no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` in the working directory or above it. If the project has one, add the line `@AGENTS.md` to that `CLAUDE.md` so both tools read the same rules. Reading `AGENTS.md` directly needs Claude Code v2.1.277 or later ([documentation](https://code.claude.com/docs/en/memory)).
- **Other hosts**: place the equivalent rule in the repository instructions they support.

Where the host supports skill discovery, keep it enabled unless you want explicit invocation only. Require the application's relevant security tests in its CI and protect consequential policy changes through code review. Do not rely on automatic discovery alone for a mandatory development policy.

## 6. Update or remove

To update, fetch the new revision in the checkout and review what changed in the bundle before installing it:

```bash
git fetch
git diff <installed-commit> <new-commit> -- SKILL.md references assets agents LICENSE LICENSES THIRD_PARTY_NOTICES.md
```

Read the "Normative changes" in [CHANGELOG.md](../CHANGELOG.md). A new catalog version can change which controls apply, so a conformance statement made against the old version stays valid for that version until its re-establish date but has to be migrated before it cites the new version; see [references/conformance.md](../references/conformance.md). Then move the old installation out of every skills directory, check out the new commit, and repeat steps 3 and 4:

```bash
backup_dir="$(mktemp -d)"
mv "$skill_destination" "$backup_dir/stand-previous"
```

Keep the backup outside the skills directory, so the host does not load two copies. Delete it once the new installation is verified. To remove the skill, delete the destination folder and the `AGENTS.md` rule if you added one.

## Redistribution

Keep `LICENSE`, `LICENSES/` and `THIRD_PARTY_NOTICES.md` with every copy you distribute. The documentation and data in the bundle are licensed under CC BY-SA 4.0, and sharing an adapted version, including an adapted SKILL.md, carries its ShareAlike condition. See [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md) for the per-path licensing.

## Sources

Checked on 2026-10-03:

- Claude Code skills: <https://code.claude.com/docs/en/skills>
- Claude Code and `AGENTS.md`: <https://code.claude.com/docs/en/memory>
- Codex skills: <https://learn.chatgpt.com/docs/build-skills> (redirected from <https://developers.openai.com/codex/skills>)
- Codex `AGENTS.md`: <https://learn.chatgpt.com/docs/agent-configuration/agents-md>
- GitHub Copilot CLI skills: <https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills>
- Gemini CLI skills: <https://geminicli.com/docs/cli/using-agent-skills/>
- Cursor skills: <https://cursor.com/docs/skills>
- Agent Skills specification: <https://agentskills.io/specification>
