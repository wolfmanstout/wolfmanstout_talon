from talon import Context, Module, actions, cron, imgui, settings

mod = Module()
ctx = Context()


EXCLUDE_MICROPHONES = {
    "Microsoft Teams Audio Device",
    "WebexMediaAudioDevice",
    "ZoomAudioDevice",
}

microphone_device_list = []
last_microphone = None
update_microphone_cron_job = None

preferred_microphones = mod.setting(
    "preferred_microphones",
    type=str,
    default="",
    desc="Comma separated list of preferred microphones.",
)


def update_microphone_list():
    global microphone_device_list
    # By convention, None and System Default are listed first
    # to match the Talon microphone menu.
    meta_devices = ["None", "System Default"]

    devices = [
        device
        for device in actions.sound.microphones()
        if device not in meta_devices and device not in EXCLUDE_MICROPHONES
    ]
    devices.sort()

    microphone_device_list = meta_devices + devices


def devices_changed(device_type):
    update_microphone_list()


mod.tag(
    "microphone_selection_open",
    "tag for commands that are available only when the list of microphones is visible",
)


@imgui.open()
def gui(gui: imgui.GUI):
    gui.text("Click or press a number key to select a microphone")
    gui.text("(or say “microphone pick #”)")
    gui.line()
    gui.text("Microphone list updates every 5 seconds")
    gui.spacer()
    active_microphone = actions.sound.active_microphone()
    for index, item in enumerate(microphone_device_list, 1):
        if gui.button(
            f"{f'[{index}] ' if index < 10 else ''}{item}{' — active' if item == active_microphone else ''}"
        ):
            actions.user.microphone_select(index)
    gui.spacer()
    if gui.button("[esc] microphone close"):
        actions.user.microphone_selection_hide()


@mod.action_class
class Actions:
    def microphone_selection_toggle():
        """Show GUI for choosing the Talon microphone"""
        global update_microphone_cron_job

        if gui.showing:
            actions.user.microphone_selection_hide()
            return
        update_microphone_list()
        gui.show()
        ctx.tags = ["user.microphone_selection_open"]
        update_microphone_cron_job = cron.interval("5s", update_microphone_list)

    def microphone_selection_hide():
        """Hide the microphone selection GUI"""
        global update_microphone_cron_job

        gui.hide()
        ctx.tags = []
        if update_microphone_cron_job:
            cron.cancel(update_microphone_cron_job)
        update_microphone_cron_job = None

    def microphone_select(index: int):
        """Selects a microphone"""
        if index >= 1 and index <= len(microphone_device_list):
            actions.sound.set_microphone(microphone_device_list[index - 1])
            actions.app.notify(
                f"Activating microphone: {microphone_device_list[index - 1]}"
            )
            actions.user.microphone_selection_hide()

    def microphone_toggle():
        """Toggles the microphone"""
        global last_microphone
        active_microphone = actions.sound.active_microphone()
        if active_microphone != "None":
            last_microphone = actions.sound.active_microphone()
            actions.user.command_mode()
            actions.sound.set_microphone("None")
        else:
            if not last_microphone:
                update_microphone_list()
                # Find the first preferred microphone in the device list
                for preferred_microphone in settings.get(
                    "user.preferred_microphones"
                ).split(","):
                    preferred_microphone = preferred_microphone.strip()
                    for device in microphone_device_list:
                        if preferred_microphone.lower() in device.lower():
                            actions.sound.set_microphone(device)
                            return
                actions.app.notify("Previously used microphone not known")
                return
            actions.sound.set_microphone(last_microphone)
            last_microphone = None
