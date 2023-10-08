from dataclasses import dataclass


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
