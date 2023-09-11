from git_tools.git_file_checker import GitFileChecker
from git_tools.git_manager import GitManager
from snippet_management.snippet_storage import SnippetStorage
from snippet_management.code_snippet import CodeSnippet
from repository_scrapping.file_scrapper import FileScrapper
from metaclasses.singleton_meta import SingletonMeta
from typing import Dict, ClassVar


class ModifiedFilesManager(metaclass=SingletonMeta):
    instance: ClassVar = None
    _file_scrapper_tail: FileScrapper
    _file_scrapper_front: FileScrapper
    _snippets_to_doc: SnippetStorage
    _snippets_to_delete: SnippetStorage
    _old_deleted_snippets_dict: Dict[int, CodeSnippet]
    _new_added_snippets_dict: Dict[int, CodeSnippet]
    _modified_snippets_dict: Dict[int, CodeSnippet]

    def __init__(self):
        self._file_scrapper_front = FileScrapper()
        self._file_scrapper_tail = FileScrapper()
        self._snippets_to_doc = SnippetStorage()
        self._snippets_to_delete = SnippetStorage()
        self._old_deleted_snippets_dict = {}
        self._new_added_snippets_dict = {}
        self._modified_snippets_dict = {}

    @property
    def snippets_to_delete(self):
        return self._snippets_to_delete

    @property
    def snippets_to_doc(self):
        return self._snippets_to_doc

    def _check_modified_files(self):
        if GitFileChecker.modified:
            self._start_file_scrappers()
            self._update_all_snippets_dict()
            self._update_snippets_to_doc()
            self._update_snippets_to_delete()

    def _update_snippets_to_doc(self):
        self.snippets_to_doc.update_storage(self._new_added_snippets_dict)
        self.snippets_to_doc.update_storage(self._modified_snippets_dict)

    def _update_snippets_to_delete(self):
        self.snippets_to_delete.update_storage(self._old_deleted_snippets_dict)

    def _start_file_scrapper_front(self):
        GitManager.select_front_commit()
        self._file_scrapper_front.scrape_specified(GitFileChecker.modified)

    def _start_file_scrapper_tail(self):
        GitManager.select_tail_commit()
        self._file_scrapper_tail.scrape_specified(GitFileChecker.modified)

    def _start_file_scrappers(self):
        self._start_file_scrapper_front()
        self._start_file_scrapper_tail()

    def _update_all_snippets_dict(self):
        self._update_new_added_snippets_dict()
        self._update_old_deleted_snippets_dict()
        self._update_modified_snippets_dict()

    def _update_old_deleted_snippets_dict(self):
        front_snippets_keys = set(self._file_scrapper_front.storage_dict.keys())
        tail_snippets_keys = set(self._file_scrapper_tail.storage_dict.keys())
        deleted_snippets_hash_ints = tail_snippets_keys - front_snippets_keys
        deleted_snippets_dict = {
            hash_int: snippet
            for hash_int, snippet in self._file_scrapper_tail.storage_dict.items()
            if hash_int in deleted_snippets_hash_ints
        }
        self._old_deleted_snippets_dict = deleted_snippets_dict

    def _update_new_added_snippets_dict(self):
        front_snippets_keys = set(self._file_scrapper_front.storage_dict.keys())
        tail_snippets_keys = set(self._file_scrapper_tail.storage_dict.keys())
        added_snippets_hash_ints = front_snippets_keys - tail_snippets_keys
        added_snippets_dict = {
            hash_int: snippet
            for hash_int, snippet in self._file_scrapper_front.storage_dict.items()
            if hash_int in added_snippets_hash_ints
        }
        self._new_added_snippets_dict = added_snippets_dict

    def _update_modified_snippets_dict(self):
        front_snippets_keys = set(self._file_scrapper_front.storage_dict.keys())
        tail_snippets_keys = set(self._file_scrapper_tail.storage_dict.keys())
        modified_snippets_hash_ints = front_snippets_keys.intersection(
            tail_snippets_keys
        )
        modified_snippets_dict: Dict[int, CodeSnippet] = {}
        for hash_int in modified_snippets_hash_ints:
            front_snippet = self._file_scrapper_front.storage_dict.get(hash_int)
            tail_snippet = self._file_scrapper_tail.storage_dict.get(hash_int)
            if front_snippet.implementation != tail_snippet.implementation:
                modified_snippets_dict[hash_int] = front_snippet
        self._modified_snippets_dict = modified_snippets_dict

    @staticmethod
    def get_snippets_to_doc() -> SnippetStorage:
        return ModifiedFilesManager.instance.snippets_to_doc

    @staticmethod
    def get_snippets_to_delete() -> SnippetStorage:
        return ModifiedFilesManager.instance.snippets_to_delete

    @staticmethod
    def check_modified_files():
        return ModifiedFilesManager.instance._check_modified_files()


ModifiedFilesManager()
