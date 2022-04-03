import logging
import re
import time
from typing import Dict, Sequence, Union

from talon import Context, Module, actions
from talon.grammar import Phrase
from .user_settings import append_to_csv, get_list_from_csv

mod = Module()
ctx = Context()

mod.list("vocabulary", desc="additional vocabulary words")
mod.list("vocabulary_keys", desc="spoken forms of additional vocabulary words, used internally for testing")
vocabulary_recording_dir = mod.setting(
    "vocabulary_recording_dir",
    type=str,
    default=None,
    desc="If specified, log vocabulary recordings to this directory.",
)

# Default words that will need to be capitalized.
# DON'T EDIT THIS. Edit settings/words_to_replace.csv instead.
# These defaults and those later in this file are ONLY used when
# auto-creating the corresponding settings/*.csv files. Those csv files
# determine the contents of user.vocabulary and dictate.word_map. Once they
# exist, the contents of the lists/dictionaries below are irrelevant.
_capitalize_defaults = [
    # NB. the lexicon now capitalizes January/February by default, but not the
    # others below. Not sure why.
    "January",
    "February",
    # March omitted because it's a regular word too
    "April",
    # May omitted because it's a regular word too
    "June",
    "July",
    "August", # technically also an adjective but the month is far more common
    "September",
    "October",
    "November",
    "December",
]

# Default words that need to be remapped.
_word_map_defaults = {
    # E.g:
    # "cash": "cache",
    # This is the opposite ordering to words_to_replace.csv (the latter has the target word first)
}
_word_map_defaults.update({word.lower(): word for word in _capitalize_defaults})


# phrases_to_replace is a spoken form -> written form map, used by our
# implementation of `dictate.replace_words` (at bottom of file) to rewrite words
# and phrases Talon recognized. This does not change the priority with which
# Talon recognizes particular phrases over others.
phrases_to_replace = get_list_from_csv(
    "words_to_replace.csv",
    headers=("Replacement", "Original"),
    default=_word_map_defaults
)

# "dictate.word_map" is used by Talon's built-in default implementation of
# `dictate.replace_words`, but supports only single-word replacements.
# Multi-word phrases are ignored.
ctx.settings["dictate.word_map"] = phrases_to_replace


# Default words that should be added to Talon's vocabulary.
# Don't edit this. Edit 'additional_vocabulary.csv' instead
_simple_vocab_default = ["nmap", "admin", "Cisco", "Citrix", "VPN", "DNS", "Minecraft"]

# Defaults for different pronounciations of words that need to be added to
# Talon's vocabulary.
_default_vocabulary = {
    "N map": "nmap",
    "under documented": "under-documented",
}
_default_vocabulary.update({word: word for word in _simple_vocab_default})

# "user.vocabulary" is used to explicitly add words/phrases that Talon doesn't
# recognize. Words in user.vocabulary (or other lists and captures) are
# "command-like" and their recognition is prioritized over ordinary words.
ctx.lists["user.vocabulary"] = get_list_from_csv(
    "additional_words.csv",
    headers=("Word(s)", "Spoken Form (If Different)"),
    default=_default_vocabulary,
)

class PhraseReplacer:
    """Utility for replacing phrases by other phrases inside text or word lists.

    Replacing longer phrases has priority.

    Args:
      - phrase_dict: dictionary mapping recognized/spoken forms to written forms
    """

    def __init__(self, phrase_dict: Dict[str, str]):
        # Index phrases by first word, then number of subsequent words n_next
        phrase_index = dict()
        for spoken_form, written_form in phrase_dict.items():
            words = spoken_form.split()
            if not words:
                logging.warning("Found empty spoken form for written form"
                                f"{written_form}, ignored")
                continue
            first_word, n_next = words[0], len(words) - 1
            phrase_index.setdefault(first_word, {}) \
                        .setdefault(n_next, {})[tuple(words[1:])] = written_form

        # Sort n_next index so longer phrases have priority
        self.phrase_index = {
            first_word: list(sorted(same_first_word.items(), key=lambda x: -x[0]))
            for first_word, same_first_word in phrase_index.items()
        }

    def replace(self, input_words: Sequence[str]) -> Sequence[str]:
        input_words = tuple(input_words) # tuple to ensure hashability of slices
        output_words = []
        first_word_i = 0
        while first_word_i < len(input_words):
            first_word = input_words[first_word_i]
            next_word_i = first_word_i + 1
            # Could this word be the first of a phrase we should replace?
            for n_next, phrases_n_next in self.phrase_index.get(first_word, []):
                # Yes. Perhaps a phrase with n_next subsequent words?
                continuation = input_words[next_word_i : next_word_i + n_next]
                if continuation in phrases_n_next:
                    # Found a match!
                    output_words.append(phrases_n_next[continuation])
                    first_word_i += 1 + n_next
                    break
            else:
                # No match, just add the word to the result
                output_words.append(first_word)
                first_word_i += 1
        return output_words

    # Wrapper used for testing.
    def replace_string(self, text: str) -> str:
        return ' '.join(self.replace(text.split()))

# Unit tests for PhraseReplacer
rep = PhraseReplacer({
    'this': 'foo',
    'that': 'bar',
    'this is': 'stopping early',
    'this is a test': 'it worked!',
})
assert rep.replace_string('gnork') == 'gnork'
assert rep.replace_string('this') == 'foo'
assert rep.replace_string('this that this') == 'foo bar foo'
assert rep.replace_string('this is a test') == 'it worked!'
assert rep.replace_string('well this is a test really') == 'well it worked! really'
assert rep.replace_string('try this is too') == 'try stopping early too'
assert rep.replace_string('this is a tricky one') == 'stopping early a tricky one'

phrase_replacer = PhraseReplacer(phrases_to_replace)

mod.mode("vocabulary_test", "a mode used internally to test vocabulary words")
test_result: str = ""

@mod.capture(rule="({user.vocabulary_keys} | <phrase>)")
def test_phrase(m) -> str:
    """User defined spoken forms or phrase."""
    try:
        return m.vocabulary_keys
    except AttributeError:
        return " ".join(actions.dictate.parse_words(m.phrase))

def _create_vocabulary_entries(spoken_form, written_form, type):
    entries = {spoken_form: written_form}
    if type == "name":
        entries[f"{spoken_form}'s"] = f"{written_form}'s"
    elif type == "noun":
        entries[f"{spoken_form}s"] = f"{written_form}s"
    return entries

@ctx.action_class('dictate')
class OverwrittenActions:
    def replace_words(words: Sequence[str]) -> Sequence[str]:
        try:
            return phrase_replacer.replace(words)
        except:
            # fall back to default implementation for error-robustness
            logging.error("phrase replacer failed!")
            return actions.next(words)

@mod.action_class
class Actions:
    def add_selection_to_vocabulary(phrase: Union[Phrase, str], type: str=""):
        """Permanently adds the currently selected text to the vocabulary."""
        written_form = actions.edit.selected_text().strip()
        acronym = re.fullmatch(r"[A-Z]+", written_form)
        default_spoken_form = " ".join(written_form) if acronym else written_form
        vocabulary = dict(ctx.lists["user.vocabulary"])
        if default_spoken_form in vocabulary:
            logging.info("Default spoken form is already in the vocabulary")
            add_default_spoken_form = False
        else:
            add_default_spoken_form = True

        if phrase == "":
            if add_default_spoken_form:
                append_to_csv("additional_words.csv",
                              _create_vocabulary_entries(default_spoken_form, written_form, type))
            return

        # Test out the new vocabulary. Don't modify the file until the end or
        # else we will invalidate the declarations in this file.
        vocabulary[default_spoken_form] = written_form
        ctx.lists["user.vocabulary_keys"] = vocabulary.keys()
        actions.mode.save()
        try:
            actions.mode.disable("command")
            actions.mode.disable("dictation")
            actions.mode.enable("user.vocabulary_test")
            if vocabulary_recording_dir.get():
                recording_path = "{}/{}_{}.flac".format(
                    vocabulary_recording_dir.get(),
                    re.sub(r"[^A-Za-z]", "_", written_form),
                    round(time.time()))
            else:
                recording_path = ""
            actions.user.parse_phrase(phrase, recording_path)
        finally:
            actions.mode.restore()
            global test_result
            spoken_form = test_result
            test_result = ""

        if spoken_form == "":
            logging.error("vocabulary test failed")
            return
        if spoken_form == default_spoken_form:
            if add_default_spoken_form:
                append_to_csv("additional_words.csv",
                              _create_vocabulary_entries(default_spoken_form, written_form, type))
        else:
            if spoken_form in vocabulary:
                logging.info("Spoken form is already in the vocabulary")
            else:
                append_to_csv("additional_words.csv",
                              _create_vocabulary_entries(spoken_form, written_form, type))

    def add_selection_to_words_to_replace(phrase: Phrase):
        """Permanently adds the currently selected text to words to replace."""
        written_form = actions.edit.selected_text().strip()
        spoken_form = " ".join(actions.dictate.parse_words(phrase))
        append_to_csv("words_to_replace.csv", {spoken_form: written_form})

    def test_vocabulary_phrase(result: str):
        """Tests the recognition of the phrase."""
        global test_result
        test_result = result
