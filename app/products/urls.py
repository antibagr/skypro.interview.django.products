from django.urls import path

from . import views

urlpatterns = [
    # NB (a.bagryanov): path doesn't have an async type hint
    path("", views.index, name="index"),  # type: ignore[arg-type]
]
