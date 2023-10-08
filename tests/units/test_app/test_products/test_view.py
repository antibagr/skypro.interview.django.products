import pytest
from django.urls import reverse

from app.common.utils import get_month_name
from app.products.models import ProductRow
from tests.units.types import Client

pytestmark = pytest.mark.django_db


def test_home_view_unauthenticated(client: Client) -> None:
    url = reverse("home")
    resp = client.get(url)
    assert resp.status_code == 302
    assert resp.url == "/accounts/login/?next=/"


def test_home_view(
    auth_client: Client,
    products_rows: list[ProductRow],
    current_month: int,
) -> None:
    url = reverse("home")
    resp = auth_client.get(url)
    assert resp.status_code == 200
    assert list(resp.context["products"]) == list(products_rows)
    assert resp.context["last_month"] == get_month_name(current_month - 1)
    assert resp.context["current_month"] == get_month_name(current_month)

    for product, row_product in zip(resp.context["products"], products_rows):
        assert product[-1] == row_product[-1] == 2
        assert product[-2] == row_product[-2] == 1


@pytest.mark.usefixtures("product_without_sales")
def test_home_view_with_product_without_sales(
    auth_client: Client,
) -> None:
    url = reverse("home")
    resp = auth_client.get(url)
    assert resp.status_code == 200
    assert len(resp.context["products"]) == 1
    assert resp.context["products"][0][-1] == 0
    assert resp.context["products"][0][-2] == 0


def test_home_view_without_products(
    auth_client: Client,
) -> None:
    url = reverse("home")
    resp = auth_client.get(url)
    assert resp.status_code == 200
    assert len(resp.context["products"]) == 0
