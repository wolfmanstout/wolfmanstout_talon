app: emacs
-
settings():
    user.mouse_wheel_down_amount = 90
    key_wait = 2

# General
^emacs close now$: key(ctrl-x ctrl-c)
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
search edit: key(alt-e)
search word: key(alt-s w)
search symbol: key(alt-s _)
regex preev: key(ctrl-alt-r)
regex next: key(ctrl-alt-s)
occur: key(alt-s o)
symbol preev: key(alt-s . ctrl-r ctrl-r)
symbol next: key(alt-s . ctrl-s)

# Editing
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
this indent: key(ctrl-alt-\)
(this|here) comment: key(alt-;)
this format [clang]: key(ctrl-alt-q)
this format comment: key(alt-q)
replace: key(alt-shift-5)
regex replace: key(ctrl-alt-shift-5)
symbol replace: key(alt-')
paste (other|preev): key(alt-y)
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
