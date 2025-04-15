from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('app.web.urls')),  # substitua 'app' pelo nome real da sua aplicação
]