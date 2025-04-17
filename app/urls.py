from django.urls import path
from app.adapters.inbound.count_by_year_view import get_count_by_year
from app.adapters.inbound.salary_per_sex_view import get_salary_per_sex


urlpatterns = [
    path('count_by_year/', get_count_by_year),
    path('salary_per_sex/', get_salary_per_sex),      
]