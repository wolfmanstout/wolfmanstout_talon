from talon import Context, Module, actions, app, speech_system, ui

mod = Module()
ctx_sleep = Context()
ctx_awake = Context()

modes = {
    "presentation": "a more strict form of sleep where only a more strict wake up command works",
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

    def dictation_mode():
        """Enables dictation mode."""
        actions.mode.disable("sleep")
        actions.mode.disable("command")
        actions.mode.enable("dictation")
        actions.mode.enable("user.dictation_command")
        actions.user.code_clear_language_mode()
        actions.user.gdb_disable()
        actions.user.dictation_format_reset()
        rect = ui.main_screen().rect
        regions = [
            actions.user.hud_create_screen_region(
                "mode",
                "FF0000",
                "",
                "Dictation",
                -1,
                rect.x,
                rect.y,
                rect.width,
                rect.height,
            )
        ]
        regions[0].text_colour = "FFFFFF"
        regions[0].vertical_centered = False
        actions.user.hud_publish_screen_regions("overlay", regions, True)
        actions.user.hud_publish_screen_regions("cursor", regions, True)

    def command_mode():
        """Enables command mode."""
        actions.mode.disable("sleep")
        actions.mode.disable("dictation")
        actions.mode.disable("user.dictation_command")
        actions.mode.enable("command")
        actions.user.hud_clear_screen_regions("overlay", "mode")
        actions.user.hud_clear_screen_regions("cursor", "mode")

    def context_sensitive_mode():
        """Enables context sensitivity."""
        actions.mode.disable("user.context_insensitive")

    def context_insensitive_mode():
        """Disables context sensitivity."""
        actions.mode.enable("user.context_insensitive")
