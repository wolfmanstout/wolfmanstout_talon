mode: command
mode: user.dictation_command
app: vscode
-
# Copilot
[suggest] keep: user.vscode("editor.action.inlineSuggest.commit")
suggest clear: user.vscode("editor.action.inlineSuggest.hide")
suggest next: user.vscode("editor.action.inlineSuggest.showNext")
suggest last: user.vscode("editor.action.inlineSuggest.showPrevious")
suggest trigger: user.vscode("editor.action.inlineSuggest.trigger")
