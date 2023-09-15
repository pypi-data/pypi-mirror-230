import datetime
import os.path
from pathlib import Path
from djangouniversallogger.utils import load_logs_dir


class Logger:
    """If a log file for today already exist, open it in append mode.
    Else, create a new log file for today, and open it in append mode.
    """
    DEBUG = False
    PADDING = 10
    FORMAT = f"|{{type:{{PADDING}}}}|{{datetime:%I:%M:%S.%f %z %Z (%c)}}|\n{{msg}}\n/////\n"

    def __init__(self, name, debug: bool = False, padding: int = None, format_: str = None, splitter: str = None,
                 logs_dir: Path = None):
        if splitter is None:
            splitter = '.'

        if logs_dir is None:
            my_dir = load_logs_dir()
        else:
            my_dir: str = str(logs_dir)
        if not os.path.exists(my_dir):
            os.makedirs(my_dir)
        for part in name.split(splitter):
            my_dir = os.path.join(my_dir, part)
            if not os.path.exists(my_dir):
                os.makedirs(my_dir)
        self.dir = my_dir
        self.DEBUG = debug
        if padding is not None:
            self.PADDING = padding
        if not (format_ is None):
            self.FORMAT = format_.format(self.PADDING)

    def __format(self, level, msg):
        return f"|{{type:{self.PADDING}}}|{{datetime:%I:%M:%S.%f %z %Z (%c)}}| {{msg}}\n".format(
            type=level,
            msg=msg,
            datetime=datetime.datetime.now(),
        )

    @property
    def file_name(self):
        year_dir = os.path.join(self.dir,  str(datetime.date.today().year))
        if not os.path.exists(year_dir):
            os.makedirs(year_dir)
        month_dir = os.path.join(year_dir, str(datetime.date.today().strftime('%m')))
        if not os.path.exists(month_dir):
            os.makedirs(month_dir)
        return os.path.join(month_dir, f'logs-{datetime.date.today().strftime("%d")}.log')

    def log(self, msg, level):
        if not self.DEBUG and level == "DEBUG":
            return
        with open(self.file_name, "a+") as file:
            file.write(self.__format(level, msg,))

    def info(self, msg):
        """Log info"""
        self.log(msg, "INFO")

    def update(self, msg):
        """Used to log whenever a state is updated"""
        self.log(msg, "UPDATE")

    def exception(self, msg):
        """Used to log when an exception is caught"""
        self.log(msg, "EXCEPTION")

    def debug(self, msg):
        """Only logs if the static variable {DEBUG} is set to True."""
        self.log(msg, "DEBUG")
