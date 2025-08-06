os: mac
app: iterm2
-
settings():
    # Selection does not work properly here by default.
    # TODO Explore built-in support for this.
    user.context_sensitive_dictation = false

tag(): terminal
# todo: filemanager support
#tag(): user.file_manager
tag(): user.generic_unix_shell
tag(): user.git
tag(): user.kubectl
tag(): user.tabs
tag(): user.readline
