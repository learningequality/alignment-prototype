import sys

from django.core.management import call_command
from django.core.management.base import BaseCommand


from importing.csvutils import load_curriculum_list
from importing.csvutils import (
    DEPTH_KEY,
    IDENTIFIER_KEY,
    KIND_KEY,
    TITLE_KEY,
    LEARNING_OBJECTIVES_KEY,
    TIME_UNITS_KEY,
    NOTES_KEY,
)
from alignmentapp.models import CurriculumDocument, StandardNode, LearningObjective



class Command(BaseCommand):
    """
    Import a chunk from a curriculum document.
    """

    def add_arguments(self, parser):
        parser.add_argument('--gsheet_id', help='Google spreadsheets sheet ID (must be world-readable)')
        parser.add_argument('--gid', help='The gid argument to indicate which sheet', default='0')
        parser.add_argument("--source_id", type=str, required=True, help='The unique id for this curriculum document')
        parser.add_argument("--digitization_method", type=str, help='How was the gsheet created?')
        parser.add_argument("--draft", type=bool, default=True, help='Set to false when ready.')
        # for documents:
        parser.add_argument("--title", type=str)
        parser.add_argument("--country", type=str)
        # for chunk:
        parser.add_argument("--startat", type=str, help='Where to start reading form the sheet.')
        parser.add_argument("--stopat", type=str, help='Last row to read form the sheet.')
        parser.add_argument("--addafter", type=str, help='StandardNode.id after which we should add this chunk.')


    def handle(self, *args, **options):
        print('Handling importchunk with options = ', options)
        source_id = options["source_id"]
        digitization_method = options["digitization_method"] or "unknown"
        title = options.get("title", "Unknown title")
        country = options["country"] or "Unknown"
        draft = options["draft"]

        document, created = CurriculumDocument.objects.get_or_create(
            source_id=source_id,
            title=title,
            country=country,
            digitization_method=digitization_method,
            is_draft=draft
        )
        if created:
            root = StandardNode.add_root(title=title, document=document)
        else:
            root = document.root

        
        curriculum_list = load_curriculum_list(options['gsheet_id'], options['gid'])

        nodes_breadcrumbs = [root]
        node_counts = [0]
        cur_level = 0
        for row in curriculum_list:
            print('Porcessing row', '  '*row['level']+'-', row[IDENTIFIER_KEY], row[TITLE_KEY])

            # staying (add a child to current parent)
            if row['level'] == cur_level:
                node_counts[cur_level] += 1
                parent = nodes_breadcrumbs[cur_level-1]
                node = _add_row_to_parent(parent, row, sort_order=node_counts[cur_level])
                if row[LEARNING_OBJECTIVES_KEY]:
                    _add_learning_objectives(node, row[LEARNING_OBJECTIVES_KEY])
                nodes_breadcrumbs[cur_level] = node
                
            # going deeper (add a child to current leaf)
            elif row['level'] > cur_level:
                parent = nodes_breadcrumbs[cur_level]
                node = _add_row_to_parent(parent, row, sort_order=node_counts[cur_level])
                if row[LEARNING_OBJECTIVES_KEY]:
                    _add_learning_objectives(node, row[LEARNING_OBJECTIVES_KEY])
                nodes_breadcrumbs.append(node)
                node_counts.append(1)
                cur_level += 1

            # popping out (add a child to parent at level)
            elif row['level'] < cur_level:
                new_level = row['level']
                parent = nodes_breadcrumbs[new_level-1]
                node_counts[new_level] += 1
                node = _add_row_to_parent(parent, row, sort_order=node_counts[new_level])
                if row[LEARNING_OBJECTIVES_KEY]:
                    _add_learning_objectives(node, row[LEARNING_OBJECTIVES_KEY])
                nodes_breadcrumbs = nodes_breadcrumbs[0:new_level] + [node]
                node_counts = node_counts[0:new_level+1]
                cur_level = new_level

        print('Import finished')



def _add_row_to_parent(parent, row, sort_order=1):
    node = parent.add_child(
        document=parent.document,
        title=row[TITLE_KEY],
        identifier=row[IDENTIFIER_KEY],
        sort_order=sort_order,
        kind=row[KIND_KEY],
        time_units=float(row[TIME_UNITS_KEY]) if row[TIME_UNITS_KEY] else None,
        notes=row[NOTES_KEY],
    )
    return node

def _add_learning_objectives(node, learning_objectives_paragraph):
    lines = learning_objectives_paragraph.splitlines()
    for line in lines:
        text = line.lstrip(' -\t').rstrip(' ,.')
        LearningObjective.objects.create(node=node, text=text)
