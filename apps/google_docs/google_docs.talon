app: google_docs
-

settings():
    user.accessibility_dictation = false

tag(): user.command_search

file rename: user.rename_document()

# Comments
add comment | comment this: user.add_comment()
comment [{user.ocr_modifiers}] (seen | scene) <user.prose_range>$:
    user.google_docs_comment_on_text(ocr_modifiers or "", prose_range)
(last | preev) comment: user.previous_comment()
next comment: user.next_comment()
enter comment: user.enter_comment()
