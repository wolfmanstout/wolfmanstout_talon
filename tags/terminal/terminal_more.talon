tag: terminal
-
reset terminal: insert("exec bash\n")
{user.shell_commands}: insert("{shell_commands} ")
u v {user.uv_subcommands}: insert("uv {uv_subcommands} ")
