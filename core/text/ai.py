import os
from typing import Optional

import openai
import openai.error
from talon import Module, actions, registry

openai.api_key = os.getenv("OPENAI_API_KEY")

mod = Module()


def num_tokens_from_string(string: str, model: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def get_chatgpt_model(prompt: str) -> str:
    """Returns the appropriate model based on the length of the prompt."""
    # Use characters instead of tokens to avoid dependency on tiktoken library
    # which doesn't work on Talon Mac. 4092 * 3 characters/token ~= 12000.
    return "gpt-3.5-turbo-16k-0613" if len(prompt) > 12000 else "gpt-3.5-turbo-0613"


def get_chatgpt_response(user_prompt: str, system_prompt: str = "") -> Optional[str]:
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
    return completion.choices[0].message.content


@mod.action_class
class Actions:
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
        actions.app.notify(response)

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
        actions.app.notify(response)
