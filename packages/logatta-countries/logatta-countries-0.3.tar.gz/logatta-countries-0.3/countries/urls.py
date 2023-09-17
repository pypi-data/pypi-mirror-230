from django.urls import path
from.views import *



urlpatterns = [
    path('countries/', get_all_countries),
    path('countries/<int:country_id>/cities/', get_cities_by_country),
    path('nationalities/', get_nationalities),
]