# fmt: off

# define the spoken forms for symbols in command and dictation mode
punctuation_dict = {}

# for dragon, we add a couple of mappings that don't work for conformer
# i.e. dragon supports some actual symbols as the spoken form
dragon_punctuation_dict = {
    "`": "`",
    ",": ",",
}

# define the spoken forms for symbols that are intended for command mode only
symbol_key_dict = {}

# define spoken form for symbols for use in create_spoken_forms.py functionality
# we define a handful of symbol only. at present, this is restricted to one entry per symbol.
symbols_for_create_spoken_forms = {
    # for application names like "Movies & TV"
    "and": "&",
    # for emails
    "at": "@",
    "dot": ".",
    # for application names like "notepad++"
    "plus": "+",
}

# Dictation-only punctuation so text insertion keeps auto-spacing behavior.
punctuation_only_dict = {
    "open paren": "(",
    "open brand": "(",
    "open print": "(",
    "close paren": ")",
    "close brand": ")",
    "close print": ")",
}


class Symbol:
    character: str
    command_and_dictation_forms: list[str] = None
    command_forms: list[str] = None

    def __init__(
        self, character: str, command_and_dictation_forms=None, command_forms=None
    ):
        self.character = character

        if command_and_dictation_forms:
            self.command_and_dictation_forms = (
                [command_and_dictation_forms]
                if isinstance(command_and_dictation_forms, str)
                else command_and_dictation_forms
            )

        if command_forms:
            self.command_forms = (
                [command_forms] if isinstance(command_forms, str) else command_forms
            )

currency_symbols = [
    Symbol("$", ["dollar sign"], ["dollar"]),
    Symbol("£", None, ["pound"]),
    Symbol("€", ["euro sign"], ["euro"]),
]

symbols = [
    Symbol("`", None, ["back tick", "grave"]),
    Symbol(",", ["comma", "coma", "come a", "kama"]),
    Symbol(".", ["period", "buried"], ["dot", "point"]),
    Symbol(";", ["semicolon", "semi colon", "semi corn", "semi cohen"], ["semi"]),
    Symbol(":", ["colon", "corn", "cohen"]),
    Symbol(
        "?",
        [
            "question look",
            "question mark",
            "question more",
            "question work",
            "quest more",
            "questioning",
            "questioner",
        ],
    ),
    Symbol(
        "!",
        ["exclamation mark", "estimation mark", "exclamation work"],
        ["bang"],
    ),
    Symbol("*", None, ["star"]),
    Symbol("#", ["number sign"], ["hash"]),
    Symbol("%", ["percent sign"], ["percent"]),
    Symbol("@", ["at symbol", "at sign"]),
    Symbol("°", ["degree sign"], ["degree", "degrees"]),
    Symbol("&", ["ampersand"], ["amper"]),
    Symbol("-", ["hyphen", "high and", "minus sign"], ["minus", "dash"]),
    Symbol("–", ["en dash", "nut dash"]),
    Symbol("—", ["em dash", "mutton dash"]),
    Symbol("=", None, ["equals"]),
    Symbol("+", ["plus sign"], ["plus"]),
    Symbol("~", None, ["tilde"]),
    Symbol("_", ["under score"], ["down score"]),
    Symbol("(", None, ["L paren", "leap"]),
    Symbol(")", None, ["R paren", "reap"]),
    Symbol("[", None,["L square", "open bracket", "lobe"],),
    Symbol("]", None, ["R square", "close bracket", "robe"]),
    Symbol("/", ["slash"]),
    Symbol("\\", None, ["backslash"]),
    Symbol("{", None, ["open brace", "lake"],),
    Symbol("}", None, ["R brace", "close brace", "rake"]),
    Symbol("<", None, ["L angle", "open angle", "less than", "luke"]),
    Symbol(">", None, ["R angle", "close angle", "greater than", "ruke"]),
    Symbol("^", None, ["caret"]),
    Symbol("|", None, ["pipe"]),
    Symbol("'", None, ["single quote", "single quad"]),
    Symbol('"', None, ["dub quote", "dub quad", "double quote", "double quad", "quote", "quad"]),
]

# by convention, symbols should include currency symbols
symbols.extend(currency_symbols)

for symbol in symbols:
    if symbol.command_and_dictation_forms:
        for spoken_form in symbol.command_and_dictation_forms:
            punctuation_dict[spoken_form] = symbol.character
            symbol_key_dict[spoken_form] = symbol.character
            dragon_punctuation_dict[spoken_form] = symbol.character

    if symbol.command_forms:
        for spoken_form in symbol.command_forms:
            symbol_key_dict[spoken_form] = symbol.character

punctuation_dict.update(punctuation_only_dict)
dragon_punctuation_dict.update(punctuation_only_dict)
