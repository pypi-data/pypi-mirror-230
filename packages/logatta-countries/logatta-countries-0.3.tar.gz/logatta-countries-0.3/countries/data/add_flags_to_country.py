import threading
from os import listdir
from django.core.files.base import ContentFile
from countries.models import Country , City , Nationality
import json
import os
import pkg_resources

def add_countries():
    # open json file and add data to database
    file_path = pkg_resources.resource_filename('countries.data', 'Country-ENTERVIALBE.json')
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        for country in data:
            country_obj = Country.objects.get_or_create(
                id=country['id'],
                name=country['name'],
                country_code=country['country_code'],
                name_ar=country['name_ar']
            )
    print("countries added successfully")
    return "countries added successfully"

def add_cities():
    file_path = pkg_resources.resource_filename('countries.data', 'City-entreviable.json')
    countries=Country.objects.all()
    with open(file_path, 'r') as json_file:
        data=json.load(json_file)
        for city in data:
           if countries.filter(id=city['country']).exists():
                city_obj=City.objects.get_or_create(
                    id=city['id'],
                    country_id=city['country'],
                    name=city['name'],
                    name_ar=city['name_ar']
                )
    print("cities added successfully")
    return "cities added successfully"

def add_nationalities():
    file_path = pkg_resources.resource_filename('countries.data', 'Nationality.json')
    with open(file_path,'r') as json_file:
        data=json.load(json_file)
        for nationality in data:
            nat=Nationality.objects.get_or_create(
                id=nationality['id'],
                name=nationality['name'],
                name_ar=nationality['name_ar']
            )    
    print("nationalities added successfully")
    return "nationalities added successfully"

def update_country_icons(chunk, countries):
    for image in chunk:
        file_path = pkg_resources.resource_filename('countries.data', 'flags/')
        image_name = image.split('.')[0].upper()
        if countries.filter(country_code=image_name).exists():
            # get the image from the folder
            if os.path.exists(file_path + image):
                with open(file_path + image, 'rb') as image_file:
                    image_content = image_file.read()
                    country = countries.filter(country_code=image_name).first()
                    if country:
                        country.icon.save(image, ContentFile(image_content))
                        country.save()
    return "flags added successfully"

def export_data():
    
    add_countries()
    add_cities()
    add_nationalities()
    
    images = listdir(pkg_resources.resource_filename('countries.data', 'flags/'))
    countries = Country.objects.all()

    chunk_size = 50
    num_threads = len(images) // chunk_size + (len(images) % chunk_size > 0)

    threads = []
    for i in range(num_threads):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, len(images))
        chunk = images[start_idx:end_idx]

        thread = threading.Thread(target=update_country_icons, args=(chunk, countries))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    print ("flags added successfully")


