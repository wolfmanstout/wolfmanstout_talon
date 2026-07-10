from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass

from talon import Module, actions

mod = Module()

# Edit modifiers are split by grammar and behavior:
# - edit_modifier targets whole structural units and is edit-only.
# - edit_modifier_boundary names positions shared by edit and navigation commands.
# - edit_modifier_repeatable names incremental movements and accepts a count.
mod.list(
    "edit_modifier",
    desc="Non-repeatable structural targets for edit commands, such as line, paragraph, or document.",
)
mod.list(
    "edit_modifier_boundary",
    desc="Non-repeatable caret positions. Navigation commands move to them; edit commands extend the selection to them.",
)
mod.list(
    "edit_modifier_repeatable",
    desc="Repeatable caret movements shared by edit and navigation commands. Say a number before the modifier to repeat it.",
)


@dataclass
class EditModifier:
    type: str
    count: int = 1


@dataclass
class EditModifierCallback:
    modifier: str
    callback: Callable


@mod.capture(
    rule="({user.edit_modifier} | {user.edit_modifier_boundary}) | "
    "([<number_small>] {user.edit_modifier_repeatable})"
)
def edit_modifier(m) -> EditModifier:
    count = 1
    with suppress(AttributeError):
        count = m.number_small

    with suppress(AttributeError):
        type = m.edit_modifier

    with suppress(AttributeError):
        type = m.edit_modifier_boundary

    with suppress(AttributeError):
        type = m.edit_modifier_repeatable

    return EditModifier(type, count=count)


modifiers = [
    EditModifierCallback("document", actions.edit.select_all),
    EditModifierCallback("paragraph", actions.edit.select_paragraph),
    EditModifierCallback("word", actions.edit.extend_word_right),
    EditModifierCallback("wordLeft", actions.edit.extend_word_left),
    EditModifierCallback("wordRight", actions.edit.extend_word_right),
    EditModifierCallback("left", actions.edit.extend_left),
    EditModifierCallback("right", actions.edit.extend_right),
    EditModifierCallback("lineUp", actions.edit.extend_line_up),
    EditModifierCallback("lineDown", actions.edit.extend_line_down),
    EditModifierCallback("line", actions.edit.select_line),
    EditModifierCallback("lineEnd", actions.edit.extend_line_end),
    EditModifierCallback("lineStart", actions.edit.extend_line_start),
    EditModifierCallback("lineStartAbsolute", actions.edit.extend_line_start),
    EditModifierCallback("fileStart", actions.edit.extend_file_start),
    EditModifierCallback("fileEnd", actions.edit.extend_file_end),
    EditModifierCallback("pageUp", actions.edit.extend_page_up),
    EditModifierCallback("pageDown", actions.edit.extend_page_down),
    EditModifierCallback("selection", actions.skip),
]

modifier_dictionary: dict[str, EditModifierCallback] = {
    item.modifier: item for item in modifiers
}


@mod.action_class
class Actions:
    def run_edit_modifier_callback(modifier: EditModifier):
        """
        Run a callback that selects or prepares text ready to apply an edit action.
        Intended for internal use and overwriting
        """
        count = modifier.count
        modifier_callback = actions.user.get_edit_modifier_callback(modifier)
        for _ in range(1, count + 1):
            modifier_callback()

    def get_edit_modifier_callback(modifier: EditModifier):
        """Convert an edit modifier created from a string into its associated EditModifierCallback"""
        modifier_type = modifier.type
        if modifier_type not in modifier_dictionary:
            raise ValueError(f"Unknown edit modifier: {modifier_type}")
        return modifier_dictionary[modifier_type].callback
