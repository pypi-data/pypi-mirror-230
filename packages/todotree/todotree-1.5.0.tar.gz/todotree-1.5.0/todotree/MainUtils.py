from datetime import datetime, timedelta
from importlib.metadata import version
from pathlib import Path
from typing import Optional

import click
from git import Repo

from todotree.ConsolePrefixes import ConsolePrefixes
from todotree.Errors.ConfigFileNotFound import ConfigFileNotFound
from todotree.Config import Config


class MainUtils:
    """
    Class containing static methods which are useful in the main class.
    """

    @staticmethod
    def initialize(config_path: Optional[Path], done_file: Optional[Path], quiet: bool, config: Config,
                   todo_file: Optional[Path], verbose: bool):
        """
        Initializes the application and loads the configuration.
        :param config: The global configuration to modify.
        :param config_path: Path to the configuration file from the command line.
        :param done_file: Path to the configuration file from the command line.
        :param quiet: --quiet value
        :param todo_file: Path to the configuration file from the command line.
        :param verbose: --verbose value.
        """
        # parsing arguments.
        try:
            config.read(config_path)
        except ConfigFileNotFound as e:
            MainUtils.handle_config_file_not_found(e, config_path, verbose)

        if todo_file is not None:
            config.todo_file = Path(todo_file)
        if done_file is not None:
            config.done_file = Path(done_file)
        if verbose:
            config.verbose = True
        if quiet:
            config.quiet = True
            config.verbose = False
        # Git pull (if needed).
        MainUtils.git_pull(config)
        # Logging
        if config.verbose:
            config.console.info(f"Version of TodoTree: {version('todotree')}")
            config.console.info(f"Read configuration from {config.config_file}")
            config.console.info(f"The todo file is supposed to be at {config.todo_file}")
            config.console.info(f"The done file is supposed to be at {config.done_file}")

    @staticmethod
    def handle_config_file_not_found(e: BaseException, config_path: Optional[Path], verbose: bool):
        """Handle when the configuration file is not found.

        :param verbose: Whether to include additional information.
        :param config_path: The path where the file was not found.
        :param e: The exception raised.
        """
        # Gentoo style prefixes.
        cp = ConsolePrefixes(True, " * ", " * ", " * ")
        cp.warning(f"The config.yaml file could not be found at {config_path}.")
        if verbose:
            cp.warning(f"The config file should be located at {config_path}")
            cp.warning(str(e))
        cp.warning("The default options are now used.")

    @staticmethod
    def handle_todo_file_not_found(e: BaseException, config: Config):
        """Inform the user that the todo.txt was not found."""
        config.console.error("The todo.txt could not be found.")
        config.console.error(f"It searched at the following location: {config.todo_file}")
        if config.verbose:
            config.console.error(str(e))

    @staticmethod
    def handle_done_file_not_found(e: BaseException, config: Config):
        """Inform the user that the done.txt was not found."""
        config.console.error("The done.txt could not be found.")
        config.console.error(f"It searched at the following location: {config.done_file}")
        if config.verbose:
            click.echo(e)

    @staticmethod
    def commit_exit(action: str, config: Config):
        """
        Commit the files with git before exiting.

        :param config: The configuration.
        :param action: The name of the action, such as list or add.
        """
        if config.git_mode not in ["Local", "Full"]:
            exit()
        repo = Repo(config.todo_folder)

        if repo.is_dirty():
            # Git add.
            repo.index.add('*')

            # Git commit.
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_commit = repo.index.commit(message=time + " " + action)
            config.console.info(f"Commit added: [{new_commit.hexsha[0:7]}] {new_commit.message} ")
            config.console.info(f"{new_commit.stats.total['files']} file(s) changed, "
                                f"{new_commit.stats.total['insertions']} insertions(+) "
                                f"{new_commit.stats.total['deletions']} deletions(-).")

            if config.git_mode == "Full":
                # Git push.
                result = repo.remote().push()[0].summary
                config.console.info(f"Push successful: {result}")
        else:
            # git repo is not dirty, we do not have to commit anything.
            config.console.info("Nothing changed, nothing to commit or push.")

    @staticmethod
    def git_pull(config: Config):
        """
        Runs `git pull` on the todotree folder.

        - Does not pull if the previous pull time was less than five minutes ago.
        - Only pulls if git_mode = Full
        """
        if config.git_mode != "Full":
            return
        # Check last pull time.
        # Repo does not have a function to access FETCH_HEAD,
        # So this is done manually.
        fetch_head = config.todo_folder / ".git" / "FETCH_HEAD"

        if fetch_head.exists():
            # Then the repo has been pulled once in its lifetime.
            if datetime.fromtimestamp(fetch_head.stat().st_mtime) < datetime.now() + timedelta(minutes=5):
                # Then the repo is pulled fairly recently. Do not do anything.
                if config.verbose:
                    config.console.info("Repo was pulled recently. Not pulling.")
                return

        # Pull the repo
        config.console.info("Pulling latest changes.")
        config.console.info(Repo(config.todo_folder).remote().pull())
