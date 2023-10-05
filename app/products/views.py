import calendar
import datetime as dt
import time

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.template.defaulttags import register
from django.utils import timezone
from loguru import logger

from .models import Category, Product


def get_categories_names() -> dict[str, str]:
    """
    Returns
    -------
    dict[str, str]
        A dictionary of category ids and names.
    """
    return {
        category["id"]: category["name"] for category in Category.objects.values("id", "name").all()
    }


@register.filter
def get_item(dictionary: dict[str, str], key: str) -> str:
    return dictionary[key]


def index(request: HttpRequest) -> HttpResponse:
    _start = time.perf_counter()

    now = dt.datetime.now(tz=timezone.utc)
    current_year, current_month = now.year, now.month

    logger.debug("Query started")
    products = Product.objects.get_products_aggr(year=current_year, month=current_month)
    logger.debug("Query took {:.3f} seconds".format(time.perf_counter() - _start))

    return render(
        request,
        "products.html",
        {
            "products": products,
            "last_month": calendar.month_name[current_month - 1],
            "current_month": calendar.month_name[current_month],
        },
    )
