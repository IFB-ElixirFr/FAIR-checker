import logging
from colorlog import ColoredFormatter

logging.basicConfig(
    level=logging.DEBUG,
    force=True,
    format="%(log_color)s%(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logging.getLogger().handlers[0].setFormatter(
    ColoredFormatter(
        "%(log_color)s%(levelname)s: %(message)s",
        log_colors={
            "DEBUG": "fg_245",
            "INFO": "white",
            "WARNING": "yellow",
            "ERROR": "red",
        },
    )
)
