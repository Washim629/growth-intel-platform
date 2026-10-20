import logging
import sys
import time
from contextlib import contextmanager


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
    )
    # Keep third-party libraries quieter unless something goes wrong
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)


@contextmanager
def log_duration(logger: logging.Logger, label: str):
    start = time.time()
    try:
        yield
    finally:
        logger.info("%s completed in %.2fs", label, time.time() - start)
