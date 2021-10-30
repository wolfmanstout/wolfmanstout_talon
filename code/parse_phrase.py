# From https://github.com/AndreasArvidsson/andreas-talon/blob/3631f25d426a9fb7526c240cb0c9961ea90072c2/andreas/misc/rephrase.py
from typing import Optional, Union
from talon import Context, Module, actions, speech_system
from talon.grammar import Phrase

mod = Module()

phrase_stack = []


def on_pre_phrase(d):
    phrase_stack.append(d)


def on_post_phrase(d):
    phrase_stack.pop()


speech_system.register("pre:phrase", on_pre_phrase)
speech_system.register("post:phrase", on_post_phrase)


@mod.action_class
class Actions:
    def parse_phrase(phrase: Union[Phrase, str]):
        """Rerun phrase"""
        if phrase == "":
            return
        current_phrase = phrase_stack[-1]
        ts = current_phrase["_ts"]
        start = phrase.words[0].start - ts
        end = phrase.words[-1].end - ts
        samples = current_phrase["samples"]
        pstart = int(start * 16_000)
        pend = int(end * 16_000)
        samples = samples[pstart:pend]

        speech_system._on_audio_frame(samples)

# Dragon doesn't support timestamps, so we fall back to mimic()
ctx = Context()
ctx.matches = r"""
speech.engine: dragon
"""

@ctx.action_class
class DragonActions:
    def parse_phrase(phrase: Union[Phrase, str]):
        if phrase == "":
            return
        command = " ".join(actions.dictate.replace_words(actions.dictate.parse_words(phrase)))
        actions.mimic(command)
