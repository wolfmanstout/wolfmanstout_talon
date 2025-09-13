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
insert text box: key(alt-i t)
match next: user.browser_match_next()
match (last | preev): user.browser_match_previous()
frame next: key(ctrl-[)
{user.website} site:
    browser.focus_address()
    insert(website)
    key(enter)
search <user.prose>$:
    browser.focus_search()
    insert(prose)
    key(enter)
{user.browser_search_engine} search:
    browser.focus_address()
    insert(browser_search_engine)
    key(tab)
{user.browser_search_engine} search <user.prose>$:
    browser.focus_address()
    insert(browser_search_engine)
    key(tab)
    insert(prose)
    key(enter)
{user.search_engine} search <user.prose>$:
    user.browser_search_with_search_engine(search_engine, prose)
