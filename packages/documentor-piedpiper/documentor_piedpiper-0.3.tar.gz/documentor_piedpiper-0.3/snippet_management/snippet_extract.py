from tree_sitter_logic.tree_sitter_util import get_identifier, get_implementation
from snippet_management.node_info import NodeInfo
from dataclasses import dataclass


@dataclass()
class SnippetExtract:
    parent_type: str
    parent_identifier: str
    snippet_type: str
    snippet_identifier: str
    snippet_implementation: str

    def __init__(self, node_info: NodeInfo, file_str: str):
        self.parent_type = node_info.parent_type
        self.parent_identifier = node_info.parent_identifier
        self.snippet_type = node_info.node.type
        self.snippet_identifier = get_identifier(node_info.node, file_str)
        self.snippet_implementation = get_implementation(node_info.node, file_str)
