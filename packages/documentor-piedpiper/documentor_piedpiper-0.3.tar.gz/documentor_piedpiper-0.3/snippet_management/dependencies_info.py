from tree_sitter_logic.tree_sitter_util import get_dependencies, get_implementation
from dataclasses import dataclass
from tree_sitter import Node


@dataclass()
class DependenciesInfo:
    dependencies: str

    def __init__(self, node: Node, file_str: str):
        self.dependencies = self._get_imports_string(node, file_str)

    def _get_imports_string(self, node: Node ,file_str: str) -> str:
        dependencies_nodes = get_dependencies(node)
        import_statements = []
        for dependency in dependencies_nodes:
            import_statements.append(get_implementation(dependency, file_str))
        imports_string = '\n'.join(import_statements)
        return imports_string
