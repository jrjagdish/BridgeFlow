import logging
import os

os.makedirs("logs",exist_ok=True)
logger = logging.getLogger("vault")
logger.setLevel(logging.INFO)
logger.propagate = False

log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)

file_handler = logging.FileHandler("logs/bridgeflow.log")
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)