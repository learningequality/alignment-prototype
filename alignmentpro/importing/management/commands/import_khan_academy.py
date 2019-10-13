import json
import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from alignmentapp.models import CurriculumDocument, HumanRelevanceJudgment, StandardNode


this_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.abspath(os.path.join(this_dir, '..', '..', 'data'))


def get_node(data, parent=None, user=None):

    kind = data['kind']

    if kind == 'video':
        # Don't make a standard node for videos
        return None

    if kind == 'exercise' and parent and user:
        if len(data['tags']) == 0:
            # print("Exercise {} doesn't have a standard associated with it".format(data))
            return None
        exercise_slugs = parent.extra_fields.get('exercise_slugs', [])
        exercise_slugs.append( data['slug'] )
        parent.extra_fields['exercise_slugs'] = exercise_slugs
        parent.save()
        standard = data['tags'][0]
        # The KA standard name uses a slightly different structure than the CCSSM docs,
        # so convert it to the CCSSM format for searching.
        standard = 'CCSS.' + standard.replace('.CC', '.Content', 1)
        ccs_query = StandardNode.objects.filter(identifier=standard)
        num_results = ccs_query.count()
        if num_results == 1:
            ccs = ccs_query.first()
            HumanRelevanceJudgment.objects.create(
                user=user, node1=ccs, node2=parent, rating=1.0, confidence=1.0
            )
        elif num_results == 0:
            print("No standard found in CCSSM tree for {}".format(standard))

        assert num_results <= 1, "Multiple StandardNodes found for identifier: {}".format(data['tags'][0])

        # Don't make a standard node for the actual exercise
        return None

    identifier = None
    if 'source_id' in data:
        identifier = data['source_id']
    elif 'slug' in data:
        identifier = data['slug']

    assert identifier, "No identifier found for {}".format(data)

    node = parent.add_child(document=parent.document,
                            title=data['title'],
                            identifier=identifier,
                            kind=kind,
                            notes=data.get('description', ''),
                            )

    return node

def get_node_data_recursive(data, level=0, parent=None, user=None):
    if level >= 5:
        return

    kind = data['kind']
    # Use KA's own type structure
    if level == 0:
        data['kind'] = 'Domain'
    elif level == 1:
        data['kind'] = 'Subject'
        print('Processing Subject=', data['title'])
    elif level == 2:
        data['kind'] = 'Topic'
    elif level == 3:
        data['kind'] = 'Tutorial'

    if 'India' in data['title'] or 'Eureka' in data['title'] or 'ICSE' in data['title']:
        print('skipping', data['title'])
        return
    else:
        node = get_node(data, parent, user)
        if node and 'children' in data:
            for child in data['children']:
                get_node_data_recursive(child, level+1, node, user)


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Importing Khan Academy topic tree from khan_academy_ricecooker_tree.json...")
        filename = os.path.join(data_dir, 'khan_academy_ricecooker_tree.json')
        root_node = json.loads(open(filename).read(), encoding='utf-8')

        source_id = "khan_academy_us"
        topic = "Khan Academy Standards-based Curriculum"
        country = "USA"
        digitization_method = "data_import"
        draft = True

        ka_user, _created = User.objects.get_or_create(username='khan_academy_org')

        try:
            existing_doc = CurriculumDocument.objects.get(source_id=source_id)
            # this will delete all children and also learning objectives due to cascade delete
            existing_doc.delete()
        except CurriculumDocument.DoesNotExist:
            pass

        ka_judgments = HumanRelevanceJudgment.objects.filter(user=ka_user)
        ka_judgments.delete()

        document = CurriculumDocument.objects.create(
            source_id=source_id,
            title=topic,
            country=country,
            digitization_method=digitization_method,
            is_draft=draft,
        )
        root = StandardNode.add_root(title=topic, identifier='KA-en', kind='channel', document=document)
        for domain in root_node['children']:
            get_node_data_recursive(domain, parent=root, user=ka_user)
