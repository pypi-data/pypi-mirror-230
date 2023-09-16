from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles.named_colors import NAMED_COLORS
from prompt_toolkit.completion import NestedCompleter


class RainbowLexer(Lexer):
    def lex_document(self, document):
        colors = list(sorted({"Teal": "#008080"}, key=NAMED_COLORS.get))

        def get_line(lineno):
            return [
                (colors[i % len(colors)], c)
                for i, c in enumerate(document.lines[lineno])
            ]

        return get_line


Completer = NestedCompleter.from_nested_dict(
    {
        "hello": None,
        "help": None,
        "exit": None,
        "close": None,
        ".": None,
        "edit": None,
        "phone": None,
        "save": None,
        "show": None,
        "all": None,
        "show all": None,
        "add": None,
        "add contact": None,
        "add phone": None,
        "add email": None,
        "add birthday": None,
        "change": None,
        "change phone": None,
        "change email": None,
        "change birthday": None,
        "delete contact": None,
        "delete phone": None,
        "delete email": None,
        "delete birthday": None,
        "find name": None,
        "get birthday": None,
        "add note": None,
        "find note": None,
        "find by tag": None,
        "show all notes": None,
        "change note": None,
        "change text": None,
        "change tag": None,
        "delete note": None,
        "add tag": None,
        "close": None,
    }
)
