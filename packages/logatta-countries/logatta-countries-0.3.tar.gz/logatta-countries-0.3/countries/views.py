from .models import *
from rest_framework.decorators import api_view
from django.views.decorators.cache import cache_page
from .serializers import *
from .utils import MyResponse
# Create your views here.


@api_view(['GET'])
@cache_page(60 * 60 * 24)  # 24 hours cache
def get_all_countries(request):
    countries = Country.objects.all()
    serializer = CountrySerializer_2(countries, many=True)
    return MyResponse({'data': serializer.data,'status':'success'})



@api_view(['GET'])
@cache_page(60 * 60 * 24) 
def get_cities_by_country(request, country_id):
    cities = City.objects.select_related("country").filter(country=country_id)
    serializer = CitySerializer(cities, many=True)
    return MyResponse({'data': serializer.data,'status':'success'})


@api_view(['GET'])
@cache_page(60 * 60 * 24) 
def get_nationalities(request):
    snippites=Nationality.objects.all()
    serializers=NationalitySerializer(snippites,many=True)
    return MyResponse({'data':serializers.data,'status':'success'})