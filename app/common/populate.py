# noqa: T201

import random

import faker_commerce
from customers.models import Cart, CartItem, Customer
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.utils import timezone
from faker import Faker
from model_bakery.recipe import foreign_key, Recipe
from products.models import Category, Product


def populate() -> None:
    fake = Faker()
    fake.add_provider(faker_commerce.Provider)

    # # Create 3 categories
    for category_idx in range(3):
        while True:
            try:
                category_name = fake.ecommerce_category()
                Category.objects.create(name=category_name)
                print(f"Category #{category_idx}: {category_name}")
                break
            except IntegrityError:
                print(f"// Category {category_name} already exists")
                continue

    categories = Category.objects.all()

    # Create 1000 products for each category
    for category_idx, category in enumerate(categories):
        for product_idx in range(1, 1000):
            name = fake.ecommerce_name()
            print(f"Product #{10 * category_idx + product_idx}: {name}")
            Product.objects.create(
                name=name,
                category=category,
                price=round((random.random() * 100) / 0.05) * 0.05,
                is_active=fake.boolean(),
            )

    return

    # Create 100 customers

    USER_MODEL = get_user_model()

    for user_idx in range(50):
        username = fake.user_name()
        print(f"User #{user_idx}: {username}")
        user = USER_MODEL.objects.create_user(
            username=username,
            email=fake.email(),
            password=fake.password(),
        )
        Customer.objects.create(user=user)

    # Create several carts for each customer

    customers = Customer.objects.all()
    products = Product.objects.all()

    for customer_idx, customer in enumerate(customers):
        for cart_idx in range(10, 100):
            now = timezone.now()
            two_months_ago = (
                now.replace(month=now.month - 2)
                if now.month > 2
                else now.replace(year=now.year - 1, month=12)
            )

            if random.random() > 0.0:
                is_purchased, purchased_at = True, fake.date_time_between(
                    start_date=two_months_ago, end_date=now, tzinfo=timezone.utc
                )
            else:
                is_purchased, purchased_at = False, None

            items_count = random.randint(10, 100)

            print(
                f"Cart #{customer_idx}: {customer.user.username} {cart_idx} - {is_purchased=} {purchased_at=} {items_count=}"
            )

            cart = Cart.objects.create(
                customer=customer,
                is_purchased=is_purchased,
                purchased_at=purchased_at,
            )

            for _ in range(1, items_count + 1):
                CartItem.objects.create(
                    cart=cart,
                    product=random.choice(products),
                    quantity=random.randint(1, 10),
                )


if __name__ == "__main__":
    populate()
