app: emacs
-

# General
^emacs close now$: user.emacs("save-buffers-kill-emacs")
exec: user.emacs("smex")
reload: key(g)
quit: key(q)
confirm:
    insert("yes")
    key(enter)
deny:
    insert("no")
    key(enter)
link open:
    user.emacs("copy-url-at-point")
    sleep(25ms)
    user.open_url(clip.text())

# Introspection
help variable: user.emacs_help("v")
help function: user.emacs_help("f")
help key: user.emacs_help("k")
help mode: user.emacs_help("m")
help back: user.emacs("help-go-back")
customize open: user.emacs("customize-apropos")

# Filesystem
save as: user.emacs("write-file")
save all: user.emacs("save-some-buffers")
save all now: user.emacs("save-some-buffers", 1)
ido close: user.emacs("ido-fallback-command")
ido reload: user.emacs("ido-reread-directory")
directory open: user.emacs("dired")
file open recent: user.emacs("ido-recentf-open")
file open split: user.emacs("find-file-other-window")
file open project: user.emacs("projectile-find-file")
project open: user.emacs("projectile-switch-project")
result next: user.emacs("xref-go-back")
def open: user.emacs("xref-find-definitions")
ref open:
    user.emacs("xref-find-references")
    key(enter)
def close: user.emacs("xref-go-back")
R grep: user.emacs("rgrep")
code search: user.emacs("cs-feeling-lucky")

# Bookmarks
bookmark open: user.emacs("bookmark-jump")
bookmark save: user.emacs("bookmark-set")
bookmark list: user.emacs("list-bookmarks")

# Movement
last | preev: user.emacs("isearch-backward")
next: user.emacs("isearch-forward")
layer (last | preev): user.emacs("sp-backward-sexp")
layer next: user.emacs("sp-forward-sexp")
layer down: user.emacs("sp-down-sexp")
layer up: user.emacs("sp-backward-up-sexp")
exper (last | preev): user.emacs("backward-cc-expression")
exper next: user.emacs("forward-cc-expression")
word (last | preev): user.emacs("smartscan-symbol-go-backward")
word next: user.emacs("smartscan-symbol-go-forward")
error preev: user.emacs("previous-error")
regex (last | preev): user.emacs("isearch-backward-regexp")
regex next: user.emacs("isearch-forward-regexp")
occur: user.emacs("occur")
symbol (last | preev):
    user.emacs("isearch-forward-symbol-at-point")
    user.emacs("isearch-repeat-backward")
    user.emacs("isearch-repeat-backward")
symbol next:
    user.emacs("isearch-forward-symbol-at-point")
    user.emacs("isearch-repeat-forward")

# Editing
ahead: user.emacs("forward-word")
behind: user.emacs("backward-word")
aheads delete | clear ahead: user.emacs("kill-word")
behinds delete | clear behind: user.emacs("backward-kill-word")
aheads | select ahead:
    user.emacs("set-mark-command")
    user.emacs("forward-word")
behinds | select behind:
    user.emacs("set-mark-command")
    user.emacs("backward-word")
line open up: user.emacs("vi-open-line-above")
line open down: user.emacs("vi-open-line-below")
(this | line) copy up: user.emacs("copy-text-up")
(line | lines) join: user.emacs("delete-indentation")
line <number_small> open:
    user.jump_modulo_line(number_small)
    user.emacs("vi-open-line-above")
this indent: user.emacs("indent-region")
(this | here) comment: user.emacs("comment-dwim")
this format [clang]: user.emacs("indent-sexp")
this format comment: user.emacs("fill-paragraph")
symbol replace: user.emacs("smartscan-symbol-replace")
paste (other | last | preev): user.emacs("yank-pop")
layer select: user.emacs("mark-sexp")
layer kill: user.emacs("sp-kill-sexp")
select more: user.emacs("er/expand-region")
select less: user.emacs("er/contract-region")
this parens: user.emacs("insert-parentheses")
tag close: user.emacs("web-mode-element-close")

# Registers
mark save (reg | rej) <user.letter>:
    user.emacs("point-to-register")
    key("{letter}")
go (reg | rej) <user.letter>:
    user.emacs("jump-to-register")
    key("{letter}")
copy (reg | rej) <user.letter>:
    user.emacs("copy-to-register")
    key("{letter}")
(reg | rej) <user.letter> paste:
    user.emacs_prefix()
    user.emacs("insert-register")
    key("{letter}")

# Templates
(snippet | template) open: user.emacs("yas-visit-snippet-file")
(snippet | template) new: user.emacs("yas-new-snippet")
(snippets | templates) reload: user.emacs("yas-reload-all")

# Compilation
file build: key(ctrl-c ctrl-g)
file test: key(ctrl-c ctrl-t)
recompile: user.emacs("recompile")

# Dired
toggle details: user.emacs("dired-hide-details-mode")

# Web editing
JavaScript mode: user.emacs("js-mode")
HTML mode: user.emacs("html-mode")

# C++
header open: user.emacs("ff-find-other-file")
header open split:
    user.emacs("split-window-right")
    user.emacs("other-window")
    user.emacs("ff-find-other-file")
import copy: key(f5)
import paste: key(f6)
this import: user.emacs("clang-include-fixer-at-point")

# Python
pie flakes: user.emacs("python-check")

# Shell
shell open: user.emacs("shell")
shell open directory: user.emacs("visit-directory-shell")
shell open vc: user.emacs("visit-vc-directory-shell")

# Clojure
closure compile: user.emacs("cider-load-buffer")
closure namespace: user.emacs("cider-repl-set-ns")

# Lisp
function run: user.emacs("eval-defun")
this run: user.emacs("eval-region")

# Version control
magit open: user.emacs("magit-status")
diff open: user.emacs("vc-diff")
VC open:
    user.emacs("vc-dir")
    key(enter)
