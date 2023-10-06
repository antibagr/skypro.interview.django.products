import datetime as dt
import threading
import time
from contextlib import suppress

from django import db
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.utils import timezone
from faker import Faker

from app.common.populate.bakery import MultiBakery
from app.common.populate.utils import (
    create_admin,
    create_faker,
    get_last_day_of_month,
    get_month_ago,
    logger,
    Settings,
    timeit,
)
from app.customers.models import Cart, CartItem, Customer
from app.products.models import Category, Product


class Populator:
    def __init__(
        self,
        settings: Settings,
        faker: Faker | None = None,
    ) -> None:
        self.fake = faker or create_faker()
        self._settings = settings
        self._baker = MultiBakery(faker=self.fake)

    def create_categories(self, amount: int) -> list[Category]:
        created = 0
        tries = 0
        categories = []
        while created < amount:
            with suppress(IntegrityError):
                tries += 1
                category = self._baker.make_category(use_default_faker=(tries > 100))
                category.save()
                categories.append(category)
                created += 1
        return categories

    def create_products(self, categories: list[Category], amount: int) -> list[Product]:
        products = self._baker.make_products(categories=categories, amount=amount)
        return Product.objects.bulk_create(products)

    def create_customers(self, amount: int) -> list[Customer]:
        User = get_user_model()
        customers = self._baker.make_customers(User, amount)

        try:
            User.objects.bulk_create([customer.user for customer in customers])
            return Customer.objects.bulk_create(customers, ignore_conflicts=True)
        except IntegrityError:
            if Customer.objects.count() < amount:
                raise
            return list(Customer.objects.all()[:amount])

    def create_carts(
        self,
        customers: list[Customer],
        carts_per_customer: int,
        min_date: dt.datetime | None = None,
        max_date: dt.datetime | None = None,
    ) -> list[Cart]:
        now = timezone.now()
        max_date = max_date or get_last_day_of_month(now)
        min_date = min_date or get_month_ago(now)

        return Cart.objects.bulk_create(
            self._baker.make_carts(
                customers=customers,
                carts_per_customer=carts_per_customer,
                min_date=min_date,
                max_date=max_date,
            )
        )

    def create_cart_items(
        self,
        carts: list[Cart],
        products: list[Product],
        cart_items_per_cart: int = 10,
    ) -> None:
        items = self._baker.make_cart_items(
            carts=carts,
            products=products,
            cart_items_per_cart=cart_items_per_cart,
        )
        CartItem.objects.bulk_create(items, ignore_conflicts=True)


class ThreadPopulator(Populator):
    def __init__(
        self,
        settings: Settings,
        thread_name: str,
        faker: Faker | None = None,
    ) -> None:
        super().__init__(settings=settings, faker=faker)
        self._thread_name = thread_name

    def populate(self) -> None:
        logger.info("Thread #{} spawned", self._thread_name)

        _start = time.perf_counter()

        logger.debug(
            "Thread {} creating {} categories", self._thread_name, self._settings.categories_count
        )
        categories = self.create_categories(amount=self._settings.categories_count)

        logger.debug(
            "Thread #{} creating {} products",
            self._thread_name,
            self._settings.products_per_category_count,
        )
        products = self.create_products(
            categories=categories,
            amount=self._settings.products_per_category_count,
        )

        logger.debug(
            "Thread #{} creating {} customers", self._thread_name, self._settings.customers_count
        )
        customers = self.create_customers(amount=self._settings.customers_count)

        logger.debug(
            "Thread #{} creating {} carts",
            self._thread_name,
            self._settings.carts_per_customer_count * self._settings.customers_count,
        )
        carts = self.create_carts(
            customers=customers,
            carts_per_customer=self._settings.carts_per_customer_count,
        )

        logger.debug(
            "Thread #{} creating {} cart items",
            self._thread_name,
            self._settings.cart_items_per_cart_count * self._settings.carts_per_customer_count,
        )
        self.create_cart_items(
            carts=carts,
            products=products,
            cart_items_per_cart=self._settings.cart_items_per_cart_count,
        )

        logger.info(
            "Thread #{} finished in {} seconds", self._thread_name, time.perf_counter() - _start
        )


def run_populator(settings: Settings, thread_name: str) -> None:
    try:
        ThreadPopulator(settings=settings, thread_name=thread_name).populate()
    except Exception as exc:
        logger.error("Thread #{} failed with exception", thread_name)
        logger.exception(exc, exc_info=True)


class ThreadsPopulator:
    def __init__(
        self,
        populator: type[ThreadPopulator],
        settings: Settings,
        threads_count: int = 4,
    ) -> None:
        self._populator = populator
        self._settings = settings
        self._threads_count = threads_count

    def populate(self) -> None:
        categories_per_thread = self._settings.categories_count // self._threads_count
        products_per_category_per_thread = (
            self._settings.products_per_category_count // self._threads_count
        )
        customers_per_thread = self._settings.customers_count // self._threads_count

        threads: list[threading.Thread] = []
        settings = Settings(
            categories_count=categories_per_thread,
            products_per_category_count=products_per_category_per_thread,
            customers_count=customers_per_thread,
            carts_per_customer_count=self._settings.carts_per_customer_count,
            cart_items_per_cart_count=self._settings.cart_items_per_cart_count,
        )
        for thread_name in range(self._threads_count):
            thread = threading.Thread(target=run_populator, args=(settings, thread_name))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()


@timeit
def populate_threads(settings: Settings | None = None, threads_count: int = 4) -> None:
    """
    Create the admin user, categories, products, customers, carts and cart items
    """

    settings = settings or Settings()

    db.connections.close_all()

    with suppress(Exception):
        create_admin()

    ThreadsPopulator(
        populator=ThreadPopulator,
        settings=settings,
        threads_count=threads_count,
    ).populate()
