---
name: integrate-upstream
description: Use when bringing upstream changes into this fork.
---

# Integrate Upstream

Use `scripts/integrate_upstream.sh` for Git setup and final handoff. It keeps the visible merge result on the real fork history, while using a temporary branch only for conflict resolution.

This fork contains intentional customizations, including renamed or removed spoken forms. A syntactically valid union of both sides is often an incorrect resolution. For behavioral conflicts, determine fork intent before choosing the resolution.

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

Record the three commits reported by `prepare`. These are authoritative because `prepare` refetches the refs used for the integration:

```text
fork tip:     <commit reported by prepare>
upstream tip: <commit reported by prepare>
merge base:   <commit reported by prepare>
```

Use these commits when reviewing behavioral conflict intent. If the output is no longer available, retrieve the recorded values with:

```sh
scripts/integrate_upstream.sh status
```

The script fails on dirty state, missing refs, missing `git-imerge`, or a current `HEAD` that does not match fetched `origin/main`. It accepts either a branch at `origin/main` or detached `HEAD` at that commit. The Talonbox session started during baseline is reused for conflict and final checks.

During baseline validation, do not keep formatter edits. If `prek` changes files at the baseline checkout, note that fact, restore the baseline checkout to a clean state, and stop if unsure. If either `prek` or `pytest` fails and quiet output is insufficient, rerun the failing command without quiet flags or only on the failing file/test.

Record known Talonbox noise as exact file/error signatures, not full log tails. If a later log has the same signature, note it as known. If the signature differs, expand the surrounding log and stop.

The `talonbox exec` log commands in this skill are quiet, triage-first defaults. Adjust grep patterns or surrounding context when needed.

After `prepare`, resolve conflicts in the current checkout. The checkout will be on the synthetic/imerge branch until finalization.

Use status when unsure:

```sh
scripts/integrate_upstream.sh status
```

## Conflict Intent Review

For each nontrivial behavioral conflict, review intent before editing. Behavioral conflicts include changes to:

- `.talon` command grammar or spoken forms
- `.talon-list` vocabulary or aliases
- `.py` action implementations
- settings, tags, or modes
- paths, startup, loading, or application detection
- deleted, moved, or split functionality

For the affected files, compare each parent with the merge base:

```sh
git diff <merge-base> <fork-tip> -- <conflict-files>
git diff <merge-base> <upstream-tip> -- <conflict-files>
```

If the purpose of the fork-side change is unclear, inspect its history:

```sh
git log --oneline --follow <fork-tip> -- <file>
git show <relevant-fork-commit> -- <file>
```

Apply these resolution rules:

1. Preserve deliberate fork behavior unless it conflicts with a required upstream structural change.
2. If a spoken form, alias, setting, or command existed in the merge base but was removed or renamed in the fork, do not restore it merely because upstream still contains it.
3. Do not combine both sides' spoken aliases simply because both compile or map to the same action.
4. If two intentionally retained spoken forms map to the same action, declare them on one line with `|` where the local style permits.
5. Preserve genuine upstream additions that do not undo fork intent.
6. If upstream moved, split, or replaced a fork-customized behavior path, carry the fork behavior into the new structure instead of resolving only the file with conflict markers.

When functionality may have moved, search the affected area:

```sh
git diff --name-status --find-renames <fork-tip> <upstream-tip> -- <affected-area>
rg '<relevant-command|action|setting|tag>' <affected-area>
```

Keep a short resolution note for each nontrivial behavioral conflict:

```text
file:
fork intent:
upstream change:
resolution:
follow-up, if any:
```

## Conflict Loop

For each imerge stop:

1. Inspect the stopped files and classify the conflict:
   - formatter/comment-only
   - simple additive upstream change
   - behavioral conflict requiring intent review
   - upstream move/split requiring cross-file review

2. For behavioral conflicts, perform the conflict intent review above before editing.

3. Resolve conflict markers and only directly required follow-up changes in the same behavior path.

4. Review the targeted working diff:

```sh
git status --short
git diff --stat
git diff -- <conflict-files>
git diff --check
```

5. If intentionally deleting tracked files, stage those deletions before running `prek --all-files`, since file-discovery hooks may otherwise attempt to inspect deleted paths:

```sh
git add -u -- <deleted-files>
```

6. Run quiet formatting and lint checks:

```sh
uv run prek --quiet --no-progress --color never run --all-files
```

If files changed, review them and rerun:

```sh
git status --short
git diff --stat
git diff -- <changed-files>
uv run prek --quiet --no-progress --color never run --all-files
```

If `prek --all-files` fails because an intentionally deleted file is still being inspected, stage only the intended deletion and rerun.

7. Run quiet tests:

```sh
uv run pytest -q
```

If either command fails and quiet output is insufficient, rerun the failing command without quiet flags or only on the failing file/test.

8. Run Talonbox when the resolution could affect loading or runtime behavior, including:
   - Python action changes
   - imports or resource paths
   - settings or tag declarations
   - modes or startup behavior
   - moved/split Talon behavior
   - grammar changes involving new action references

Pure spoken-form removals, alias consolidation, list-only edits, comments, formatting, and deleted empty setting shells may be deferred to final Talonbox validation when `prek` passes and no action reference changed.

When Talonbox is needed, reuse the session:

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

If the triage command finds an error summary or a signature that is not already known, expand around actual errors:

```sh
talonbox exec -- sh -lc 'grep -n -B 3 -A 12 -E "ERROR|Traceback|Exception|ModuleNotFoundError" ~/.talon/talon.log | tail -n 180 || true'
```

Ignore only errors captured during baseline or proven by checking the same signature on the fork tip or upstream tip. If the signature differs, stop and report.

9. Stage all and only intentional resolution or formatter changes:

```sh
git status --short
git diff --stat
git diff -- <conflict-files>
git add <intentional-files>
git imerge continue --name upstream-sync --no-edit
```

Repeat until imerge is complete.

## Formatter Migrations

If `.pre-commit-config.yaml`, formatter versions, `.editorconfig`, or formatter hooks change, expect `prek` to rewrite many files.

In that case:

1. Resolve conflict markers.
2. Review whether formatter configuration changed intentionally.
3. Run quiet `prek --all-files`.
4. If it modifies files, review `git status --short`, `git diff --name-only`, and `git diff --check`.
5. Rerun quiet `prek --all-files`.
6. Stage formatter churn only after confirming that no unrelated files appeared.

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

If Talonbox reports a summarized startup error, expand it before deciding whether it is known:

```sh
talonbox exec -- sh -lc 'grep -n -B 3 -A 12 -E "ERROR|Traceback|Exception|ModuleNotFoundError" ~/.talon/talon.log | tail -n 180 || true'
```

## Final Semantic Backstop

The conflict-loop intent review is the primary semantic check. Before reporting completion or pushing, perform a targeted final review of nontrivial behavioral resolutions and areas where upstream moved or split fork-customized functionality.

Review the recorded behavioral conflict files:

```sh
git show --remerge-diff --color=never HEAD -- <recorded-behavioral-conflict-files>
```

For any affected area where functionality moved or split, also inspect the final result relative to the fork tip:

```sh
git diff <fork-tip> HEAD -- <affected-area>
rg '<relevant-command|action|setting|tag>' <affected-area>
```

Look specifically for:

- fork-removed spoken forms accidentally restored
- renamed commands reintroduced under their former names
- duplicate aliases mapped to one action on separate lines
- fork path or startup fixes overwritten by upstream variants
- fork mode/settings behavior not carried into newly created upstream files
- functionality retained in an old path after upstream introduced its replacement

This is a backstop, not a substitute for resolving behavioral intent during each conflict stop.

If this review reveals an incorrect merge resolution before the merge is published, amend the merge commit, then rerun final validation and Talonbox checks. Do not create a follow-up cleanup commit for an unpublished merge-resolution mistake.

## Report

Report:

- final commit
- final branch
- validation results
- known Talonbox warnings/errors retained from baseline
- nontrivial conflict resolutions and their intent
- significant integrated upstream changes, including important changes that did not conflict
- any duplicate functionality identified and whether it was resolved or left for follow-up

If the merge was clean, say that directly.

Stop and report instead of guessing if:

- the script refuses to continue
- the checkout has unexpected changes
- intent for a behavioral conflict cannot be determined safely
- a new Talonbox error signature appears
- final tree verification fails
