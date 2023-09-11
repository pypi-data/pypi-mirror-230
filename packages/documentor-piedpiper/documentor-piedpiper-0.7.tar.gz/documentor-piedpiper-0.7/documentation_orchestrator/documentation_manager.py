from documentation_orchestrator.modified_files_manager import ModifiedFilesManager
from documentation_orchestrator.added_files_manager import AddedFilesManager
from documentation_orchestrator.first_run_manager import FirstRunManager
from snippet_management.snippet_storage import SnippetStorage
from git_tools.git_file_checker import GitFileChecker
from git_tools.git_manager import GitManager
from metaclasses.singleton_meta import SingletonMeta
from doc_log.doc_log import DocLog
from typing import List, ClassVar
from pathlib import Path


# GitFileChecker. Solo se ha de usar su update aqui
class DocumentationManager(metaclass=SingletonMeta):
    instance: ClassVar
    _snippets_to_doc: SnippetStorage
    _snippets_to_delete: SnippetStorage
    _files_to_delete: List[Path]

    def __init__(self):
        self._snippets_to_doc = SnippetStorage()
        self._snippets_to_delete = SnippetStorage()
        self._files_to_delete = None

    def _update_snippets_to_doc(self):
        added_file_snippets_dict = AddedFilesManager.get_snippets_to_doc().storage
        self._snippets_to_doc.update_storage(added_file_snippets_dict)
        modified_file_snippets_dict = ModifiedFilesManager.get_snippets_to_doc().storage
        self._snippets_to_doc.update_storage(modified_file_snippets_dict)

    def _update_snippets_to_doc_first_run(self):
        all_snippets_to_doc = FirstRunManager.get_snippets_to_doc().storage
        self._snippets_to_doc.update_storage(all_snippets_to_doc)

    def _update_snippets_to_delete(self):
        deleted_file_snippets_dict = (
            ModifiedFilesManager.get_snippets_to_delete().storage
        )
        self._snippets_to_delete.update_storage(deleted_file_snippets_dict)

    def _update_files_to_delete(self):
        self._files_to_delete = GitFileChecker.deleted

    @staticmethod
    def start_documentation():
        if not DocLog.exists_doc_log():
            DocumentationManager._run_first_diagnosis()
        else:
            DocumentationManager._run_diagnosis()

    @staticmethod
    def update_doc_log():
        to_doc = DocumentationManager.instance._snippets_to_doc
        to_delete = DocumentationManager.instance._snippets_to_delete
        DocLog.update_doc_log(to_doc, to_delete)

    @staticmethod
    def _run_first_diagnosis():
        FirstRunManager.start_first_run()
        DocumentationManager.instance._update_snippets_to_doc_first_run()
        DocumentationManager.update_doc_log()

    @staticmethod
    def _run_diagnosis():
        GitFileChecker.update_changed_files()
        AddedFilesManager.check_added_files()
        ModifiedFilesManager.check_modified_files()
        DocumentationManager.instance._update_snippets_to_doc()
        DocumentationManager.instance._update_snippets_to_delete()
        DocumentationManager.instance._update_files_to_delete()
        DocumentationManager.update_doc_log() # cambio

    @staticmethod
    def get_snippets_to_doc() -> SnippetStorage:
        return DocumentationManager.instance._snippets_to_doc

    @staticmethod
    def get_snippets_to_delete() -> SnippetStorage:
        return DocumentationManager.instance._snippets_to_delete

    @staticmethod
    def show_results():
        print("-------------------------------------------------------------\n")
        print("\t\tSNIPPETS TO DOCUMENTATE\n")
        print("-------------------------------------------------------------\n")
        DocumentationManager.get_snippets_to_doc().show_storage()
        print("\n\n\n\n")
        print("-------------------------------------------------------------\n")
        print("\t\tSNIPPETS TO DELETE\n")
        print("-------------------------------------------------------------\n")
        DocumentationManager.get_snippets_to_delete().show_storage()
        print("-------------------------------------------------------------\n")
        print("\n\n\nEND")


DocumentationManager()
