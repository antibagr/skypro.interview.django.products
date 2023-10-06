import datetime as dt
import random

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.utils import timezone
from faker import Faker

from app.customers.models import Cart, CartItem, Customer
from app.products.models import Category, Product


class SingleBakery:
    def __init__(self, faker: Faker) -> None:
        self.fake = faker

    def make_category(self, use_default_faker: bool = False) -> Category:
        if use_default_faker:
            name = f"{self.fake.word().capitalize()} {self.fake.word()}"
        else:
            name = self.fake.ecommerce_category()
        return Category(name=name)

    def make_product(self, category: Category) -> Product:
        return Product(
            name=self.fake.ecommerce_name(),
            category=category,
            price=max(0.25, round((random.random() * 100) / 0.05) * 0.05),
            is_active=self.fake.boolean(),
        )

    def make_user(self, user_model: type[User]) -> User:
        return user_model(
            username=self.fake.user_name(),
            email=self.fake.email(),
            password=make_password(self.fake.password()),
            is_active=True,
        )

    def make_customer(self, user_model: type[User]) -> Customer:
        return Customer(user=self.make_user(user_model=user_model))

    def make_cart(
        self,
        customer: Customer,
        min_date: dt.datetime,
        max_date: dt.datetime,
    ) -> Cart:
        # Every 1/5 carts is not purchased
        if is_purchased := (random.random() > 0.2):
            purchased_at = self.fake.date_time_between(
                start_date=min_date,
                end_date=max_date,
                tzinfo=timezone.utc,
            )
        else:
            purchased_at = None

        return Cart(
            customer=customer,
            is_purchased=is_purchased,
            purchased_at=purchased_at,
        )

    def make_cart_item(self, cart: Cart, products: list[Product]) -> CartItem:
        return CartItem(
            cart=cart,
            product=random.choice(products),
            quantity=random.randint(1, 10),
        )


class MultiBakery(SingleBakery):
    def __init__(
        self,
        faker: Faker,
    ) -> None:
        self.fake = faker

    def make_products(self, categories: list[Category], amount: int) -> list[Product]:
        return [
            self.make_product(category=category)
            for _ in range(1, amount + 1)
            for category in categories
        ]

    def make_customers(self, user_model: type[User], amount: int) -> list[Customer]:
        return [self.make_customer(user_model=user_model) for _ in range(1, amount + 1)]

    def make_carts(
        self,
        customers: list[Customer],
        carts_per_customer: int,
        min_date: dt.datetime,
        max_date: dt.datetime,
    ) -> list[Cart]:
        carts = []
        for customer in customers:
            carts += [
                self.make_cart(customer=customer, min_date=min_date, max_date=max_date)
                for _ in range(random.randint(1, carts_per_customer + 1))
            ]
        return carts

    def make_cart_items(
        self,
        carts: list[Cart],
        products: list[Product],
        cart_items_per_cart: int = 10,
    ) -> list[CartItem]:
        cart_items = []
        for cart in carts:
            cart_items += [
                self.make_cart_item(cart=cart, products=products)
                for _ in range(random.randint(1, cart_items_per_cart + 1))
            ]
        return cart_items
