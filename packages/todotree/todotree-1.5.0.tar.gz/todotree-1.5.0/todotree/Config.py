from typing import Optional, Callable

from pathlib import Path

import xdg_base_dirs as xdg
import yaml

from todotree.ConsolePrefixes import ConsolePrefixes
from todotree.Errors import ConfigFileNotFound


class Config:
    """
    The configuration of todotree.

    For a user guide, please refer to the content in `examples/config.yaml` instead.
    Not all values are mapped 1-to-1.
    """

    def __init__(self):
        #  Main variables.
        self.todo_folder: Path = xdg.xdg_data_home() / "todotree"
        """
        Path to the folder containing the data files.
        
        Relative paths are calculated from the HOME folder. 
        """

        self.project_tree_folder: Path = xdg.xdg_data_home() / "todotree" / "projects"
        """
        Path to the folder containing the projects.
        Defaults to the XDG_DATA_DIR/todotree/projects if not set.
        """

        self.todo_file: Path = Path(self.todo_folder) / "todo.txt"
        """
        Path to the todo.txt file.
        """

        self.done_file: Path = Path(self.todo_folder) / "done.txt"
        """
        Path to the done.txt file.
        """

        self.config_file: Optional[Path] = None
        """
        Path to the config file.
        
        Defaults to None if not set.
        """

        self.addons_folder: Path = Path(self.todo_folder) / "addons"
        """
        Path to the addons folder.
        """

        self.git_mode: str = "None"
        """The mode that git runs in. 
        - None: disables it,
        - Local: add and commits automatically,
        - Full: also pulls and pushes to a remote repo.
        """

        # Features - Enables or disables certain features.
        self.quiet: bool = False
        """A value indicating whether to print anything except the output. Useful in scripts."""

        self.verbose: bool = False
        """A value indicating whether to print more detailed messages."""

        self.enable_wishlist_folder: bool = True
        """A value indicating whether to enable the wishlist folder functionality."""

        self.enable_project_folder: bool = True
        """A value indicating whether to enable the project folder functionality."""

        #  Localization. #
        self.wishlistName: str = "wishlist"
        self.noProjectString: str = "No Project"
        self.noContextString: str = "No Context"
        self.emptyProjectString: str = "> (A) Todo: add next todo for this."

        #  Status Decorators.
        self.console: ConsolePrefixes = ConsolePrefixes(True, ' * ', ' ! ', '!!!')

        # Tree prints.
        self.t_print: str = " ├──"
        self.l_print: str = " │  "
        self.s_print: str = " └──"
        self.e_print: str = "    "

        # Debug
        self.__yaml_object = None
        """Raw config object, for debugging."""

    def __str__(self):
        # Print each attribute in the list.
        s = "Configuration:\n"
        for item in self.__dict__:
            s += f"\t{item} = {self.__dict__[item]} \n"
        return s

    def read(self, path: Optional[Path] = None):
        """
        Loads the configuration from the given file at `path`.

        If empty, reads from default locations.
        """
        if path is not None:
            # print(f"Path is not None: {path}") # FUTURE: Verbose logging
            self.read_from_file(path)
            return
        # xdg compliant directory.
        if Path(xdg.xdg_config_home() / "todotree" / "config.yaml").exists():
            # print(f"Path is XDG Config") # FUTURE: Verbose logging
            self.read_from_file(Path(xdg.xdg_config_home() / "todotree" / "config.yaml"))
            return
        # xdg compliant directory if config file is considered "data".
        if Path(xdg.xdg_data_home() / "todotree" / "config.yaml").exists():
            # print(f"Path is XDG DATA") # FUTURE: Verbose logging
            self.read_from_file(Path(xdg.xdg_data_home() / "todotree" / "config.yaml"))
            return
        # No paths: use the defaults.
        return

    def read_from_file(self, file: Path):
        """Reads and parses yaml content from `file`."""
        self.config_file = file
        try:
            with open(file, 'r') as f:
                self._read_from_yaml(f.read())
        except FileNotFoundError as e:
            raise ConfigFileNotFound from e

    def _read_from_yaml(self, yaml_content: str):
        """Reads and overrides config settings defined in `yaml_content`."""
        # Convert yaml to python object.
        self.__yaml_object = yaml.safe_load(yaml_content)
        if self.__yaml_object is None:
            return
        # Map each item to the self config.
        self.__section('main', self.__section_main)
        self.__section('paths', self.__section_paths)
        self.__section('localization', self.__section_localization)
        self.__section('decorators', self.__section_decorators)
        self.__section('tree', self.__section_tree)

    def __section(self, section_name: str, section_parser: Callable):
        """
        Checks if the section exists and passes it to the sub parser.
        """
        if self.__yaml_object.get(section_name) is not None:
            if self.verbose:
                self.console.info(f"[{section_name}] section found, reading it.")
            # Parse the actual values.
            section_parser()
        elif self.verbose:
            self.console.warning(f"[{section_name}] section not found, skipping it.")

    def __section_tree(self):
        self.t_print = self.__yaml_object['tree'].get('t', self.t_print)
        self.l_print = self.__yaml_object['tree'].get('l', self.l_print)
        self.s_print = self.__yaml_object['tree'].get('s', self.s_print)
        self.e_print = self.__yaml_object['tree'].get('e', self.e_print)

    def __section_decorators(self):
        self.console = ConsolePrefixes(
            self.__yaml_object['decorators'].get('enable_colors', self.console.enable_colors),
            self.__yaml_object['decorators'].get('info', self.console.console_good),
            self.__yaml_object['decorators'].get('warning', self.console.console_warn),
            self.__yaml_object['decorators'].get('error', self.console.console_error))

    def __section_localization(self):
        self.emptyProjectString = self.__yaml_object['localization'].get('empty_project', self.emptyProjectString)
        self.wishlistName = self.__yaml_object['localization'].get('wishlist_name', self.wishlistName)
        self.noProjectString = self.__yaml_object['localization'].get('no_project', self.noProjectString)
        self.noContextString = self.__yaml_object['localization'].get('no_context', self.noContextString)

    def __section_paths(self):
        self.todo_folder = Path(self.__yaml_object['paths'].get('folder', self.todo_folder)).expanduser()
        self.todo_file = Path(
            self.__yaml_object['paths'].get('todo_file', Path(self.todo_folder) / "todo.txt")).expanduser()
        self.done_file = Path(
            self.__yaml_object['paths'].get('done_file', Path(self.todo_folder) / "done.txt")).expanduser()
        self.project_tree_folder = Path(
            self.__yaml_object['paths'].get('project_folder', self.project_tree_folder)).expanduser()
        self.addons_folder = Path(
            self.__yaml_object['paths'].get('addons_folder', self.addons_folder)).expanduser()

    def __section_main(self):
        self.enable_wishlist_folder = self.__yaml_object['main'].get('enable_wishlist_folder',
                                                                     self.enable_wishlist_folder)
        self.enable_project_folder = self.__yaml_object['main'].get('enable_project_folder',
                                                                    self.enable_project_folder)
        self.git_mode = self.__yaml_object['main'].get("git_mode", self.git_mode)
        self.quiet = self.__yaml_object['main'].get("quiet", self.quiet)
        self.verbose = self.__yaml_object['main'].get("verbose", self.verbose)
