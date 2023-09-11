from ai_logic.documentor_chat import DocumentorChat
from snippet_management.code_snippet import CodeSnippet
from documentation_orchestrator.documentation_manager import DocumentationManager
from typing import Dict, ClassVar
from pathlib import Path
from metaclasses.singleton_meta import SingletonMeta


class DocWriter(metaclass=SingletonMeta):
    instance: ClassVar
    doc_path: Path = Path("./docs")
    snippets_to_doc: Dict[int, CodeSnippet] = None
    current_snippet: CodeSnippet = None
    current_doc_path: Path = None
    snippet_documentation: str = None

    def __init__(self):
        self.doc_path = Path("./docs")
        self.snippets_to_doc = None
        self.current_snippet = None
        self.current_doc_path = None
        self.snippet_documentation = None

    @staticmethod
    def start_writing_documentation():
        DocWriter.instance._main()

    def _main(self):
        self._get_snippets_to_doc()
        for snippet_to_doc in self.snippets_to_doc.values():
            self._set_current_snippet(snippet_to_doc)
            self._document_current_snippet()

    def _get_snippets_to_doc(self):
        self.snippets_to_doc = DocumentationManager.get_snippets_to_doc().storage

    def _set_current_snippet(self, snippet_to_doc: CodeSnippet):
        self.current_snippet = snippet_to_doc

    def _document_current_snippet(self):
        self._get_current_snippet_documentation()
        self._set_current_doc_path()
        self._create_doc_md()

    def _get_current_snippet_documentation(self):
        DocumentorChat.set_snippet_to_doc(self.current_snippet)
        DocumentorChat.ask_documentation()
        self.snippet_documentation = DocumentorChat.get_documentation_answer()

    def _set_current_doc_path(self):
        file_path = self.current_snippet.file_path.parent
        file_name_without_extension = str(self.current_snippet.file_path.stem)
        file_doc = Path(file_name_without_extension + ".md")
        doc_file_path = self.doc_path / file_path / file_doc
        self.current_doc_path = doc_file_path

    def _set_current_doc_path(self):
        file_path = self.current_snippet.file_path.parent
        file_name = str(self.current_snippet.file_path.stem)
        file_doc = Path(self.current_snippet.code_snippet_identifier + ".md")
        doc_file_path = self.doc_path / file_path / file_name 
        if self.current_snippet.parent_type == "class_definition":
            doc_file_path = doc_file_path / f"{self.current_snippet.parent_identifier}"
        doc_file_path = doc_file_path / file_doc
        self.current_doc_path = doc_file_path

    def _create_doc_md(self):
        self.current_doc_path.parent.mkdir(parents=True, exist_ok=True)
        self.current_doc_path.touch(exist_ok=True)
        self.current_doc_path.write_text(self.snippet_documentation, encoding="utf-8")


DocWriter()
