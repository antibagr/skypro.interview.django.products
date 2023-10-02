import calendar
from datetime import datetime

from django.db.models import Q, Sum, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.template.defaulttags import register
from django.utils import timezone

from .models import Category, Product


def month_sales_queryset(year: int, month: int) -> Sum:
    """
    Return the sum of the quantity of all cart items purchased in the given month and year.
    """
    return Sum(
        "cartitem__quantity",
        filter=Q(
            cartitem__cart__purchased_at__year=year,
            cartitem__cart__purchased_at__month=month,
            cartitem__cart__is_purchased=True,
        ),
        default=0,
    )


def get_products(year: int, month: int) -> QuerySet:
    """
    Parameters
    ----------
    year : int
        The year to filter monthly sales by.
    month : int
        The month to filter monthly sales by.

    Returns
    -------
    `QuerySet`
        A queryset of all products with the following annotations:
        - last_month_sales: the sum of the quantity of all cart items purchased in the previous month
        - current_month_sales: the sum of the quantity of all cart items purchased in the current month
    """

    return (
        Product.objects.annotate(
            last_month_sales=month_sales_queryset(year=year, month=month - 1),
            current_month_sales=month_sales_queryset(year=year, month=month),
        )
        .values_list(
            "id",
            "name",
            "category",
            "is_active",
            "price",
            "last_month_sales",
            "current_month_sales",
        )
        .all()[:100]
    )


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
    now = datetime.now(tz=timezone.utc)
    current_year, current_month = now.year, now.month

    products = get_products(year=current_year, month=current_month)

    categories = get_categories_names()

    return render(
        request,
        "products.html",
        {
            "products": products,
            "categories": categories,
            "last_month": calendar.month_name[current_month - 1],
            "current_month": calendar.month_name[current_month],
        },
    )
