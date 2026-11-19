app: emacs
title: /- Shell -/
-

tag(): terminal
shell up: user.emacs("comint-previous-input")
shell down: user.emacs("comint-next-input")
shell (last | preev | back): user.emacs("comint-history-isearch-backward-regexp")
output open: user.emacs("comint-show-output")
