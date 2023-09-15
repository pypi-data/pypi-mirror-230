
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

from git import Repo, InvalidGitRepositoryError

from todotree.ConsolePrefixes import ConsolePrefixes
from todotree.Errors.GitError import GitError


class GitHandler:
    """
    Handles all git related functionality.
    """

    class GitModeEnum(Enum):
        disabled = 0
        """Git functionality is disabled."""
        local = 1
        """Add and commits automatically"""
        full = 2
        """Also pulls and pushes to a remote repo"""

    def __init__(self, new_git_mode: str, pull_time_minutes: int, todo_folder: Path, console: ConsolePrefixes):
        self.todo_folder = todo_folder
        self.console = console
        self.pull_time_minutes = pull_time_minutes
        self.git_mode = new_git_mode

    @property
    def git_mode(self):
        return self.__git_mode

    @git_mode.setter
    def git_mode(self, new_mode):
        self.__git_mode: GitHandler.GitModeEnum = GitHandler.GitModeEnum[new_mode.lower()]
        if self.__git_mode is not GitHandler.GitModeEnum.disabled:
            try:
                self.repo: Repo = Repo(self.todo_folder)
            except InvalidGitRepositoryError:
                self.console.error("Git repository is not initialized.")
                raise GitError

    def git_pull(self):
        """
        Runs `git pull` on the todotree folder.

        - Does not pull if the previous pull time recent.
        - Only pulls if git_mode = Full
        """
        if self.__git_mode != GitHandler.GitModeEnum.full:
            return
        # Check last pull time.
        # Repo does not have a function to access FETCH_HEAD,
        # So this is done manually.
        fetch_head = Path(self.repo.git_dir) / "FETCH_HEAD"

        if fetch_head.exists():
            # Then the repo has been pulled once in its lifetime.
            if (datetime.fromtimestamp(fetch_head.stat().st_mtime) >
                    datetime.now() + timedelta(minutes=self.pull_time_minutes)):
                # Then the repo is pulled fairly recently. Do not do anything.
                self.console.verbose(
                    f"Repo was pulled recently at {datetime.fromtimestamp(fetch_head.stat().st_mtime)}. Not pulling.")
                return
        else:
            self.console.info("Pulling git repo for the first time.")

        # Pull the repo
        self.console.info("Pulling latest changes.")
        try:
            Repo(self.todo_folder).remote()
        except ValueError as e:
            self.console.error("Error Pulling Changes.")
            self.console.error(e.args[0])
            self.console.error("Exiting the program.")
            raise GitError("Error Pulling changes, remote does not exist.")
        pull_result = self.repo.git.pull()
        self.console.info(pull_result)

    def commit_and_push(self, action: str):
        """
        Commit and push the files (if configured to do so).

        :param action: The name of the action, such as list or add.
        """
        if self.__git_mode is GitHandler.GitModeEnum.disabled:
            return

        if self.repo.is_dirty():
            self._commit(action)
            self._push()
        else:
            # git repo is not dirty, we do not have to commit anything.
            self.console.info("Nothing changed, nothing to commit or push.")

    def _push(self):
        if self.__git_mode is GitHandler.GitModeEnum.full:
            # Git push.
            result = self.repo.remote().push()
            result.raise_if_error()
            self.console.info(f"Push successful: {result[0].summary}")

    def _commit(self, action):
        self.repo.index.add('*')
        # Git commit.
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_commit = self.repo.index.commit(message=time + " " + action)
        self.console.info(f"Commit added: [{new_commit.hexsha[0:7]}] {new_commit.message} ")
        self.console.info(f"{new_commit.stats.total['files']} file(s) changed, "
                          f"{new_commit.stats.total['insertions']} insertions(+) "
                          f"{new_commit.stats.total['deletions']} deletions(-).")
