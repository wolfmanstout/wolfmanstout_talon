# Dictation AI cleanup eval

This eval runs the production cleanup harness and retains both the raw model
response and the post-processed result. Each task is graded independently on:

- expected user-visible behavior;
- word, punctuation, and directional capitalization preservation;
- allowed punctuation scope;
- read-only context isolation;
- input-tag leakage;
- raw proposal safety; and
- efficient use of `NOCHANGE`.

Severity belongs to criteria, not tasks. Required criteria cover clear
instruction violations: invalid word edits, removal of existing punctuation or
capitalization, changes to protected capitalized words, read-only context
leakage, and tag leakage. Advisory criteria cover judgment and efficiency: the preferred
correction, capitalization additions, punctuation scope, raw proposal
acceptance, and `NOCHANGE` use. Every applicable criterion contributes equally
to the score, while any required failure independently fails the grade. The
checker still reports every applicable metric after a required failure.

The required word-shape criteria allow one localized one-to-two-word split or
merge, or one restored recognition omission. Whether that edit was warranted
is advisory. Standalone word deletion, multiple lexical edit regions, broad
rewrites, and punctuation safety violations remain required failures.

Each run also stores the exact prompt and a hash of the runtime source. When
the custom checker changes, increment its `version` in `graders/default.yaml`;
`smevals` snapshots grader configuration but does not hash checker source.

Run the default MLX configuration:

```bash
uv run smevals run .evals/dictation-ai-cleanup -g
uv run smevals report .evals/dictation-ai-cleanup --by-task
```

The runner honors `DICTATION_AI_CLEANUP_BACKEND`,
`DICTATION_AI_CLEANUP_URL`, and `DICTATION_AI_CLEANUP_TIMEOUT_S`. Pass `-m` to
compare another model. Runs are ignored by Git and can instead be stored
outside the repository with `--runs-dir`.

Implementation note: backend, URL, and timeout are inherited from the process
environment because smevals currently exposes only `model` from a Config to
its Runner. Ideally, smevals would pass arbitrary scalar Config fields through
as `SMEVALS_CONFIG_<KEY>` variables and preserve the resolved Config in
`run.yaml`. We could then keep all harness settings in the Config YAML instead
of splitting them between YAML and environment variables.

Each `tasks/*.yaml` file contains the adjacent text before and after the
utterance, the utterance itself, and its category. `text_before` and
`text_after` may each be omitted when unavailable or empty.
Changed cases define one preferred `expected` output; unchanged cases instead
say `unchanged: true`, avoiding a duplicated utterance. All criteria and their
severities are defined centrally by the checker rather than repeated in every
task. The historical unspoken-comma cases live in
`tasks-disabled-unspoken-commas/`, which `smevals` intentionally does not
discover.

`text_before`, `utterance`, and `text_after` must preserve their exact on-screen
boundaries; the eval runner does not add or remove spacing. An utterance commonly
starts with a separating space after ordinary text, but not after an opening
delimiter: `text (` plus `inside)` represents `text (inside)`, not
`text ( inside)`. Likewise, word text after a word-ending utterance generally
starts with a space.
