# django-countries



## Installation

```bash
pip install logatta-countries
```

2- add `countries` to your `INSTALLED_APPS` in `settings.py` file

```python

'logatta_countries',
```


## ADD data to database 

1- migrate the database

```bash
python manage.py migrate
```

2- run the command

```bash
python manage.py upload_data

```


# to import MyResponse ,get_path , etc...

```python
from countries.utils import *

or 

from countries.utils import MyResponse ,get_path , etc...
```



