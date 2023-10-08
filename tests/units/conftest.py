import datetime as dt

import pytest
from django.contrib.auth.models import User
from faker import Faker

from app.common.utils import create_faker, get_month_ago, MultiBakery
from app.customers.models import Cart, CartItem, Customer
from app.products.models import Category, Product, ProductRow
from tests.units.types import Client


@pytest.fixture()
def now() -> dt.datetime:
    return dt.datetime.now(tz=dt.timezone.utc)


@pytest.fixture()
def current_year(now: dt.datetime) -> int:
    return now.year


@pytest.fixture()
def current_month(now: dt.datetime) -> int:
    return now.month


@pytest.fixture()
def faker() -> Faker:
    return create_faker()


@pytest.fixture()
def bakery(faker: Faker) -> MultiBakery:
    return MultiBakery(faker=faker)


@pytest.mark.django_db()
@pytest.fixture()
def user(django_user_model: type[User], bakery: MultiBakery) -> User:
    _user = bakery.make_user(user_model=django_user_model)
    _user.save()
    return _user


@pytest.mark.django_db()
@pytest.fixture()
def categories(bakery: MultiBakery) -> list[Category]:
    names = ["Bakery", "Coffee", "Anime Books", "Manga Books", "Donuts"]
    _categories = [bakery.make_category() for _ in range(2)]

    # Make sure the names are unique
    for name, category in zip(names, _categories):
        category.name = name

    Category.objects.bulk_create(_categories)
    return _categories


@pytest.mark.django_db()
@pytest.fixture()
def products(bakery: MultiBakery, categories: list[Category]) -> list[Product]:
    _products = bakery.make_products(categories=categories, amount=5)
    Product.objects.bulk_create(_products)
    return _products


@pytest.mark.django_db()
@pytest.fixture()
def product_without_sales(bakery: MultiBakery, categories: list[Category]) -> Product:
    product = bakery.make_product(category=categories[0])
    product.save()
    return product


@pytest.mark.django_db()
@pytest.fixture()
def customers(bakery: MultiBakery, django_user_model: type[User]) -> list[Customer]:
    _customers = bakery.make_customers(user_model=django_user_model, amount=5)
    django_user_model.objects.bulk_create([customer.user for customer in _customers])
    Customer.objects.bulk_create(_customers)
    return _customers


@pytest.mark.django_db()
@pytest.fixture()
def carts(bakery: MultiBakery, customers: list[Customer], now: dt.datetime) -> list[Cart]:
    month_ago = get_month_ago(now)
    _carts = [
        bakery.make_cart(customer=customer, min_date=month_ago, max_date=now)
        for customer in customers
    ]

    # One is not purchased
    _carts[0].is_purchased = False

    # two purchased month ago
    _carts[3].is_purchased, _carts[3].purchased_at = True, month_ago
    _carts[4].is_purchased, _carts[4].purchased_at = True, month_ago

    # One purchased now
    _carts[1].is_purchased, _carts[1].purchased_at = True, now

    # One purchased three months ago
    _carts[2].is_purchased, _carts[2].purchased_at = True, get_month_ago(month_ago)

    Cart.objects.bulk_create(_carts)
    return _carts


@pytest.mark.django_db()
@pytest.fixture()
def cart_items(carts: list[Cart], products: list[Product]) -> list[CartItem]:
    _cart_items = []
    for cart in carts:
        for product in products:
            _cart_items.append(
                CartItem(
                    cart=cart,
                    product=product,
                    quantity=1,
                )
            )
    CartItem.objects.bulk_create(_cart_items)
    return _cart_items


@pytest.fixture()
def products_rows(
    cart_items: list[CartItem],  # noqa: U100
    current_year: int,
    current_month: int,
) -> list[ProductRow]:
    return Product.objects.get_products_aggr(year=current_year, month=current_month)


@pytest.mark.django_db()
@pytest.fixture()
def auth_client(client: Client, user: User) -> Client:
    client.force_login(user)
    return client
