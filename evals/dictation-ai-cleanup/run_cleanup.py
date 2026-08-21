#!/usr/bin/env python
import hashlib
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(REPO_ROOT / "test" / "stubs"), str(REPO_ROOT)]

from core.text.text_and_dictation import (  # noqa: E402
    _cleanup_prompt,
    _current_sentence_fragment,
    _run_ai_cleanup_result,
)


def main() -> int:
    backend = os.getenv("DICTATION_AI_CLEANUP_BACKEND", "mlx")
    default_url = (
        "http://127.0.0.1:11434/api/generate"
        if backend == "ollama"
        else "http://127.0.0.1:8080/chat/completions"
    )
    text_before = os.environ.get("SMEVALS_TASK_TEXT_BEFORE", "")
    utterance = os.environ["SMEVALS_TASK_UTTERANCE"]

    result = _run_ai_cleanup_result(
        text_before,
        utterance,
        os.environ["SMEVALS_MODEL"],
        os.getenv("DICTATION_AI_CLEANUP_URL", default_url),
        int(os.getenv("DICTATION_AI_CLEANUP_TIMEOUT_S", "30")),
        backend,
    )
    effective_output = (
        utterance if result.corrected_text is None else result.corrected_text
    )
    artifact = {
        "utterance": utterance,
        "model_output": result.model_output,
        "corrected_text": result.corrected_text,
        "effective_output": effective_output,
        "outcome": result.outcome,
    }
    run_dir = Path(os.environ["SMEVALS_RUN_DIR"])
    prompt = _cleanup_prompt(_current_sentence_fragment(text_before), utterance)
    source = REPO_ROOT / "core" / "text" / "text_and_dictation.py"
    artifact["harness_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
    (run_dir / "result.json").write_text(json.dumps(artifact, indent=2) + "\n")
    (run_dir / "prompt.txt").write_text(prompt)
    print(result.model_output or "", end="")
    return 1 if result.outcome == "error" else 0


if __name__ == "__main__":
    raise SystemExit(main())
