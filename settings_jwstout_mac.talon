os: mac
hostname: /jwstout/
-
settings():
    # user.vocabulary_recording_dir = "/Users/jwstout/.talon/vocabulary_recordings"
    user.model_llm_plugins = "llm-echo,llm-templates-fabric,llm-fragments-github,llm-docs,llm-gemini,llm-fragments-markitdown,llm-templates-github"
    user.model_llm_path = "/Users/jwstout/.local/bin/llm"
    user.model_markdownify_path = "/Users/jwstout/.local/bin/markdownify"
    user.model_markdown_it_py_path = "/Users/jwstout/.local/bin/markdown-it"
    user.markdownify_path = "/Users/jwstout/.local/bin/markdownify"
    user.strip_tags_path = "/Users/jwstout/.local/bin/strip-tags"
    user.model_default = "gemini-flash-no-thinking"
    # user.ocr_logging_dir = "/Users/jwstout/.talon/ocr"
