from talon import Module, app, cron, speech_system

mod = Module()


@mod.scope
def speech_engine_scope():
    return {"speech_engine": repr(speech_system.engine)}


def update_speech_engine_scope():
    speech_engine_scope.update()


def on_ready():
    cron.interval("1s", update_speech_engine_scope)


app.register("ready", on_ready)
