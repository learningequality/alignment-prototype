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

from django.core.management import call_command
from django.core.management.base import BaseCommand

from alignmentapp.models import CurriculumDocument, StandardNode


def get_tree_as_markdown(root, options):
    lines = []

    def get_subtree_as_markdown(lines, subtree, indent=0):
        line = ""
        line += "   " * indent + " - "
        line += " (" + subtree.kind + ")"
        if options.get("short_identifiers", False):
            line += " [" + subtree.identifier[-7:] + "] "
        else:
            line += " [" + subtree.identifier + "] "
        line += subtree.title + " "
        if subtree.notes:
            line += 'notes= ' + str(subtree.notes.replace('\n', ' '))
        if subtree.extra_fields:
            line += str(subtree.extra_fields)
        lines.append(line)
        for child in subtree.get_children():
            get_subtree_as_markdown(lines, child, indent=indent + 1)

    get_subtree_as_markdown(lines, root)
    return "\n".join(lines)


def get_document_header(document):
    md_str = ""
    md_str += "# " + document.title + "\n\n"
    md_str += "source_id: " + document.source_id + "  \n"
    md_str += "is_draft: " + str(document.is_draft) + "  \n"
    md_str += "country: " + document.country + "  \n"
    md_str += "digitization_method: " + document.digitization_method + "\n\n"
    return md_str


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
        parser.add_argument("--short_identifiers", action="store_true")
        parser.add_argument("--format", default="html")

    def handle(self, *args, **options):
        print("Handling printtree with options = ", options)
        source_id = options["source_id"]
        country = options["country"]

        if source_id is None and country is None:
            print("Please select what to print with --source_id or --country")
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
            md_str = get_document_header(document)
            md_str += get_tree_as_markdown(root, options)
            print(md_str)

        if country:
            documents = CurriculumDocument.objects.filter(country=country)
            md_str = ""
            for document in documents:
                root = document.root
                md_str += get_document_header(document)
                md_str += get_tree_as_markdown(root, options)
                md_str += "\n\n\n"

        if options["format"] == "html":
            if country:
                filename_base = country
            else:
                filename_base = source_id
            mdfilename = filename_base + ".md"
            htmlfilename = filename_base + ".html"
            with open(mdfilename, "w") as mdfile:
                mdfile.write(md_str)
                mdfile.close()
                subprocess.run(
                    [
                        "pandoc",
                        "--from",
                        "gfm",
                        mdfilename,
                        "--standalone",
                        "-o",
                        htmlfilename,
                    ]
                )
                subprocess.run(["rm", mdfilename])
