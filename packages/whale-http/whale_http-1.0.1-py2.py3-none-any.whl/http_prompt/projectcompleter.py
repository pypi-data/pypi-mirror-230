from prompt_toolkit.completion import Completer, Completion

from .utils import fuzzyfinder


class ProjectCollectCompleter(Completer):
    def __init__(self, project_names, project_dict):
        super().__init__()
        self.prjnames = project_names
        self.prjdict = project_dict

    def get_completions(self, document, complete_event):
        cur_text: str = document.text_before_cursor
        if cur_text.startswith("cp"):
            cur_word: str = document.get_word_before_cursor()
            suggestions = fuzzyfinder(cur_word, collection=self.prjnames)
            for word in suggestions:
                desc = self.prjdict.get(word, "")
                yield Completion(word, -len(cur_word), display_meta=desc)
