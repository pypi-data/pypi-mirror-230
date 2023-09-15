from importlib.metadata import version
from pathlib import Path
from typing import Optional

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
            config.console.set_verbose()
        if quiet:
            config.console.set_quiet()
        # Git pull (if needed).
        config.git.git_pull()

        # Logging
        config.console.verbose(f"Version of TodoTree: {version('todotree')}")
        config.console.verbose(f"Read configuration from {config.config_file}")
        config.console.verbose(f"The todo file is supposed to be at {config.todo_file}")
        config.console.verbose(f"The done file is supposed to be at {config.done_file}")

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
        config.console.verbose(str(e))

    @staticmethod
    def handle_done_file_not_found(e: BaseException, config: Config):
        """Inform the user that the done.txt was not found."""
        config.console.error("The done.txt could not be found.")
        config.console.error(f"It searched at the following location: {config.done_file}")
        config.console.verbose(e)

