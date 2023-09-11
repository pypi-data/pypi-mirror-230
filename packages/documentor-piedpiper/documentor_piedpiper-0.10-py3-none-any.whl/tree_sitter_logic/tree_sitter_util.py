from snippet_management.node_info import NodeInfo
from tree_sitter import Node
from typing import List, Set


def _descendants_with_type(node: Node, node_type: str) -> List[Node]:
    nodes = list()
    if node.type == node_type:
        nodes.append(node)
    for child in node.children:
        nodes.extend(_descendants_with_type(child, node_type))
    return nodes


def global_node_types(root: Node, node_types: Set[str]) -> List[Node]:
    return [child for child in root.children if child.type in node_types]


def get_specified_nodes(root: Node, node_types: Set[str]) -> List[Node]:
    nodes = list()
    for node_type in node_types:
        nodes.extend(_descendants_with_type(root, node_type))
    return nodes


def get_identifier(node: Node, file_str: str) -> str:
    for child in node.children:
        if child.type == "identifier":
            return file_str[child.start_byte : child.end_byte]
    return None


def get_dependencies(root: Node) -> List[Node]:
    dependencies_types = {"import_from_statement", "import_from_statement"}
    return global_node_types(root, dependencies_types)


def get_implementation(node: Node, file_str: str) -> str:
    implementation = ""
    if node.type == "class_definition":
        implementation = _get_class_implementation(node, file_str)
    else:
        implementation = file_str[node.start_byte : node.end_byte]
    return implementation


def _get_class_implementation(node: Node, file_str: str) -> str:
    valid_types = {"typed_parameter", "expression_statement", "assignment"}
    class_implementation = [
        get_implementation(block_child, file_str)
        for child in node.children
        if child.type == "block"
        for block_child in child.children
        if block_child.type in valid_types
    ]
    implementation = "\n".join(class_implementation)
    return implementation if implementation else "NO ARGUMENTS SPECIFIED IN THIS CLASS"


def _recursive_get_nodes(
    parent_node_info: NodeInfo, types: Set[str], file_str: str
) -> List[NodeInfo]:
    nodes_list: List[NodeInfo] = list()
    for child in parent_node_info.children:
        child_node_info = NodeInfo(child, parent_node_info, file_str)
        child_nodes = _recursive_get_nodes(child_node_info, types, file_str)
        nodes_list.extend(child_nodes)
        if child.type in types:
            nodes_list.append(child_node_info)
    return nodes_list


def get_nodes(root: Node, types: Set[str], file_str: str) -> List[NodeInfo]:
    root_node_info: NodeInfo = NodeInfo(root)
    return _recursive_get_nodes(root_node_info, types, file_str)
