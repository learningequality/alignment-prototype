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

import csv
import json
import os
import random
import subprocess

from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from django.utils.timezone import localtime

from .models import CurriculumDocument, HumanRelevanceJudgment, StandardNode
from .models import Parameter, DataExport, UserProfile


# HIGH LEVEL API
################################################################################


def export_data(drafts=False, includetestdata=False):
    """
    Export the curriculum and human judgment data to be used for ML training.
    """
    exportdirname = timezone.localtime().strftime("%Y%m%d-%H%M")
    export_base_dir = settings.DATA_EXPORT_BASE_DIR
    if not os.path.exists(export_base_dir):
        os.makedirs(export_base_dir)
    exportpath = os.path.join(export_base_dir, exportdirname)
    if not os.path.exists(exportpath):
        os.makedirs(exportpath)

    export_metadata = DataExport.objects.create(exportdirname=exportdirname)

    # PART 1: EXPORT CURRICULUM DATA
    ########################################################################
    if drafts:
        documents = CurriculumDocument.objects.all()
    else:
        documents = CurriculumDocument.objects.filter(is_draft=False)
    #
    all_documents = []
    all_nodes = []
    for document in documents:
        all_documents.append(document)
        root = document.root
        nodes = [root] + list(document.root.get_descendants())
        all_nodes.extend(nodes)

    csvpath1 = os.path.join(exportpath, settings.CURRICULUM_DOCUMENTS_FILENAME)
    export_documents(all_documents, csvpath1)
    csvpath2 = os.path.join(exportpath, settings.STANDARD_NODES_FILENAME)
    export_nodes(all_nodes, csvpath2)

    # PART 2: EXPORT HUMAN JUDGMENTS DATA
    ########################################################################

    all_users = User.objects.filter(profile__exclude=False)
    all_judgments = HumanRelevanceJudgment.objects.filter(user__in=all_users)

    # set the `is_test_data` field for new data
    with transaction.atomic():
        new_feedback_data = all_judgments.filter(is_test_data=None).order_by("?")
        count = new_feedback_data.count()

        test_fraction = float(
            Parameter.objects.get(key="test_size").value
        )  # proportion of new jugments to be kept for test
        test_count = int(test_fraction * count)

        new_ids = list(new_feedback_data.values_list("id", flat=True))

        all_judgments.filter(id__in=new_ids[:test_count]).update(is_test_data=True)
        all_judgments.filter(id__in=new_ids[test_count:]).update(is_test_data=False)

    judgments_test = all_judgments.filter(is_test_data=True)
    judgments_train = all_judgments.filter(is_test_data=False)

    # write out the human judgments for training, and possibly also for testing
    csvpath5 = os.path.join(exportpath, settings.HUMAN_JUDGMENTS_FILENAME)
    export_human_judgments(judgments_train, csvpath5)
    if includetestdata:
        csvpath6 = os.path.join(exportpath, settings.HUMAN_JUDGMENTS_TEST_FILENAME)
        export_human_judgments(judgments_test, csvpath6)

    # export the user profiles
    csvpath7 = os.path.join(exportpath, settings.USERPROFILES_FILENAME)
    export_userprofiles(all_users, csvpath7)

    # update latest symlink
    latestpath = os.path.join(export_base_dir, "latest")
    if os.path.exists(latestpath):
        os.remove(latestpath)
    subprocess.run(["ln", "-s", exportpath, latestpath])

    finished = timezone.now()
    metadata = dict(
        exportdirname=exportdirname,
        drafts=drafts,
        includetestdata=includetestdata,
        finished=localtime(finished).isoformat(),
    )
    with open(os.path.join(exportpath, settings.METADATA_FILENAME), "w") as json_file:
        json.dump(metadata, json_file, indent=2, ensure_ascii=False)

    print("Data export to dir", exportpath, "complete.")
    print("Data base URL: {}/{}".format(settings.DATA_EXPORT_URL, exportdirname))
    export_metadata.finished = finished
    export_metadata.save()
    return exportdirname


# CURRICULUM DOCUMENT CSV EXPORT FORMAT
################################################################################
DOCUMENT_ID_KEY = "document_id"
COUNTRY_KEY = "country"
TITLE_KEY = "title"
DIGITIZATION_METHOD_KEY = "digitization_method"
SOURCE_ID_KEY = "source_id"
SOURCE_URL_KEY = "source_url"
CREATED_KEY = "created"


CURRICULUM_DOCUMENT_HEADER_V0 = [
    DOCUMENT_ID_KEY,
    COUNTRY_KEY,
    TITLE_KEY,
    DIGITIZATION_METHOD_KEY,
    SOURCE_ID_KEY,
    SOURCE_URL_KEY,
    CREATED_KEY,
]


def document_to_rowdict(document):
    datum = {
        DOCUMENT_ID_KEY: document.id,
        COUNTRY_KEY: document.country,
        TITLE_KEY: document.title,
        DIGITIZATION_METHOD_KEY: document.digitization_method,
        SOURCE_ID_KEY: document.source_id,
        SOURCE_URL_KEY: document.source_url,
        CREATED_KEY: str(document.created),
    }
    return datum


def export_documents(documents, csvfilepath):
    """
    Writes the documents data in `documents` to the CSV file at `csvfilepath`.
    """
    with open(csvfilepath, "w") as csv_file:
        csvwriter = csv.DictWriter(csv_file, CURRICULUM_DOCUMENT_HEADER_V0)
        csvwriter.writeheader()
        for document in documents:
            rowdict = document_to_rowdict(document)
            csvwriter.writerow(rowdict)


# STANDARD NODE CSV EXPORT FORMAT
################################################################################
ID_KEY = "id"
# DOCUMENT_ID_KEY = 'document_id'
DEPTH_KEY = "depth"
DIST_FROM_LEAF_KEY = "dist_from_leaf"
PARENT_ID_KEY = "parent_id"
SORT_ORDER_KEY = "sort_order"
IDENTIFIER_KEY = "identifier"
KIND_KEY = "kind"
# TITLE_KEY = 'title'
TIME_UNITS_KEY = "time_units"
NOTES_KEY = "notes"
EXTRA_FIELDS_KEY = "extra_fields"

STANDARD_NODE_HEADER_V0 = [
    ID_KEY,
    DOCUMENT_ID_KEY,
    DEPTH_KEY,
    DIST_FROM_LEAF_KEY,
    PARENT_ID_KEY,
    SORT_ORDER_KEY,
    IDENTIFIER_KEY,
    KIND_KEY,
    TITLE_KEY,
    TIME_UNITS_KEY,
    NOTES_KEY,
    EXTRA_FIELDS_KEY,
]

# TODO: add dist_from_leaf
def dist_from_furthest_leaf(node):
    descendant_data = StandardNode.get_annotated_list(node)
    max_child_level = 0
    for desc in descendant_data:
        item, data = desc
        level = data["level"]
        if level > max_child_level:
            max_child_level = level

    return max_child_level


def node_to_rowdict(node):
    parent_node = node.get_parent()
    datum = {
        ID_KEY: node.id,
        DOCUMENT_ID_KEY: node.document_id,
        DEPTH_KEY: node.depth,
        DIST_FROM_LEAF_KEY: dist_from_furthest_leaf(node),
        PARENT_ID_KEY: parent_node.id if parent_node else None,
        SORT_ORDER_KEY: node.sort_order,
        IDENTIFIER_KEY: node.identifier,
        KIND_KEY: node.kind,
        TITLE_KEY: node.title,
        TIME_UNITS_KEY: node.time_units,
        NOTES_KEY: node.notes,
        EXTRA_FIELDS_KEY: json.dumps(node.extra_fields),
    }
    return datum


def export_nodes(nodes, csvfilepath):
    """
    Writes the standard nodes data in `nodes` to the CSV file at `csvfilepath`.
    """
    with open(csvfilepath, "w") as csv_file:
        csvwriter = csv.DictWriter(csv_file, STANDARD_NODE_HEADER_V0)
        csvwriter.writeheader()
        for node in nodes:
            noderow = node_to_rowdict(node)
            csvwriter.writerow(noderow)


# HUMAN JUDGMENT CSV EXPORT FORMAT
################################################################################
# ID_KEY = 'id'
NODE1_KEY = "node1_id"
NODE2_KEY = "node2_id"
RATING_KEY = "rating"
CONFIDENCE_KEY = "confidence"
MODE_KEY = "mode"
# UI_NAME_KEY = 'ui_name'
# UI_VERSION_HASH_KEY = 'ui_version_hash'
USER_ID_KEY = "user_id"
# CREATED_KEY = 'created'
# EXTRA_FIELDS_KEY = 'extra_fields',

HUMAN_JUDGMENTS_HEADER_V0 = [
    ID_KEY,
    NODE1_KEY,
    NODE2_KEY,
    RATING_KEY,
    CONFIDENCE_KEY,
    MODE_KEY,
    USER_ID_KEY,
    EXTRA_FIELDS_KEY,
]


def human_judgment_to_rowdict(human_judgment):
    datum = {
        ID_KEY: human_judgment.id,
        NODE1_KEY: human_judgment.node1_id,
        NODE2_KEY: human_judgment.node2_id,
        RATING_KEY: human_judgment.rating,
        CONFIDENCE_KEY: human_judgment.confidence,
        MODE_KEY: human_judgment.mode,
        USER_ID_KEY: human_judgment.user_id,
        EXTRA_FIELDS_KEY: json.dumps(human_judgment.extra_fields),
    }
    return datum


def export_human_judgments(human_judgments, csvfilepath):
    """
    Writes the human judgements data to the CSV file at `csvfilepath`.
    """
    with open(csvfilepath, "w") as csv_file:
        csvwriter = csv.DictWriter(csv_file, HUMAN_JUDGMENTS_HEADER_V0)
        csvwriter.writeheader()
        for human_judgment in human_judgments:
            rowdict = human_judgment_to_rowdict(human_judgment)
            csvwriter.writerow(rowdict)


# USERS CSV EXPORT FORMAT
################################################################################
# ID_KEY = 'id'
BACKGROUND_KEY = "background"
SUBJECT_AREAS_KEY = "subject_areas"

USERPROFILES_HEADER_V0 = [ID_KEY, BACKGROUND_KEY, SUBJECT_AREAS_KEY]


def user_to_rowdict(user):
    try:
        profile = user.profile
    except User.profile.RelatedObjectDoesNotExist:
        # create UserProfile if it doesn't exist (e.g. for admin user...)
        profile = UserProfile.objects.create(user=user, background="other")
    subject_areas_str = ",".join([sa.name for sa in user.profile.subject_areas.all()])
    datum = {
        ID_KEY: user.id,
        BACKGROUND_KEY: user.profile.background,
        SUBJECT_AREAS_KEY: subject_areas_str,
    }
    return datum


def export_userprofiles(users, csvfilepath):
    """
    Writes the user profile data to the CSV file at `csvfilepath`.
    """
    with open(csvfilepath, "w") as csv_file:
        csvwriter = csv.DictWriter(csv_file, USERPROFILES_HEADER_V0)
        csvwriter.writeheader()
        for user in users:
            rowdict = user_to_rowdict(user)
            csvwriter.writerow(rowdict)
