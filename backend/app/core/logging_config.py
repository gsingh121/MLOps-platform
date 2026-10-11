import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    logger = logging.getLogger()
    log_handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s %(correlation_id)s"
    )
    log_handler.setFormatter(formatter)
    logger.handlers = [log_handler]
    logger.setLevel(logging.INFO)
    return logger
