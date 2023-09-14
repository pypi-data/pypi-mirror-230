"""Github GraphQL Objects"""

from __future__ import annotations
from datetime import datetime

from typing import List, Optional
from pydantic import root_validator, Field
from gitaudit.git.change_log_entry import IntegrationRequest
from .graphql_base import GraphQlBase


class GitActor(GraphQlBase):
    """Represents an actor in a Git commit (ie. an author or committer)."""

    name: Optional[str] = None
    email: Optional[str] = None
    date: Optional[datetime] = None


class Actor(GraphQlBase):
    """Represents an object which can
    take actions on GitHub. Typically a User or Bot."""

    login: Optional[str] = None


class Label(GraphQlBase):
    """A label for categorizing Issues, Pull Requests,
    Milestones, or Discussions with a given Repository."""

    name: Optional[str] = None
    color: Optional[str] = None
    id: Optional[str] = None


class Comment(GraphQlBase):
    """Represents a comment."""

    body: Optional[str] = None


class PullRequestReview(GraphQlBase):
    """A review object for a given pull request."""

    author: Optional[Actor] = None
    body: Optional[str] = None
    state: Optional[str] = None


class Submodule(GraphQlBase):
    """A submodule reference"""

    name: Optional[str] = None
    subproject_commit_oid: Optional[str] = None
    branch: Optional[str] = None
    git_url: Optional[str] = None
    path: Optional[str] = None


class Commit(GraphQlBase):
    """Represents a Git commit."""

    oid: Optional[str] = None
    additions: Optional[int] = None
    deletions: Optional[int] = None
    message: Optional[str] = None
    message_body: Optional[str] = None
    message_headline: Optional[str] = None
    author: Optional[GitActor] = None
    committed_date: Optional[datetime] = None


class PullRequest(GraphQlBase):
    """A repository pull request."""

    author: Optional[Actor] = None
    number: Optional[int] = None
    comments: Optional[List[Comment]] = Field(default_factory=list)
    commits: Optional[List[Commit]] = Field(default_factory=list)
    labels: Optional[List[Label]] = None
    base_ref_name: Optional[str] = None
    head_ref_name: Optional[str] = None
    merge_commit: Optional[Commit] = None
    body: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    id: Optional[str] = None
    repository: Optional[Repository] = None
    reviews: Optional[List[PullRequestReview]] = None

    @root_validator(pre=True)
    def unwrap_commit(cls, data: dict):  # pylint: disable=no-self-argument
        """Unwraps commits

        Args:
            data (dict): The to be validated input data

        Returns:
            dict: The valiated and transformed input data
        """
        if "commits" in data:
            if "nodes" in data["commits"]:
                data["commits"] = list(map(lambda x: x["commit"], data["commits"]["nodes"]))
            else:
                data["commits"] = list(map(lambda x: x["commit"], data["commits"]))
        return data

    def to_integration_request(self) -> IntegrationRequest:
        """Converts the pull request into a generic integration request.

        Returns:
            IntegrationRequest: The created integration request
        """
        return IntegrationRequest(
            owner=self.repository.owner.login,
            repo=self.repository.name,
            number=self.number,
            title=self.title,
            url=self.url,
        )


class Repository(GraphQlBase):
    """A repository contains the content for a project."""

    id: Optional[str] = None
    name: Optional[str] = None
    owner: Optional[Actor] = None
    pull_requests: Optional[List[PullRequest]] = Field(default_factory=list)
    name_with_owner: Optional[str] = None
    pull_request: Optional[PullRequest] = None
    ssh_url: Optional[str] = None


PullRequest.update_forward_refs()
