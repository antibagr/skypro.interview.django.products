import asyncio
import datetime as dt
import time
from contextlib import suppress

import uvloop
from asgiref.sync import sync_to_async
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


class AsyncPopulator:
    def __init__(
        self,
        settings: Settings,
        task_name: str,
        faker: Faker | None = None,
    ) -> None:
        self.fake = faker or create_faker()
        self._settings = settings
        self._baker = MultiBakery(faker=self.fake)
        self._task_name = task_name

    async def create_categories(self, amount: int) -> list[Category]:
        created = 0
        tries = 0
        categories = []
        while created < amount:
            with suppress(IntegrityError):
                tries += 1
                category = self._baker.make_category(use_default_faker=(tries > 100))
                await category.asave()
                categories.append(category)
                created += 1
        return categories

    async def create_products(self, categories: list[Category], amount: int) -> list[Product]:
        products = self._baker.make_products(categories=categories, amount=amount)
        return await Product.objects.abulk_create(products)

    async def create_customers(self, amount: int) -> list[Customer]:
        User = get_user_model()

        loop = asyncio.get_event_loop()

        customers = await loop.run_in_executor(None, self._baker.make_customers, User, amount)

        try:
            await User.objects.abulk_create([customer.user for customer in customers])
            return await Customer.objects.abulk_create(customers, ignore_conflicts=True)
        except IntegrityError:
            if await sync_to_async(Customer.objects.count)() < amount:
                raise
            customers = []
            added = 0
            async for customer in Customer.objects.all():
                customers.append(customer)
                added += 1
                if added == amount:
                    break
            return customers

    async def create_carts(
        self,
        customers: list[Customer],
        carts_per_customer: int,
        min_date: dt.datetime | None = None,
        max_date: dt.datetime | None = None,
    ) -> list[Cart]:
        now = timezone.now()
        max_date = max_date or get_last_day_of_month(now)
        min_date = min_date or get_month_ago(now)

        return await Cart.objects.abulk_create(
            self._baker.make_carts(
                customers=customers,
                carts_per_customer=carts_per_customer,
                min_date=min_date,
                max_date=max_date,
            )
        )

    async def create_cart_items(
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
        await CartItem.objects.abulk_create(items, ignore_conflicts=True)

    async def populate(self) -> None:
        logger.info("Task #{} spawned", self._task_name)
        _start = time.perf_counter()

        logger.debug(
            "Task {} creating {} categories", self._task_name, self._settings.categories_count
        )
        categories = await self.create_categories(amount=self._settings.categories_count)

        logger.debug(
            "Task #{} creating {} products",
            self._task_name,
            self._settings.products_per_category_count,
        )
        products = await self.create_products(
            categories=categories,
            amount=self._settings.products_per_category_count,
        )

        logger.debug(
            "Task #{} creating {} customers", self._task_name, self._settings.customers_count
        )
        customers = await self.create_customers(amount=self._settings.customers_count)

        logger.debug(
            "Task #{} creating {} carts",
            self._task_name,
            self._settings.carts_per_customer_count * self._settings.customers_count,
        )
        carts = await self.create_carts(
            customers=customers,
            carts_per_customer=self._settings.carts_per_customer_count,
        )

        logger.debug(
            "Task #{} creating {} cart items",
            self._task_name,
            self._settings.cart_items_per_cart_count * self._settings.carts_per_customer_count,
        )
        await self.create_cart_items(
            carts=carts,
            products=products,
            cart_items_per_cart=self._settings.cart_items_per_cart_count,
        )

        logger.info(
            "Task #{} finished in {:.2f} seconds", self._task_name, time.perf_counter() - _start
        )


class AsyncPopulatorPool:
    def __init__(
        self,
        populator: type[AsyncPopulator],
        settings: Settings,
        tasks_count: int = 4,
    ) -> None:
        self._populator = populator
        self._settings = settings
        self._tasks_count = tasks_count

    async def populate(self) -> None:
        categories_per_task = self._settings.categories_count // self._tasks_count
        customers_per_task = self._settings.customers_count // self._tasks_count

        settings = Settings(
            categories_count=categories_per_task,
            products_per_category_count=self._settings.products_per_category_count,
            customers_count=customers_per_task,
            carts_per_customer_count=self._settings.carts_per_customer_count,
            cart_items_per_cart_count=self._settings.cart_items_per_cart_count,
        )
        populators = [
            self._populator(settings=settings, task_name=str(task_name))
            for task_name in range(1, self._tasks_count + 1)
        ]
        await asyncio.gather(*[p.populate() for p in populators])


async def main(settings: Settings, tasks_count: int) -> None:
    await sync_to_async(db.connections.close_all)()

    with suppress(Exception):
        await sync_to_async(create_admin)()

    workers = AsyncPopulatorPool(
        populator=AsyncPopulator, settings=settings, tasks_count=tasks_count
    )
    await workers.populate()


@timeit
def populate_async(settings: Settings | None = None, tasks_count: int = 4) -> None:
    """
    Create the admin user, categories, products, customers, carts and cart items
    """
    settings = settings or Settings()
    uvloop.install()
    asyncio.run(main(settings=settings, tasks_count=tasks_count))
