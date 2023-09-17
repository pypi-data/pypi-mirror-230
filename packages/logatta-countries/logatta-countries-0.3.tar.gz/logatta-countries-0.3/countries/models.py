from django.db import models
from countries.utils import get_path

# Create your models here.
class Country(models.Model):
    id=models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    country_code = models.CharField(max_length=5, blank=True, null=True)
    name_ar = models.CharField(max_length=200, blank=True, null=True)
    icon = models.ImageField(upload_to=get_path, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Countries"
        ordering = ['name_ar']


class City(models.Model):
    id=models.AutoField(primary_key=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name="core_Citys")
    name = models.CharField(max_length=200)
    name_ar = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Cities"
        ordering = ['name_ar']
    
class Nationality(models.Model):
    id=models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    name_ar = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Nationalities"
        ordering = ['name_ar']