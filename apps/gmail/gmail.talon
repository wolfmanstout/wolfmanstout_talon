app: gmail
-

settings():
    user.peek_right_after_insertion = true
    # Gmail sometimes swallows lone newlines, so don't force paste for them
    user.paste_to_insert_newlines = false
    user.accessibility_dictation = true

tag(): user.emoji

# Composing
compose: key(+ c)
reply: key(+ r)
reply all: key(+ a)
forward: key(+ f)
# go field to: ClickElementAction("//*[@aria-label='To']")
go field cc: key(ctrl-shift-c)
this send: key(ctrl-enter)
[suggest] keep: key(tab)

touch discard:
    user.mouse_helper_position_save()
    user.mouse_helper_move_image_relative("2023-08-25_11.31.37.425605.png", 0, 0, 0, user.mouse_helper_calculate_relative_rect("0 -200 -0 -0"))
    sleep(0.05)
    mouse_click(0)
    sleep(0.05)
    user.mouse_helper_position_restore()

# Messages
open: key(+ o)
[this] archive: key(+ {)
[this] done: key(+ [)
this unread: key(+ _)
gmail undo: key(+ z)
list: key(+ u)
important: key(+ +)
this star: key(+ s)
this important: key(+ +)
this not important: key(+ -)
snooze tomorrow:
    key(+ b)
    sleep(50ms)
    key(down down)
    sleep(50ms)
    key(enter)
label waiting:
    key(+ l)
    sleep(500ms)
    insert("waiting")
    sleep(500ms)
    key(enter)
label snooze:
    key(+ l)
    sleep(500ms)
    insert("snooze")
    sleep(500ms)
    key(enter)
# snooze:
#     key(+ l)
#     sleep(500ms)
#     insert("snooze")
#     sleep(500ms)
#     key(enter)
#     sleep(500ms)
#     key(+ [)
label vacation:
    key(+ l)
    sleep(500ms)
    insert("vacation")
    sleep(500ms)
    key(enter)
label house:
    key(+ l)
    sleep(500ms)
    insert("house")
    sleep(500ms)
    key(enter)
label taxes:
    key(+ l)
    sleep(500ms)
    insert("taxes")
    sleep(500ms)
    key(enter)
label hiring:
    key(+ l)
    sleep(500ms)
    insert("hiring")
    sleep(500ms)
    key(enter)
label pa for air:
    key(+ l)
    sleep(500ms)
    insert("P4AIR")
    sleep(500ms)
    key(enter)
label: key(+ l)
this select: key(+ x)
# <n> select: {['plus, x, plus, j']}n
(message | messages) reload: key(+ N)
go inbox | going box: key(+ g i)
go (starred | star): key(+ g s)
go sent: key(+ g t)
go drafts: key(+ g d)
touch expand (all | al):
    user.mouse_helper_position_save()
    user.mouse_helper_move_image_relative("2023-09-26_12.58.32.898292.png", 0)
    sleep(0.05)
    mouse_click(0)
    sleep(0.05)
    user.mouse_helper_position_restore()

touch collapse (all | al):
    user.mouse_helper_position_save()
    user.mouse_helper_move_image_relative("2023-08-12_16.01.41.668613.png", 0)
    sleep(0.05)
    mouse_click(0)
    sleep(0.05)
    user.mouse_helper_position_restore()

touch message options:
    user.mouse_helper_position_save()
    user.mouse_helper_move_image_relative("2023-10-09_17.20.54.079391.png", 0, 0, 0, user.mouse_helper_calculate_relative_rect("0 -200 -0 -0"))
    sleep(0.05)
    mouse_click(0)
    sleep(0.05)
    user.mouse_helper_position_restore()

chat open: key(+ q)
go search: key(+ /)
last | preev: key(+ k)
next: key(+ j)
message (last | preev): key(+ p)
message next: key(+ n)
section next: key(+ `)
section (last | preev): key(+ ~)
