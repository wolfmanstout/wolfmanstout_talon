import os

from talon import Module, app, settings

mod = Module()
setting_openai_api_key = mod.setting(
    "openai_api_key",
    type=str,
    default=None,
    desc="API key to use in calls to the OpenAI API. Keep this secret.",
)


def on_ready():
    api_key = settings.get("user.openai_api_key")
    if api_key:
        # For use in talon-ai-tools.
        if settings.get("user.model_endpoint") != "llm":
            os.environ["OPENAI_API_KEY"] = api_key


app.register("ready", on_ready)
