import nbformat
import os
import subprocess
import sys

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from nbconvert.preprocessors import ExecutePreprocessor


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Starting model runs...")
        os.environ["RUNMODE"] = "production"
        base_dir = os.path.join(settings.MEDIA_ROOT, "models")
        model_dirs = os.listdir(base_dir)
        for name in model_dirs:
            print("Preparing to run model {}...".format(name))
            model_path = os.path.join(base_dir, name)
            dirty_path = os.path.join(model_path, "dirty")
            if not os.path.exists(dirty_path):
                print("No updates, skipping.")
                continue
            print("Location:", model_path)
            with open(os.path.join(model_path, "model.ipynb")) as f:
                nb = nbformat.read(f, as_version=4)
            ep = ExecutePreprocessor(timeout=600, kernel_name="python3")
            ep.preprocess(nb, {"metadata": {"path": model_path}})
            os.unlink(dirty_path)
