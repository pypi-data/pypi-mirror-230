import logging
import os
import secrets
import string
from datetime import time, date, timedelta, datetime


def add_times(a_time: time, a_time_delta: timedelta):
    """
    Adds a timedelta to a time, ignoring 24h rollover.
    """
    return (datetime.combine(date.today(), a_time) + a_time_delta).time()


def subtract_times(a_time: time, a_time_delta: timedelta):
    """
    Adds a timedelta to a time, ignoring 24h rollover.
    """
    return (datetime.combine(date.today(), a_time) - a_time_delta).time()


def compare_times(a_time: time, b_time: time) -> timedelta:
    """
    Compares two times, ignoring 24 rollover, i.e. 23h - 1h the next day will give a time difference of 22 hours!
    """
    return datetime.combine(date.today(), a_time) - datetime.combine(
        date.today(), b_time
    )


def generate_unique_name(length: int = 6) -> str:
    characters = string.ascii_letters + string.digits
    unique_string = "".join(secrets.choice(characters) for _ in range(length))
    return unique_string


def setup_logging():
    loglevel = logging.DEBUG if os.getenv("DEBUG") else logging.WARNING
    logging.basicConfig(
        level=loglevel,
        format="%(asctime)s - %(levelname)s@%(module)s:%(lineno)d - %(message)s",
        datefmt="[%H:%M:%S]",
    )
