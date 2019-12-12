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

import sys

from django.core.management import call_command
from django.core.management.base import BaseCommand

from alignmentapp.management.commands.printtree import get_tree_as_markdown


from importing.csvutils import load_curriculum_list
from importing.csvutils import (
    DEPTH_KEY,
    IDENTIFIER_KEY,
    KIND_KEY,
    TITLE_KEY,
    TIME_UNITS_KEY,
    NOTES_KEY,
)
from alignmentapp.models import CurriculumDocument, StandardNode


class Command(BaseCommand):
    """
    Import a chunk from a curriculum document.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--gsheet_id", help="Google spreadsheets sheet ID (must be world-readable)"
        )
        parser.add_argument(
            "--gid", help="The gid argument to indicate which sheet", default="0"
        )
        parser.add_argument(
            "--source_id",
            type=str,
            required=True,
            help="The unique id for this curriculum document",
        )
        parser.add_argument(
            "--digitization_method", type=str, help="How was the gsheet created?"
        )
        parser.add_argument(
            "--draft", type=bool, default=True, help="Set to false when ready."
        )
        # for documents:
        parser.add_argument("--title", type=str)
        parser.add_argument("--country", type=str)
        # for chunk:
        parser.add_argument(
            "--startat", type=str, help="Where to start reading form the sheet."
        )
        parser.add_argument(
            "--stopat", type=str, help="Last row to read form the sheet."
        )
        parser.add_argument(
            "--addafter",
            type=str,
            help="StandardNode.id after which we should add this chunk.",
        )

    def handle(self, *args, **options):
        print("Handling importchunk with options = ", options)
        source_id = options["source_id"]
        digitization_method = options["digitization_method"] or "unknown"
        title = options.get("title", "Unknown title")
        country = options["country"] or "Unknown"
        draft = options["draft"]

        try:
            document = CurriculumDocument.objects.get(source_id=source_id)
            if document.is_draft:
                print("Deleting old draft verison of curriculum document...")
                document.delete()
            else:
                print('ERROR: document is no longer in draft state so cannot be updated.')
                sys.exit(1)
        except CurriculumDocument.DoesNotExist:
            pass

        document = CurriculumDocument.objects.create(
            source_id=source_id,
            title=title,
            country=country,
            digitization_method=digitization_method,
            is_draft=draft,
        )
        root = StandardNode.add_root(title=title, document=document)

        curriculum_list = load_curriculum_list(options["gsheet_id"], options["gid"])

        nodes_breadcrumbs = [root, None]
        node_counts = [None, 0]
        cur_level = 1
        for row in curriculum_list:
            assert len(node_counts) == cur_level+1, 'wrong node_counts'
            assert len(nodes_breadcrumbs) == cur_level+1, 'wrong nodes_breadcrumbs'

            # staying at the same level
            if row["level"] == cur_level:
                pass

            # going deeper (add a child to current leaf)
            elif row["level"] > cur_level:
                if not (row["level"] - 1 == cur_level):
                    print("ERR too many indentnts at \n", list(row.values()))
                    sys.exit(1)
                cur_level = row["level"]
                nodes_breadcrumbs.append(None)
                node_counts.append(0)

            # popping out (add a child to parent at level)
            elif row["level"] < cur_level:
                cur_level = row["level"]
                nodes_breadcrumbs = nodes_breadcrumbs[0:cur_level+1]
                node_counts = node_counts[0:cur_level+1]

            # Add the node to the appropriate location
            parent = nodes_breadcrumbs[cur_level - 1]
            node_counts[cur_level] += 1
            node = parent.add_child(
                document=parent.document,
                title=row[TITLE_KEY],
                identifier=row[IDENTIFIER_KEY],
                sort_order=node_counts[cur_level],
                kind=row[KIND_KEY],
                time_units=float(row[TIME_UNITS_KEY]) if row[TIME_UNITS_KEY] else None,
                notes=row[NOTES_KEY] or '',
            )
            nodes_breadcrumbs[cur_level] = node

        print("Import finished")
        print(get_tree_as_markdown(root, {}))

