import logging
import os

os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("vault")
logger.setLevel(logging.DEBUG)
logger.propagate = False

_fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

_console = logging.StreamHandler()
_console.setLevel(logging.INFO)
_console.setFormatter(_fmt)
logger.addHandler(_console)

_file = logging.FileHandler("logs/bridgeflow.log")
_file.setLevel(logging.DEBUG)
_file.setFormatter(_fmt)
logger.addHandler(_file)

_errors = logging.FileHandler("logs/bridgeflow_errors.log")
_errors.setLevel(logging.ERROR)
_errors.setFormatter(_fmt)
logger.addHandler(_errors)
