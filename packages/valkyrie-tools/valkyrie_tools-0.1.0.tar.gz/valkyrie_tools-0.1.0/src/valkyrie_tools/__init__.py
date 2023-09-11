# src/valkyrie/__init__.py
import logging

from .__version__ import (  # noqa
    __author__,
    __author_email__,
    __build__,
    __copyright__,
    __description__,
    __hello__,
    __license__,
    __title__,
    __url__,
    __version__,
)

# logging formatting
log_message_format = "%%(message)s"
log_date_format = "%Y-%m-%d %H:%M:%S"
logging.getLogger(__name__).addHandler(logging.NullHandler())

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
# get basename of script and name is filename
# without extension
handler.setFormatter(logging.Formatter(log_message_format, log_date_format))
logger.addHandler(handler)
