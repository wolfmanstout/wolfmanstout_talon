tag: browser
-
link: key(ctrl-,)
link tab | tab [new] link: key(ctrl-.)
(link | links) background [tab]: key(alt-f)
tab move left: key(ctrl-shift-pageup)
tab move right: key(ctrl-shift-pagedown)
workspace open: key(alt-a)
workspace tab (open | new): key(alt-s)
workspace close: key(alt-w)
workspace new: key(alt-n)
workspace [tab] save: key(alt-shift-d)
(caret | carrot) browsing: key(f7)
code search (voice access | VA):
    browser.focus_address()
    insert("csva")
    key(tab)
code search car:
    browser.focus_address()
    insert("csc")
    key(tab)
code search simulator:
    browser.focus_address()
    insert("css")
    key(tab)
code search:
    browser.focus_address()
    insert("cs")
    key(tab)
calendar site:
    browser.focus_address()
    insert("calendar.google.com")
    key(enter)
critique site:
    browser.focus_address()
    insert("cr/")
    key(enter)
buganizer site:
    browser.focus_address()
    insert("b/")
    key(enter)
drive site:
    browser.focus_address()
    insert("drive.google.com")
    key(enter)
docs site:
    browser.focus_address()
    insert("docs.google.com")
    key(enter)
slides site:
    browser.focus_address()
    insert("slides.google.com")
    key(enter)
sheets site:
    browser.focus_address()
    insert("sheets.google.com")
    key(enter)
new (docs | doc) site:
    browser.focus_address()
    insert("doc.new")
    key(enter)
new (slides | slide) site:
    browser.focus_address()
    insert("slides.new")
    key(enter)
new (sheets | sheet) site:
    browser.focus_address()
    insert("sheet.new")
    key(enter)
new (scripts | script) site:
    browser.focus_address()
    insert("script.new")
    key(enter)
amazon site:
    browser.focus_address()
    insert("smile.amazon.com")
    key(enter)
meet site:
    browser.focus_address()
    insert("meet.google.com")
    key(enter)
insert text box: key(alt-i t)
match next: user.browser_match_next()
match preev: user.browser_match_previous()
bookmark open: key(ctrl-;)
tab [new] bookmark: key(ctrl-')
frame next: key(ctrl-[)
# webdriver test: 'test_driver'()
# go search: ClickElementAction('q')
search <user.text>$:
    browser.focus_search()
    insert(text)
    sleep(15ms)
    key(enter)
history search <user.text>$:
    browser.focus_search()
    insert("history")
    key(tab)
    insert(text)
    key(enter)
history search:
    browser.focus_search()
    insert("history")
    key(tab)
moma search <user.text>$:
    browser.focus_search()
    insert("moma")
    key(tab)
    insert(text)
    key(enter)
moma search:
    browser.focus_search()
    insert("moma")
    key(tab)
# <text> (touch|click) [left]: ClickTextOrButtonAction('%(text)s', dynamic)
