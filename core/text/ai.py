from talon import Module, actions
import os
import openai
import openai.error

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
            actions.app.notify("Invalid request, try a different prompt")
            return
        if not result.choices:
            actions.app.notify("No response provided")
            return
        actions.clip.set_text(result.choices[0].text)
        actions.edit.paste()

    def ai_edit_code_selection(instruction: str):
        """Applies the provided instruction to the currently-selected code."""
        actions.self.ai_edit_selection(instruction, model="code-davinci-edit-001")
