from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

handler404 = "app.common.views.handler404"
handler500 = "app.common.views.handler500"


urlpatterns = [
    path("", include("app.products.urls")),
    path("admin/", admin.site.urls),
    # TODO (a.bagryanov): Figure out how to use debug toolbar
    # only in development mode.
    path("__debug__/", include("debug_toolbar.urls")),
]

urlpatterns += static(  # type: ignore[arg-type]
    settings.STATIC_URL,
    document_root=settings.STATIC_ROOT,
)
