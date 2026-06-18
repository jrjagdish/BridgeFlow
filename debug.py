import logging
import os

logger = logging.getLogger("vault")
logger.setLevel(logging.DEBUG)
logger.propagate = False

_fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

_console = logging.StreamHandler()
_console.setLevel(logging.INFO)
_console.setFormatter(_fmt)
logger.addHandler(_console)


def _add_file_handler(path: str, level: int) -> bool:
    """Add a file handler; return False if the filesystem is read-only."""
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        h = logging.FileHandler(path)
        h.setLevel(level)
        h.setFormatter(_fmt)
        logger.addHandler(h)
        return True
    except OSError:
        return False


# Try the configured log dir (default "logs"), fall back to /tmp, else console-only.
_log_dir = os.getenv("LOG_DIR", "logs")
if not _add_file_handler(f"{_log_dir}/bridgeflow.log", logging.DEBUG):
    _add_file_handler("/tmp/bridgeflow.log", logging.DEBUG)

if not _add_file_handler(f"{_log_dir}/bridgeflow_errors.log", logging.ERROR):
    _add_file_handler("/tmp/bridgeflow_errors.log", logging.ERROR)
