#!/usr/bin/env bash
set -euo pipefail

die() {
  printf 'error: %s\n' "$*" >&2
  exit 1
}

usage() {
  cat <<'EOF'
usage:
  integrate_upstream.sh baseline [--fork-ref origin/main] [--upstream upstream/main]
  integrate_upstream.sh prepare [--fork-ref origin/main] [--upstream upstream/main] [--final-branch NAME]
  integrate_upstream.sh status
  integrate_upstream.sh finalize
EOF
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

repo_root() {
  git rev-parse --show-toplevel 2>/dev/null || die "not inside a git worktree"
}

require_clean() {
  local root="$1"
  local status
  status="$(git -C "$root" status --porcelain=v1)"
  [[ -z "$status" ]] || die "worktree is dirty:
$status"
}

fetch_remote_branch_ref() {
  local ref="$1"
  local remote branch tracking

  if [[ "$ref" == refs/remotes/*/* ]]; then
    local remote_branch="${ref#refs/remotes/}"
    remote="${remote_branch%%/*}"
    branch="${remote_branch#*/}"
    tracking="$ref"
  elif [[ "$ref" == */* ]]; then
    remote="${ref%%/*}"
    branch="${ref#*/}"
    tracking="refs/remotes/${remote}/${branch}"
  else
    die "ref must look like remote/branch or refs/remotes/remote/branch: $ref"
  fi

  git fetch "$remote" "+refs/heads/${branch}:${tracking}" >&2
  git rev-parse --verify "${tracking}^{commit}"
}

parse_refs() {
  fork_ref="origin/main"
  upstream_ref="upstream/main"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --fork-ref)
        [[ $# -ge 2 ]] || die "--fork-ref requires a value"
        fork_ref="$2"
        shift 2
        ;;
      --upstream)
        [[ $# -ge 2 ]] || die "--upstream requires a value"
        upstream_ref="$2"
        shift 2
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        die "unknown argument: $1"
        ;;
    esac
  done
}

state_file() {
  git -C "$1" rev-parse --git-path integrate-upstream/state.bash
}

write_state() {
  local file="$1"
  mkdir -p "$(dirname "$file")"
  {
    printf 'root=%q\n' "$root"
    printf 'original_branch=%q\n' "$original_branch"
    printf 'was_detached=%q\n' "$was_detached"
    printf 'fork_ref=%q\n' "$fork_ref"
    printf 'upstream_ref=%q\n' "$upstream_ref"
    printf 'fork_tip=%q\n' "$fork_tip"
    printf 'upstream_tip=%q\n' "$upstream_tip"
    printf 'merge_base=%q\n' "$merge_base"
    printf 'synthetic_commit=%q\n' "$synthetic_commit"
    printf 'synthetic_branch=%q\n' "$synthetic_branch"
    printf 'merge_name=%q\n' "$merge_name"
    printf 'result_branch=%q\n' "$result_branch"
    printf 'final_branch=%q\n' "$final_branch"
  } >"$file"
}

load_state() {
  root="$(repo_root)"
  local file
  file="$(state_file "$root")"
  [[ -f "$file" ]] || die "no integrate-upstream state found; run prepare first"
  # shellcheck disable=SC1090
  source "$file"
}

baseline() {
  parse_refs "$@"

  require_command git

  root="$(repo_root)"
  require_clean "$root"

  local start_branch start_commit
  start_branch="$(git -C "$root" symbolic-ref --quiet --short HEAD || true)"
  start_commit="$(git -C "$root" rev-parse --verify HEAD)"

  fork_tip="$(fetch_remote_branch_ref "$fork_ref")"
  upstream_tip="$(fetch_remote_branch_ref "$upstream_ref")"
  merge_base="$(git -C "$root" merge-base "$fork_tip" "$upstream_tip")"
  [[ -n "$merge_base" ]] || die "could not compute merge-base"

  printf 'Baseline commit: %s\n' "$merge_base"
  if [[ -n "$start_branch" ]]; then
    printf 'Restore with: git switch %s\n' "$start_branch"
  else
    printf 'Restore with: git switch --detach %s\n' "$start_commit"
  fi

  git -C "$root" switch --detach "$merge_base"
}

prepare() {
  fork_ref="origin/main"
  upstream_ref="upstream/main"
  final_branch=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --fork-ref)
        [[ $# -ge 2 ]] || die "--fork-ref requires a value"
        fork_ref="$2"
        shift 2
        ;;
      --upstream)
        [[ $# -ge 2 ]] || die "--upstream requires a value"
        upstream_ref="$2"
        shift 2
        ;;
      --final-branch)
        [[ $# -ge 2 ]] || die "--final-branch requires a value"
        final_branch="$2"
        shift 2
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        die "unknown prepare argument: $1"
        ;;
    esac
  done

  require_command git
  require_command git-imerge

  root="$(repo_root)"
  require_clean "$root"

  local file
  file="$(state_file "$root")"
  [[ ! -f "$file" ]] || die "workflow state already exists at $file"

  fork_tip="$(fetch_remote_branch_ref "$fork_ref")"
  upstream_tip="$(fetch_remote_branch_ref "$upstream_ref")"

  local head_commit
  head_commit="$(git -C "$root" rev-parse --verify HEAD)"
  [[ "$head_commit" == "$fork_tip" ]] || die "current HEAD $head_commit does not match fetched $fork_ref $fork_tip"

  original_branch="$(git -C "$root" symbolic-ref --quiet --short HEAD || true)"
  if [[ -n "$original_branch" ]]; then
    was_detached="0"
    [[ -z "$final_branch" || "$final_branch" == "$original_branch" ]] || die "started on $original_branch; final branch must be the same branch"
    final_branch="$original_branch"
  else
    was_detached="1"
    if [[ -z "$final_branch" ]]; then
      final_branch="integrate-upstream-$(date -u +%Y%m%d%H%M%S)"
    fi
    git -C "$root" check-ref-format --branch "$final_branch" >/dev/null 2>&1 || die "invalid final branch name: $final_branch"
    git -C "$root" show-ref --verify --quiet "refs/heads/${final_branch}" && die "final branch already exists: $final_branch"
  fi

  merge_base="$(git -C "$root" merge-base "$fork_tip" "$upstream_tip")"
  [[ -n "$merge_base" ]] || die "could not compute merge-base"
  if [[ "$merge_base" == "$upstream_tip" ]]; then
    printf 'Upstream %s is already integrated into %s.\n' "$upstream_ref" "$fork_ref"
    return 0
  fi

  local fork_tree run_id
  fork_tree="$(git -C "$root" rev-parse "${fork_tip}^{tree}")"
  synthetic_commit="$(
    git -C "$root" commit-tree "$fork_tree" -p "$merge_base" \
      -m "Temporary upstream integration base" \
      -m "Fork tip: ${fork_tip}
Merge-base: ${merge_base}"
  )"

  run_id="$(date -u +%Y%m%d%H%M%S)"
  synthetic_branch="integrate-upstream/${run_id}"
  result_branch="integrate-upstream-result/${run_id}"
  merge_name="upstream-sync"

  git -C "$root" switch -c "$synthetic_branch" "$synthetic_commit"
  write_state "$file"

  printf 'Prepared upstream integration.\n'
  printf 'branch: %s\n' "$synthetic_branch"
  printf 'fork tip: %s\n' "$fork_tip"
  printf 'upstream tip: %s\n' "$upstream_tip"
  printf 'merge-base: %s\n' "$merge_base"
  printf 'final branch: %s\n' "$final_branch"
  printf '\nStarting imerge...\n'

  set +e
  git -C "$root" imerge start \
    --name "$merge_name" \
    --goal merge \
    --branch "$result_branch" \
    --first-parent \
    "$upstream_tip"
  local imerge_status=$?
  set -e

  local status
  status="$(git -C "$root" status --porcelain=v1)"
  if [[ -n "$status" ]]; then
    printf '\nimerge paused with worktree changes. Resolve conflicts here and continue.\n'
  elif [[ "$imerge_status" -eq 0 ]]; then
    printf '\nimerge did not stop for conflicts. Run finalize next.\n'
  elif git -C "$root" imerge list | sed 's/^[* ]*//' | grep -qx "$merge_name"; then
    printf '\nimerge paused in a resumable state. Run status for details.\n'
  else
    die "git imerge start failed before creating a resumable state"
  fi
}

status_workflow() {
  load_state
  printf 'branch now: '
  git -C "$root" branch --show-current || true
  printf 'synthetic branch: %s\n' "$synthetic_branch"
  printf 'fork ref: %s\n' "$fork_ref"
  printf 'upstream ref: %s\n' "$upstream_ref"
  printf 'fork tip: %s\n' "$fork_tip"
  printf 'upstream tip: %s\n' "$upstream_tip"
  printf 'merge-base: %s\n' "$merge_base"
  printf 'result branch: %s\n' "$result_branch"
  printf 'final branch: %s\n' "$final_branch"
  printf '\nWorktree status:\n'
  git -C "$root" status --short
  printf '\nimerge state:\n'
  git -C "$root" imerge list || true
}

finalize() {
  require_command git
  require_command git-imerge
  load_state
  require_clean "$root"

  GIT_EDITOR=true git -C "$root" imerge finish \
    --name "$merge_name" \
    --branch "$result_branch" \
    --force

  local result_commit final_commit
  result_commit="$(git -C "$root" rev-parse --verify "${result_branch}^{commit}")"
  final_commit="$(
    git -C "$root" commit-tree "${result_commit}^{tree}" \
      -p "$fork_tip" \
      -p "$upstream_tip" \
      -m "Merge ${upstream_ref} into fork" \
      -m "Resolved through ${result_branch}."
  )"

  git -C "$root" diff --quiet "${final_commit}^{tree}" "${result_commit}^{tree}" || die "final merge tree differs from imerge result tree"
  git -C "$root" merge-base --is-ancestor "$fork_tip" "$final_commit" || die "final commit does not descend from fork tip"
  git -C "$root" merge-base --is-ancestor "$upstream_tip" "$final_commit" || die "final commit does not descend from upstream tip"

  if [[ "$was_detached" == "0" ]]; then
    git -C "$root" branch --force "$final_branch" "$final_commit"
    git -C "$root" switch "$final_branch"
  else
    git -C "$root" switch -c "$final_branch" "$final_commit"
  fi

  git -C "$root" branch -D "$synthetic_branch" >/dev/null 2>&1 || true
  git -C "$root" branch -D "$result_branch" >/dev/null 2>&1 || true
  rm -f "$(state_file "$root")"

  printf 'Final merge commit: %s\n' "$final_commit"
  printf 'Final branch: %s\n' "$final_branch"
}

main() {
  [[ $# -gt 0 ]] || {
    usage
    exit 2
  }

  local command="$1"
  shift
  case "$command" in
    baseline)
      baseline "$@"
      ;;
    prepare)
      prepare "$@"
      ;;
    status)
      [[ $# -eq 0 ]] || die "status does not accept arguments"
      status_workflow
      ;;
    finalize)
      [[ $# -eq 0 ]] || die "finalize does not accept arguments"
      finalize
      ;;
    -h|--help|help)
      usage
      ;;
    *)
      die "unknown command: $command"
      ;;
  esac
}

main "$@"
