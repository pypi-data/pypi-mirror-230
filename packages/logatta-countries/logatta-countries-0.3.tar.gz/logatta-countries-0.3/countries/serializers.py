from rest_framework import serializers
from .models import *
import random

class CountrySerializer_2(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "name_ar"]
        
        
class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["id", "name_ar"]


class NationalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Nationality
        fields = ["id", "name_ar"]
