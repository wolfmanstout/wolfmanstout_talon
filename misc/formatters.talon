#provide both anchored and unachored commands via 'over'
phrase <user.text>$: user.insert_formatted(text, "NOOP")
phrase <user.text> over: user.insert_formatted(text, "NOOP")
phrase <user.text> {user.post_dictation_keys}:
    user.insert_formatted(text, "NOOP")
    key(post_dictation_keys)
say <user.raw_prose>$: user.dictation_insert(raw_prose)
say <user.raw_prose> over: user.dictation_insert(raw_prose)
say <user.raw_prose> {user.post_dictation_keys}:
    user.dictation_insert(raw_prose)
    key(post_dictation_keys)
{user.prose_formatter} <user.prose>$: user.insert_formatted(prose, prose_formatter)
{user.prose_formatter} <user.prose> over: user.insert_formatted(prose, prose_formatter)
{user.prose_formatter} <user.prose> {user.post_dictation_keys}:
    user.insert_formatted(prose, prose_formatter)
    key(post_dictation_keys)
<user.format_text>+$: user.insert_many(format_text_list)
<user.format_text>+ over: user.insert_many(format_text_list)
<user.format_text>+ {user.post_dictation_keys}:
    user.insert_many(format_text_list)
    key(post_dictation_keys)
<user.formatters> that: user.formatters_reformat_selection(user.formatters)
word <user.word>: user.insert_formatted(user.word, "NOOP")
recent list: user.toggle_phrase_history()
recent close: user.phrase_history_hide()
recent repeat <number_small>: insert(user.get_recent_phrase(number_small))
recent copy <number_small>: clip.set_text(user.get_recent_phrase(number_small))
select that: user.select_last_phrase()
before that: user.before_last_phrase()
nope that | scratch that: user.clear_last_phrase()
nope that was <user.formatters>: user.formatters_reformat_last(formatters)
