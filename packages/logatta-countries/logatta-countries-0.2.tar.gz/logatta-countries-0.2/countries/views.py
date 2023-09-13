from .models import *
from rest_framework.decorators import api_view

from .utils import MyResponse
# Create your views here.


@api_view(['GET'])
def get_all_countries(request):
    countries = Country.objects.all()
    serializer = CountrySerializer_2(countries, many=True)
    return MyResponse({'data': serializer.data,'status':'success'})



@api_view(['GET'])
def get_cities_by_country(request, country_id):
    cities = City.objects.select_related("country").filter(country=country_id)
    serializer = CitySerializer(cities, many=True)
    return MyResponse({'data': serializer.data,'status':'success'})


@api_view(['GET'])
def get_nationalities(request):
    snippites=Nationality.objects.all()
    serializers=NationalitySerializer(snippites,many=True)
    return MyResponse({'data':serializers.data,'status':'success'})