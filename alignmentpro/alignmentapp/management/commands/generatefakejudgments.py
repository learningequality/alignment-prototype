import subprocess
import sys
import random

from django.core.management import call_command
from django.core.management.base import BaseCommand

from alignmentapp.models import CurriculumDocument, StandardNode, HumanRelevanceJudgment


class Command(BaseCommand):
    """
    Export training data to local disk (in timestamped folder) to be used for ML.
    """

    def add_arguments(self, parser):
        parser.add_argument("--number", type=int, default=1000)

    def handle(self, *args, **options):
        print("Generating fake human judgments data...")
        
        for i in range(options['number']):
            n1, n2 = StandardNode.objects.all().order_by("?")[:2]
            e = HumanRelevanceJudgment(node1=n1, node2=n2, rating=random.random())
            e.save()
        print("Fake judgements created")