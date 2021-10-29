title: /Emacs editor/
-
# General
cancel: key(ctrl-g)
^emacs close now$: key(ctrl-x ctrl-c)

# Movement
preev: key(ctrl-r)
next: key(ctrl-s)
layer preev: key(ctrl-alt-b)
layer next: key(ctrl-alt-f)
layer down: key(ctrl-alt-d)
layer up: key(ctrl-alt-u)
exper preev: key(ctrl-c c ctrl-b)
exper next: key(ctrl-c c ctrl-f)
word preev: key(alt-p)
word next: key(alt-n)
error preev: key(f11)
error next: key(f12)
go before [preev] <user.word>:
    key(ctrl-r)
    insert(word)
    key(enter)
go after preev <user.word>:
    key(left ctrl-r)
    insert(word)
    key(enter)
go before next <user.word>:
    key(right ctrl-s)
    insert(word)
    key(enter)
go after [next] <user.word>:
    key(ctrl-s)
    insert(word)
    key(enter)
words <user.text>:
    key(ctrl-c c ctrl-r)
    insert(text)
    key(enter)
words <user.word> through <user.word>:
    key(ctrl-c c ctrl-t)
    insert(word_1)
    key(enter)
    insert(word_2)
    key(enter)
replace <user.word> with <user.word>:
    key(ctrl-c c alt-shift-5)
    insert(word_1)
    key(enter)
    insert(word_2)
    key(enter)

# General
exec: key(alt-x)
helm: key(ctrl-x c)
helm open: key(ctrl-x c b)
prefix: key(ctrl-u)
reload: key(g)
quit: key(q)
confirm:
    insert("yes")
    key(enter)
deny:
    insert("no")
    key(enter)
link open:
    key(ctrl-c c u)
    sleep(25ms)
    user.open_url(clip.text())

# Introspection
help variable: key(ctrl-h v)
help function: key(ctrl-h f)
help key: key(ctrl-h k)
help mode: key(ctrl-h m)
help back: key(ctrl-c ctrl-b)
customize open:
    key(ctrl-c alt-x)
    insert("customize-apropos")
    key(enter)

# Window manipulation
buff open: key(ctrl-x b)
buff open split: key(ctrl-x 3 ctrl-x o ctrl-x b)
buff switch: key(ctrl-x b enter)
buff close: key(ctrl-x 0)
buff done: key(ctrl-x #)
buff kill: key(ctrl-x k enter)
buff even: key(ctrl-x +)
buff up:
    key(ctrl-c alt-x)
    insert("windmove-up")
    key(enter)
buff down:
    key(ctrl-c alt-x)
    insert("windmove-down")
    key(enter)
buff left:
    key(ctrl-c alt-x)
    insert("windmove-left")
    key(enter)
buff right:
    key(ctrl-c alt-x)
    insert("windmove-right")
    key(enter)
buff revert:
    key(ctrl-c alt-x)
    insert("revert-buffer")
    key(enter)

# Filesystem
save as: key(ctrl-x ctrl-w)
save all: key(ctrl-x s)
save all now: key(ctrl-u ctrl-x s)
file open: key(ctrl-x ctrl-f)
ido close: key(ctrl-f)
ido reload: key(ctrl-l)
directory open: key(ctrl-x d)
file open recent: key(ctrl-x ctrl-r)
file open split: key(ctrl-x 4 f)
file open project: key(ctrl-c p f)
file open simulator: key(ctrl-c c p s)
project open: key(ctrl-c p p)
project switch: key(ctrl-c s)
result next: key(alt-,)
def open: key(alt-.)
ref open: key(alt-shift-/ enter)
def close: key(alt-,)
R grep:
    key(ctrl-c alt-x)
    insert("rgrep")
    key(enter)
code search:
    key(ctrl-c alt-x)
    insert("cs-feeling-lucky")
    key(enter)

# Bookmarks
bookmark open: key(ctrl-x r b)
bookmark save: key(ctrl-x r m)
bookmark list: key(ctrl-x r l)

# Movement
start: key(alt-m)
line <number_small> [short]:
    key(ctrl-u)
    insert("{number_small}")
    key(ctrl-c c g)
here scroll: key(ctrl-l)
mark set: key(ctrl-space)
mark save: key(ctrl-\)
go mark: key(ctrl-<)
go change: key(ctrl-c c c)
go symbol: key(alt-i)
go mark switch: key(ctrl-c ctrl-x)
search edit: key(alt-e)
search word: key(alt-s w)
search symbol: key(alt-s _)
regex preev: key(ctrl-alt-r)
regex next: key(ctrl-alt-s)
occur: key(alt-s o)
symbol preev: key(alt-s . ctrl-r ctrl-r)
symbol next: key(alt-s . ctrl-s)
go before [preev] <user.any_alphanumeric_key>: key("ctrl-c c b {any_alphanumeric_key}")
go after [next] <user.any_alphanumeric_key>: key("ctrl-c c f {any_alphanumeric_key}")
go before next <user.any_alphanumeric_key>: key("ctrl-c c s {any_alphanumeric_key}")
go after preev <user.any_alphanumeric_key>: key("ctrl-c c e {any_alphanumeric_key}")
other screen up: key(ctrl-- ctrl-alt-v)
other screen down: key(ctrl-alt-v)
# go eye <char>: ['c-c, c, j']+'%(char)s'+'"go eye <char>": Key("c-c, c, j") + Text(u"%(char)s") + Function(lambda: tracker.type_gaze_point("%d\\n%d\\n")),'()

# Editing
delete: key(ctrl-c c ctrl-w)
ahead: key(alt-f)
behind: key(alt-b)
aheads delete | clear ahead: key(alt-d)
behinds delete | clear behind: key(alt-backspace)
aheads | select ahead: key(ctrl-space alt-f)
behinds | select behind: key(ctrl-space alt-b)
line open up: key(alt-enter)
line open down: key(ctrl-enter)
(this|line) copy up: key(alt-shift-up)
(line|lines) join: key(alt-shift-6)
line <number_small> open:
    key(ctrl-u)
    insert("{number_small}")
    key(ctrl-c c g alt-enter)
this select: key(ctrl-x ctrl-x)
this indent: key(ctrl-alt-\)
(this|here) comment: key(alt-;)
this format [clang]: key(ctrl-alt-q)
this format comment: key(alt-q)
replace: key(alt-shift-5)
regex replace: key(ctrl-alt-shift-5)
symbol replace: key(alt-')
paste (other|preev): key(alt-y)
# Avoid optionals to work around https://github.com/talonvoice/talon/issues/385
<number_small> (through | until) [select]: user.mark_lines(number_small_1, -1)
<number_small> (through | until) <number_small> [select]: user.mark_lines(number_small_1, number_small_2)
<number_small> (through | until) short [select]: user.mark_lines(number_small_1, -1, 1)
<number_small> (through | until) <number_small> short [select]: user.mark_lines(number_small_1, number_small_2, 1)
<number_small> (through | until) copy here: user.use_lines(number_small_1, -1, "alt-w", "ctrl-y")
<number_small> (through | until) <number_small> copy here: user.use_lines(number_small_1, number_small_2, "alt-w", "ctrl-y")
<number_small> (through | until) short copy here: user.use_lines(number_small_1, -1, "alt-w", "ctrl-y", 1)
<number_small> (through | until) <number_small> short copy here: user.use_lines(number_small_1, number_small_2, "alt-w", "ctrl-y", 1)
<number_small> (through | until) move here: user.use_lines(number_small_1, -1, "ctrl-w", "ctrl-y")
<number_small> (through | until) <number_small> move here: user.use_lines(number_small_1, number_small_2, "ctrl-w", "ctrl-y")
<number_small> (through | until) short move here: user.use_lines(number_small_1, -1, "ctrl-w", "ctrl-y", 1)
<number_small> (through | until) <number_small> short move here: user.use_lines(number_small_1, number_small_2, "ctrl-w", "ctrl-y", 1)
other <number_small> (through | until) copy here: user.use_lines(number_small_1, -1, "alt-w", "ctrl-y", 0, 1)
other <number_small> (through | until) <number_small> copy here: user.use_lines(number_small_1, number_small_2, "alt-w", "ctrl-y", 0, 1)
other <number_small> (through | until) short copy here: user.use_lines(number_small_1, -1, "alt-w", "ctrl-y", 1, 1)
other <number_small> (through | until) <number_small> short copy here: user.use_lines(number_small_1, number_small_2, "alt-w", "ctrl-y", 1, 1)
other <number_small> (through | until) move here: user.use_lines(number_small_1, -1, "ctrl-w", "ctrl-y", 0, 1)
other <number_small> (through | until) <number_small> move here: user.use_lines(number_small_1, number_small_2, "ctrl-w", "ctrl-y", 0, 1)
other <number_small> (through | until) short move here: user.use_lines(number_small_1, -1, "ctrl-w", "ctrl-y", 1, 1)
other <number_small> (through | until) <number_small> short move here: user.use_lines(number_small_1, number_small_2, "ctrl-w", "ctrl-y", 1, 1)
layer select: key(ctrl-alt-shift-2)
layer kill: key(ctrl-alt-k)
select more: key(ctrl-=)
select less: key(ctrl-+)
this parens: key(alt-()
tag close: key(ctrl-c ctrl-e)

# Registers
mark save (reg|rej) <user.letter>: key("ctrl-x r space {letter}")
go (reg|rej) <user.letter>: key("ctrl-x r j {letter}")
copy (reg|rej) <user.letter>: key("ctrl-x r s {letter}")
(reg|rej) <user.letter> paste: key("ctrl-u ctrl-x r i {letter}")

# Templates
(snippet | template) open: key(ctrl-c & ctrl-v)
(snippet | template) new: key(ctrl-c & ctrl-n)
(snippets | templates) reload:
    key(ctrl-c alt-x)
    insert("yas-reload-all")
    key(enter)

# Compilation
file build: key(ctrl-c ctrl-g)
file test: key(ctrl-c ctrl-t)
recompile:
    key(ctrl-c alt-x)
    insert("recompile")
    key(enter)

# Dired
toggle details:
    key(ctrl-c alt-x)
    insert("dired-hide-details-mode")
    key(enter)

# Web editing
JavaScript mode:
    key(ctrl-c alt-x)
    insert("js-mode")
    key(enter)
HTML mode:
    key(ctrl-c alt-x)
    insert("html-mode")
    key(enter)

# C++
header open: key(ctrl-x ctrl-h)
header open split: key(ctrl-x 3 ctrl-x o ctrl-x ctrl-h)
import copy: key(f5)
import paste: key(f6)
this import:
    key(ctrl-c alt-x)
    insert("clang-include-fixer-at-point")
    key(enter)

# Python
pie flakes: key(ctrl-c ctrl-v)

# Shell
shell open:
    key(ctrl-c alt-x)
    insert("shell")
    key(enter)
shell open directory: key(ctrl-c c $)
shell open vc: key(ctrl-c c v)

# Clojure
closure compile: key(ctrl-c ctrl-k)
closure namespace: key(ctrl-c alt-n)

# Lisp
function run: key(ctrl-alt-x)
this run:
    key(ctrl-c alt-x)
    insert("eval-region")
    key(enter)

# Version control
magit open: key(ctrl-c m)
diff open: key(ctrl-x v =)
VC open: key(ctrl-x v d enter)

# GhostText
ghost close: key(ctrl-c ctrl-c)
