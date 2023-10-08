from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView

handler404 = "app.common.views.handler404"
handler500 = "app.common.views.handler500"


urlpatterns = [
    path("", include("app.products.urls")),
    path("accounts/", include("allauth.urls")),
    path("me/", include("users.urls", namespace="users")),
    path("admin/login/", RedirectView.as_view(url="/accounts/login/", permanent=True)),
    path("admin/logout/", RedirectView.as_view(url="/accounts/logout/", permanent=True)),
    path("admin/", admin.site.urls),
    # TODO (a.bagryanov): Figure out how to use debug toolbar
    # only in development mode.
    path("__debug__/", include("debug_toolbar.urls")),
    path(
        "favicon.ico",
        RedirectView.as_view(url=settings.STATIC_URL + "images/icon/favicon.ico", permanent=True),
    ),
]

urlpatterns += static(
    settings.STATIC_URL,
    document_root=settings.STATIC_ROOT,
)
