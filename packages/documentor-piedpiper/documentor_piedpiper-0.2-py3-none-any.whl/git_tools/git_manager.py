from metaclasses.singleton_meta import SingletonMeta
from pathlib import Path
from pygit2 import Repository, Commit, Tree
from typing import ClassVar, List


class GitManager(metaclass=SingletonMeta):
    instance: ClassVar = None
    project_repo: Repository
    head_commit: Commit
    front_commit: Commit  # default = HEAD
    tail_commit: Commit  # default = HEAD^
    selected_commit: Commit  # default = HEAD^
    front_commit_tree: Tree
    tail_commit_tree: Tree
    selected_commit_tree: Tree
    project_file_paths: List[Path]

    def __init__(self, repo_path: Path = Path.cwd()):
        self.project_repo = Repository(repo_path)
        self.head_commit = self.project_repo.head.peel(Commit)
        self.front_commit = self.head_commit
        self.front_commit_tree = self.front_commit.tree
        if self.head_commit.parents[0]:
            self.tail_commit = self.head_commit.parents[0]
        else:
            raise Exception(
                "GitManager_Error: get_head_parent_commit(), No head parent commit."
            )
        self.tail_commit_tree = self.tail_commit.tree
        self.selected_commit = self.tail_commit
        self.selected_commit_tree = self.tail_commit_tree

    def _update_front_commit(self, front_commit_hash: str):
        new_front_commit = self.project_repo[front_commit_hash]
        if self.project_repo.descendant_of(self.tail_commit.id, new_front_commit.id):
            self.front_commit = new_front_commit
            self.front_commit_tree = self.front_commit.tree
        else:
            raise Exception(
                "GitManager_Error: The front commit can't be previous to the tail commit"
            )

    def _update_tail_commit(self, tail_commit_hash: str):
        new_tail_commit = self.project_repo[tail_commit_hash]
        if self.project_repo.descendant_of(new_tail_commit.id, self.front_commit.id):
            self.tail_commit = new_tail_commit
            self.tail_commit_tree = self.tail_commit.tree
        else:
            raise Exception(
                "GitManager_Error: The tail commit can't be next to the tail commit"
            )

    def _select_front_commit(self):
        self.selected_commit = self.front_commit
        self.selected_commit_tree = self.front_commit_tree

    def _select_tail_commit(self):
        self.selected_commit = self.tail_commit
        self.selected_commit_tree = self.tail_commit_tree

    def _stage_file(self, file_path: Path):
        repo: Repository = self.project_repo
        repo.index.add(file_path)
        repo.index.write()

    def _stage_file_list(self, files_paths: List[Path]):
        for file_path in files_paths:
            self._stage_file(file_path)

    def _commit(self, commit_msg: str = None):
        if not commit_msg:
            commit_msg = f"DOCUMENTED COMMIT:{self.head_commit.short_id}"
        repo: Repository = self.project_repo
        author = repo.default_signature
        tree = repo.index.write_tree()
        repo.create_commit("HEAD", author, author, commit_msg, tree, [repo.head.target])

    @staticmethod
    def stage_file(file_path: Path):
        GitManager.instance._stage_file(file_path)

    @staticmethod
    def stage_file_list(files_paths: List[Path]):
        GitManager.instance._stage_file_list(files_paths)

    @staticmethod
    def commit(commit_msg: str = None):
        GitManager.instance._commit(commit_msg)

    @staticmethod
    def commit_doc_changes():  # also should stage docs directory
        doc_log_path = Path("./doc.log")
        GitManager.stage_file(doc_log_path)
        GitManager.commit()

    @staticmethod
    def update_front_commit(front_commit_hash: str):
        GitManager.instance._update_front_commit(front_commit_hash)

    @staticmethod
    def update_tail_commit(tail_commit_hash: str):
        GitManager.instance._update_tail_commit(tail_commit_hash)

    @staticmethod
    def select_front_commit():
        GitManager.instance._select_front_commit()

    @staticmethod
    def select_tail_commit():
        GitManager.instance._select_tail_commit()

    @staticmethod
    def project_repo() -> Repository:
        return GitManager.instance.project_repo

    @staticmethod
    def head_commit() -> Commit:
        return GitManager.instance.head_commit

    @staticmethod
    def front_commit() -> Commit:
        return GitManager.instance.front_commit

    @staticmethod
    def front_commit_tree() -> Tree:
        return GitManager.instance.front_commit_tree

    @staticmethod
    def tail_commit() -> Commit:
        return GitManager.instance.tail_commit

    @staticmethod
    def tail_commit_tree() -> Tree:
        return GitManager.instance.tail_commit_tree

    @staticmethod
    def selected_commit() -> Commit:
        return GitManager.instance.selected_commit

    @staticmethod
    def selected_commit_tree() -> Tree:
        return GitManager.instance.selected_commit_tree

    @staticmethod
    def get_head_parent_commit() -> Commit:
        if GitManager.head_commit().parents[0]:
            return GitManager.head_commit().parents[0]
        else:
            raise Exception(
                "GitManager_Error: get_head_parent_commit(), No head parent commit."
            )


GitManager()
