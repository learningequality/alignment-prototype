import subprocess
import sys

from django.core.management import call_command
from django.core.management.base import BaseCommand

from alignmentapp.models import CurriculumDocument, StandardNode
from alignmentapp.exporting import export_data


class Command(BaseCommand):
    """
    Export training data to local disk (in timestamped folder) to be used for ML.
    """

    def add_arguments(self, parser):
        parser.add_argument("--drafts", action="store_true")
        parser.add_argument("--includetestdata", action="store_true")

    def handle(self, *args, **options):
        print("Starting data export...")
        exportdir = export_data(
            drafts=options["drafts"], includetestdata=options["includetestdata"]
        )
        print("Data exported to directory", exportdir)
