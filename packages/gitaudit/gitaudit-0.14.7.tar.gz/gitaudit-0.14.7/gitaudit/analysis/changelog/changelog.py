"""Analyse Gitlogs
"""
import logging

from datetime import timedelta, datetime
from typing import List, Callable
import os

from gitaudit.github.instance import Github
from gitaudit.github.graphql_objects import Submodule
from gitaudit.git.controller import Git
from gitaudit.git.change_log_entry import SubmoduleUpdate
from gitaudit.branch.hierarchy import linear_log_to_hierarchy_log
from gitaudit.branch.submodule import insert_submodule_updates


logger = logging.getLogger(__name__)


def daterange(start_date: datetime, end_date: datetime):
    """
    Generator for a range of dates.

    Args:
        start_date (datetime): The starting date.
        end_date (datetime): The ending date.

    Yields:
        datetime: Each date from start_date to end_date inclusive.
    """
    for n_days in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(days=n_days)


def get_submodule_split(end_submodules: List[Submodule], start_submodules: List[Submodule]):
    """
    Splits and maps submodules into three categories - existing in both, only in start,
    and only in end.

    Args:
        end_submodules (List[Submodule]): List of submodules at the end.
        start_submodules (List[Submodule]): List of submodules at the start.

    Returns:
        tuple: Tuple containing three lists:
            - Submodules that exist in both the start and the end.
            - Submodules that exist only at the start.
            - Submodules that exist only at the end.
    """
    start_module_map = {sub.name: sub for sub in start_submodules}
    end_module_map = {sub.name: sub for sub in end_submodules}

    end_submodules_names = set(map(lambda x: x.name, end_submodules))
    start_submodules_names = set(map(lambda x: x.name, start_submodules))

    both_names = end_submodules_names.intersection(start_submodules_names)
    start_only_names = start_submodules_names.difference(both_names)
    end_only_names = end_submodules_names.difference(both_names)

    both_submodules = list(
        map(lambda x: (start_module_map[x], end_module_map[x]), both_names))

    start_only_submodules = list(map(start_module_map.get, start_only_names))
    end_only_submodules = list(map(end_module_map.get, end_only_names))

    return both_submodules, start_only_submodules, end_only_submodules


class GithubChangeLog:
    """
    Class for generating a change log for a GitHub repository.
    """

    def __init__(self, github: Github, local_repo_root: str, cache_root: str) -> None:
        """
        Initialize a new GithubChangeLog instance.

        Args:
            github (Github): An instance of Github API client.
            local_repo_root (str): Path to the root directory of local repositories.
            cache_root (str): Path to the cache root directory.
        """
        self.github = github
        self.local_repo_root = local_repo_root
        self.cache_root = cache_root

    def get_change_log(  # noqa: C901
        self,
        owner: str,
        repo: str,
        start_ref: str,
        end_ref: str,
        pr_querydata: str,
        no_patch_if_no_submodules: True,
        follow_submodules: bool = True,
        specify_submodules: List[str] = None,
        commit_url_provider: Callable[[str, str, str], str] = None,
        issues_provider: Callable[[str, str], str] = None,
        no_submodule_entries_on_first_commit: bool = True,
        numstat_filepath_prefix: str = '',
        first_parent=False,
    ):
        """
        Retrieves the change log of a repository.

        Args:
            owner (str): The owner of the repository.
            repo (str): The repository name.
            start_ref (str): The starting reference point.
            end_ref (str): The ending reference point.
            no_patch_if_no_submodules (True): If true, no patch will be applied if there are no
                submodules.
            follow_submodules (bool, optional): If true, the function will follow submodule changes.
                Default is True.
            specify_submodules (List[str], optional): A list of specific submodules to consider.
                Default is None.
            commit_url_provider (Callable[[str, str, str], str], optional): Function that provides
                URL for a commit.

        Returns:
            list: A hierarchical change log of the repository.
        """
        logger.info(
            'Gathering changelog for "%s/%s" in range "%s..%s"',
            owner, repo, start_ref, end_ref,
        )
        if specify_submodules is None:
            specify_submodules = []

        ssh_url = self.github.get_repository(owner, repo, 'sshUrl').ssh_url

        start_submodules = self.github.get_submodules(
            owner, repo, start_ref, 'name subprojectCommitOid path gitUrl')
        end_submodules = self.github.get_submodules(
            owner, repo, end_ref, 'name subprojectCommitOid path gitUrl')

        has_submodules = any(start_submodules) or any(end_submodules)

        if has_submodules:
            patch = True
        else:
            patch = not no_patch_if_no_submodules

        local = os.path.join(self.local_repo_root, owner, repo)
        git = Git(
            local=local,
            remote=ssh_url,
            commit_url_provider=lambda sha: commit_url_provider(
                owner, repo, sha),
            issues_provider=issues_provider,
        )

        git.fetch()

        changelog = git.log_changelog(
            end_ref, start_ref, patch=patch,
            first_parent=first_parent)
        start_entry = git.show_changelog_entry(
            start_ref, patch=patch)
        start_entry.submodule_updates = {sub.path: SubmoduleUpdate(
            path=sub.path,
            from_sha=sub.subproject_commit_oid,
            to_sha=sub.subproject_commit_oid,
        ) for sub in start_submodules}
        if start_entry:
            changelog.append(start_entry)

        if not changelog:
            return changelog

        pr_query_start_datetime = changelog[-1].commit_date - \
            timedelta(minutes=1)
        pr_query_end_datetime = changelog[0].commit_date + timedelta(minutes=1)
        logger.info(
            'Gathering pull requests for "%s/%s" between time range "%s..%s"',
            owner, repo,
            pr_query_start_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            pr_query_end_datetime.strftime('%Y-%m-%d %H:%M:%S'),
        )
        pull_requests = self.github.search_pull_requests_merged_datetime_range(
            search_query=f'is:pr repo:{owner}/{repo} ',
            query_data=pr_querydata,
            start_datetime=pr_query_start_datetime,
            end_datetime=pr_query_end_datetime,
        )
        pull_request_map = {
            pr.merge_commit.oid: pr for pr in pull_requests}

        if numstat_filepath_prefix:
            assert numstat_filepath_prefix[-1] == '/', \
                'If "numstat_filepath_prefix" is set it must end in an "/"!'

        for entry in changelog:
            if entry.sha in pull_request_map:
                entry.integration_request = pull_request_map[entry.sha].to_integration_request(
                )

            for num_entry in entry.numstat:
                num_entry.path = numstat_filepath_prefix + num_entry.path

        # make it hierarchichal
        changelog = linear_log_to_hierarchy_log(changelog)

        if has_submodules and follow_submodules:
            both_submodules, _, _ = get_submodule_split(
                end_submodules, start_submodules)

            for submodule_start, submodule_end in both_submodules:
                submodule_name = submodule_start.git_url.split('/')[1]
                if submodule_name not in specify_submodules:
                    continue

                submodule_changelog = self.get_change_log(
                    owner=owner,
                    repo=submodule_name,
                    start_ref=submodule_start.subproject_commit_oid,
                    end_ref=submodule_end.subproject_commit_oid,
                    pr_querydata=pr_querydata,
                    no_patch_if_no_submodules=no_patch_if_no_submodules,
                    follow_submodules=follow_submodules,
                    specify_submodules=specify_submodules,
                    commit_url_provider=commit_url_provider,
                    issues_provider=issues_provider,
                    no_submodule_entries_on_first_commit=no_submodule_entries_on_first_commit,
                    numstat_filepath_prefix=numstat_filepath_prefix+submodule_start.path+'/',
                    first_parent=first_parent,
                )

                insert_submodule_updates(
                    changelog, submodule_start.path, submodule_changelog)

        if no_submodule_entries_on_first_commit:
            for submodule in changelog[-1].submodule_updates.values():
                submodule.entries = []

        return changelog
