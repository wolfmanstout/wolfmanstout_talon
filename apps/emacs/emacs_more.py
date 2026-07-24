from talon import Module, actions

mod = Module()


@mod.action_class
class Actions:
    def jump_modulo_line(n: int):
        """Jumps to the nearest line number modulo 100."""
        actions.user.emacs("goto-modulo-line", n)

    def mark_lines(n1: int, n2: int = -1, tight: bool = False, tree: bool = False):
        """Marks the lines from n1 to n2."""
        actions.user.jump_modulo_line(n1)
        if tree:
            actions.user.emacs("org-mark-element")
            return
        if tight:
            actions.user.emacs("back-to-indentation")
        actions.user.emacs("set-mark-command")
        if n2 != -1:
            actions.user.jump_modulo_line(n2)
        if tight:
            actions.user.emacs("move-end-of-line")
        else:
            actions.user.emacs("next-line")

    def use_lines(
        n1: int,
        n2: int = -1,
        copy: bool = False,
        tight: bool = False,
        other_buffer: bool = False,
        tree: bool = False,
    ):
        """Copies or moves lines to the current position."""
        if other_buffer:
            actions.user.emacs("other-window")
        else:
            actions.user.emacs("push-mark-no-activate")

        actions.user.mark_lines(n1, n2, tight, tree)
        actions.user.emacs("kill-ring-save" if copy else "kill-region")
        actions.user.emacs("jump-to-mark")

        if other_buffer:
            actions.user.emacs("other-window")
        else:
            actions.user.emacs("jump-to-mark")
        if not tight and not tree:
            actions.user.emacs("move-beginning-of-line")
        actions.user.emacs("org-paste-special" if tree else "yank")
