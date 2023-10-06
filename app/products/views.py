import calendar
import datetime as dt
import time

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from loguru import logger

from app.products.models import Product


@login_required
def index(request: HttpRequest) -> HttpResponse:
    """
    Fetch all products with aggregated data for current month and previous month sales.
    """

    _start = time.perf_counter()

    now = dt.datetime.now(tz=timezone.utc)
    current_year, current_month = now.year, now.month

    logger.debug("Query started")
    products = Product.objects.get_products_aggr(year=current_year, month=current_month)
    products = products[:100]
    logger.debug("Query took {:.2f} seconds", time.perf_counter() - _start)

    return render(
        request,
        "products.html",
        {
            "products": products,
            "last_month": calendar.month_name[current_month - 1],
            "current_month": calendar.month_name[current_month],
        },
    )
