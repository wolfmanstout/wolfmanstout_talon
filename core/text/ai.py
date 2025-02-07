import os
from typing import List, Optional, Union

try:
    import openai
    from openai import OpenAI
except ImportError as e:
    print(f"Unable to import openai: {e}")
    openai = None
from talon import Module, actions, app, imgui, registry, settings

mod = Module()
setting_openai_api_key = mod.setting(
    "openai_api_key",
    type=str,
    default=None,
    desc="API key to use in calls to the OpenAI API. Keep this secret.",
)


def on_ready():
    global client
    api_key = settings.get("user.openai_api_key")
    if api_key:
        if openai:
            client = OpenAI(api_key=api_key)
        # For use in talon-ai-tools.
        if settings.get("user.model_endpoint") != "llm":
            os.environ["OPENAI_API_KEY"] = api_key
    else:
        print("Set the openai_api_key setting to use the AI chat feature.")
        client = None


app.register("ready", on_ready)

response = ""


def get_chatgpt_model(prompt: str, use_smart: bool) -> str:
    """Returns the appropriate model based on the length of the prompt and use_smart
    parameter."""
    if use_smart:
        return "gpt-4-1106-preview"
    else:
        return "gpt-3.5-turbo-1106"


def get_chatgpt_response(
    user_prompt: Union[str, List[str]],
    system_prompt: str = "",
    use_smart_model: bool = True,
) -> Optional[str]:
    global response
    assert client is not None
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if isinstance(user_prompt, str):
        messages.append({"role": "user", "content": user_prompt})
    elif isinstance(user_prompt, list):
        for prompt in user_prompt:
            messages.append({"role": "user", "content": prompt})
    else:
        raise ValueError(f"Invalid user_prompt type: {type(user_prompt)}")
    try:
        total_prompt = system_prompt + (
            user_prompt if isinstance(user_prompt, str) else "\n".join(user_prompt)
        )
        completion = client.chat.completions.create(
            model=get_chatgpt_model(total_prompt, use_smart_model),
            messages=messages,
        )
    except openai.APIStatusError as e:
        actions.app.notify("Invalid request, try a different prompt: " + e.message)
        return
    if not completion.choices:
        actions.app.notify("No response provided")
        return
    response = completion.choices[0].message.content or ""
    return response


@imgui.open(y=0)
def gui(gui: imgui.GUI):
    global response
    gui.text("AI Chat")
    gui.line()
    for line in response.split("\n"):
        while len(line) > 80:
            pos = line.rfind(" ", 0, 80)
            if pos != -1:
                gui.text(line[:pos])
                line = line[pos + 1 :]
            else:
                gui.text(line[:80])
                line = line[80:]
        gui.text(line)
    gui.spacer()
    if gui.button("AI Chat close"):
        actions.user.ai_chat_disable()


@mod.action_class
class Actions:
    def ai_chat_enable():
        """Enable the AI chat window."""
        gui.show()

    def ai_chat_disable():
        """Disable the AI chat window."""
        gui.hide()

    def ai_edit_selection(
        instruction: str,
        system_prompt: str = "Apply the change requested by the user to the text.",
    ):
        """Applies the provided instruction to the currently-selected text."""
        selected = actions.edit.selected_text()
        if not selected:
            actions.app.notify("No text selected")
            return
        response = get_chatgpt_response(
            user_prompt=[selected, instruction],
            system_prompt=system_prompt,
        )
        if not response:
            return
        actions.clip.set_text(response)
        actions.edit.paste()

    def ai_edit_code_selection(instruction: str):
        """Applies the provided instruction to the currently-selected code."""
        actions.self.ai_edit_selection(
            instruction,
            system_prompt="Apply the change requested by the user to the code.",
        )

    def ai_query_selection(question: str):
        """Queries the currently-selected text with the provided question."""
        selected = actions.edit.selected_text()
        if not selected:
            actions.app.notify("No text selected")
            return
        system_prompt = (
            "Answer questions about the provided text. The text will be delimited with"
            " triple quotes."
        )
        user_prompt = f'Question: {question}\n\nText: """{selected}"""'
        response = get_chatgpt_response(user_prompt, system_prompt)
        if not response:
            return
        actions.self.ai_chat_enable()

    def ai_query_active_commands(question: str):
        """Queries the list of active commands."""
        system_prompt = (
            "Describe tersely how to perform the user request using currently active"
            " Talon commands. Talon is a voice control system for desktop computers."
            " All active commands will be listed. They will be grouped into contexts"
            " and listed under each context."
        )
        user_prompt = f'Request: {question}\n\nActive Commands: """\n'
        for context in registry.active_contexts():
            if not context.commands:
                continue
            user_prompt += f"{context.path}\n"
            for _, command in context.commands.items():
                user_prompt += f"- {command.rule.rule}\n"
            user_prompt += "\n"
        user_prompt += '"""'
        response = get_chatgpt_response(user_prompt, system_prompt)
        if not response:
            return
        actions.self.ai_chat_enable()
