from typing import final
from uuid import uuid4

from django.db import models
from django_stubs_ext.db.models import TypedModelMeta
from djmoney.models.fields import MoneyField

from app.common.models import TimeStampMixin


@final
class Category(TimeStampMixin):
    name = models.CharField(max_length=100, unique=True)

    class Meta(TypedModelMeta):
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return self.name


@final
class Product(TimeStampMixin):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    price = MoneyField(max_digits=14, decimal_places=2, default_currency="USD")
    is_active = models.BooleanField(default=False)

    class Meta(TypedModelMeta):
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self) -> str:
        return f"[{self.category}] {self.name}"
