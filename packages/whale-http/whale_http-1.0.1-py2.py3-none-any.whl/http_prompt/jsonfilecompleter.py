import json
from pathlib import Path

from prompt_toolkit.completion import Completer, FuzzyWordCompleter


class JsonFileCompleter(Completer):
    def parse(self):
        return [req["name"] for req in self.jsondata["requests"]]

    def __init__(self, filename):
        super().__init__()
        self.filename = filename

        if Path(filename).exists():
            with open(filename, "r", encoding="utf-8") as f:
                self.jsondata = json.load(f)
        else:
            self.jsondata = {}

        self.fuzzycompleter = FuzzyWordCompleter(words=self.parse())

    def get_completions(self, document, complete_event):
        return self.fuzzycompleter.get_completions(document, complete_event)
