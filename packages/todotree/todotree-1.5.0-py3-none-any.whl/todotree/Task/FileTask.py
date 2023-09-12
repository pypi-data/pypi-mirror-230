from todotree.Task.Task import Task


class FileTask(Task):
    """
    Task class for printing to a file.
    """

    def __init__(self, i: int, task_string: str):
        super().__init__(i, task_string)
