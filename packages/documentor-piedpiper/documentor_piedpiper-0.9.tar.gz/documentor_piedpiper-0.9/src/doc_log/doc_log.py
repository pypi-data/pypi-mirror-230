from snippet_management.snippet_storage import SnippetStorage
from git_tools.git_manager import GitManager
from git_tools.git_retrieaver import GitRetrieaver
from textwrap import dedent
from pathlib import Path

# snippets to delete does not count the deleted files


class DocLog:
    @staticmethod
    def create_doc_log():
        desired_path = DocLog.get_doc_log_path()
        desired_path.touch()

    @staticmethod
    def update_doc_log(
        snippets_to_doc: SnippetStorage, snippets_to_delete: SnippetStorage
    ):
        DocLog.create_doc_log()
        num_snippets_to_doc = len(snippets_to_doc)
        num_snippets_to_delete = len(snippets_to_delete)
        head_commit_hash: str = GitManager.head_commit().short_id
        new_log_message = dedent(
            f"""
        COMMIT_HASH:{head_commit_hash}
        NUMBER_OF_SNIPPETS_TO_DOC:{num_snippets_to_doc}
        NUMBER_OF_SNIPPETS_TO DELETE:{num_snippets_to_delete}
        """
        )
        doc_log_path = DocLog.get_doc_log_path()
        original_log_content = doc_log_path.read_text()
        doc_log_path.write_text(new_log_message + original_log_content)

    @staticmethod
    def exists_doc_log() -> bool:
        desired_path = Path("./doc.log")
        try:
            GitManager.select_front_commit()
            GitRetrieaver.get_file_git_object(desired_path)
            return True
        except Exception:
            return False

    @staticmethod
    def get_doc_log_path() -> Path:
        return Path("./doc.log")
