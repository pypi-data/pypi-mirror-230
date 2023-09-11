from tree_sitter import Language
from enum import Enum
from typing import Tuple, Set

Language.build_library(
    # Store the library in the `build` directory
    "build/my-languages.so",
    # Include one or more languages
    ["tree-sitter-python"],
)


class FileExtension(Enum):
    py: Language = Language("build/my-languages.so", "python")


class LanguageNodes(Enum):
    """
    (wholecode, only global scope)
    """

    py: Tuple[Set[str], Set[str]] = (
        {"class_definition", "function_definition"},
        { "function_definition"},
    )
