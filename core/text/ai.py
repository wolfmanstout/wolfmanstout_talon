import os

import openai
import openai.error
import tiktoken
from talon import Module, actions

openai.api_key = os.getenv("OPENAI_API_KEY")

mod = Module()


def num_tokens_from_string(string: str, model: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def get_chatgpt_model(prompt: str) -> str:
    """Returns the appropriate model based on the number of tokens in the prompt."""
    # Use 4000 instead of 4096 to account for tokens added internally by ChatGPT.
    return (
        "gpt-3.5-turbo-16k-0613"
        if num_tokens_from_string(prompt, "gpt-3.5-turbo-0613") > 4000
        else "gpt-3.5-turbo-0613"
    )


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
        prompt = (
            f'Selected text: """{selected}"""\n\n'
            f'Question: """{question}"""\n\n'
            f"Answer the above question with respect to the currently selected text."
        )
        try:
            completion = openai.ChatCompletion.create(
                model=get_chatgpt_model(prompt),
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
            )
        except openai.error.InvalidRequestError as e:
            actions.app.notify(
                "Invalid request, try a different prompt: " + e.error.message
            )
            return
        if not completion.choices:
            actions.app.notify("No response provided")
            return
        actions.app.notify(completion.choices[0].message.content)
