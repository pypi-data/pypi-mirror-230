from django.contrib import admin

# Register your models here.
from .models import City,Country,Nationality

admin.site.register(City)
admin.site.register(Country)
admin.site.register(Nationality)