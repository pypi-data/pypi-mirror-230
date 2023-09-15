import os
import subprocess
from pathlib import Path

import click

from todotree.Config import Config


# Addons https://click.palletsprojects.com/en/8.1.x/commands/#custom-multi-commands

class Addons:

    def __init__(self, config: Config = Config()):
        self.rv = []
        """List of programs."""

        self.default_config = config
        """Configuration"""

    def list(self):
        """List the addons detected."""
        rv = []
        if Path(self.default_config.addons_folder).exists():
            for filename in Path(self.default_config.addons_folder).iterdir():
                if os.access(filename, os.X_OK):
                    # Then the file is executable, add to the list.
                    rv.append(str(filename.parts[-1]))
            rv.sort()
        self.rv = rv
        return rv

    def run(self, name):
        """Run the addon with the name `name`."""
        file = Path(self.default_config.addons_folder / name)
        if not file.exists():
            raise FileNotFoundError
        result = subprocess.run([file, str(self.default_config.todo_file)], capture_output=True, text=True)
        return result
