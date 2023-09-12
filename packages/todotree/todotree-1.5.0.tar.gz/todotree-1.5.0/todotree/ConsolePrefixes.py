import click


class ConsolePrefixes:
    """Class for handling the prefixes in the terminal.

    The class is somewhat similar to a simple logger. It prints messages with a configured prefix.
    """

    def __init__(self, enable_colors: bool, console_good: str, console_warn: str, console_error: str):
        """
        Initialize a new Console Prefix.
        :param enable_colors: Whether to enable colors.
        :param console_good: The prefix for information messages.
        :param console_warn: The prefix for warning messages.
        :param console_error: The prefix for error messages.
        """
        self.enable_colors = enable_colors
        self.console_error = console_error
        self.console_warn = console_warn
        self.console_good = console_good

    def info(self, message):
        """
        Print an information message to console.
        :param message: The message.
        """
        self.__emit(self.console_good, 'green', message)

    def warning(self, message: str):
        """
        Print a warning message to the console.
        :param message: The message
        """
        self.__emit(self.console_warn, 'yellow', message)

    def error(self, message: str):
        """
        Print an error message to the console.
        :param message: The message to print.
        """
        self.__emit(self.console_error, 'red', message)

    def __emit(self, prefix: str, color: str, message: str):
        """
        Print a message with a prefix.
        :param prefix: The prefix of the message.
        :param message: The message itself.
        """
        # Emit the prefix.
        if self.enable_colors:
            click.secho(prefix, fg=color, nl=False)
        else:
            click.echo(prefix, nl=False)
        # Emit the message.
        click.echo(message)
