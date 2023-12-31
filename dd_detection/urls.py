
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import static
from django.conf import settings
from drf_spectacular.views import (
        SpectacularAPIView,
        SpectacularRedocView,
        SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('webapp.urls')),
    path('api/user/', include('api.urls')),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    *static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]
