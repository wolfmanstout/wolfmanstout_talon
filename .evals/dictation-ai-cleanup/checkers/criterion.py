#!/usr/bin/env python
import json
import os
import re
import unicodedata
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

import yaml

PUNCTUATION = ",;:!?-"
CRITERION_SEVERITY = {
    "preferred_output": "advisory",
    "word_edit_shape_valid": "required",
    "capitalization_not_removed": "required",
    "punctuation_not_removed": "required",
    "capitalization_matches_preferred": "advisory",
    "punctuation_scope": "advisory",
    "proposal_word_edit_shape_valid": "required",
    "proposal_capitalization_not_removed": "required",
    "proposal_punctuation_not_removed": "required",
    "proposal_capitalization_matches_preferred": "advisory",
    "proposal_punctuation_scope": "advisory",
    "context_not_output": "required",
    "tags_absent": "required",
    "proposal_accepted": "advisory",
    "nochange_protocol": "advisory",
}
CRITERIA = list(CRITERION_SEVERITY)


def words(text):
    return re.findall(r"\b[\w']+\b", text)


def removes_capitalization(original, candidate):
    return any(
        char.isupper() and (index >= len(candidate) or not candidate[index].isupper())
        for index, char in enumerate(original)
    )


def is_allowed_word_replacement(original_words, candidate_words):
    return len(original_words) == len(candidate_words) or (
        bool(original_words)
        and bool(candidate_words)
        and len(original_words) <= 2
        and len(candidate_words) <= 2
    )


def preserves_existing_capitalization(original, candidate):
    old_words = words(original)
    new_words = words(candidate)
    matcher = SequenceMatcher(
        None,
        [word.casefold() for word in old_words],
        [word.casefold() for word in new_words],
        autojunk=False,
    )
    for operation, old_start, old_end, new_start, new_end in matcher.get_opcodes():
        if operation == "equal" and any(
            removes_capitalization(old, new)
            for old, new in zip(
                old_words[old_start:old_end],
                new_words[new_start:new_end],
                strict=True,
            )
        ):
            return False
        if operation == "replace":
            old_span = old_words[old_start:old_end]
            new_span = new_words[new_start:new_end]
            if removes_capitalization("".join(old_span), "".join(new_span)):
                return False
            if any(
                index > 0 and any(char.isupper() for char in old)
                for index, old in enumerate(old_span, old_start)
            ):
                return False
            for old, new in zip(old_span, new_span, strict=False):
                if removes_capitalization(old, new):
                    return False
    return True


def capitalization_edits(original, candidate):
    old_words = words(original)
    new_words = words(candidate)
    matcher = SequenceMatcher(
        None,
        [word.casefold() for word in old_words],
        [word.casefold() for word in new_words],
        autojunk=False,
    )
    edits = []
    for operation, old_start, old_end, new_start, new_end in matcher.get_opcodes():
        if operation != "equal":
            continue
        for index, (old, new) in enumerate(
            zip(
                old_words[old_start:old_end],
                new_words[new_start:new_end],
                strict=True,
            ),
            old_start,
        ):
            if old != new:
                edits.append({"index": index, "original": old, "corrected": new})
    return edits


def punctuation_additions(original, candidate):
    old = Counter(char for char in original if char in PUNCTUATION)
    new = Counter(char for char in candidate if char in PUNCTUATION)
    return Counter({char: max(0, new[char] - old[char]) for char in PUNCTUATION})


def punctuation_removals(original, candidate):
    old = Counter(
        char for char in original if unicodedata.category(char).startswith("P")
    )
    new = Counter(
        char for char in candidate if unicodedata.category(char).startswith("P")
    )
    removed = old - new

    old_words = words(original)
    new_words = words(candidate)
    matcher = SequenceMatcher(
        None,
        [word.casefold() for word in old_words],
        [word.casefold() for word in new_words],
        autojunk=False,
    )
    allowed = Counter()
    for operation, old_start, old_end, new_start, new_end in matcher.get_opcodes():
        if operation != "replace" or old_end - old_start != new_end - new_start:
            continue
        for old_word, new_word in zip(
            old_words[old_start:old_end],
            new_words[new_start:new_end],
            strict=True,
        ):
            if (
                old_word.replace("'", "").casefold()
                != new_word.replace("'", "").casefold()
            ):
                continue
            removed_apostrophes = old_word.count("'") - new_word.count("'")
            if removed_apostrophes > 0:
                allowed["'"] += removed_apostrophes
    return removed - allowed


def word_edit_shape(original, candidate):
    old_words = words(original)
    new_words = words(candidate)
    matcher = SequenceMatcher(
        None,
        [word.casefold() for word in old_words],
        [word.casefold() for word in new_words],
        autojunk=False,
    )
    changes = []
    deletion_spans = 0
    deleted_word_count = 0
    lexical_edit_spans = 0
    reason = None
    for operation, old_start, old_end, new_start, new_end in matcher.get_opcodes():
        if operation == "equal":
            continue
        old = old_words[old_start:old_end]
        new = new_words[new_start:new_end]
        changes.append(
            {
                "operation": operation,
                "old_words": old,
                "new_words": new,
            }
        )
        if operation == "replace" and is_allowed_word_replacement(old, new):
            lexical_edit_spans += 1
            continue
        if operation == "insert" and len(new) == 1:
            lexical_edit_spans += 1
            continue
        if operation in {"delete", "replace"} and not new:
            if not 1 <= len(old) <= 2:
                reason = "a punctuation name may consume only one or two words"
                break
            deletion_spans += 1
            deleted_word_count += len(old)
            continue
        reason = "words were inserted, reordered, or replaced unevenly"
        break

    if reason is None and lexical_edit_spans > 1:
        reason = "more than one lexical edit span"
    added_marks = punctuation_additions(original, candidate)
    if reason is None and deletion_spans > sum(added_marks.values()):
        reason = "deleted words were not replaced by punctuation"
    required_deleted_words = (
        sum(count for mark, count in added_marks.items() if mark != "-")
        + added_marks["?"]
        + added_marks["!"]
    )
    if reason is None and deleted_word_count < required_deleted_words:
        reason = "a multiword punctuation name was not fully consumed"
    return reason is None, changes, reason


def stays_within_punctuation_scope(original, candidate, expected):
    actual_additions = punctuation_additions(original, candidate)
    expected_additions = punctuation_additions(original, expected)
    passed = all(
        actual_additions[mark] <= expected_additions[mark] for mark in PUNCTUATION
    )
    return passed, actual_additions, expected_additions


def load_inputs():
    run_dir = Path(os.environ["SMEVALS_RUN_DIR"])
    run = yaml.safe_load((run_dir / "run.yaml").read_text())
    task = run["task"]
    result = json.loads((run_dir / "result.json").read_text())
    return task, result


def task_expectation(task, original):
    has_expected = "expected" in task
    has_unchanged = "unchanged" in task
    if has_expected == has_unchanged:
        raise ValueError("Task must define exactly one of expected or unchanged")
    if has_unchanged:
        if task["unchanged"] is not True:
            raise ValueError("Task unchanged value must be true")
        return True, original
    return False, task["expected"].strip()


def evaluate(criterion, task, result):
    original = result["utterance"].strip()
    actual = result["effective_output"].strip()
    raw = (result.get("model_output") or "").strip()
    unchanged, expected = task_expectation(task, original)
    proposal = original if raw == "NOCHANGE" else raw
    applicable = True

    if criterion == "preferred_output":
        passed = actual == expected
        details = {"actual": actual, "expected": expected}
    elif criterion == "word_edit_shape_valid":
        passed, actual_changes, reason = word_edit_shape(original, actual)
        details = {"actual_changes": actual_changes, "reason": reason}
    elif criterion == "capitalization_not_removed":
        passed = preserves_existing_capitalization(original, actual)
        details = {"actual": actual}
    elif criterion == "punctuation_not_removed":
        removals = punctuation_removals(original, actual)
        passed = not removals
        details = {"removed_punctuation": dict(removals)}
    elif criterion == "capitalization_matches_preferred":
        actual_edits = capitalization_edits(original, actual)
        expected_edits = capitalization_edits(original, expected)
        passed = actual_edits == expected_edits
        details = {"actual_edits": actual_edits, "expected_edits": expected_edits}
    elif criterion == "punctuation_scope":
        passed, actual_additions, expected_additions = stays_within_punctuation_scope(
            original, actual, expected
        )
        details = {
            "actual_additions": dict(actual_additions),
            "expected_additions": dict(expected_additions),
        }
    elif criterion == "proposal_word_edit_shape_valid":
        passed, proposal_changes, reason = word_edit_shape(original, proposal)
        details = {"proposal_changes": proposal_changes, "reason": reason}
    elif criterion == "proposal_capitalization_not_removed":
        passed = preserves_existing_capitalization(original, proposal)
        details = {"proposal": proposal}
    elif criterion == "proposal_punctuation_not_removed":
        removals = punctuation_removals(original, proposal)
        passed = not removals
        details = {"removed_punctuation": dict(removals)}
    elif criterion == "proposal_capitalization_matches_preferred":
        proposal_edits = capitalization_edits(original, proposal)
        expected_edits = capitalization_edits(original, expected)
        passed = proposal_edits == expected_edits
        details = {
            "proposal_edits": proposal_edits,
            "expected_edits": expected_edits,
        }
    elif criterion == "proposal_punctuation_scope":
        passed, proposal_additions, expected_additions = stays_within_punctuation_scope(
            original, proposal, expected
        )
        details = {
            "proposal_additions": dict(proposal_additions),
            "expected_additions": dict(expected_additions),
        }
    elif criterion == "context_not_output":
        context = {
            "text_before": task.get("text_before", "").strip(),
            "text_after": task.get("text_after", "").strip(),
        }
        populated_context = {name: value for name, value in context.items() if value}
        applicable = bool(populated_context)
        passed = (
            not applicable
            or raw == "NOCHANGE"
            or all(
                value.casefold() not in raw.casefold()
                for value in populated_context.values()
            )
        )
        details = {"context": populated_context, "raw_output": raw}
    elif criterion == "tags_absent":
        passed = not re.search(r"</?(?:utterance|text_before|text_after)>", raw)
        details = {"raw_output": raw}
    elif criterion == "proposal_accepted":
        passed = result["outcome"] != "unsafe"
        details = {"outcome": result["outcome"]}
    elif criterion == "nochange_protocol":
        applicable = unchanged
        passed = not applicable or raw == "NOCHANGE"
        details = {"raw_output": raw}
    else:
        raise ValueError(f"Unknown criterion: {criterion}")
    return applicable, passed, details


def emit_grade(task, result):
    entries = []
    metrics = {}
    tags = [f"category_{task['category']}"]
    details = {}
    for criterion in CRITERIA:
        applicable, passed, criterion_details = evaluate(criterion, task, result)
        if not applicable:
            continue
        severity = CRITERION_SEVERITY[criterion]
        entries.append(
            {
                "criterion": criterion,
                "passed": passed,
                "severity": severity,
            }
        )
        metrics[criterion] = passed
        details[criterion] = criterion_details
        if not passed:
            tags.append(f"failed_{criterion}")
        if criterion == "proposal_accepted" and result["outcome"] in {
            "unsafe",
            "identical",
        }:
            tags.append(f"proposal_{result['outcome']}")

    possible = len(entries)
    earned = sum(entry["passed"] for entry in entries)
    score = earned / possible if possible else 0.0
    required_pass = all(
        entry["passed"] for entry in entries if entry["severity"] == "required"
    )
    metrics.update({"required_pass": required_pass})
    failed = [entry["criterion"] for entry in entries if not entry["passed"]]
    print(
        json.dumps(
            {
                "score": score,
                "metrics": metrics,
                "tags": tags,
                "notes": (
                    "all applicable criteria passed"
                    if not failed
                    else "failed: " + ", ".join(failed)
                ),
                "details": {"criteria": entries, "diagnostics": details},
            }
        )
    )
    return 0 if required_pass else 1


def main():
    task, result = load_inputs()
    return emit_grade(task, result)


if __name__ == "__main__":
    raise SystemExit(main())
