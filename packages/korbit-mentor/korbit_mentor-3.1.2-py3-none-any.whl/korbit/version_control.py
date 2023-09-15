from pathlib import Path

import git


class BranchNotFound(Exception):
    def __init__(self, branch_name):
        super().__init__(f"Branch not found: {branch_name}")
        self.branch_name = branch_name


def branch_exists(repo: git.Repo, branch_name):
    return any(branch.name == branch_name for branch in repo.branches + repo.refs)


def get_diff_paths(repo_path: Path, compare_branch: str) -> list[str]:
    repo = git.Repo(repo_path)
    if not branch_exists(repo, compare_branch):
        raise BranchNotFound(compare_branch)
    compare_commit_head_hash = repo.git.rev_parse(compare_branch)
    current_commit_head_hash = repo.head.commit.hexsha
    diff = repo.git.diff(compare_commit_head_hash, current_commit_head_hash, name_only=True)
    return diff.split("\n") if diff else []
