from snippet_management.code_snippet import CodeSnippet
from dataclasses import dataclass, field
from typing import Dict, Union


@dataclass
class SnippetStorage:
    _storage: Dict[int, CodeSnippet] = field(default_factory=dict)

    def __contains__(self, code_snippet: CodeSnippet):
        return isinstance(self.get_code_snippet(code_snippet), CodeSnippet)

    def __len__(self):
        return len(self.storage)

    @property
    def storage(self) -> Dict[int, CodeSnippet]:
        return self._storage

    def update_storage(self, snippets_dict: Dict[int, CodeSnippet]):
        self.storage.update(snippets_dict)

    def get_code_snippet(self, code_snippet: CodeSnippet) -> Union[CodeSnippet, None]:
        hashed_snippet = hash(code_snippet)
        if hashed_snippet in self._storage:
            return self._storage.get(hashed_snippet)
        else:
            return None

    def add_code_snippet(self, code_snippet: CodeSnippet) -> bool:
        if code_snippet in self:
            return False
        hashed_snippet = hash(code_snippet)
        self._storage.update({hashed_snippet: code_snippet})
        return True

    def update_code_snippet(self, code_snippet: CodeSnippet) -> bool:
        # only changes the implementation
        if code_snippet not in self:
            return False
        hashed_snippet = hash(code_snippet)
        self._storage.update({hashed_snippet: code_snippet})
        return True

    def delete_code_snippet(self, code_snippet: CodeSnippet) -> bool:
        if code_snippet not in self:
            return False
        hashed_snippet = hash(code_snippet)
        self._storage.pop(hashed_snippet)
        return True

    def show_storage(self):
        for key, value in (self._storage).items():
            print(f"{key}: {value}")
