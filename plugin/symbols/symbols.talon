new line: "\\n"
carriage return: "\\r"
line feed: "\\r\\n"
angle that:
    text = edit.selected_text()
    user.paste("<{text}>")
(square | bracket) that:
    text = edit.selected_text()
    user.paste("[{text}]")
brace that:
    text = edit.selected_text()
    user.paste("{{{text}}}")
(parens | args) that:
    text = edit.selected_text()
    user.paste("({text})")
percent that:
    text = edit.selected_text()
    user.paste("%{text}%")
single (quote | quad) that:
    text = edit.selected_text()
    user.paste("'{text}'")
((quote | quad) | dub (quote | quad)) that:
    text = edit.selected_text()
    user.paste('"{text}"')
(grave | back tick) that:
    text = edit.selected_text()
    user.paste("`{text}`")
