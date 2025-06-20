os: mac
hostname: /jwstout/
-
settings():
    # user.vocabulary_recording_dir = "/Users/jwstout/.talon/vocabulary_recordings"
    user.model_llm_plugins = "llm-echo,llm-templates-fabric,llm-fragments-github,llm-docs,llm-gemini,llm-fragments-markitdown,llm-templates-github"
    user.model_llm_path = "/Users/jwstout/.local/bin/llm"
    user.model_markitdown_path = "/Users/jwstout/.local/bin/markitdown"
    user.model_markdown_py_path = "/Users/jwstout/.local/bin/markdown_py"
    user.markitdown_path = "/Users/jwstout/.local/bin/markitdown"
    user.strip_tags_path = "/Users/jwstout/.local/bin/strip-tags"
    user.model_default = "gemini-flash-no-thinking"
    # user.ocr_logging_dir = "/Users/jwstout/.talon/ocr"
