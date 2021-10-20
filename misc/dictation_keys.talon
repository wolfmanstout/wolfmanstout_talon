mode: command
mode: dictation
-
<user.letter>: key(letter)
(ship | uppercase | upper) <user.letters> [(lowercase | sunk)]:
    user.insert_formatted(letters, "ALL_CAPS")
<user.symbol_key>: key(symbol_key)
padded <user.symbol_key>: key(space symbol_key space)
<user.function_key>: key(function_key)
<user.special_key>: key(special_key)
press <user.modifiers>: key(modifiers)
