from django.core.management.base import BaseCommand, CommandError
from .needle_old_data import needleImportDatas
from ...views.annotation import import_external_annotations


class Command(BaseCommand):
    help = 'Import Needle Data'

    def handle(self, *args, **options):
        print("do import")
        import_external_annotations(reversed(needleImportDatas), " ")
        print("import done!")
