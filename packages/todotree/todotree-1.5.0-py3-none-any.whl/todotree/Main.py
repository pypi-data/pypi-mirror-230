# using Click implementation
import re
import subprocess

from pathlib import Path
from typing import List, Optional, Tuple

import click  # CLI magic

from todotree.Addons import Addons
from todotree.Errors.TodoFileNotFound import TodoFileNotFound
from todotree.Errors.DoneFileNotFound import DoneFileNotFound
from todotree.Task.DoneTask import DoneTask
from todotree.Taskmanager import Taskmanager
from todotree.Config import Config
from todotree.MainUtils import MainUtils

# GLOBALS. #
config = Config()
addons = Addons(config)
taskManager = Taskmanager(config)


# Click Replaces:
# Argparse
#
# NOTE: this file cannot be in a class. See: https://github.com/pallets/click/issues/601
# But context and variable ferrying can be done using the context option.
# We just call the context 'self' and hope the issue does resolve itself.
# https://click.palletsprojects.com/en/8.1.x/commands/#nested-handling-and-contexts


@click.group()
@click.option('--config-path', default=None, help="Path to the configuration file.")
@click.option('--todo-file', default=None, help="Path to the todo.txt file, overrides --config.")
@click.option('--done-file', default=None, help="Path to the done.txt file, overrides --config.")
@click.option('--verbose', is_flag=True, help="Increases verbosity in messages.", is_eager=True)
@click.option('--quiet', is_flag=True, help="Do not print messages, only output. Useful in scripts.",
              is_eager=True)
def root(config_path: Optional[Path], todo_file: Optional[Path], done_file: Optional[Path],
         verbose: bool, quiet: bool):
    """
    The main list of todotree's command.

    Options must be before the actual argument,
    so `todotree --verbose list` will work, but `todotree list --verbose` will not.
    """
    # ^ This text also shows up in the help command.
    # Root click group. This manages all the command line interactions.
    # ensure that ctx.obj exists and is a dict
    config.verbose = False  # FUTURE: Fix properly.
    MainUtils.initialize(config_path, done_file, quiet, config, todo_file, verbose)
    # Pass to another command.
    pass


@root.command('add', short_help='Add a task to the task list')
@click.argument('task', type=str, nargs=-1)
def add(task: Tuple):
    # Convert tuple to string
    task: str = " ".join(map(str, task))
    try:
        # Disable fancy imports, because they are not needed.
        config.enable_project_folder = False
        # Import tasks.
        taskManager.import_tasks()
        # Add task
        new_number = taskManager.add_task_to_file(task.strip() + "\n")
        config.console.info("Task added:")
        click.echo(f"{new_number} {task}")
        MainUtils.commit_exit("add", config)
    except TodoFileNotFound as e:
        MainUtils.handle_todo_file_not_found(e, config)
        exit(1)


@root.command('addx', short_help='Add a task and immediately mark it as done')
@click.argument('task', type=str, nargs=-1)
def add_x(task: Tuple):
    """
    Adds a completed task to done.txt. The task is not added to todo.txt.
    :param task: The task to add to done.txt.
    """
    try:
        done = DoneTask.task_to_done(" ".join(map(str, task)))
        with config.done_file.open("a") as f:
            f.write(done)
        click.echo(done)
    except FileNotFoundError as e:
        MainUtils.handle_done_file_not_found(e, config)
        exit(1)


@root.command('append', short_help='append `append_string` to `task_nr`')
@click.argument('task_nr', type=int)
@click.argument('append_string', type=str, nargs=-1)
def append(task_nr: int, append_string: Tuple[str]):
    """
    Appends the contents of append_string to the task represented by task_nr.
    A space is inserted between the two tasks, so you do not have to worry that words aretogether.
    """
    # Disable fancy imports, because they are not needed.
    config.enable_project_folder = False
    # Import tasks.
    try:
        taskManager.import_tasks()
    except TodoFileNotFound as e:
        MainUtils.handle_todo_file_not_found(e, config)
        exit(1)
    # Convert tuple to string.
    append_string = " ".join(append_string)

    # Append task.
    config.console.info("The new task is: ")
    click.echo(taskManager.append_to_task(task_nr, append_string.strip()))
    MainUtils.commit_exit("append", config)


@root.command('context', short_help='list task in a tree, by context')
def context():
    """list a tree, of which the first node is the context, the second nodes are the tasks"""
    try:
        taskManager.import_tasks()
    except TodoFileNotFound as e:
        MainUtils.handle_todo_file_not_found(e, config)
        exit(1)
    click.echo(taskManager.print_context_tree())
    exit()


@root.command('cd', short_help='print directory of the todo.txt directory')
def cd():
    """print directory of the todo.txt directory"""
    config_path: Path = Path(config.todo_folder)
    if config.verbose:
        config.console.info("The location to the data folder is: ")

    if config_path.is_absolute():
        # Then the configured path is printed.
        click.echo(str(config_path))
        exit()
    # Then the relative path is resolved to be absolute.
    base_path: Path = Path.home()
    full_path: Path = base_path / config_path
    click.echo(str(full_path))
    exit()


@root.command('do', short_help='mark task as done and move it to the done.txt')
@click.argument('task_numbers', type=list, nargs=-1)  # type=list[int]
def do(task_numbers: List[Tuple]):
    """
    Mark tasks as done, therefor moving them to done.txt with a date stamp of today.
    :param task_numbers: The list of tasks which are completed.
    """
    # Convert to ints. Task numbers is a list of tuples. Each tuple contains one digit of the number.
    new_numbers: List[int] = []
    for task_tuple in task_numbers:
        new_number: str = ""
        for task_digit in task_tuple:
            new_number += task_digit
        new_numbers.append(int(new_number))
    # Write back to old value.
    task_numbers = new_numbers
    # Marking something as Done cannot be done with fancy imports
    # So we disable them.
    config.enable_project_folder = False
    try:
        taskManager.import_tasks()
    except TodoFileNotFound as e:
        MainUtils.handle_todo_file_not_found(e, config)
        exit(1)
    try:
        completed_tasks = taskManager.mark_as_done(task_numbers)
    except DoneFileNotFound as e:
        MainUtils.handle_done_file_not_found(e, config)
        exit(1)
    # Print the results
    config.console.info("Tasks marked as done:")
    for task in completed_tasks:
        click.echo(task)
    MainUtils.commit_exit("do", config)


@root.command('due', short_help='List tasks by their due date')
def due():
    """List tasks in a tree by their due date."""
    # Disable fancy imports, because they do not have due dates.
    config.enable_project_folder = False
    # Import tasks.
    try:
        taskManager.import_tasks()
    except TodoFileNotFound as e:
        MainUtils.handle_todo_file_not_found(e, config)
        exit(1)
    # Print due tree.
    click.echo(taskManager.print_by_due())
    exit()


@root.command('edit', short_help='open the todo.txt in an editor.')
def edit():
    """
    Open the todo.txt in an editor for manual editing of tasks.
    This is useful when you need to modify a lot of tasks, which would be complicated when doing it with todotree.
    """
    # Disable fancy imports.
    config.enable_project_folder = False
    click.edit(filename=str(config.todo_file))
    MainUtils.commit_exit("edit", config)


@root.command('filter', short_help='only show tasks containing the search term.')
@click.argument('search_term')
def filter_list(search_term):
    """
    Only show tasks which have search term in them. This can also be a keyword.

    :param search_term: The term to search.
    """
    try:
        taskManager.import_tasks()
    except TodoFileNotFound as e:
        MainUtils.handle_todo_file_not_found(e, config)
        exit(1)

    if config.verbose:
        config.console.info("The todo list is:")
    elif not config.quiet:
        config.console.info("Todos")

    taskManager.filter_by_string(search_term)
    click.echo(taskManager)


@root.command('list', short_help='List tasks')
def list_tasks():
    """
    Print a flat list of tasks, sorted by their priority.
    """
    try:
        taskManager.import_tasks()
    except TodoFileNotFound as e:
        MainUtils.handle_todo_file_not_found(e, config)
        exit(1)

    if config.verbose:
        config.console.info("The todo list is:")
    elif not config.quiet:
        config.console.info("Todos")

    click.echo(taskManager)


@root.command('list_done', short_help='List tasks which are marked as done')
def list_done():
    """
    List tasks which are marked as done. The numbers can be used with the revive command.
    """
    try:
        taskManager.list_done()
    except DoneFileNotFound as e:
        MainUtils.handle_done_file_not_found(e, config)
        exit(1)


@root.command('print_raw', short_help='print todo.txt without any formatting or filtering')
def print_raw():
    """
    Output the todo.txt without any processing.
    This is equivalent to `cat $(todo cd)/todo.txt` in bash.
    """
    try:
        with open(taskManager.config.todo_file, "r") as f:
            click.echo(f.read())
    except FileNotFoundError as e:
        MainUtils.handle_todo_file_not_found(e, config)


@root.command('priority', short_help='set new priority to task')
@click.argument('task_number', type=int)
@click.argument('new_priority', type=str)
def priority(task_number, new_priority):
    """
    Adds or updates the priority of the task.
    :param task_number: The task to re-prioritize.
    :param new_priority: The new priority.
    """
    # Disable fancy imports.
    config.enable_project_folder = False
    # Run task.
    try:
        taskManager.import_tasks()
    except TodoFileNotFound as e:
        MainUtils.handle_todo_file_not_found(e, config)
        exit(1)
    taskManager.add_or_update_priority(
        priority=(new_priority.upper()), task_number=task_number)


@root.command('project', short_help='print tree by project')
def project():
    # Import tasks.
    try:
        taskManager.import_tasks()
    except TodoFileNotFound as e:
        MainUtils.handle_todo_file_not_found(e, config)
        exit(1)
    # Print due tree.
    click.echo(taskManager.print_project_tree())
    exit()


@root.command('revive', short_help='Revive a task that was accidentally marked as done.')
@click.argument('done_number', type=int)
def revive(done_number):
    """
    Move a task from done.txt to todo.txt.
    The `done_number` can be found using the `list_done` command.
    :param done_number: The number of the task to revive.
    """
    try:
        click.echo(taskManager.revive_task(done_number))
    except TodoFileNotFound as e:
        MainUtils.handle_todo_file_not_found(e, config)
        exit(1)
    except DoneFileNotFound as e:
        MainUtils.handle_done_file_not_found(e, config)
        exit(1)
    MainUtils.commit_exit("revive", config)


@root.command('schedule', short_help='hide task until date.')
@click.argument('task_number', type=int)
@click.argument('new_date', type=str, nargs=-1)
def schedule(task_number: int, new_date: Tuple[str]):
    """
    hide the task until the date given. If new_date is not in ISO format (yyyy-mm-dd) such as "Next Wednesday",
    then it tries to figure out the date with the `date` program, which is only in linux.
    """
    # Disable fancy imports, because they do not have t dates.
    config.enable_project_folder = False
    # Convert
    date = " ".join(new_date)
    date_pattern = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
    if not date_pattern.match(date):
        if config.verbose:
            config.console.info(f"Attempt to parse {date} with the `date` program.")
        # Try to use the `date` utility.
        dat = subprocess.run(
            ["date", "-d " + date, "+%F "],
            capture_output=True,
            encoding="utf-8"
        )
        if dat.returncode > 0:
            config.console.error(f"The date {new_date} could not be parsed.")
            exit(1)
        date = dat.stdout.strip()
    try:
        taskManager.import_tasks()
        config.console.info(f"Task {task_number} hidden until {date}")
        updated_task = taskManager.add_or_update_t_date(date, task_number)
        config.console.info(str(updated_task))
    except TodoFileNotFound as e:
        MainUtils.handle_todo_file_not_found(e, config)
        exit(1)

    MainUtils.commit_exit("schedule", config)


@root.command('addons', short_help='Run an addon script')
@click.argument('command', type=str)
def addons_command(command: str):
    """
    Run an addon script.
    The script must be in the addons_folder. It can be any language you like: It does not have to be python.
    However, it must have the executable bit set.

    :param command: The script/command to run.
    """
    try:
        result = Addons(config).run(command)
    except FileNotFoundError:
        config.console.error(f"There is no script at {Path(config.addons_folder / command)}")
        exit(1)
    click.echo(result.stdout, nl=False)
    if result.returncode != 0:
        click.echo(result.stderr)
    MainUtils.commit_exit(f"addons {command}", config)


#  End Region Command Definitions.
#  Setup Click

CONTEXT_SETTINGS: dict = dict(help_option_names=['-h', '--help'])
"""Click context settings. See https://click.palletsprojects.com/en/8.1.x/complex/ for more information."""
cli: click.CommandCollection = click.CommandCollection(
    sources=[root],
    context_settings=CONTEXT_SETTINGS
)
"""Command Collection defining defaults. https://click.palletsprojects.com/en/8.1.x/api/#click.CommandCollection ."""

if __name__ == '__main__':
    cli()
