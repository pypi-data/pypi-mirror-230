from functools import wraps

from django.http import HttpRequest, HttpResponse
from djangouniversallogger.logger_ import Logger


def view_logger(logger: Logger):
    def decorator(func):
        @wraps(func)
        def wrapper(request: HttpRequest, *args, **kwargs):
            logger.info(f"Request: {request.body.decode('utf-8')}\n{request.path}\n{request.headers}")
            response: HttpResponse = func(request, *args, **kwargs)
            logger.info(f"Response: {response.content.decode('utf-8')}")
            return response
        return wrapper

    return decorator
