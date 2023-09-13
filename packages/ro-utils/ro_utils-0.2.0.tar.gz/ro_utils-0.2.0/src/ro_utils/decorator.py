import time
from functools import wraps
import logging


def continue_when_error(func):
    """
    continue when error
    :param func:
    :return:
    """

    @wraps(func)
    def fn(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(e)

    return fn


def retry_when_error(func):
    """
    retry when error, default 3 times
    :param func:
    :return:
    """

    @wraps(func)
    def fn(*args, **kwargs):
        """docstring for fn"""
        for k, item in enumerate(range(3)):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if k == 2:
                    logging.exception(e)

    return fn


def retry_when_error_with_params(*out_args, **out_kwargs):
    """
    return when error with param, delay and times
    :param out_args:
    :param out_kwargs:
    :return:
    """

    def retry_when_error_occur(func):
        @wraps(func)
        def fn(*args, **kwargs):
            times = int(out_kwargs.get("times", 5))
            delay = int(out_kwargs.get("delay", 0))
            for k, item in enumerate(range(times)):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if k == times - 1:
                        logging.exception(e)
                    if delay > 0:
                        time.sleep(delay)

        return fn

    return retry_when_error_occur


def retry_when_error_with_times(times):
    """
    retry when error with times params
    :param times:
    :return:
    """

    return retry_when_error_with_params(times=times)


def singleton(cls):
    instances = {}

    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper
