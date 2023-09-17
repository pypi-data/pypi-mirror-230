
# django-countries


django-countries is a Django app to  that provides sessional features to your Django project.


Detailed documentation is in the "docs" directory.

Quick start

1. Add "polls" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...,
        "countries",
    ]


2. Include the polls URLconf in your project urls.py like this::

    path("countries/", include("countries.urls")),

3. Run ``python manage.py migrate`` to create the polls models.

4. Run ``python manage.py upload_data`` to upload the data to the database.

5. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a poll (you'll need the Admin app enabled).

6. Visit http://127.0.0.1:8000/polls/ to participate in the poll


7. to import MyResponse ,get_path , etc...
use ``from countries.utils import *``


``from countries.utils import MyResponse ,get_path , etc...``

