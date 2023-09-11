from git_tools.git_manager import GitManager
from doc_ignore.doc_ignore import DocIgnore
from pathlib import Path
from pygit2 import Tree, GIT_OBJ_COMMIT
from typing import List


# Don't work with repos inside repos, polyrepos.
class GitFilePaths:
    doc_ignore = DocIgnore()

    @staticmethod
    def _valid_file(sys_path: Path) -> bool:
        return not (
            (sys_path.name in GitFilePaths.doc_ignore)
            or (sys_path.suffix in GitFilePaths.doc_ignore)
            or (sys_path.name == ".docignore")
            or (sys_path.name == ".git")
            or (sys_path.name == ".gitignore")
            or (sys_path.name == "doc.log")
        )

    @staticmethod
    def get_all_valid_paths(
        git_tree: Tree = None,
        parent_path: Path = Path("."),
    ) -> List[Path]:
        paths: List[Path] = []
        if not git_tree:
            GitManager.select_front_commit()
            git_tree = GitManager.selected_commit_tree()
        for entry in git_tree:
            full_path: Path = parent_path / entry.name
            conditions = (
                not full_path.exists()
                or entry.type == GIT_OBJ_COMMIT
                or not GitFilePaths._valid_file(full_path)
            )
            if conditions:
                continue
            if full_path.is_file():
                paths.append(full_path)
            elif full_path.is_dir():
                dir_paths: List[Path] = GitFilePaths.get_all_valid_paths(
                    GitManager.project_repo()[entry.oid], full_path
                )
                paths.extend(dir_paths)
        return paths
