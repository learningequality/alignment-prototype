import os
import subprocess
import sys

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from alignmentapp.models import CurriculumDocument, StandardNode

from django.core import serializers


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--source_id",
            type=str,
            required=False,
            help="The unique id for this curriculum document",
        )
        parser.add_argument(
            "--country",
            type=str,
            required=False,
            help="Export all documents for this country.",
        )

    def handle(self, *args, **options):
        print("Exporting data fixtures.  options = ", options)
        source_id = options["source_id"]
        country = options["country"]

        if source_id is None and country is None:
            print("Please select what fixtures to export with --source_id or --country")
            documents = CurriculumDocument.objects.all()
            all_countries = set()
            print("Possible arguments for --source_id")
            for document in documents:
                print("  -", document.source_id)
                all_countries.add(document.country)
            print("Possible arguments for --country")
            for c in all_countries:
                print("  >", c)
            sys.exit(1)

        if source_id:
            document = CurriculumDocument.objects.get(source_id=source_id)
            root = document.root
            all_objects = [document, root, *root.get_descendants()]
            data_str = serializers.serialize("json", all_objects)

        elif country:
            documents = CurriculumDocument.objects.filter(country=country)
            all_objects = []
            for document in documents:
                root = document.root
                all_objects.extend([document, root, *root.get_descendants()])
            data_str = serializers.serialize("json", all_objects)

        if country:
            filename_base = country
        else:
            filename_base = source_id

        exportpath = settings.CURRICULUM_DOCS_FIXTURES_DIR
        if not os.path.exists(exportpath):
            os.makedirs(exportpath)
        filename = os.path.join(exportpath, filename_base + ".json")
        with open(filename, "w") as jsonfile:
            jsonfile.write(data_str)

        print("Finished exporting json fixtures to", filename)
