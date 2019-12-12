##################################################
# MIT License
#
# Copyright (c) 2019 Learning Equality
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
##################################################

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