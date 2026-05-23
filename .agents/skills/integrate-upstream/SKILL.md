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
uv run prek run --all-files
uv run pytest
talonbox start
talonbox rsync -av --delete --exclude .git --exclude .venv ./ guest:/Users/lume/.talon/user/wolfmanstout_talon/
talonbox restart-talon
talonbox exec -- sh -lc 'tail -n 250 ~/.talon/talon.log'
<restore command printed by baseline>
scripts/integrate_upstream.sh prepare --upstream upstream/main
```

The script fails on dirty state, missing refs, missing `git-imerge`, or a current `HEAD` that does not match fetched `origin/main`. It accepts either a branch at `origin/main` or detached `HEAD` at that commit. The Talonbox session started during baseline is reused for conflict and final checks.

During baseline validation, do not keep formatter edits. If `prek` changes files at the baseline checkout, note that fact, restore the baseline checkout to a clean state, and stop if unsure. Keep concise notes on baseline failures and Talon warnings/errors so later conflict-loop logs can be compared after context compaction.

After `prepare`, resolve conflicts in the current checkout. The checkout will be on the synthetic/imerge branch until finalization.

Use status when unsure:

```sh
scripts/integrate_upstream.sh status
```

## Conflict Loop

For each imerge stop:

1. Resolve conflict markers and only directly required follow-up changes in the same affected behavior path.
2. Run `uv run prek run --all-files`; if it edits files, review and rerun it.
3. Run `uv run pytest`.
4. Reuse the Talonbox session:

```sh
talonbox rsync -av --delete --exclude .git --exclude .venv ./ guest:/Users/lume/.talon/user/wolfmanstout_talon/
talonbox restart-talon
talonbox exec -- sh -lc 'tail -n 250 ~/.talon/talon.log'
```

5. Ignore only errors captured during baseline or proven by checking the same command on the fork tip or upstream tip. Otherwise stop and report.
6. Review `git diff`, then stage all and only files intentionally changed by the conflict resolution or formatter:

```sh
git add <intentional-files>
git imerge continue --name upstream-sync --no-edit
```

Repeat until imerge is complete.

## Finish

When the checkout is clean and imerge is complete:

```sh
scripts/integrate_upstream.sh finalize
```

The script creates the final merge commit with the real fork tip and upstream tip as parents, verifies that its tree matches the imerge result, and leaves the checkout on the final branch.

Run final checks from that branch:

```sh
uv run prek run --all-files
uv run pytest
talonbox rsync -av --delete --exclude .git --exclude .venv ./ guest:/Users/lume/.talon/user/wolfmanstout_talon/
talonbox restart-talon
talonbox exec -- sh -lc 'tail -n 250 ~/.talon/talon.log'
```

Report the final commit, final branch, validation results, any nontrivial conflict resolutions, and a summary of significant integrated upstream changes, including important changes that did not cause conflicts. If the merge was clean, say that directly. If conflict work revealed likely duplicate functionality between fork and upstream, call it out with file references and whether it was resolved or left as follow-up.

Stop and report instead of guessing if the script refuses to continue, if the checkout has unexpected changes, or if final tree verification fails.
