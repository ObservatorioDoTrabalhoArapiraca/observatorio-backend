from django.contrib import admin
from django.urls import path, include
from app.web import urls as app_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(app_urls)),
]
