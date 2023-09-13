# mypackage/management/commands/upload_data.py

from django.core.management.base import BaseCommand
from django.conf import settings
from countries.data.add_flags_to_country import export_data

class Command(BaseCommand):
    help = 'Upload data to the database'

    def handle(self, *args, **options):

        # Perform data upload logic here
        # Example: YourModel.objects.create(field1=setting_value, ...)
        export_data()

        self.stdout.write(self.style.SUCCESS('Data uploaded successfully'))
