"""Prune changelogs"""

from typing import List

from gitaudit.git.change_log_entry import ChangeLogEntry
from gitaudit.branch.hierarchy import (
    hierarchy_log_to_linear_log_entry,
    hierarchy_log_to_linear_log,
)


def match_in_entry(entry: ChangeLogEntry, file_list: List[str]) -> bool:
    """Determines if any numstat entry matches the file list

    Args:
        entry (ChangeLogEntry): Change log entry to be analysed for numstat entries
        file_list (List[str]): The list of file paths used for pruning. If a changelog entry is
            associated with a file in this list, it remains in the pruned changelog.

    Returns:
        bool: True if any numstat entries matches the filelist
    """
    return any(map(lambda x: x.path in file_list, entry.numstat))


def first_parent_prune_by_file_list(changelog: List[ChangeLogEntry], file_list: List[str]):
    """
    Prune entries from the changelog based on a provided file list.

    This function traverses the given changelog, and checks whether each entry
    has any associated file in the provided file list. If an entry does not
    have any associated file in the file list either in its numstat or in its
    submodule updates, the entry is pruned from the changelog.

    Additionally, if a submodule update becomes empty after pruning, it is
    also removed from the changelog entry.

    Parameters
    ----------
    changelog : List[ChangeLogEntry]
        The changelog entries to be pruned. Each entry contains 'numstat'
        and 'submodule_updates' attributes.
    file_list : List[str]
        The list of file paths used for pruning. If a changelog entry is
        associated with a file in this list, it remains in the pruned changelog.

    Returns
    -------
    List[ChangeLogEntry]
        The pruned changelog.

    Notes
    -----
    This function directly modifies the given changelog, rather than creating
    a new one.
    """
    remove_indices = []

    for index, entry in enumerate(changelog):
        entry_to_linlog = hierarchy_log_to_linear_log_entry(entry)
        matches_in_numstat = any(
            map(
                lambda x: match_in_entry(x, file_list),
                entry_to_linlog,
            )
        )

        remove_submodules = []

        for sub_path, sub_module_update in entry.submodule_updates.items():
            sub_module_update.entries = first_parent_prune_by_file_list(
                sub_module_update.entries,
                file_list,
            )

            if not sub_module_update.entries:
                remove_submodules.append(sub_path)

        for sub_path in remove_submodules:
            entry.submodule_updates.pop(sub_path)

        matches_in_submodules = any(
            filter(
                lambda sub: sub.entries,
                entry.submodule_updates.values(),
            )
        )

        if not matches_in_numstat and not matches_in_submodules:
            remove_indices.append(index)

    for index in reversed(remove_indices):
        changelog.pop(index)

    return changelog


class HierarchyPrune:
    """This class is used for handling and pruning the hierarchy logs.

    Attributes:
        hierarchy_log (List[ChangeLogEntry]): The list of change log entries forming a hierarchy.
        linear_log: The linear version of the hierarchy log.
        sha_to_entry_map (dict): Mapping from SHA to the corresponding change log entry.
        sha_to_parent_map (dict): Mapping from SHA to the parent change log entry.
    """

    def __init__(self, hierarchy_log: List[ChangeLogEntry]) -> None:
        """Initializes the HierarchyPrune with the given hierarchy log.

        Args:
            hierarchy_log (List[ChangeLogEntry]): The list of change log entries forming a
                hierarchy.
        """
        self.hierarchy_log = hierarchy_log

        self.linear_log = hierarchy_log_to_linear_log(self.hierarchy_log)

        self.sha_to_entry_map = {}
        self.sha_to_parent_map = {}

        self._create_parent_map(self.hierarchy_log)

    def _create_parent_map(
        self,
        hier_log: List[ChangeLogEntry],
        current_parent: ChangeLogEntry = None,
    ):
        """Recursively creates parent mapping for the given hierarchy log.

        Args:
            hier_log (List[ChangeLogEntry]): List of change log entries for mapping.
            current_parent (ChangeLogEntry, optional): The current parent change log entry.
                Defaults to None.
        """
        for entry in hier_log:
            self.sha_to_entry_map[entry.sha] = entry

            if current_parent:
                self.sha_to_parent_map[entry.sha] = current_parent

            if entry.other_parents:
                for sub_hier_log in entry.other_parents:
                    self._create_parent_map(sub_hier_log, entry)

    def prune_sha(self, sha: str) -> None:
        """Prunes the hierarchy log by removing the change log entry with the given SHA.

        If the SHA is found in the hierarchy, the method recursively prunes other parent
            entries if necessary.

        Args:
            sha (str): The SHA identifier of the change log entry to be pruned.
        """
        if sha not in self.sha_to_parent_map:
            self.hierarchy_log = list(filter(lambda x: x.sha != sha, self.hierarchy_log))
        else:
            parent_entry = self.sha_to_parent_map[sha]

            for index, sub_hier_log in enumerate(parent_entry.other_parents):
                parent_entry.other_parents[index] = list(
                    filter(
                        lambda x: x.sha != sha,
                        sub_hier_log,
                    )
                )

            if all(map(lambda x: not x, parent_entry.other_parents)):
                self.prune_sha(parent_entry.sha)
