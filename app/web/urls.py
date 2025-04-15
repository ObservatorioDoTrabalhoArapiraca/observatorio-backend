from django.urls import path
from .views import health_check
from .views import get_bigquery_data

urlpatterns = [
    path('health/', health_check),
    path('bigquery/', get_bigquery_data),
]