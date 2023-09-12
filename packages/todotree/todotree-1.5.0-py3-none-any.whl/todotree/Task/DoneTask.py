from datetime import date

from todotree.Task.Task import Task


class DoneTask:

    @staticmethod
    def task_to_done(tsk):
        """
        Format the task String to a done state, by adding x 2020-02-02 in front of it.
        :param tsk: A task_string.
        :return: A done_string with a today's time stamp.
        """
        if type(tsk) == Task:  # Flatten to string
            tsk = tsk.task_string
        done = "x " + str(date.today()) + " " + tsk
        return done

    @staticmethod
    def task_to_undone(tsk):
        """
        Removes the x 2020-02-02 part so the task can be added to the task file list
        :param tsk: A done string.
        :return: A task string.
        """
        # 13 is the number of chars of "x 2020-02-02 "
        return str.strip(tsk[13:])
