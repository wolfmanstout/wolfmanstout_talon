from copy import deepcopy

from talon import Context, Module

mod = Module()
mod.list("letter", desc="The spoken phonetic alphabet")
mod.list("symbol_key", desc="All symbols from the keyboard")
mod.list("arrow_key", desc="All arrow keys")
mod.list("number_key", desc="All number keys")
mod.list("modifier_key", desc="All modifier keys")
mod.list("function_key", desc="All function keys")
mod.list("special_key", desc="All special keys")
mod.list("keypad_key", desc="All keypad keys")
mod.list("punctuation", desc="words for inserting punctuation into text")


@mod.capture(rule="{self.modifier_key}+")
def modifiers(m) -> str:
    "One or more modifier keys"
    return "-".join(m.modifier_key_list)


@mod.capture(rule="{self.arrow_key}")
def arrow_key(m) -> str:
    "One directional arrow key"
    return m.arrow_key


@mod.capture(rule="<self.arrow_key>+")
def arrow_keys(m) -> str:
    "One or more arrow keys separated by a space"
    return str(m)


@mod.capture(rule="{self.number_key}")
def number_key(m) -> str:
    "One number key"
    return m.number_key


@mod.capture(rule="{self.keypad_key}")
def keypad_key(m) -> str:
    "One keypad key"
    return m.keypad_key


@mod.capture(rule="{self.letter}")
def letter(m) -> str:
    "One letter key"
    return m.letter


@mod.capture(rule="{self.special_key}")
def special_key(m) -> str:
    "One special key"
    return m.special_key


@mod.capture(rule="{self.symbol_key}")
def symbol_key(m) -> str:
    "One symbol key"
    return m.symbol_key


@mod.capture(rule="{self.function_key}")
def function_key(m) -> str:
    "One function key"
    return m.function_key


@mod.capture(rule="( <self.letter> | <self.number_key> | <self.symbol_key> )")
def any_alphanumeric_key(m) -> str:
    "any alphanumeric key"
    return str(m)


@mod.capture(
    rule="( <self.letter> | <self.number_key> | <self.symbol_key> "
    "| <self.arrow_key> | <self.function_key> | <self.special_key> | <self.keypad_key>)"
)
def unmodified_key(m) -> str:
    "A single key with no modifiers"
    return str(m)


@mod.capture(rule="{self.modifier_key}* <self.unmodified_key>")
def key(m) -> str:
    "A single key with optional modifiers"
    try:
        mods = m.modifier_key_list
    except AttributeError:
        mods = []
    return "-".join(mods + [m.unmodified_key])


@mod.capture(rule="<self.key>+")
def keys(m) -> str:
    "A sequence of one or more keys with optional modifiers"
    return " ".join(m.key_list)


@mod.capture(rule="{self.letter}+")
def letters(m) -> str:
    "Multiple letter keys"
    return "".join(m.letter_list)


ctx = Context()

# `punctuation_words` is for words you want available BOTH in dictation and as key names in command mode.
# `symbol_key_words` is for key names that should be available in command mode, but NOT during dictation.
punctuation_words = {
    "comma": ",",
    # Workaround for issue with conformer b-series; see #946
    "coma": ",",
    "come a": ",",
    "kama": ",",
    "period": ".",
    "buried": ".",
    "semicolon": ";",
    "semi colon": ";",
    "colon": ":",
    "corn": ":",
    "slash": "/",
    "question mark": "?",
    "questioner": "?",
    "exclamation mark": "!",
    "estimation mark": "!",
    "exclamation work": "!",
    "number sign": "#",
    "percent sign": "%",
    "at sign": "@",
    "ampersand": "&",
    "hyphen": "-",
    "high and": "-",
    "under score": "_",
    # Currencies
    "dollar sign": "$",
    "plus sign": "+",
}
symbol_key_words = {
    "dot": ".",
    "point": ".",
    "single quote": "'",
    "single quad": "'",
    "L square": "[",
    "open bracket": "[",
    "lobe": "[",
    "R square": "]",
    "close bracket": "]",
    "robe": "]",
    "backslash": "\\",
    "minus": "-",
    "dash": "-",
    "equals": "=",
    "plus": "+",
    "grave": "`",
    "tilde": "~",
    "bang": "!",
    "down score": "_",
    "L paren": "(",
    "leap": "(",
    "R paren": ")",
    "reap": ")",
    "open brace": "{",
    "lake": "{",
    "R brace": "}",
    "close brace": "}",
    "rake": "}",
    "L angle": "<",
    "open angle": "<",
    "less than": "<",
    "luke": "<",
    "R angle": ">",
    "close angle": ">",
    "greater than": ">",
    "ruke": ">",
    "star": "*",
    "hash": "#",
    "percent": "%",
    "caret": "^",
    "amper": "&",
    "pipe": "|",
    "dub quote": '"',
    "dub quad": '"',
    "double quote": '"',
    "double quad": '"',
    "quote": '"',
    "quad": '"',
    "back tick": "`",
    # Currencies
    "dollar": "$",
    "pound": "£",
}

# make punctuation words also included in {user.symbol_keys}
symbol_key_words.update(punctuation_words)
# Only allow the following words in dictation so that auto-spacing is always applied.
punctuation_words.update(
    {
        "open paren": "(",
        "open brand": "(",
        "open print": "(",
        "close paren": ")",
        "close brand": ")",
        "close print": ")",
    }
)
ctx.lists["self.punctuation"] = punctuation_words
ctx.lists["self.symbol_key"] = symbol_key_words


@mod.action_class
class Actions:
    def get_punctuation_words() -> dict[str, str]:
        """Get a copy of the punctuation words dict."""
        return deepcopy(punctuation_words)
