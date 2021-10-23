double dash: "--"
triple quote: "'''"
(triple grave | triple back tick | gravy):
    insert("```")
(dot dot | dotdot): ".."
ellipses: "..."
(comma and | spamma): ", "
arrow: "->"
padded arrow: " -> "
dub arrow | fat arrow: "=>"
padded (dub arrow | fat arrow): " => "
padded equals twice: " == "
padded plus equals: " += "
padded minus equals: " -= "
new line: "\\n"
carriage return: "\\r"
line feed: "\\r\\n"
empty (string | quotes | dubquotes): '""'
empty escaped (string | quotes | dubquotes): '\\"\\"'
(empty parens | args): "()"
empty (squares | square brackets | list): "[]"
empty (braces | dict): "{}"
empty percent: "%%"
empty single quotes: "''"
empty (graves | back ticks): "``"
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
single quote that:
    text = edit.selected_text()
    user.paste("'{text}'")
(quote | dubquote) that:
    text = edit.selected_text()
    user.paste('"{text}"')
(grave | back tick) that:
    text = edit.selected_text()
    user.paste('`{text}`')
