import talon

if hasattr(talon, "test_mode"):
    import importlib.util
    import json
    from pathlib import Path

    import yaml

    CHECKER_PATH = (
        Path(__file__).parents[1]
        / ".evals"
        / "dictation-ai-cleanup"
        / "checkers"
        / "criterion.py"
    )
    SPEC = importlib.util.spec_from_file_location(
        "dictation_ai_smevals_checker", CHECKER_PATH
    )
    assert SPEC is not None and SPEC.loader is not None
    checker = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(checker)

    def test_word_edit_shape_allows_one_replacement_but_not_unrelated_deletion():
        original = "Commit then rebase on maine and push"

        replacement, _, _ = checker.word_edit_shape(
            original, "Commit then rebase on main and push"
        )
        deletion, _, _ = checker.word_edit_shape(
            original, "Commit rebase on main and push"
        )
        insertion, _, _ = checker.word_edit_shape(
            original, "Commit then definitely rebase on main and push"
        )

        assert replacement
        assert not deletion
        assert not insertion

    def test_punctuation_scope_rejects_an_unspoken_comma():
        passed, _, _ = checker.stays_within_punctuation_scope(
            "Yes I agree", "Yes, I agree", "Yes I agree"
        )

        assert not passed

    def test_capitalization_additions_are_advisory_but_removals_are_rejected():
        assert checker.preserves_existing_capitalization("ask michael", "ask Michael")
        assert not checker.preserves_existing_capitalization("ask Sponge", "ask sponge")
        assert checker.capitalization_edits("ask michael", "ask Michael") == [
            {"index": 1, "original": "michael", "corrected": "Michael"}
        ]

    def test_severity_is_owned_by_the_criterion():
        assert (
            checker.CRITERION_SEVERITY["proposal_word_edit_shape_valid"] == "required"
        )
        assert checker.CRITERION_SEVERITY["proposal_punctuation_scope"] == "advisory"
        assert checker.CRITERION_SEVERITY["preferred_output"] == "advisory"

    def test_tasks_define_exactly_one_explicit_expectation():
        eval_root = CHECKER_PATH.parents[1]
        task_roots = [
            eval_root / "tasks",
            eval_root / "tasks-disabled-unspoken-commas",
        ]

        for task_root in task_roots:
            for task_path in task_root.glob("*.yaml"):
                task = yaml.safe_load(task_path.read_text())
                assert ("expected" in task) != ("unchanged" in task), task_path
                if "unchanged" in task:
                    assert task["unchanged"] is True, task_path

    def test_advisory_failure_does_not_block_grade(capsys):
        task = {"category": "homophone", "expected": "cache is warm"}
        result = {
            "utterance": "cash is warm",
            "effective_output": "cash is warm",
            "model_output": "NOCHANGE",
            "outcome": "nochange",
        }

        exit_code = checker.emit_grade(task, result)
        grade = json.loads(capsys.readouterr().out)

        assert exit_code == 0
        assert grade["metrics"]["required_pass"]
        assert not grade["metrics"]["preferred_output"]

    def test_required_failure_blocks_grade(capsys):
        task = {"category": "preservation", "unchanged": True}
        result = {
            "utterance": "cash is warm",
            "effective_output": "cash is warm",
            "model_output": "cash warm",
            "outcome": "unsafe",
        }

        exit_code = checker.emit_grade(task, result)
        grade = json.loads(capsys.readouterr().out)

        assert exit_code == 1
        assert not grade["metrics"]["required_pass"]
        assert not grade["metrics"]["proposal_word_edit_shape_valid"]

    def test_context_is_rejected_even_when_repeated_after_the_utterance():
        task = {
            "unchanged": True,
            "text_before": "What time is it question mark",
        }
        result = {
            "utterance": " I don't know",
            "effective_output": " I don't know",
            "model_output": "I don't know What time is it question mark",
            "outcome": "unsafe",
        }

        applicable, passed, _ = checker.evaluate("context_not_output", task, result)

        assert applicable
        assert not passed
