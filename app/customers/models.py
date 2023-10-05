from __future__ import annotations

from datetime import datetime
from typing import Any, cast, final

from django.conf import settings
from django.db import models
from django.utils import timezone
from django_stubs_ext.db.models import TypedModelMeta

from app.common.models import TimeStampMixin


@final
class Customer(TimeStampMixin):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="customer",
    )

    def __str__(self) -> str:
        return cast(str, self.user.username)

    class Meta(TypedModelMeta):
        verbose_name = "Customer"
        verbose_name_plural = "Customers"


@final
class CartItem(models.Model):
    cart = models.ForeignKey("Cart", on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self) -> str:
        return f"{self.cart} -> {self.quantity} {self.product.name}"

    class Meta(TypedModelMeta):
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"

        indexes = [
            models.Index(fields=["product"], name="cartitem_product_idx"),
            models.Index(fields=["cart"], name="cartitem_cart_idx"),
        ]


@final
class Cart(TimeStampMixin):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="cart")
    items = models.ManyToManyField("products.Product", through=CartItem, related_name="carts")

    is_purchased = models.BooleanField(default=False)
    purchased_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        If the cart `is_purchased`, set the `purchased_at` field to the current datetime.

        If the cart is not purchased, set the `purchased_at` field to None.
        """
        if self.is_purchased and not self.purchased_at:
            self.purchased_at = datetime.now(tz=timezone.utc)
        elif self.purchased_at and not self.is_purchased:
            self.purchased_at = None
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.customer}'s cart {'(unpaid)' if not self.is_purchased else ''}"

    class Meta(TypedModelMeta):
        verbose_name = "Cart"
        verbose_name_plural = "Carts"
