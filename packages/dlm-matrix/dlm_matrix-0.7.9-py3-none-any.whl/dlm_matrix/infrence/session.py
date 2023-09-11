from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.html import HtmlLexer
from prompt_toolkit import PromptSession
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.styles import Style


class CustomValidator(Validator):
    def validate(self, document):
        if not document.text:
            raise ValidationError(
                message="Input cannot be empty", cursor_position=len(document.text)
            )


class PromptSessionWrapper:
    def __init__(self, history_path: str = "dlm_matrix/logs/chat_history.txt"):
        self.completer_words = ["quit", "restart", "help", "history"]
        self.history_path = history_path
        self.custom_style = Style.from_dict(
            {
                "prompt": "#00aa00",  # Green color for prompt messages
                "input": "#ff0066",  # Pink color for user input
                "message": "#00aaff",  # Blue color for other messages
            }
        )
        self.setup_session()

    def setup_session(self):
        self.session = PromptSession(
            history=FileHistory(self.history_path),
            auto_suggest=AutoSuggestFromHistory(),
            completer=WordCompleter(self.completer_words, ignore_case=True),
            lexer=PygmentsLexer(HtmlLexer),
            validator=CustomValidator(),
            style=self.custom_style,
        )

    def get_input(self, prompt_message: str) -> str:
        try:
            return self.session.prompt(
                [
                    ("class:prompt", prompt_message)
                ],  # Apply 'prompt' style to prompt_message
                bottom_toolbar=[("class:message", "Type /help for a list of commands")],
            )
        except ValidationError as e:
            print(str(e))
            return self.get_input(prompt_message)

    def set_completer_words(self, words: list):
        self.completer_words = words
        self.setup_session()

    def set_history_path(self, path: str):
        self.history_path = path
        self.setup_session()

    def add_to_history(self, message: str):
        with open(self.history_path, "a") as f:
            f.write(message + "\n")

    def clear_history(self):
        with open(self.history_path, "w") as f:
            f.write("")
