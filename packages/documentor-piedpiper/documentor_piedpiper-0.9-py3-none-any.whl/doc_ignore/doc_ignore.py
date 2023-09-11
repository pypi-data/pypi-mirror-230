from metaclasses.singleton_meta import SingletonMeta
from git_tools.git_retrieaver import GitRetrieaver
from git_tools.git_manager import GitManager
from pathlib import Path
from typing import ClassVar


# .docignore file must be found at the root directory
class DocIgnore(metaclass=SingletonMeta):
    instance: ClassVar

    def __init__(self, root_path: Path = None):
        project_root = root_path if root_path != None else Path(".")
        doc_ignore_path = project_root / ".docignore"
        if doc_ignore_path.exists():
            GitManager.select_front_commit()
            read_doc = GitRetrieaver.retrieve_file(doc_ignore_path)
            doc_lines = read_doc.splitlines()
            doc_set = set(doc_lines)
            clean_doc_set = {line.strip() for line in doc_set}
            self.ignore = clean_doc_set
            GitManager.select_tail_commit()
        else:
            raise Exception(
                "DocIgnore_.docignore_not_found: .docignore is not at the root dir"
            )

    def __contains__(self, sys_object: str):
        return sys_object in self.ignore
