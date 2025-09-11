tag: browser
-
tag(): user.rango_explicit_clicking

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
{user.website} site:
    browser.focus_address()
    insert(website)
    key(enter)
insert text box: key(alt-i t)
match next: user.browser_match_next()
match (last | preev): user.browser_match_previous()
frame next: key(ctrl-[)
# webdriver test: 'test_driver'()
# go search: ClickElementAction('q')
search <user.prose>$:
    browser.focus_search()
    insert(prose)
    sleep(15ms)
    key(enter)
history search <user.prose>$:
    browser.focus_search()
    insert("history")
    key(tab)
    insert(prose)
    key(enter)
history search:
    browser.focus_search()
    insert("history")
    key(tab)
moma search <user.prose>$:
    browser.focus_search()
    insert("moma")
    key(tab)
    insert(prose)
    key(enter)
moma search:
    browser.focus_search()
    insert("moma")
    key(tab)
# <text> (touch|click) [left]: ClickTextOrButtonAction('%(text)s', dynamic)
