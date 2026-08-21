# Dictation AI cleanup eval

This eval runs the production cleanup harness and retains both the raw model
response and the post-processed result. Each task is graded independently on:

- expected user-visible behavior;
- word preservation and directional capitalization safety;
- allowed punctuation scope;
- read-only context isolation;
- input-tag leakage;
- raw proposal safety; and
- efficient use of `NOCHANGE`.

Severity belongs to criteria, not tasks. Required criteria cover clear
instruction violations: invalid word edits, removal of existing capitalization,
changes to protected capitalized words, read-only context leakage, and tag
leakage. Advisory criteria cover judgment and efficiency: the preferred
correction, capitalization additions, punctuation scope, raw proposal
acceptance, and `NOCHANGE` use. Every applicable criterion contributes equally
to the score, while any required failure independently fails the grade. The
checker still reports every applicable metric after a required failure.

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

Each `tasks/*.yaml` file contains the adjacent text, utterance, and category.
Changed cases define one preferred `expected` output; unchanged cases instead
say `unchanged: true`, avoiding a duplicated utterance. All criteria and their
severities are defined centrally by the checker rather than repeated in every
task. The historical unspoken-comma cases live in
`tasks-disabled-unspoken-commas/`, which `smevals` intentionally does not
discover.
