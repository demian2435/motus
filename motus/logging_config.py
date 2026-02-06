"""Motus logging configuration powered by colorist."""

import logging

from colorist import BgColor, Color


class ColorFormatter(logging.Formatter):
    """Colorized formatter for Motus logs."""

    def __init__(self) -> None:
        """Configure level colors and reusable tokens."""
        super().__init__()
        self.reset = Color.OFF
        self.level_colors = {
            "DEBUG": Color.CYAN,
            "INFO": Color.GREEN,
            "WARNING": Color.YELLOW,
            "ERROR": Color.RED,
            "CRITICAL": BgColor.RED,
        }
        self.text = Color.WHITE
        self.file = f"{BgColor.MAGENTA}{Color.BLACK}"
        # Core modules highlighted with background for easy distinction
        self.file_core = f"{BgColor.CYAN}{Color.BLACK}"

    def format(self, record: logging.LogRecord) -> str:
        """Render a log record with ANSI colors."""
        lvl_color = self.level_colors.get(record.levelname, self.text)
        asctime = f"{self.text}{self.formatTime(record, self.datefmt)}{self.reset}"
        levelname = f"{lvl_color}{record.levelname}{self.reset}"
        name_color = self.file_core if record.name.startswith("motus.") else self.file
        name = f"{name_color}{record.name}{self.reset}"
        message = f"{self.text}{record.getMessage()}{self.reset}"
        return f"{asctime} | {levelname} | {name} | {message}"


def setup_logging() -> None:
    """Configure global logging for Motus."""
    handler = logging.StreamHandler()
    handler.setFormatter(ColorFormatter())
    logging.basicConfig(level=logging.INFO, handlers=[handler])
