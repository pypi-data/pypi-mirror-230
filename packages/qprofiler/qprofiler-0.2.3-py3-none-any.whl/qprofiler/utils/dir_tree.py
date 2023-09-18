import os
import pathlib
from typing import List

PIPE = "|"
ELBOW = "└──"
TEE = "├──"
PIPE_PREFIX = "|   "
SPACE_PREFIX = "    "


class DirTree:
    def __init__(self, root_dir: pathlib.Path) -> None:
        self._generator = _TreeGenerator(root_dir)

    def generate(self) -> None:
        tree = self._generator.build_tree()
        for item in tree:
            print(item)


class _TreeGenerator:
    def __init__(self, root_dir: pathlib.Path) -> None:
        self._tree = []
        self._root_dir = root_dir

    def build_tree(self) -> List[str]:
        self._tree_head()
        self._tree_body(self._root_dir)
        return self._tree

    def _tree_head(self) -> None:
        self._tree.append(f"{self._root_dir}{os.sep}")
        self._tree.append(PIPE)

    def _tree_body(self, directory: pathlib.Path, prefix: str = "") -> None:
        entries = directory.iterdir()
        entries = sorted(entries, key=lambda x: x.is_file())
        entry_count = len(entries)
        for index, entry in enumerate(entries):
            connector = ELBOW if index == entry_count - 1 else TEE
            if entry.is_dir():
                self._add_directory(entry, index, entry_count, prefix, connector)
            else:
                self._add_file(entry, prefix, connector)

    def _add_directory(
        self,
        directory: pathlib.Path,
        index: int,
        entry_count: int,
        prefix: str,
        connector: str,
    ) -> None:
        self._tree.append(f"{prefix}{connector}{directory.name}{os.sep}")
        if entry_count != index - 1:
            prefix += PIPE_PREFIX
        else:
            prefix += SPACE_PREFIX
        self._tree_body(directory=directory, prefix=prefix)
        self._tree.append(prefix.rstrip())

    def _add_file(self, file: pathlib.Path, prefix: str, connector: str) -> None:
        self._tree.append(f"{prefix}{connector}{file.name}")
