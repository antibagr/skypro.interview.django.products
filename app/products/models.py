from __future__ import annotations

import calendar
import datetime as dt
from typing import cast, final, NamedTuple

from django.db import connection, models
from django.db.models import Q, Sum
from django.utils import timezone
from django_stubs_ext.db.models import TypedModelMeta
from djmoney.models.fields import MoneyField
from loguru import logger

from app.common.models import TimeStampMixin


class ProductRow(NamedTuple):
    id: int
    name: str
    category: str
    is_active: bool
    price: float
    last_month_sales: int
    current_month_sales: int


@final
class Category(TimeStampMixin):
    name = models.CharField(max_length=100, unique=True)

    class Meta(TypedModelMeta):
        verbose_name = "Category"
        verbose_name_plural = "Categories"

        indexes = [
            models.Index(fields=["id", "name"]),
        ]

    def __str__(self) -> str:
        return self.name


@final
class ProductManager(models.Manager["Product"]):
    """
    Extends the default manager for the Product model with a custom method
    to get a list of products with the following annotations:
    - last_month_sales:
        the sum of the quantity of all cart
        items purchased in the previous month
    - current_month_sales:
        the sum of the quantity of all cart items
        purchased in the current month
    """

    def _get_dt_to_filter(self, year: int, month: int) -> list[dt.datetime]:
        """
        Get a list of datetime to filter monthly sales by.

        Parameters
        ----------
        year : int
            The year to filter monthly sales by.
        month : int
            The month to filter monthly sales by.

        Returns
        -------
        list[dt.datetime]
            A list of date_from, date_to, previous_month_from, previous_month_to
        """
        d_fmt = "{0:>02}.{1:>02}.{2}"
        date_from = dt.datetime.strptime(d_fmt.format(1, month, year), "%d.%m.%Y")
        _last_day_of_month = calendar.monthrange(year, month)[1]
        date_to = dt.datetime.strptime(d_fmt.format(_last_day_of_month, month, year), "%d.%m.%Y")

        date_from = date_from.replace(tzinfo=timezone.utc)
        date_to = date_to.replace(tzinfo=timezone.utc)

        previous_month_to = date_from - dt.timedelta(days=1)
        previous_month_from = previous_month_to.replace(day=1)

        return [date_from, date_to, previous_month_from, previous_month_to]

    def _month_sales_queryset(self, dt_from: dt.datetime, dt_to: dt.datetime) -> Sum:
        """
        Return the sum of the quantity of all cart items purchased in the given month and year.
        """
        return Sum(
            "cartitem__quantity",
            filter=Q(
                cartitem__cart__purchased_at__gte=dt_from,
                cartitem__cart__purchased_at__lte=dt_to,
                cartitem__cart__is_purchased=True,
            ),
            default=0,
        )

    def get_products_orm_fallback(self, year: int, month: int) -> list[ProductRow]:
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
            - last_month_sales:
                the sum of the quantity of all cart
                items purchased in the previous month
            - current_month_sales:
                the sum of the quantity of all cart items
                purchased in the current month
        """

        date_from, date_to, previous_month_from, previous_month_to = self._get_dt_to_filter(
            year=year, month=month
        )

        return list(
            Product.objects.prefetch_related("category", "cartitem_set__cart")
            .annotate(
                last_month_sales=self._month_sales_queryset(date_from, date_to),
                current_month_sales=self._month_sales_queryset(
                    previous_month_from, previous_month_to
                ),
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
            .all()
        )

    def get_products_raw_pg(self, year: int, month: int) -> list[ProductRow]:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                PREPARE get_products(TIMESTAMP, TIMESTAMP, TIMESTAMP, TIMESTAMP) AS
                WITH paid_carts AS (
                        SELECT cart.id
                            ,cart.purchased_at
                        FROM customers_cart cart
                        WHERE cart.is_purchased = TRUE
                        )
                    ,this_month_carts AS (
                        SELECT c.id
                        FROM paid_carts c
                        WHERE c.purchased_at >= $1
                            AND c.purchased_at < $2
                        )
                    ,previous_month_carts AS (
                        SELECT c.id
                        FROM paid_carts c
                        WHERE c.purchased_at >= $3
                            AND c.purchased_at < $4
                        )
                    ,category_names AS (
                        SELECT c.id
                            ,c.NAME
                        FROM products_category c
                        )
                    ,this_month_items AS (
                        SELECT items.product_id
                            ,SUM(items.quantity) AS total
                        FROM customers_cartitem items
                        WHERE EXISTS (
                                SELECT
                                FROM this_month_carts c
                                WHERE c.id = items.cart_id
                                )
                        GROUP BY items.product_id
                        )
                    ,previous_month_items AS (
                        SELECT items.product_id
                            ,SUM(items.quantity) AS total
                        FROM customers_cartitem items
                        WHERE EXISTS (
                                SELECT
                                FROM previous_month_carts c
                                WHERE c.id = items.cart_id
                                )
                        GROUP BY items.product_id
                        )

                SELECT p.*
                    ,c.NAME
                FROM (
                    SELECT p.*
                        ,tm.total
                    FROM (
                        SELECT p.id
                            ,p.NAME
                            ,p.category_id
                            ,p.is_active
                            ,COALESCE(p.price, 0)
                            ,COALESCE(pm.total, 0)
                        FROM products_product p
                        LEFT JOIN previous_month_items pm ON p.id = pm.product_id
                        ) p
                    LEFT JOIN this_month_items tm ON p.id = tm.product_id
                    ) p
                LEFT JOIN category_names c ON p.category_id = c.id;

                EXECUTE get_products(% s, % s, % s, % s);
                """,
                self._get_dt_to_filter(year=year, month=month),
            )
            return cast(list[ProductRow], cursor.fetchall())

    def get_products_aggr(self, year: int, month: int) -> list[ProductRow]:
        """
        Get a list of products with the following annotations:
        - last_month_sales:
            the sum of the quantity of all cart
            items purchased in the previous month
        - current_month_sales:
            the sum of the quantity of all cart items
            purchased in the current month

        Parameters
        ----------
        year : int
            The year to filter monthly sales by.
        month : int
            The month to filter monthly sales by.

        Returns
        -------
        list[ProductRow]
            A list of products with the following annotations:
            - last_month_sales:
                the sum of the quantity of all cart
                items purchased in the previous month
            - current_month_sales:
                the sum of the quantity of all cart items
                purchased in the current month
        """

        logger.debug(f"Querying products for {year}-{month}, {connection.vendor=}")

        match connection.vendor:
            case "postgresql":
                return self.get_products_raw_pg(year=year, month=month)
            case _:
                logger.warning("Unsupported database backend. Falling back to ORM")
                return self.get_products_orm_fallback(year=year, month=month)


@final
class Product(TimeStampMixin):
    objects: ProductManager = ProductManager()

    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    price = MoneyField(max_digits=14, decimal_places=2, default_currency="USD")
    is_active = models.BooleanField(default=False)

    class Meta(TypedModelMeta):
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self) -> str:
        return f"[{self.category}] {self.name}"
