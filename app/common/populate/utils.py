import datetime as dt
import logging
import os
import time
from dataclasses import dataclass
from typing import Callable, ParamSpec, TypeVar

import faker_commerce
from django.contrib.auth import get_user_model
from faker import Faker

P = ParamSpec("P")
T = TypeVar("T")


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


def timeit(func: Callable[P, T]) -> Callable[P, T]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        _start = time.perf_counter()
        logger.debug("Running {}", func.__name__)
        results = func(*args, **kwargs)
        logger.debug(
            "{} took {} seconds",
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


@dataclass(frozen=True)
class Settings:
    """
    Settings for populate_async and populate_threads
    """

    categories_count: int = 100
    products_per_category_count: int = 1000
    customers_count: int = 100
    carts_per_customer_count: int = 5
    cart_items_per_cart_count: int = 10
