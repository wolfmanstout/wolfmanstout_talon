---
name: integrate-upstream
description: Use when bringing upstream changes into this fork.
---

# Integrate Upstream

Use `scripts/integrate_upstream.sh` for the Git setup and final handoff. It keeps the visible merge result on the real fork history, while using a temporary branch only for conflict resolution.

## Start

Before starting, the worktree must be clean and `HEAD` must be either the branch that tracks `origin/main` or detached at the fetched `origin/main` commit. If starting detached, choose the final branch name now with `prepare --final-branch NAME`; if starting on a branch, the final branch must be the current branch.

Run:

```sh
scripts/integrate_upstream.sh baseline --upstream upstream/main
uv run prek --quiet --no-progress --color never run --all-files
uv run pytest -q
talonbox start
talonbox rsync -a --delete \
  --exclude .git \
  --exclude .venv \
  --exclude __pycache__ \
  --exclude .pytest_cache \
  --exclude node_modules \
  ./ guest:/Users/lume/.talon/user/wolfmanstout_talon/
talonbox restart-talon
talonbox exec -- sh -lc 'tail -n 500 ~/.talon/talon.log | grep -n -E "ERROR|WARNING|Traceback|Exception|ModuleNotFoundError" | tail -n 120 || true'
<restore command printed by baseline>
scripts/integrate_upstream.sh prepare --upstream upstream/main
```

The script fails on dirty state, missing refs, missing `git-imerge`, or a current `HEAD` that does not match fetched `origin/main`. It accepts either a branch at `origin/main` or detached `HEAD` at that commit. The Talonbox session started during baseline is reused for conflict and final checks.

During baseline validation, do not keep formatter edits. If `prek` changes files at the baseline checkout, note that fact, restore the baseline checkout to a clean state, and stop if unsure. If either `prek` or `pytest` fails and the quiet output is insufficient, rerun the failing command without quiet flags or only on the failing file/test. Record known Talonbox noise as exact grep snippets, not full log tails. If a later log has the same file/error signature, note it as known. If the signature differs, expand the surrounding log and stop.

The `talonbox exec` log commands in this skill are examples of a quiet, triage-first default. Adjust the grep pattern, line counts, or surrounding context when the observed log output suggests more or less context is needed.

After `prepare`, resolve conflicts in the current checkout. The checkout will be on the synthetic/imerge branch until finalization.

Use status when unsure:

```sh
scripts/integrate_upstream.sh status
```

## Conflict Loop

For each imerge stop:

1. Resolve conflict markers and only directly required follow-up changes in the same affected behavior path.
2. Run quiet `prek`; if it edits files, review `git status --short` and rerun the same quiet command:

```sh
uv run prek --quiet --no-progress --color never run --all-files
# If files changed, review `git status --short` and rerun:
uv run prek --quiet --no-progress --color never run --all-files
```

3. Run quiet tests:

```sh
uv run pytest -q
```

If either command fails and the quiet output is insufficient, rerun the failing command without quiet flags or only on the failing file/test.

4. Run Talonbox after each behavioral conflict involving `.py`, `.talon`, settings, modes, startup, tags, or command grammar. For comment-only, list-only, formatter-only, or pre-commit-only conflicts, Talonbox may be deferred to the next behavioral stop, but must run before `git imerge continue` if Talon syntax could have changed. Reuse the Talonbox session:

```sh
talonbox rsync -a --delete \
  --exclude .git \
  --exclude .venv \
  --exclude __pycache__ \
  --exclude .pytest_cache \
  --exclude node_modules \
  ./ guest:/Users/lume/.talon/user/wolfmanstout_talon/
talonbox restart-talon
talonbox exec -- sh -lc 'tail -n 500 ~/.talon/talon.log | grep -n -E "ERROR|WARNING|Traceback|Exception|ModuleNotFoundError" | tail -n 120 || true'
```

If the triage command finds a new error signature, expand around real errors before deciding. This is a useful default shape, but tune the context window to the actual failure:

```sh
talonbox exec -- sh -lc 'grep -n -B 3 -A 12 -E "ERROR|Traceback|Exception|ModuleNotFoundError" ~/.talon/talon.log | tail -n 180 || true'
```

5. Ignore only errors captured during baseline or proven by checking the same command on the fork tip or upstream tip. Match known Talonbox noise by exact file/error signatures. If the signature differs, expand the surrounding log and stop.
6. Review the status and targeted diff, then stage all and only files intentionally changed by the conflict resolution or formatter:

```sh
git status --short
git diff --stat
git diff -- <conflict-files>
```

For huge formatter migrations, use:

```sh
git diff --name-only
git diff --check
```

Then continue:

```sh
git add <intentional-files>
git imerge continue --name upstream-sync --no-edit
```

Repeat until imerge is complete.

If `.pre-commit-config.yaml`, formatter versions, `.editorconfig`, or formatter hooks change, expect `prek` to rewrite many files. In that case:

1. Resolve conflict markers.
2. Run quiet `prek --all-files`.
3. If it modifies files, review `git status --short` and rerun quiet `prek --all-files`.
4. Stage the formatter churn only after confirming no unrelated files appeared.

## Finish

When the checkout is clean and imerge is complete:

```sh
scripts/integrate_upstream.sh finalize
```

The script creates the final merge commit with the real fork tip and upstream tip as parents, verifies that its tree matches the imerge result, and leaves the checkout on the final branch.

Run final checks from that branch:

```sh
uv run prek --quiet --no-progress --color never run --all-files
uv run pytest -q
talonbox rsync -a --delete \
  --exclude .git \
  --exclude .venv \
  --exclude __pycache__ \
  --exclude .pytest_cache \
  --exclude node_modules \
  ./ guest:/Users/lume/.talon/user/wolfmanstout_talon/
talonbox restart-talon
talonbox exec -- sh -lc 'tail -n 500 ~/.talon/talon.log | grep -n -E "ERROR|WARNING|Traceback|Exception|ModuleNotFoundError" | tail -n 120 || true'
```

Report the final commit, final branch, validation results, any nontrivial conflict resolutions, and a summary of significant integrated upstream changes, including important changes that did not cause conflicts. If the merge was clean, say that directly. If conflict work revealed likely duplicate functionality between fork and upstream, call it out with file references and whether it was resolved or left as follow-up.

Stop and report instead of guessing if the script refuses to continue, if the checkout has unexpected changes, or if final tree verification fails.
