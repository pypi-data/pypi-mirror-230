from django.apps import AppConfig

from djangouniversallogger.logger_ import Logger
from djangouniversallogger.utils import load_check_logger


class DjangouniversalloggerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'djangouniversallogger'

    def ready(self):
        if load_check_logger():
            logger = Logger("SET<CHECK_LOGGER>FALSE_FOR_SKIPPING")
            logger.info("This is a test")
            logger.info("running something")
            logger.debug("Some debugging details")
            logger.exception("Critical error!")
            logger.debug("Some more debugging details")
            logger.info("This is a test")
            logger.info("running something")
            logger.debug("Some debugging details")
            logger.exception("Critical error!")
            logger.debug("Some more debugging details")
