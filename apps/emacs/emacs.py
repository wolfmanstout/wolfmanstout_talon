from talon import Context, actions
ctx = Context()
ctx.matches = r"""
title: /Emacs editor/
"""

ctx.tags = ['user.find_and_replace', 'user.line_commands']

@ctx.action_class('edit')
class EditActions:
    def copy():
        actions.key('alt-w')
    def cut():
        actions.key('ctrl-w')
    # def delete():
    #     actions.key('backspace')
    # def delete_line():
    #     actions.edit.select_line()
    #     actions.edit.delete()
    #     #action(edit.delete_paragraph):
    #     #action(edit.delete_sentence):
    def delete_word():
        actions.key('ctrl-backspace')
    # def down():
    #     actions.key('down')
    #     #action(edit.extend_again):
    #     #action(edit.extend_column):
    # def extend_down():
    #     actions.key('shift-down')
    # def extend_file_end():
    #     actions.key('ctrl-space alt->')
    # def extend_file_start():
    #     actions.key('ctrl-space alt-<')
    # def extend_left():
    #     actions.key('shift-left')
    #     #action(edit.extend_line):
    # def extend_line_down():
    #     actions.key('shift-down')
    # def extend_line_end():
    #     actions.key('shift-end')
    # def extend_line_start():
    #     actions.key('shift-home')
    # def extend_line_up():
    #     actions.key('shift-up')
    # def extend_page_down():
    #     actions.key('shift-pagedown')
    # def extend_page_up():
    #     actions.key('shift-pageup')
    #     #action(edit.extend_paragraph_end):
    #     #action(edit.extend_paragraph_next()):
    #     #action(edit.extend_paragraph_previous()):
    #     #action(edit.extend_paragraph_start()):
    # def extend_right():
    #     actions.key('shift-right')
    #     #action(edit.extend_sentence_end):
    #     #action(edit.extend_sentence_next):
    #     #action(edit.extend_sentence_previous):
    #     #action(edit.extend_sentence_start):
    # def extend_up():
    #     actions.key('shift-up')
    # def extend_word_left():
    #     actions.key('ctrl-shift-left')
    # def extend_word_right():
    #     actions.key('ctrl-shift-right')
    # def file_end():
    #     actions.key('ctrl-end')
    # def file_start():
    #     actions.key('ctrl-home')
    def find(text: str=None):
        actions.key('ctrl-s')
        actions.actions.insert(text)
    def find_next():
        actions.key('ctrl-s')
        #action(edit.find_previous):
    # def indent_less():
    #     actions.key('home delete')
    # def indent_more():
    #     actions.key('home tab')
    #     #action(edit.jump_column(n: int)
    #     #action(edit.jump_line(n: int)
    # def left():
    #     actions.key('left')
    # def line_down():
    #     actions.key('down home')
    # def line_end():
    #     actions.key('end')
    # def line_insert_up():
    #     actions.key('home enter up')
    # def line_start():
    #     actions.key('home')
    # def line_up():
    #     actions.key('up home')
    #     #action(edit.move_again):
    # def page_down():
    #     actions.key('pagedown')
    # def page_up():
    #     actions.key('pageup')
    #     #action(edit.paragraph_end):
    #     #action(edit.paragraph_next):
    #     #action(edit.paragraph_previous):
    #     #action(edit.paragraph_start):
    def paste():
        actions.key('ctrl-y')
        #action(paste_match_style):
    # def print():
    #     actions.key('ctrl-p')
    def redo():
        actions.key('ctrl-shift-/')
    # def right():
        actions.key('right')
    def save():
        actions.key('ctrl-x ctrl-s')
    def save_all():
        actions.key('ctrl-x ctrl-shift-s')
    def select_all():
        actions.key('ctrl-x h')
    # def select_line(n: int=None):
    #     actions.key('end shift-home')
    #     #action(edit.select_lines(a: int, b: int)):
    def select_none():
        actions.key('ctrl-g')
        #action(edit.select_paragraph):
        #action(edit.select_sentence):
    # def select_word():
    #     actions.key('ctrl-left ctrl-shift-right')
    #     #action(edit.selected_text): -> str
    #     #action(edit.sentence_end):
    #     #action(edit.sentence_next):
    #     #action(edit.sentence_previous):
    #     #action(edit.sentence_start):
    def undo():
        actions.key('ctrl-/')
    # def up():
    #     actions.key('up')
    # def word_left():
    #     actions.key('ctrl-left')
    # def word_right():
    #     actions.key('ctrl-right')
    # def zoom_in():
    #     actions.key('ctrl-+')
    # def zoom_out():
    #     actions.key('ctrl--')
    # def zoom_reset():
    #     actions.key('ctrl-0')

    def jump_line(n: int):
        # actions.key("alt-g alt-g")
        # actions.insert(str(n))
        # actions.key("enter")
        actions.key("ctrl-u")
        actions.insert(str(n))
        actions.key("ctrl-c c g")

@ctx.action_class("code")
class CodeActions:
    # talon code actions
    def toggle_comment():
        actions.key("alt-;")

@ctx.action_class("win")
class WinActions:
    def filename():
        title = actions.win.title()

        result = title.split(" — ")[0]

        if "." in result:
            return result

        return ""