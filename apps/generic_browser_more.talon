tag: browser
-
link: key(ctrl-,)
link tab | tab [new] link: key(ctrl-.)
(link | links) background [tab]: key(alt-f)
tab move left: key(ctrl-shift-pageup)
tab move right: key(ctrl-shift-pagedown)
tab (dupe | duplicate): key(ctrl-l alt-enter)
workspace open: key(alt-a)
workspace tab (open|new): key(alt-s)
workspace close: key(alt-w)
workspace new: key(alt-n)
workspace [tab] save: key(alt-shift-d)
(caret|carrot) browsing: key(f7)
code search (voice access|VA):
    key(ctrl-l)
    insert("csva")
    key(tab)
code search car:
    key(ctrl-l)
    insert("csc")
    key(tab)
code search simulator:
    key(ctrl-l)
    insert("css")
    key(tab)
code search:
    key(ctrl-l)
    insert("cs")
    key(tab)
calendar site:
    key(ctrl-l)
    insert("calendar.google.com")
    key(enter)
critique site:
    key(ctrl-l)
    insert("cr/")
    key(enter)
buganizer site:
    key(ctrl-l)
    insert("b/")
    key(enter)
drive site:
    key(ctrl-l)
    insert("drive.google.com")
    key(enter)
docs site:
    key(ctrl-l)
    insert("docs.google.com")
    key(enter)
slides site:
    key(ctrl-l)
    insert("slides.google.com")
    key(enter)
sheets site:
    key(ctrl-l)
    insert("sheets.google.com")
    key(enter)
new (docs|doc) site:
    key(ctrl-l)
    insert("doc.new")
    key(enter)
new (slides|slide) site:
    key(ctrl-l)
    insert("slides.new")
    key(enter)
new (sheets|sheet) site:
    key(ctrl-l)
    insert("sheet.new")
    key(enter)
new (scripts|script) site:
    key(ctrl-l)
    insert("script.new")
    key(enter)
amazon site:
    key(ctrl-l)
    insert("smile.amazon.com")
    key(enter)
meet site:
    key(ctrl-l)
    insert("meet.google.com")
    key(enter)
insert text box: key(alt-i t)
match next: key(ctrl-g)
match preev: key(ctrl-shift-g)
bookmark open: key(ctrl-;)
tab [new] bookmark: key(ctrl-')
frame next: key(ctrl-[)
# webdriver test: 'test_driver'()
# go search: ClickElementAction('q')
search <user.text>$:
    key(ctrl-l)
    insert(text)
    sleep(15ms)
    key(enter)
history search <user.text>$:
    key(ctrl-l)
    insert("history")
    key(tab)
    insert(text)
    key(enter)
history search:
    key(ctrl-l)
    insert("history")
    key(tab)
moma search <user.text>$:
    key(ctrl-l)
    insert("moma")
    key(tab)
    insert(text)
    key(enter)
moma search:
    key(ctrl-l)
    insert("moma")
    key(tab)
# <text> (touch|click) [left]: ClickTextOrButtonAction('%(text)s', dynamic)
