from django.contrib import admin
from django.urls import path, include
from django.utils.translation import gettext_lazy as _
from django.conf.urls import static
from django.conf import settings


admin.site.site_header = _('DD administration')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('webapp.urls')),
    path('api/user/', include('api.urls')),
   
]

if settings.DEBUG:
    from drf_spectacular.views import (
        SpectacularAPIView,
        SpectacularRedocView,
        SpectacularSwaggerView,
    )
    urlpatterns = [
        *urlpatterns,
        # YOUR PATTERNS
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        # Optional UI:
        path(
            "docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"
        ),
        path(
            "api/schema/redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
        ),
        *static.static(settings.STATIC_URL,
                       document_root=settings.STATIC_ROOT),
        *static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    ]