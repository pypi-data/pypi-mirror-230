import logging
from colorama import Style, Fore, Back
import time

DEFAULT_FORMATTER = "[%(asctime)s] %(levelname)s IN %(filename)s LINE %(lineno)s: \n%(message)s"

class Default(logging.Formatter):
    def __init__(self, fmt=DEFAULT_FORMATTER):
        logging.Formatter.__init__(self, fmt)


class Colorised(logging.Formatter):

    def __init__(self):
        logging.Formatter.__init__(self, "%(levelno)s: %(msg)s")


    def format(self, record):

        format_orig = self._fmt

        message = record.getMessage()
        created = self.converter(record.created)
        created = time.strftime(self.default_time_format, created)

        self._fmt = format_orig

        if record.levelno == logging.INFO:
            levelname = Fore.GREEN + "INFO" + Fore.RESET

        elif record.levelno == logging.ERROR:
            levelname = Fore.RED + "ERROR" + Fore.RESET

        elif record.levelno == logging.WARN:
            levelname = Fore.YELLOW + "WARNING" + Fore.RESET

        elif record.levelno == logging.CRITICAL:
            levelname = Back.RED + " CRITICAL " + Back.RESET
        
        elif record.levelno == logging.DEBUG:
            levelname = Fore.LIGHTBLACK_EX + "DEBUG" + Fore.RESET

        datetime = "[" + Style.DIM + created + Style.NORMAL + "]"

        filename = Fore.LIGHTYELLOW_EX + record.filename + Fore.RESET

        line = Fore.LIGHTYELLOW_EX + f"{record.lineno}" + Fore.RESET

        result = f"{datetime} {levelname} IN {filename} LINE {line}: \n{message}"

        return result
