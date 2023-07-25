from dotenv import load_dotenv
import os

load_dotenv()

LOG_LEVEL: str = os.getenv("LOG_LEVEL") if os.getenv("LOG_LEVEL") is not None else "INFO"
FORMAT: str = "%(levelprefix)s %(asctime)s | %(message)s"

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "basic": {
            "()": "uvicorn.logging.DefaultFormatter",
            "format": FORMAT,
        }
    },
    "handlers": {
        "default": {
            "formatter": "basic",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
            "level": LOG_LEVEL,
        }
    },
    "loggers": {
        "rest": {
            "handlers": ["default"],
            "level": LOG_LEVEL,
        }
    },
}