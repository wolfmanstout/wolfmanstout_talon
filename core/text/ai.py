import os

import openai
import openai.error
from talon import Module, actions

openai.api_key = os.getenv("OPENAI_API_KEY")

mod = Module()


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
                model="gpt-3.5-turbo",
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
