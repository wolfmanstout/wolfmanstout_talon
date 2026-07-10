from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass
from typing import Literal

from talon import Module, actions, settings


@dataclass
class NavigationStep:
    modifier: Literal[
        "wordLeft",
        "wordRight",
        "word",
        "left",
        "right",
        "lineUp",
        "lineDown",
        "lineStart",
        "lineStartAbsolute",
        "lineEnd",
        "lineMiddle",
        "fileStart",
        "fileEnd",
        "pageUp",
        "pageDown",
    ]
    count: int


mod = Module()


@mod.capture(rule="line mid")
def edit_navigation_line_middle(_m) -> NavigationStep:
    """Navigation-only because extending an existing selection to a line's middle is unreliable."""
    return NavigationStep("lineMiddle", 1)


@mod.capture(
    rule="([<number_small>] {user.edit_modifier_repeatable}) | "
    "{user.edit_modifier_boundary} | <user.edit_navigation_line_middle>"
)
def navigation_step(m) -> NavigationStep:
    with suppress(AttributeError):
        return m.edit_navigation_line_middle

    with suppress(AttributeError):
        return NavigationStep(m.edit_modifier_boundary, 1)

    count = 1
    modifier = m.edit_modifier_repeatable

    with suppress(AttributeError):
        count = m.number_small

    return NavigationStep(
        modifier=modifier,
        count=count,
    )


@mod.action_class
class Actions:
    def perform_navigation_steps(steps: list[NavigationStep]):
        """Navigate by a series of steps"""
        for step in steps:
            match step.modifier:
                case "wordLeft":
                    repeat_action(actions.edit.word_left, step.count, True)
                case "wordRight":
                    repeat_action(actions.edit.word_right, step.count, True)
                case "word":
                    repeat_action(actions.edit.word_right, step.count, True)
                case "left":
                    repeat_action(actions.edit.left, step.count)
                case "right":
                    repeat_action(actions.edit.right, step.count)
                case "lineUp":
                    repeat_action(actions.edit.up, step.count)
                case "lineDown":
                    repeat_action(actions.edit.down, step.count)
                case "lineStart":
                    repeat_action(actions.edit.line_start, step.count)
                case "lineStartAbsolute":
                    repeat_action(actions.edit.line_start, 2)
                case "lineEnd":
                    repeat_action(actions.edit.line_end, step.count)
                case "lineMiddle":
                    repeat_action(actions.user.line_middle, step.count)
                case "fileStart":
                    repeat_action(actions.edit.file_start, step.count)
                case "fileEnd":
                    repeat_action(actions.edit.file_end, step.count)
                case "pageUp":
                    repeat_action(actions.edit.page_up, step.count)
                case "pageDown":
                    repeat_action(actions.edit.page_down, step.count)


def repeat_action(action: Callable, count: int, delay: bool = False):
    delay_string = None

    if delay:
        delay_string = f"{settings.get('user.edit_command_word_selection_delay')}ms"

    for _ in range(count):
        action()

        if delay_string:
            actions.sleep(delay_string)
