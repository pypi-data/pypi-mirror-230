"""
This module contains several functions and classes for working with time
including parsing, measurement, estimation.
"""

from time import time
from functools import wraps
from datetime import datetime


def parse_date(s):
    """
    Converts string to date with the format "%Y-%m-%d".
    """
    return datetime.strptime(s, "%Y-%m-%d").date()


def parse_datetime(s):
    """
    Converts string to datetime with the format "%Y-%m-%d %H:%M:%S".
    """
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")


def stringify_date(dt):
    """
    Converts date to string with the format "%Y-%m-%d".
    """
    return dt.strftime('%Y-%m-%d')


def stringify_datetime(dt):
    """
    Converts datetime to string with the format "%Y-%m-%d %H:%M:%S".
    """
    return dt.strftime('%Y-%m-%d %H:%M:%S')


class Meter:
    """
    This class describes an object that measures time of a section of the code.
    It can be used as a context manager as well.

    Example:

        with Meter() as tm:
            ...
        print("Time:", tm.duration())
    """

    def __init__(self):
        self._start = None
        self._stop = None

    def duration(self):
        """
        Returns measured duration.
        """
        return self._stop - self._start

    def reset(self):
        """
        Sets the object to the initial state
        """
        self._start = None
        self._stop = None

    def start(self):
        """
        Starts measurement.
        """
        self._start = time()

    def stop(self):
        """
        Stops measurement.
        """
        self._stop = time()

    def __enter__(self):
        self.reset()
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    @classmethod
    def as_decorator(cls, func):
        """
        A decorator that measures the duration of the execution of a function.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            meter = cls()
            with meter:
                result = func(*args, **kwargs)
            print(f"Time: {meter.duration()} sec")
            return result
        return wrapper


class Estimator:
    """
    A class that represents an approach to estimate the duration
    of the execution of a long loop.

    Example:

        with Estimator(total=100) as te:
            for i in range(100):
                ...
                te.send()
    """

    FORMAT = "Done {counter} of {total}. It takes: {duration}. " \
             "It took: {spent}. It finishes in {left}, at {finish}."

    def __init__(self, total, period=1):
        self._total = total
        self._period = period
        self._start = None
        self._stop = None
        self._counter = None
        self._state_line = None

    def reset(self):
        """
        Sets the object to the initial state.
        """
        self._start = None
        self._stop = None
        self._counter = 0
        self._last_line = ""

    def __enter__(self):
        self.reset()
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finish()

    def start(self):
        """
        Starts estimation.
        """
        self._start = time()

    def finish(self):
        """
        Finishes estimation.
        """
        self._stop = time()
        self._print_completed_line()

    def send(self, count=1):
        """
        Sends the number of the new executed iterations.
        """
        self._counter += count
        if self._counter % self._period == 0:
            self._print_state_line()

    def print(self, *args, sep=" "):
        """
        As far as the object keeps a special line that is being updated
        all the time, there is a special function that prints correctly.
        Standard 'print' will break the output.
        """
        line = sep.join(map(str, args))
        state_line = self._last_line
        self._print_line(line, new_line=True)
        self._print_line(state_line)

    def _get_state(self):
        now = time()
        spent = now - self._start
        duration = spent * self._total / self._counter
        return {
            'duration': duration,
            'spent': spent,
            'left': duration - spent,
            'finish': datetime.fromtimestamp(self._start + duration),
        }

    def _print_line(self, line, new_line=False):
        print(
            '\r' + line + " " * max(len(self._last_line) - len(line), 0),
            end='\n' if new_line else ''
        )
        self._last_line = "" if new_line else line

    def _print_state_line(self):
        state = self._get_state()
        line = self.FORMAT.format(
            counter=self._counter,
            total=self._total,
            duration=self._prettify_duration(state['duration']),
            spent=self._prettify_duration(state['spent']),
            left=self._prettify_duration(state['left']),
            finish=state['finish'].strftime("%Y-%m-%d %H:%M:%S"),
        )
        self._print_line(line)

    def _print_completed_line(self):
        state = self._get_state()
        line = f"Completed. It took: " \
               f"{self._prettify_duration(state['duration'])}."
        self._print_line(line, new_line=True)

    @classmethod
    def _prettify_duration(cls, duration):
        t = int(duration)
        t, s = divmod(t, 60)
        t, m = divmod(t, 60)
        t, h = divmod(t, 24)
        y, d = divmod(t, 365)
        lst = (
            f"{y}y" if y else "",
            f"{d}d" if d else "",
            f"{h}h" if h else "",
            f"{m}m" if m else "",
            f"{s}s",
        )
        return " ".join(filter(lambda x: x, lst))
