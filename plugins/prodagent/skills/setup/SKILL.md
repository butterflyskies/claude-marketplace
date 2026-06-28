---
name: prodagent:setup
description: "Bootstrap a prodagent config tailored to the user's workflow. Discovers commonly used commands (opt-in scan), proposes policy decisions with explanations, refines interactively, and writes the final config. Use when the user asks to set up prodagent, configure tool gating, bootstrap command policies, or says 'prodagent setup'."
---

# /prodagent:setup --- Bootstrapping a prodagent configuration

Guide the user through creating a `~/.config/prodagent/config.toml` (or XDG
equivalent) that reflects their actual workflow. The output is a TOML config
consumed by prodagent's three-tier configuration cascade.

## Context: what prodagent does

Prodagent is a command policy engine for AI coding agents. It parses shell
commands, classifies them by effect (read-only, mutating, unknown), and returns
an authorization decision (allow, ask, deny). It ships with embedded knowledge
covering 170+ commands across git, cargo, gh, kubectl, common Unix tools, and
21 wrapper commands.

The user config sits in the middle of a three-tier merge:

1. **Defaults** (embedded in the binary) --- sensible baselines.
2. **User** (`~/.config/prodagent/config.toml`) --- personal policy floor.
3. **Project** (`.prodagent/config.toml` in a repo) --- repo-specific tightening.

The user layer is what this skill creates. It has two sections:

- **`[knowledge]`** --- teach prodagent about commands it doesn't know yet.
- **`[policy]`** --- override the default allow/ask/deny decisions.

A project layer can tighten user policy (escalate to ask/deny) but **never
weaken** it. This monotonicity invariant is enforced at load time.

## When to invoke

- User asks to set up, configure, or bootstrap prodagent.
- User asks about command gating, tool policies, or permission decisions.
- User has just installed prodagent and wants initial configuration.
- User says "prodagent setup" or similar.

## Argument handling

| Argument | Behavior |
|---|---|
| *(empty)* | Full interactive workflow: discover, propose, refine, write |
| `--scan` | Include shell history command scan (requires explicit consent) |
| `--minimal` | Skip discovery, generate a minimal config from defaults |
| `--show` | Show current effective config (runs `prodagent-tool-gate --dump-config`) |
| `--verify` | Verify an existing config file (load + validate + explain) |

---

## Phase 1: Discover

Understand what the user actually runs. Two paths depending on whether `--scan`
was passed.

### Without `--scan` (default)

1. Check for existing configuration files:
   - `~/.config/prodagent/config.toml` (user config)
   - `.prodagent/config.toml` (project config in CWD)
   - `~/.config/cc-toolgate/config.toml` (legacy cc-toolgate config)
   - `.claude/settings.json` (for existing permission patterns)
   - `.claude/settings.local.json` (for local-only permission patterns)
2. **Scan nearby projects** for per-project configs. Walk the user's common
   development directories (e.g., `~/dev`, `~/src`, `~/projects`, or
   wherever CWD sits) and look for:
   - `.prodagent/config.toml` --- existing project-level prodagent configs
   - `.claude/settings.json` / `.claude/settings.local.json` --- Claude Code
     permission patterns (extract `allowedTools`, `permissions` entries)
   - `.config/cc-toolgate/config.toml` or `.cc-toolgate.toml` --- legacy
     cc-toolgate project configs

   ```sh
   # Find project configs in the user's dev tree (respect depth limit)
   find ~/dev -maxdepth 3 -type f \( \
     -path '*/.prodagent/config.toml' -o \
     -path '*/.claude/settings.json' -o \
     -path '*/.claude/settings.local.json' -o \
     -name '.cc-toolgate.toml' \
   \) 2>/dev/null
   ```

   Aggregate patterns across projects: if multiple repos allow `cargo test`
   or `npm run build`, that signals a user-level policy candidate.
3. If a cc-toolgate config exists (user-level or in any scanned project),
   offer to migrate it.
4. Ask the user what kind of work they do (web dev, systems, infra, data, etc.)
   and which tools they use most. Use their answers to seed the proposal.

### With `--scan` (opt-in)

**Before scanning, get explicit consent:**

> I can scan your shell history to discover which commands you use most
> frequently. For privacy, I will only extract the **first word** of each
> history line (the command name) --- never full command lines, which may
> contain secrets, tokens, passwords, or sensitive paths.
>
> This runs: `history | awk '{print $2}' | sort | uniq -c | sort -rn | head -40`
>
> Shall I proceed?

Only proceed after the user confirms. If they decline, fall back to the
non-scan path.

**Scan procedure:**

```sh
# Extract command names ONLY (first word). Never read full lines.
# The awk field index may be $2 (bash) or $1 (zsh with setopt HIST_NO_STORE).
# Try the user's shell first, fall back to common patterns.
fc -l 1 2>/dev/null | awk '{print $2}' | sort | uniq -c | sort -rn | head -40
```

If `fc` is unavailable:
```sh
# bash
HISTFILE=~/.bash_history history -r 2>/dev/null && history | awk '{print $2}' | sort | uniq -c | sort -rn | head -40
# zsh
fc -l 1 2>/dev/null || cat ~/.zsh_history 2>/dev/null | sed 's/^[^;]*;//' | awk '{print $1}' | sort | uniq -c | sort -rn | head -40
```

**What to extract from the scan:**

- Commands that appear frequently but are NOT in prodagent's embedded knowledge
- Patterns suggesting specific toolchains (e.g., `terraform`, `helm`, `pnpm`,
  `poetry`, `docker compose`)
- Wrapper commands the user relies on (e.g., `distrobox`, `toolbox`, `nix-shell`)

**What to ignore:**

- Shell builtins (`cd`, `alias`, `export`) --- already handled
- Commands already in prodagent's embedded defaults (git, cargo, gh, kubectl,
  ls, cat, grep, etc.)

Present the findings as a summary list:

> Based on your history, you frequently use:
> - **terraform** (143 invocations) --- not in defaults, infrastructure tool
> - **helm** (89) --- not in defaults, Kubernetes package manager
> - **pnpm** (67) --- not in defaults, Node package manager
> - **docker** (52) --- not in defaults, container runtime
>
> These are already covered by prodagent defaults:
> - git (1204), cargo (445), kubectl (203), grep (178), ...

### Session log mining (opt-in)

Claude Code session transcripts contain rich signal about what commands the
agent actually runs and how the user responded (allowed, denied, modified).
This is the highest-fidelity source for policy decisions --- it captures
real dispositions, not just command names.

**Before scanning, get explicit consent:**

> I can scan your Claude Code session logs to extract tool call patterns ---
> which Bash commands were invoked and whether they were allowed or denied.
> Session logs may contain sensitive content, so I will run them through a
> secret-stripping pass first (see below). Only command names and
> dispositions are extracted; argument values are discarded.
>
> Shall I proceed?

Only proceed after the user confirms.

**Scan procedure:**

```sh
# Locate session transcripts
# Claude Code stores sessions under ~/.claude/sessions/ or
# ~/.config/claude/sessions/ — check both.
SESSION_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/claude/sessions"
[ -d "$SESSION_DIR" ] || SESSION_DIR="$HOME/.claude/sessions"

# Extract tool_use blocks with tool_name "Bash", pull command field,
# take first word only. Never extract full command lines.
find "$SESSION_DIR" -name '*.jsonl' -newer /dev/null -mtime -30 2>/dev/null | \
  xargs grep -h '"tool_name":"Bash"' 2>/dev/null | \
  jq -r '.tool_input.command // empty' 2>/dev/null | \
  awk '{print $1}' | sort | uniq -c | sort -rn | head -40
```

**Disposition mining** (if transcript format includes tool results):

```sh
# Extract allow/deny signals from tool results.
# Look for PreToolUse hook results alongside the tool calls.
find "$SESSION_DIR" -name '*.jsonl' -mtime -30 2>/dev/null | \
  xargs grep -h 'PreToolUse\|tool_result' 2>/dev/null | \
  jq -r 'select(.type == "tool_result") | .decision // empty' 2>/dev/null | \
  sort | uniq -c | sort -rn
```

The goal is to identify:
- Commands the user consistently allows --- candidates for `allow` policy.
- Commands the user consistently denies --- candidates for `deny` policy.
- Commands with mixed dispositions --- keep at `ask`.

### Secret stripping

Before mining shell history or session logs, sanitize the stream to prevent
accidental exposure of secrets. Use established detection libraries:

**Preferred tools** (in order of availability):

1. **`detect-secrets`** (Yelp) --- fast inline scanner, pip-installable.
   ```sh
   pip install detect-secrets 2>/dev/null
   # Pipe history through detect-secrets scan and redact matches
   fc -l 1 2>/dev/null | detect-secrets scan --list-all-secrets 2>/dev/null
   ```

2. **`gitleaks`** --- binary, checks for 140+ secret patterns.
   ```sh
   # Scan a file for secrets before reading it
   gitleaks detect --source=<file> --no-git 2>/dev/null
   ```

3. **`trufflehog`** --- deep scanner, good for filesystem sweeps.

4. **Manual regex pass** (fallback if no tool is installed):
   ```sh
   # Strip lines matching common secret patterns before processing
   grep -vE '(ghp_|gho_|sk-|AKIA|AIza|token=|password=|secret=|Bearer )' <input>
   ```

**Policy:** If no stripping tool is available and the user has not explicitly
waived the check, do NOT mine session logs or full history lines. Fall back
to the first-word-only extraction from `fc` which is inherently safe. Report
to the user which stripping method was used (or that none was available).

---

## Phase 2: Propose

Generate a config file based on discovery results. Walk the user through each
section with explanations.

### Structure of the config

```toml
# ~/.config/prodagent/config.toml
#
# User-level prodagent configuration.
# Merged on top of embedded defaults, below project-level overrides.
# Docs: https://github.com/butterflyskies/prodagent

# ── Policy defaults ──────────────────────────────────────────────────
# Effect-class decisions. These are the built-in defaults shown for
# reference. Uncomment and change only if you want different behavior.
#
# [policy.defaults]
# read_only = "allow"    # Read-only commands run without prompting
# mutating = "ask"       # Mutating commands prompt for confirmation
# unknown = "ask"        # Unrecognized commands prompt for confirmation

# ── Per-command policy overrides ─────────────────────────────────────
# Override the default decision for specific commands.
# Values: "allow", "ask", "deny"

[policy.commands]
# Example: always allow npm/pnpm build commands
# npm = { base = "ask", subcommands = { "run" = "allow", "test" = "allow", "install" = "ask", "publish" = "deny" } }

# ── Knowledge overrides ─────────────────────────────────────────────
# Teach prodagent about commands it doesn't know, or adjust existing
# command classifications.

# [knowledge.commands.terraform]
# effect = "unknown"
# [knowledge.commands.terraform.subcommands.entries.plan]
# effect = "read-only"
# [knowledge.commands.terraform.subcommands.entries.apply]
# effect = "mutating"
```

### Proposal rules

For each discovered command, apply these heuristics:

| Pattern | Effect | Policy | Rationale |
|---|---|---|---|
| Build/check/lint/test tools | read-only | allow | Safe operations, high frequency |
| Package install/add | mutating | ask | Modifies dependencies |
| Package publish/deploy | mutating | deny or ask | Irreversible in production |
| Container run/exec | unknown | ask | Arbitrary code execution |
| Infrastructure plan/diff | read-only | allow | Preview operations |
| Infrastructure apply/destroy | mutating | ask or deny | State mutations |
| System package managers | mutating | ask | OS-level changes |
| Destructive commands (rm -rf, drop, reset) | mutating | deny | Data loss risk |
| Privilege escalation (sudo, su) | wrapper | ask (floor) | Wrapper with escalation |

When proposing, explain each choice:

> **terraform**: I'm classifying `plan` as read-only (it only previews) and
> `apply` as mutating (it changes infrastructure state). The default for
> unknown terraform subcommands will be "ask" since unrecognized terraform
> operations could mutate state.

### Policy decision values

- **`allow`** --- command runs silently, no confirmation prompt.
- **`ask`** --- command requires user confirmation before executing.
- **`deny`** --- command is blocked outright (can be overridden to ask with
  `--escalate-deny` at the binary level).

### Effect values (knowledge layer)

- **`read-only`** --- does not modify state (ls, git status, terraform plan).
- **`mutating`** --- modifies state (rm, git push, terraform apply).
- **`unknown`** --- effect cannot be determined statically (scripts, eval).

### PolicyDecision ordering

Decisions are ordered by restrictiveness: `allow < ask < deny`. Prodagent
enforces monotonicity --- project configs can escalate (ask -> deny) but never
relax (deny -> allow). Present this to the user.

### Subcommand policy patterns

Commands with subcommands use the `Detailed` variant:

```toml
# Flat: one decision for the entire command
[policy.commands]
rm = "deny"

# Detailed: per-subcommand decisions
[policy.commands.docker]
base = "ask"                   # Default for unrecognized docker subcommands

[policy.commands.docker.subcommands]
"ps" = "allow"                 # docker ps is read-only
"images" = "allow"             # docker images is read-only
"build" = "allow"              # docker build is local
"run" = "ask"                  # docker run executes arbitrary code
"push" = "ask"                 # docker push publishes images
"system prune" = "ask"         # docker system prune is destructive
```

---

## Phase 3: Refine

After presenting the proposal, ask targeted questions. Do NOT ask open-ended
"anything else?" --- ask specific, actionable questions based on what was
discovered.

### Questions to ask

1. **Strictness level:**
   "Do you want unknown commands to prompt (`ask`) or block (`deny`)? Blocking
   is safer but means you'll need to add commands to the config as you encounter
   them."

2. **Path-based trust boundaries:**
   "Are there directory trees where you want a more permissive policy? For
   example, many developers blanket-authorize mutating commands under their
   `~/dev` tree since everything there is version-controlled and recoverable,
   while keeping stricter policies outside it."

   Suggest concrete path-scoped policies based on what was discovered:

   - **Development trees** (`~/dev`, `~/src`, `~/projects`): Relax mutating
     commands to `allow` for build/test/install operations. The reasoning:
     these directories are under version control, changes are recoverable,
     and the friction of confirming every `cargo build` or `npm install`
     inside your own projects outweighs the risk.
   - **Home directory root** (`~`): Keep at `ask` for mutating operations.
     Dotfiles, configs, and credentials live here.
   - **System paths** (`/etc`, `/usr`, `/var`): Keep at `ask` or escalate
     to `deny`. Changes here affect the whole system.
   - **Infrastructure/deploy paths**: Keep at `ask`. These are
     high-consequence even if version-controlled.

   Path-scoped policies are implemented via **project-level configs**. For a
   blanket dev-tree policy, suggest creating a shared config:

   ```sh
   # Create a shared prodagent config for the entire dev tree
   mkdir -p ~/dev/.prodagent
   ```

   ```toml
   # ~/dev/.prodagent/config.toml
   # Applies to all repos under ~/dev via prodagent's project config discovery.
   # This RELAXES nothing (monotonicity holds) — it adds allow decisions for
   # commands that default to ask at the user level.

   [policy.commands]
   cargo = { base = "allow", subcommands = { "publish" = "ask" } }
   npm = { base = "allow", subcommands = { "publish" = "deny" } }
   pnpm = { base = "allow", subcommands = { "publish" = "deny" } }
   make = "allow"
   just = "allow"
   ```

   > **Note:** Project configs can only **tighten** policy (escalate from
   > allow to ask/deny), not relax it. To achieve a permissive dev-tree
   > policy, set the **user-level** config conservative and use project
   > configs only for further restrictions. Alternatively, if the user wants
   > broad permission under `~/dev`, set the user-level policy for those
   > commands to `allow` and use project configs in sensitive repos to
   > tighten back to `ask`.

3. **Path protection** (if they work with infrastructure or sensitive dirs):
   "Are there directories that should always require confirmation when modified?
   For example, `/etc`, production deploy paths, or database directories."

4. **Specific tool preferences** (based on discovered commands):
   "You use `helm` frequently. Should `helm upgrade` and `helm install` require
   confirmation, or do you want them allowed since you run them often?"

5. **Wrapper behavior:**
   "You use `distrobox enter` as a wrapper. Should commands inside distrobox
   inherit the same policy, or should distrobox entry itself require
   confirmation?"

6. **Env gates** (if relevant patterns detected):
   "I see you use `git push` with `GIT_CONFIG_GLOBAL` set. Should git push
   be allowed only when that env var is set, or always require confirmation?"

Adjust the config after each answer. Show the diff of what changed.

---

## Phase 4: Write

### Save the config

1. Determine the config path:
   ```sh
   # XDG-compliant path (what prodagent uses via dirs::config_dir())
   # Linux: ~/.config/prodagent/config.toml
   # macOS: ~/Library/Application Support/prodagent/config.toml
   # Windows: C:\Users\<user>\AppData\Roaming\prodagent\config.toml
   ```

2. Create the directory if needed:
   ```sh
   mkdir -p ~/.config/prodagent
   ```

3. Write the file. Include comments explaining each section.

4. If a cc-toolgate config exists at `~/.config/cc-toolgate/config.toml`,
   note that both configs are independent --- prodagent does not read
   cc-toolgate config files.

### Verify the result

Run the dump-config command to show the merged effective configuration:

```sh
prodagent-tool-gate --dump-config
```

If `prodagent-tool-gate` is not installed:

```sh
# Install from crates.io
cargo install prodagent-tool-gate --locked
```

If neither is available, explain the config structure and skip verification.

Present the output to the user and highlight:
- Which values came from defaults vs their config
- Any unexpected interactions between layers
- Whether the monotonicity invariant holds

### Next steps

Tell the user:

1. **Wire as a PreToolUse hook** for their AI coding agent. The exact
   mechanism depends on the agent:
   - For Claude Code: add to `.claude/settings.json` under
     `hooks.PreToolUse` with matcher `"Bash"`, or install the gate plugin
     from the butterflyskies marketplace.
   - For other agents: wire `prodagent-tool-gate` as a pre-execution hook
     that reads the command from stdin (JSON with `tool_input.command`)
     and writes a decision to stdout.

2. **Project-level overrides**: create `.prodagent/config.toml` in
   repositories that need tighter rules. The project layer can only
   escalate decisions (ask -> deny), never relax them.

3. **Iterate**: the config is designed to evolve. Start permissive (`ask`
   for unknowns) and tighten as you learn what the agent actually runs.
   Use `prodagent-tool-gate --dump-config` to inspect the merged result
   at any time.

---

## Migration: cc-toolgate to prodagent

If the user has an existing `~/.config/cc-toolgate/config.toml`, offer to
translate it.

### Mapping

| cc-toolgate | prodagent |
|---|---|
| `[commands] allow = ["ls", ...]` | `[policy.commands] ls = "allow"` (but unnecessary --- these are defaults) |
| `[commands] ask = ["curl", ...]` | `[policy.commands] curl = "ask"` |
| `[commands] deny = ["shred", ...]` | `[policy.commands] shred = "deny"` |
| `[git] allowed_with_config = [...]` | Knowledge-layer env gates (see below) |
| `[git] safe_subcommands = [...]` | Already in embedded knowledge as read-only |
| `[git] mutating_subcommands = [...]` | Already in embedded knowledge as mutating |
| `[settings] escalate_deny = true` | CLI flag `--escalate-deny` (not in config) |
| `replace = true` / `remove_*` | Use `remove_commands` in knowledge/policy layers |

### Env gates (cc-toolgate `allowed_with_config` replacement)

cc-toolgate's pattern of allowing commands only when specific env vars are set
maps to prodagent's knowledge-layer env gates:

```toml
# cc-toolgate style:
# [git]
# allowed_with_config = ["push", "commit"]
# [git.config_env]
# GIT_CONFIG_GLOBAL = "~/.gitconfig.ai"

# prodagent equivalent:
# (Env gates are defined in the knowledge layer, not the policy layer.
#  They're part of what the command IS, not what to DO about it.)
[knowledge.commands.git.subcommands.entries.push]
effect = "mutating"
[[knowledge.commands.git.subcommands.entries.push.env_gates]]
var = "GIT_CONFIG_GLOBAL"
condition = "set"
decision = "allow"
```

Only migrate values that differ from prodagent's embedded defaults.
Avoid generating a config full of redundant entries that match what the
binary already does.

---

## Example complete config

For a systems/infrastructure developer:

```toml
# ~/.config/prodagent/config.toml

# Policy: unknown commands require confirmation (default).
# Uncomment to block unknown commands entirely:
# [policy.defaults]
# unknown = "deny"

[policy.commands]
# Infra tools --- plan is safe, apply needs confirmation
terraform = { base = "ask", subcommands = { "plan" = "allow", "validate" = "allow", "fmt" = "allow", "init" = "ask", "apply" = "ask", "destroy" = "deny" } }
helm = { base = "ask", subcommands = { "list" = "allow", "status" = "allow", "template" = "allow", "install" = "ask", "upgrade" = "ask", "rollback" = "ask", "uninstall" = "deny" } }

# Container tools
docker = { base = "ask", subcommands = { "ps" = "allow", "images" = "allow", "inspect" = "allow", "logs" = "allow", "build" = "allow", "run" = "ask", "push" = "ask", "system prune" = "ask" } }

# Destructive commands --- block outright
shred = "deny"
dd = "deny"

# Teach prodagent about tools it doesn't know
[knowledge.commands.terraform]
effect = "unknown"
[knowledge.commands.terraform.subcommands.entries.plan]
effect = "read-only"
[knowledge.commands.terraform.subcommands.entries.apply]
effect = "mutating"
[knowledge.commands.terraform.subcommands.entries.destroy]
effect = "mutating"
[knowledge.commands.terraform.subcommands.entries.validate]
effect = "read-only"
[knowledge.commands.terraform.subcommands.entries.fmt]
effect = "read-only"
[knowledge.commands.terraform.subcommands.entries.init]
effect = "mutating"
```

For a web developer:

```toml
# ~/.config/prodagent/config.toml

[policy.commands]
npm = { base = "ask", subcommands = { "run" = "allow", "test" = "allow", "start" = "allow", "ci" = "allow", "install" = "ask", "publish" = "deny" } }
pnpm = { base = "ask", subcommands = { "run" = "allow", "test" = "allow", "dev" = "allow", "build" = "allow", "install" = "ask", "publish" = "deny" } }
yarn = { base = "ask", subcommands = { "run" = "allow", "test" = "allow", "dev" = "allow", "build" = "allow", "add" = "ask", "publish" = "deny" } }

[knowledge.commands.npm]
effect = "unknown"
[knowledge.commands.npm.subcommands.entries.run]
effect = "read-only"
[knowledge.commands.npm.subcommands.entries.test]
effect = "read-only"
[knowledge.commands.npm.subcommands.entries.start]
effect = "read-only"
[knowledge.commands.npm.subcommands.entries.ci]
effect = "read-only"
[knowledge.commands.npm.subcommands.entries.install]
effect = "mutating"
[knowledge.commands.npm.subcommands.entries.publish]
effect = "mutating"
```

---

## Guardrails

- **Never read full shell history lines.** Only extract command names (first
  word). History can contain passwords, tokens, API keys, and sensitive paths
  passed as arguments.
- **Never store secrets in the config file.** The config is plaintext TOML,
  likely committed to dotfiles repos.
- **Explain every policy choice.** The user should understand why each command
  gets allow/ask/deny, not just see the result.
- **Don't over-configure.** If a command is already correctly classified by
  prodagent's embedded defaults, don't add a redundant entry. The config
  should contain only overrides and additions.
- **Respect the monotonicity invariant.** When explaining project configs,
  make clear that projects can only tighten, never relax.
- **Provider-agnostic.** This config works with any AI coding agent that wires
  prodagent as a pre-execution hook. Do not assume Claude Code specifically.
