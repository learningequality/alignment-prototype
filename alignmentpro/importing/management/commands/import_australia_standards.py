import glob
import json
import os
import re
import textwrap

from django.core.management.base import BaseCommand

import xmltodict

from alignmentapp.models import CurriculumDocument, StandardNode


this_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.abspath(os.path.join(this_dir, '..', '..', 'data'))


def get_topic_children_recursive(parent, topics_list):
    """
    The XML document stores the standards as a flat list and uses IDs to identify parent and
    child relationships. This function converts this list into a tree recursively.
    :param parent: Parent item to check for children
    :param topics_list: Complete, flat list of standard topics with IDs as keys.
    """
    if 'gem:hasChild' in parent:
        children = parent['gem:hasChild']
        # if there's a single child, it's a dict, but if there are
        # multiple children, it's an array...
        if isinstance(children, dict):
            children = [children]
        for resource in children:
            id = resource['@rdf:resource']
            if not 'children' in parent:
                parent['children'] = []
            child = topics_list[id]
            if not child in parent['children']:
                parent['children'].append(child)
                get_topic_children_recursive(child, topics_list)


def get_topic_hierarchy(data):
    """
    Get the flat list of topics from the XML file, then convert it into a hierarchical tree representation.
    :param data: XML data converted to a Python dict format by xmltodict.
    :return:
    """
    topics_list = data['rdf:RDF']['rdf:Description']
    topics = {}
    for topic in topics_list:
        topics[topic['@rdf:about']] = topic

    # root topics are ones whose 'parent' is the standard itself, and the standard's ID
    # is external to this document. So if we can't find the parent's ID in the doc, it's
    # a root topic.
    root_topics = []
    for topic_id in topics:
        topic = topics[topic_id]
        parents = topic['gem:isChildOf']
        if isinstance(parents, dict):
            parents = [parents]
        for parent in parents:
            parent_id = parent['@rdf:resource']
            if not parent_id in topics:
                root_topics.append(topic)

    for root in root_topics:
        get_topic_children_recursive(root, topics)

    return root_topics


def add_standard(subject_json, parent, indent=0):
    try:
        kind = subject_json['asn:statementLabel']['#text']
        # the tree has two organizations, one by year level, and another by
        # strand. They are the same data
        if kind == 'Strand':
            return
        if 'dct:title' in subject_json:
            title = subject_json['dct:title']['#text']
            # For achievement standards, the title is just "Achievement Standard", but the description
            # is where the actual data is. So merge the title and description in this case.
            if title == "Achievement Standard":
                title = title + ": " + re.sub('<[^<]+?>', '', subject_json['dct:description']['#text'])
        else:
            title = re.sub('<[^<]+?>', '', subject_json['dct:description']['#text'])

        if kind == "Content description":
            kind = "content"

        print("{}{}".format(" " * indent, textwrap.shorten(title, 80)))

        node = parent.add_child(document=parent.document,
                         title=title,
                         identifier=subject_json["@rdf:about"],
                         kind=kind
        )
        if 'children' in subject_json:
            for child in subject_json['children']:
                add_standard(child, parent=node, indent=indent + 2)
    except:
        print("Error adding object, keys = {}".format(list(subject_json.keys())))
        raise


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        Imports Australian curriculum standards into the alignment prototype database.

        This command expects to find rdf files named "<subject grades>.rdf" (e.g. "Mathematics F-10.rdf") in the
        alignmentpro/importing/data/australia_standards directory. These files can be retrieved from:

        http://rdf.australiancurriculum.edu.au/

        Currently, this function accepts no arguments.
        """
        standards_dir = os.path.join(data_dir, 'australia_standards')
        for afile in glob.glob(os.path.join(standards_dir, '*.rdf')):
            basename = os.path.basename(afile)
            topic = os.path.splitext(basename)[0]
            with open(afile, encoding='utf-8') as doc:
                data = xmltodict.parse(doc.read())
                json_file = os.path.join(standards_dir, basename + ".json")
                f = open(json_file, 'w', encoding='utf-8')
                f.write(json.dumps(data, ensure_ascii=False, indent=2))
                f.close()
                # continue

                source_id = "australia_standards_{}".format(topic.lower().replace(" ", "_"))
                country = "Australia"
                digitization_method="data_import"
                draft = True

                # For now, clean out old runs so we don't proliferate the db.
                try:
                    existing_doc = CurriculumDocument.objects.get(source_id=source_id)
                    # this will delete all children and also learning objectives due to cascade delete
                    existing_doc.delete()
                except CurriculumDocument.DoesNotExist:
                    pass

                document = CurriculumDocument.objects.create(
                    source_id=source_id,
                    title=topic,
                    country=country,
                    digitization_method=digitization_method,
                    is_draft=draft,
                )

                root = StandardNode.add_root(title=topic, kind='document', document=document)
                topic_tree = get_topic_hierarchy(data)
                for subject in topic_tree:
                    add_standard(subject, parent=root)