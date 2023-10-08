import calendar
import datetime as dt
import os
import time
from typing import Callable, ParamSpec, TypeVar

import faker_commerce
from django.contrib.auth import get_user_model
from faker import Faker
from loguru import logger

P = ParamSpec("P")
T = TypeVar("T")


def timeit(func: Callable[P, T]) -> Callable[P, T]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        _start = time.perf_counter()
        logger.debug("Running {}", func.__name__)
        results = func(*args, **kwargs)
        logger.debug(
            "{} took {:.2f} seconds",
            func.__name__,
            time.perf_counter() - _start,
        )
        return results

    return wrapper


def create_faker() -> Faker:
    faker = Faker()
    faker.add_provider(faker_commerce.Provider)
    return faker


def get_last_day_of_month(now: dt.datetime) -> dt.datetime:
    if now.month == 12:
        return now.replace(day=31)
    return now.replace(month=now.month + 1, day=1) - dt.timedelta(days=1)


def get_month_ago(now: dt.datetime) -> dt.datetime:
    if now.month > 1:
        return now.replace(month=now.month - 1)
    return now.replace(month=now.month - 1, year=now.year - 1)


def get_month_name(month: int) -> str:
    return calendar.month_name[month]


def create_admin() -> None:
    """
    Create a superuser with the following credentials:
    - username: `environ['DJANGO_SUPERUSER_USERNAME']` (default: `admin`)
    - email: `environ[DJANGO_SUPERUSER_EMAIL']` (default: `admin@mail.com`)
    - password: `environ['DJANGO_SUPERUSER_PASSWORD']` (default: `admin`)
    """
    get_user_model().objects.create_superuser(
        os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin"),
        os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@mail.com"),
        os.environ.get("DJANGO_SUPERUSER_PASSWORD", "admin"),
    )
