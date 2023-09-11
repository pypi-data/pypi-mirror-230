from repository_scrapping.file_scrapper import FileScrapper
from snippet_management.snippet_storage import SnippetStorage
from git_tools.git_file_checker import GitFileChecker
from git_tools.git_manager import GitManager
from metaclasses.singleton_meta import SingletonMeta
from typing import ClassVar


class AddedFilesManager(metaclass=SingletonMeta):
    instance: ClassVar
    _added_file_scrapper: FileScrapper
    _snippets_to_doc: SnippetStorage

    def __init__(self):
        self._added_file_scrapper = FileScrapper()
        self._snippets_to_doc = SnippetStorage()

    def _start_added_file_scrapper(self):
        if GitFileChecker.added:
            GitManager.select_front_commit()
            self._added_file_scrapper.scrape_specified(GitFileChecker.added)

    def _update_snippets_to_doc(self):
        self._start_added_file_scrapper()
        snippets_to_doc_dict = self._added_file_scrapper.storage_dict
        self._snippets_to_doc.update_storage(snippets_to_doc_dict)

    @staticmethod
    def get_snippets_to_doc() -> SnippetStorage:
        return AddedFilesManager.instance._snippets_to_doc

    @staticmethod
    def check_added_files():
        AddedFilesManager.instance._update_snippets_to_doc()


AddedFilesManager = AddedFilesManager()
