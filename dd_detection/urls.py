
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('api.urls')),
    path('', include('webapp.urls')),
    *static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]
