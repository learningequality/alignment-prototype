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
