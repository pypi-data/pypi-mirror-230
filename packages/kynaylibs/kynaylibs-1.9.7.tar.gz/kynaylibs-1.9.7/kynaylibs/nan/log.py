import logging
from logging.handlers import RotatingFileHandler

LOG_FILE_NAME = "logs.txt"

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler(LOG_FILE_NAME, maxBytes=50000000, backupCount=10),
        logging.StreamHandler(),
    ],
)
logging.getLogger("asyncio").setLevel(logging.CRITICAL)
logging.getLogger("pytgcalls").setLevel(logging.WARNING)
logging.getLogger("kymang").setLevel(logging.WARNING)
logging.getLogger("kymang.client").setLevel(logging.WARNING)
logging.getLogger("kymang.session.auth").setLevel(logging.CRITICAL)
logging.getLogger("kymang.session.session").setLevel(logging.CRITICAL)
logging.basicConfig(level=logging.INFO)

LOG = logging.getLogger(__name__)


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
