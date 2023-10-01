from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .models import Product


def index(request: HttpRequest) -> HttpResponse:
    products = Product.objects.all()
    return render(request, "products.html", {"products": products})
