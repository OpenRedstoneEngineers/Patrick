import logging
import sys


class StreamLogFormatter(logging.Formatter):
    """Log formatter for terminal streams. This class will format log messages to be more readable.
    The formats use ANSI codes for formatting.
    Each ANSI code starts with \x1b[ (ASCII escape code) and ends with m.
    The codes are separated by semicolons. For example, \x1b[31;1m is red text with bold font.
    The codes are as follows:
    - 0: reset
    - 1: bold
    - 2: dim
    - 3: italic
    - 4: underline
    - 9: strikethrough
    - 30: black text
    - 31: red text
    - 32: green text
    - 33: yellow text
    - 34: blue text
    - 35: magenta text
    - 36: cyan text
    - 37: white text
    - 40: black BG
    - 41: red BG
    - 42: green BG
    - 43: yellow BG
    - 44: blue BG
    - 45: magenta BG
    - 46: cyan BG
    - 47: white BG

    Each record also has format codes for the following:
    - %(name)s: The name of the logger
    - %(asctime)s: The human-readable time the log message was created
    - %(levelno)s: The numeric level of the log message
    - %(levelname)s: The level of the log message
    - %(filename)s: The name of the file the log message was created in
    - %(funcName)s: The name of the function the log message was created in
    These are just a few common ones. You can find the full list at https://docs.python.org/3/library/logging.html#logrecord-attributes
    """

    color_names = {
        logging.DEBUG: ("\x1b[30;47;1m", "DBUG"),
        logging.INFO: ("\x1b[36;1m", "INFO"),
        logging.WARNING: ("\x1b[33;1m", "WARN"),
        logging.ERROR: ("\x1b[31;1m", "EROR"),
        logging.CRITICAL: ("\x1b[37;41;1m", "CRIT"),
    }

    formats = {
        level: logging.Formatter(
            f"\x1b[0m\x1b[47;30;1m%(asctime)s\x1b[0m \x1b[37;1m%(name)s {color_name[0]}%(levelno)s {color_name[1]}\x1b[0m  \x1b[37;1m%(message)s"
        )
        for level, color_name in color_names.items()
    }

    def format(self, record):
        log_fmt = self.formats.get(record.levelno, self.formats[logging.INFO])

        if record.exc_info:
            text = log_fmt.formatException(record.exc_info)
            record.exc_text = f"\x1b[31m{text}\x1b[0m"

        record.exc_info = None

        return log_fmt.format(record)


class FileLogFormatter(logging.Formatter):
    """Log formatter for file streams. This class will format log messages to be more readable.
    Unlike the StreamLogFormatter, this class does not use ANSI codes for formatting.
    The formats use the same format as the StreamLogFormatter, but without the ANSI codes.
    """

    names = {
        logging.DEBUG: "DBUG",
        logging.INFO: "INFO",
        logging.WARNING: "WARN",
        logging.ERROR: "EROR",
        logging.CRITICAL: "CRIT",
    }

    formats = {
        level: logging.Formatter(
            f"%(asctime)s %(name)s %(levelno)s {name}  %(message)s"
        )
        for level, name in names.items()
    }

    def format(self, record):
        log_fmt = self.formats.get(record.levelno, self.formats[logging.INFO])

        if record.exc_info:
            text = log_fmt.formatException(record.exc_info)
            record.exc_text = f"{text}"

        record.exc_info = None

        return log_fmt.format(record)


def setup_logger(name, level=logging.INFO, logging_file="latest.log"):
    """Setup a logger with the given name and level."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(StreamLogFormatter())
    logger.addHandler(ch)

    if logging_file:
    # Create file handler
        fh = logging.FileHandler(logging_file, mode="w")
        fh.setLevel(level)
        fh.setFormatter(FileLogFormatter())
        logger.addHandler(fh)

    return logger
