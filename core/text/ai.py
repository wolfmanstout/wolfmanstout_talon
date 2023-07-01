import os
from typing import Optional

import openai
import openai.error
from talon import Module, actions, imgui, registry

openai.api_key = os.getenv("OPENAI_API_KEY")

mod = Module()

response = ""


def get_chatgpt_model(prompt: str) -> str:
    """Returns the appropriate model based on the length of the prompt."""
    # Use characters instead of tokens to avoid dependency on tiktoken library
    # which doesn't work on Talon Mac. 4092 * 3 characters/token ~= 12000.
    return "gpt-3.5-turbo-16k-0613" if len(prompt) > 12000 else "gpt-3.5-turbo-0613"


def get_chatgpt_response(user_prompt: str, system_prompt: str = "") -> Optional[str]:
    global response
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})
    try:
        completion = openai.ChatCompletion.create(
            model=get_chatgpt_model(system_prompt + user_prompt),
            messages=messages,
        )
    except openai.error.InvalidRequestError as e:
        actions.app.notify(
            "Invalid request, try a different prompt: " + e.error.message
        )
        return
    if not completion.choices:
        actions.app.notify("No response provided")
        return
    response = completion.choices[0].message.content
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

    def ai_edit_selection(instruction: str, model: str = "text-davinci-edit-001"):
        """Applies the provided instruction to the currently-selected text."""
        selected = actions.edit.selected_text()
        if not selected:
            actions.app.notify("No text selected")
            return
        try:
            result = openai.Edit.create(
                model=model,
                input=selected,
                instruction=instruction,
                temperature=0.5,
            )
        except openai.error.InvalidRequestError:
            actions.app.notify(
                "Invalid request, try a different prompt: " + e.error.message
            )
            return
        if not result.choices:
            actions.app.notify("No response provided")
            return
        actions.clip.set_text(result.choices[0].text)
        actions.edit.paste()

    def ai_edit_code_selection(instruction: str):
        """Applies the provided instruction to the currently-selected code."""
        actions.self.ai_edit_selection(instruction, model="code-davinci-edit-001")

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
