from talon import Module, actions, app, speech_system, ui

mod = Module()

modes = {
    "admin": "enable extra administration commands terminal (docker, etc)",
    "debug": "a way to force debugger commands to be loaded",
    "gdb": "a way to force gdb commands to be loaded",
    "ida": "a way to force ida commands to be loaded",
    "presentation": "a more strict form of sleep where only a more strict wake up command works",
    "windbg": "a way to force windbg commands to be loaded",
    "private": "a mode that disables recording",
}

for key, value in modes.items():
    mod.mode(key, value)


@mod.action_class
class Actions:
    def talon_mode():
        """For windows and Mac with Dragon, enables Talon commands and Dragon's command mode."""
        actions.speech.enable()

        engine = speech_system.engine.name
        # app.notify(engine)
        if "dragon" in engine:
            if app.platform == "mac":
                actions.user.engine_sleep()
            elif app.platform == "windows":
                actions.user.engine_wake()
                # note: this may not do anything for all versions of Dragon. Requires Pro.
                actions.user.engine_mimic("switch to command mode")

    def dragon_mode():
        """For windows and Mac with Dragon, disables Talon commands and exits Dragon's command mode"""
        engine = speech_system.engine.name
        # app.notify(engine)

        if "dragon" in engine:
            # app.notify("dragon mode")
            actions.speech.disable()
            if app.platform == "mac":
                actions.user.engine_wake()
            elif app.platform == "windows":
                actions.user.engine_wake()
                # note: this may not do anything for all versions of Dragon. Requires Pro.
                actions.user.engine_mimic("start normal mode")

    def dictation_mode():
        """Enables dictation mode."""
        actions.mode.disable("sleep")
        actions.mode.disable("command")
        actions.mode.enable("dictation")
        actions.user.code_clear_language_mode()
        actions.mode.disable("user.gdb")
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
        actions.mode.enable("command")
        actions.user.hud_clear_screen_regions("overlay", "mode")
        actions.user.hud_clear_screen_regions("cursor", "mode")
