import datetime
import re
from datetime import datetime, date, timedelta

from typing import List, Optional

from dateutil.utils import today

from todotree.Errors.TaskParseError import TaskParseError


class Task:
    """
    Base class that reads from a task from a file.
    """

    t_date_pattern = re.compile(r"t:(\d{4})-(\d{2})-(\d{2})\s?")
    """Regex pattern which defines t:dates in a task string."""

    project_pattern = re.compile(r"\+\S+\s?")
    """Regex pattern which defines projects in a task string."""

    context_pattern = re.compile(r"@\w+\s?")
    """Regex pattern which defines contexts in a task string."""

    priority_pattern = re.compile(r"^\([a-zA-Z]\)\s?")
    """Regex pattern which defines the priority in a task string."""

    due_date_pattern = re.compile(r"due:(\d{4})-(\d{2})-(\d{2})\s?")
    """Regex pattern which defines due dates in a string.
    
    The format is due:yyyy-mm-dd.
    This is a due date for a single time.
    """

    due_month_pattern = re.compile(r"duy:(\d{2})-(\d{2})\s?")
    """Regex pattern which defines dum dates in a string.

    The format is due:mm-dd.
    This is a due date which recurs each year.
    
    An example case would be doing taxes. Each year you have to them before a certain date.
    """

    due_day_pattern = re.compile(r"dum:(\d{2})\s?")
    """Regex pattern which defines dum dates in a string.

    The format is due:dd.
    This is a due date for a deadline which recurs each month.
    """

    block_pattern = re.compile(r"(bl:)(\w+)\s?")
    """Regex pattern which defines a block key. format: bl:string"""

    blocked_by_pattern = re.compile(r"(by:)(\w+)\s?")
    """Regex pattern which defines a blocked by key. format: by:string"""

    @property
    def t_date(self) -> Optional[date]:
        """Property which returns the latest t date of the task."""
        return max(self.t_date_all) if len(self.t_date_all) > 0 else None
    # FUTURE: t_date Setter.

    @property
    def due_date(self) -> Optional[date]:
        """Property which returns the earliest due date."""
        return min(self.due_date_all) if len(self.due_date_all) > 0 else None
    # FUTURE: due_date setter. https://mathspp.com/blog/pydonts/properties

    @property
    def due_date_band(self) -> str:
        """
        Property which returns the time until the due date lapses in human-readable language.
        """
        if self.due_date is None:
            return "No due date."
        # List with options.
        difference = self.due_date - datetime.today().date()
        if difference < timedelta(days=0):
            return "Overdue"
        if difference < timedelta(days=1):
            return "Due today"
        if difference < timedelta(days=2):
            return "Due tomorrow"
        if difference < timedelta(days=7):
            return "Due in the next 7 days"
        return "Due date further than the next 7 days"

    @property
    def priority(self) -> int:
        """
        Property which defines the priority of a `Task` as an integer.
        """
        return ord(self.priority_string.upper()) - 65 if self.priority_string != "" else 684

    def __init__(self, i: int, task_string: str):
        """
        Initializes a single task from a string.
        :param i: The task number.
        :param task_string: The string containing the task.
        """

        self.t_date_all: List[datetime.date] = []
        """All t dates of a task."""

        self.due_date_all: List[datetime.date] = []
        """All due dates of a task"""

        self.task_string: str = ""
        """raw un formatted string"""

        self.other_string: str = task_string
        """String containing any part which is not captured in another variable."""

        self.i: int = i
        """Task Number"""

        self.priority_string: str = ""  # FUTURE: Convert to property instead.
        """priority as a String."""

        self.projects: List[str] = []
        """List of all projects"""

        self.contexts: List[str] = []
        """List of all contexts"""

        self.blocks: List[str] = []
        """List of all block identifiers."""

        self.blocked: List[str] = []
        """List of all blocked by identifiers"""

        # Parse the various properties from the task.
        if task_string:  # task is not empty
            self.task_string = task_string.strip()  # Remove whitespace and the \n.
            self.write_string = task_string

            # Parse the various items.
            self.__parse_priority(task_string)

            self.__parse_project(task_string)
            self.__parse_context(task_string)
            self.__parse_t_date(task_string)
            self.__parse_due_date(task_string)
            self.__parse_due_month(task_string)
            self.__parse_due_day(task_string)
            self.__parse_block_list(task_string)
            self.__parse_blocked_by_list(task_string)

            # Final cleanup of other_string.
            self.other_string = self.other_string.strip()

    def __parse_priority(self, task_string):
        """
        Parse the priority from the `task_string`.
        """
        if self.priority_pattern.match(task_string):
            with_parentheses = self.priority_pattern.match(task_string).group(0)
            self.priority_string = with_parentheses[1]
            self.other_string = self.priority_pattern.sub("", self.other_string).lstrip()

    def __parse_project(self, task_string):
        """
        Parse the projects from the `task_string`.
        """
        if self.project_pattern.search(task_string):
            projects_with_plus = self.project_pattern.findall(task_string)
            for p in projects_with_plus:
                # strip is for the trailing whitespace.
                self.projects.append(re.sub(r"\+", "", p).strip())
        self.other_string = self.project_pattern.sub("", self.other_string)

    def __parse_context(self, task_string):
        """
        Parse the contexts from the `task_string`.
        """
        if self.context_pattern.search(task_string):
            context_with_at = self.context_pattern.findall(task_string)
            for c in context_with_at:
                self.contexts.append(re.sub(r"@", "", c).strip())
        self.other_string = self.context_pattern.sub("", self.other_string)

    def __parse_t_date(self, task_string):
        """
        Parse the t_dates from the `task_string`.
        """
        for year, month, day in self.t_date_pattern.findall(task_string):
            try:
                # Add t:date to the t date list.
                self.t_date_all.append(datetime(int(year), int(month), int(day)).date())
            except ValueError:
                raise TaskParseError(f"This task has an incorrect t:date.{year}-{month}-{day}")
        self.other_string = self.t_date_pattern.sub("", self.other_string)

    def __parse_due_date(self, task_string):
        """
        Parse the due date from the `task_string`.
        """
        for year, month, day in self.due_date_pattern.findall(task_string):
            try:
                self.due_date_all.append(datetime(int(year), int(month), int(day)).date())
            except ValueError:
                raise TaskParseError(f"This task has an incorrect due:date. date: {year}-{month}-{day}")
        self.other_string = self.due_date_pattern.sub("", self.other_string)

    def __parse_due_month(self, task_string):
        """
        Parse the dum date from the `task_string`.
        """
        for month, day in self.due_month_pattern.findall(task_string):
            try:
                date_next_year = datetime(datetime.today().year + 1, int(month), int(day))
                if date_next_year - today() < timedelta(weeks=4):
                    self.due_date_all.append(date_next_year.date())
                else:
                    self.due_date_all.append(datetime(datetime.today().year, int(month), int(day)).date())
            except ValueError:
                raise TaskParseError(f"This task has an incorrect dum:date. date: {month} {day}")
        self.other_string = self.due_month_pattern.sub("", self.other_string)

    def __parse_due_day(self, task_string):
        """
        Parses the duy date from `task_string`.
        """
        for day in self.due_day_pattern.findall(task_string):
            try:
                date_next_month = datetime(datetime.today().year, datetime.today().month + 1, int(day))
                if date_next_month - today() < timedelta(days=7):
                    # The deadline in the next month is less than 7 days away.
                    self.due_date_all.append(date_next_month.date())
                else:
                    self.due_date_all.append(datetime(datetime.today().year, datetime.today().month, int(day)).date())
            except ValueError:
                raise TaskParseError(f"This task has an incorrect duy:date.")
        self.other_string = self.due_day_pattern.sub("", self.other_string)

    def __parse_blocked_by_list(self, task_string):
        """
        Parse the blocked by list.
        """
        for blocked_item in self.blocked_by_pattern.finditer(task_string):
            self.blocked.append(str(blocked_item.group(2)))
        self.other_string = self.blocked_by_pattern.sub("", self.other_string)

    def __parse_block_list(self, task_string):
        """
        Parse the block list.
        """
        for item in self.block_pattern.finditer(task_string):
            self.blocks.append(str(item.group(2)))
        self.other_string = self.block_pattern.sub("", self.other_string)

    def add_or_update_priority(self, new_priority: str) -> bool:
        """
        Adds or updates the priority.
        :param new_priority: the new priority
        :return: A value indicating whether it was added or updated.
        True means it was added. False that it was updated.
        """
        if self.priority < 600:
            # Then there is already a priority defined.
            self.priority_string = new_priority
            self.task_string = self.priority_pattern.sub("(" + new_priority + ")", self.task_string)
            return False
        else:
            # There was no priority defined.
            self.priority_string = new_priority
            self.task_string = "(" + new_priority + ") " + self.task_string
            return True

    def add_or_update_due(self, new_due: datetime) -> bool:
        """
        Updates the due date, or adds it if it does not exist.
        :param new_due: the new due date.
        :return: True if it was added. False if the due date is updated.
        """
        if self.due_date < datetime(9999, 12, 31).date():
            # There already are due dates, check if this is the closest to now.
            self.task_string = self.due_date_pattern.sub(
                "due:" + new_due.strftime("%Y-%m-%d"), self.task_string
            )
            return False
        # There was no due_date, substitute the default.
        self.task_string += " due:" + new_due.strftime("%Y-%m-%d")
        return True

    def add_or_update_t_date(self, new_t_date: str):
        """
        Adds or updates the t:date
        :param new_t_date: The new `t_date` in the format yyyy-mm-dd.
        """
        if self.t_date is not None:
            self.task_string = self.t_date_pattern.sub("t:" + new_t_date, self.task_string)
        else:
            self.task_string += " t:" + new_t_date

    def __add__(self, other):
        """
        :param other: the string or task to append to this task.
        """
        if isinstance(other, str):
            return Task(self.i, self.task_string + " " + other.strip())
        if isinstance(other, Task):
            return Task(self.i, self.task_string + " " + other.task_string)
        return NotImplemented

    def __str__(self):
        prefix = self.i if self.i > 0 else ""
        task = self.task_string
        return str(prefix) + " " + task
