mode: command
and not mode: dictation
tag: browser
-

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
