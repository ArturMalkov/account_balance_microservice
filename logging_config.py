from pydantic import BaseModel


class LoggingConfig(BaseModel):
    LOGGER_NAME = "avito account balance microservice"
    LOGGING_FORMAT = "%(levelprefix)s | %(asctime)s | %(message)s"  # TODO: to look for a format config!
    LOGGING_LEVEL = "INFO"

    # Logging config - https://stackoverflow.com/questions/63510041/adding-python-logging-to-fastapi-endpoints-hosted-on-docker-doesnt-display-api
    disable_existing_loggers = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOGGING_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    }
    handlers = {}
    loggers = {}
