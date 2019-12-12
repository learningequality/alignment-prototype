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

import json
import nbformat
import os
import subprocess
import sys

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from ...evaluators import ranking


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Starting model evaluations...")
        os.environ["RUNMODE"] = "production"
        base_dir = os.path.join(settings.MEDIA_ROOT, "models")
        model_dirs = os.listdir(base_dir)
        for name in model_dirs:
            print("Preparing to evaluate model {}...".format(name))
            model_path = os.path.join(base_dir, name)
            dirty_path = os.path.join(model_path, "dirty")
            if os.path.exists(dirty_path):
                print("Model is dirty! Skipping.")
                continue
            scores = ranking(name)
            with open(os.path.join(model_path, "scores.json"), "w") as f:
                json.dump(scores, f, indent=4)
