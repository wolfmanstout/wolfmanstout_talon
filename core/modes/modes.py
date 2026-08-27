from talon import Context, Module, actions, app, speech_system, ui

mod = Module()
ctx_sleep = Context()
ctx_awake = Context()

modes = {
    "private": "a mode that disables recording",
    "context_insensitive": "a mode that disables context sensitivity",
    "dictation_command": "a mode that enables commands within dictation mode",
}

for key, value in modes.items():
    mod.mode(key, value)

ctx_sleep.matches = r"""
mode: sleep
"""

ctx_awake.matches = r"""
not mode: sleep
"""

DICTATION_CURSOR_READY_COLOR = "FF0000"
DICTATION_CURSOR_PROCESSING_COLOR = "FFBF00"


def _create_dictation_mode_region(color: str):
    rect = ui.main_screen().rect
    region = actions.user.hud_create_screen_region(
        "mode",
        color,
        "",
        "Dictation",
        -1,
        rect.x,
        rect.y,
        rect.width,
        rect.height,
    )
    region.text_colour = "FFFFFF"
    region.vertical_centered = False
    return region


def _publish_dictation_cursor(processing: bool):
    color = (
        DICTATION_CURSOR_PROCESSING_COLOR
        if processing
        else DICTATION_CURSOR_READY_COLOR
    )
    actions.user.hud_publish_screen_regions(
        "cursor", [_create_dictation_mode_region(color)], True
    )


@ctx_sleep.action_class("speech")
class ActionsSleepMode:
    def disable():
        actions.app.notify("Talon is already asleep")


@ctx_awake.action_class("speech")
class ActionsAwakeMode:
    def enable():
        actions.app.notify("Talon is already awake")


@mod.action_class
class Actions:
    def command_mode():
        """Enables command mode."""
        actions.mode.disable("sleep")
        actions.mode.disable("dictation")
        actions.mode.disable("user.dictation_command")
        actions.mode.enable("command")
        actions.user.hud_clear_screen_regions("overlay", "mode")
        actions.user.hud_clear_screen_regions("cursor", "mode")

    def dictation_mode():
        """Enables dictation mode."""
        actions.mode.disable("sleep")
        actions.mode.enable("dictation")
        actions.mode.enable("user.dictation_command")
        actions.mode.enable("command")
        actions.user.code_clear_language_mode()
        actions.user.gdb_disable()
        actions.user.dictation_format_reset()
        regions = [_create_dictation_mode_region(DICTATION_CURSOR_READY_COLOR)]
        actions.user.hud_publish_screen_regions("overlay", regions, True)
        actions.user.hud_publish_screen_regions("cursor", regions, True)

    def dictation_mode_set_processing(processing: bool):
        """Changes the dictation cursor indicator while an utterance is processed."""
        _publish_dictation_cursor(processing)

    def talon_mode():
        """For windows and Mac with Dragon, enables Talon commands and Dragon's command mode."""
        actions.speech.enable()

        engine = speech_system.engine.name
        # app.notify(engine)
        if "dragon" in engine:
            if app.platform == "mac":
                actions.user.dragon_engine_sleep()
            elif app.platform == "windows":
                actions.user.dragon_engine_wake()
                # note: this may not do anything for all versions of Dragon. Requires Pro.
                actions.user.dragon_engine_command_mode()

    def dragon_mode():
        """For windows and Mac with Dragon, disables Talon commands and exits Dragon's command mode"""
        engine = speech_system.engine.name
        # app.notify(engine)

        if "dragon" in engine:
            # app.notify("dragon mode")
            actions.speech.disable()
            if app.platform == "mac":
                actions.user.dragon_engine_wake()
            elif app.platform == "windows":
                actions.user.dragon_engine_wake()
                # note: this may not do anything for all versions of Dragon. Requires Pro.
                actions.user.dragon_engine_normal_mode()

    def context_sensitive_mode():
        """Enables context sensitivity."""
        actions.mode.disable("user.context_insensitive")

    def context_insensitive_mode():
        """Disables context sensitivity."""
        actions.mode.enable("user.context_insensitive")
