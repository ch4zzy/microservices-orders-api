import sys
from datetime import datetime

from elasticsearch import Elasticsearch
from loguru import logger

import logging
from core.config import settings

ELASTIC_URL = settings.ELASTIC_URL
SERVICE_NAME = settings.SERVICE_NAME

es = Elasticsearch(ELASTIC_URL)


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging():
    logger.remove()

    logger.add(sys.stdout, level="INFO", colorize=True)

    def elastic_sink(message):
        try:
            record = message.record
            log_document = {
                "@timestamp": record["time"].isoformat(),
                "level": record["level"].name,
                "message": record["message"],
                "service": SERVICE_NAME,
                "module": record["module"],
                "function": record["function"],
                "line": record["line"],
                "extra": record["extra"],
            }

            es.index(
                index=f"{settings.SERVICE_NAME}-{datetime.now().strftime('%Y.%m.%d')}",
                document=log_document
            )
        except Exception as e:
            print(f"Помилка відправки логу в Elasticsearch: {e}", file=sys.stderr)

    logger.add(elastic_sink, level="INFO", enqueue=True)

    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
    logging.getLogger("uvicorn.error").handlers = [InterceptHandler()]
    logging.getLogger("uvicorn").handlers = [InterceptHandler()]

    logging.getLogger("uvicorn.access").propagate = False
    logging.getLogger("uvicorn.error").propagate = False


setup_logging()
