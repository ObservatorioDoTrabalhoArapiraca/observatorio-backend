from django.urls import path
from app.adapters.inbound.count_by_year_view import get_dados 

urlpatterns = [
    path('count_by_year/', get_dados),
]