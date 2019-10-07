import csv
import json
import os
import random

from django.conf import settings

from .models import CurriculumDocument, HumanRelevanceJudgment


# HIGH LEVEL API
################################################################################

def export_data(dir_name, test_size):
    export_base_dir = settings.DATA_EXPORT_BASE_DIR
    if not os.path.exists(export_base_dir):
        os.makedirs(export_base_dir)
    export_dir = os.path.join(export_base_dir, dir_name)
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)

    # PART 1: EXPORT CURRICULUM DATA
    ########################################################################
    all_documents = []
    all_nodes = []
    all_learning_objectives = []
    documents = CurriculumDocument.objects.filter(is_draft=False)
    for document in documents:
        all_documents.append(document)
        root = document.root
        nodes = [root] + list(document.root.get_descendants())
        all_nodes.extend(nodes)
        for node in nodes:
            all_learning_objectives.extend(list(node.learning_objectives.all()))

    csvpath1 = os.path.join(export_dir, settings.CURRICULUM_DOCUMENTS_FILENAME)
    export_documents(all_documents, csvpath1)
    csvpath2 = os.path.join(export_dir, settings.STANDARD_NODES_FILENAME)
    export_nodes(all_nodes, csvpath2)
    csvpath3 = os.path.join(export_dir, settings.LEARNING_OBJECTIVES_FILENAME)
    export_learning_objectives(all_learning_objectives, csvpath3)


    # PART 2: EXPORT HUMAN JUDGMENTS DATA
    ########################################################################
    judgments_test = list(HumanRelevanceJudgment.objects.filter(is_test_data=True))
    judgments_train = list(HumanRelevanceJudgment.objects.filter(is_test_data=False))
    new_feedback_data = HumanRelevanceJudgment.objects.filter(is_test_data=None)
    for new_datum in new_feedback_data:
        is_test_data = random.random() < test_size
        if is_test_data:
            new_datum.is_test_data = True
            judgments_test.append(new_datum)
        else:
            new_datum.is_test_data = False
            judgments_train.append(new_datum)
    csvpath4 = os.path.join(export_dir, settings.HUMAN_JUDGMENTS_TEST_FILENAME)
    export_human_judgments(judgments_test, csvpath4)
    csvpath5 = os.path.join(export_dir, settings.HUMAN_JUDGMENTS_TRAIN_FILENAME)
    export_human_judgments(judgments_train, csvpath5)
    # TODO: export METADATA_FILENAME = 'metadata.json'
    print('Data export to dir', export_dir, 'comlete.')



# CURRICULUM DOCUMENT CSV EXPORT FORMAT
################################################################################
DOCUMENT_ID_KEY = 'document_id'
COUNTRY_KEY = 'country'
TITLE_KEY = 'title'
DIGITIZATION_METHOD_KEY = 'digitization_method'
SOURCE_ID_KEY = 'source_id'
SOURCE_URL_KEY = 'source_url'
CREATED_KEY = 'created'


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
    with open(csvfilepath, 'w') as csv_file:
        csvwriter = csv.DictWriter(csv_file, CURRICULUM_DOCUMENT_HEADER_V0)
        csvwriter.writeheader()    
        for document in documents:
            rowdict = document_to_rowdict(document)
            csvwriter.writerow(rowdict)
    return csvfilepath



# STANDARD NODE CSV EXPORT FORMAT
################################################################################
ID_KEY = 'id'
# DOCUMENT_ID_KEY = 'document_id'
PARENT_ID_KEY = 'parent_id'
IDENTIFIER_KEY = 'identifier'
KIND_KEY = 'kind'
# TITLE_KEY = 'title'
TIME_UNITS_KEY = 'time_units'
NOTES_KEY = 'notes'
EXTRA_FIELDS_KEY = 'extra_fields'

STANDARD_NODE_HEADER_V0 = [
    ID_KEY,
    DOCUMENT_ID_KEY,
    PARENT_ID_KEY,
    IDENTIFIER_KEY,
    KIND_KEY,
    TITLE_KEY,
    TIME_UNITS_KEY,
    NOTES_KEY,
    EXTRA_FIELDS_KEY,
]

def node_to_rowdict(node):
    parent_node = node.get_parent()
    datum = {
        ID_KEY: node.id,
        DOCUMENT_ID_KEY: node.document_id,
        PARENT_ID_KEY: parent_node.id if parent_node else None,
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
    with open(csvfilepath, 'w') as csv_file:
        csvwriter = csv.DictWriter(csv_file, STANDARD_NODE_HEADER_V0)
        csvwriter.writeheader()    
        for node in nodes:
            noderow = node_to_rowdict(node)
            csvwriter.writerow(noderow)
    return csvfilepath



# LEARNING OBJECTIVE CSV EXPORT FORMAT
################################################################################
STANDARD_NODE_ID_KEY = 'node_id'
# ID_KEY = 'id'
LEARNING_OBJECTIVE_TEXT_KEY = 'text'
LEARNING_OBJECTIVE_KIND_KEY = 'kind'

LEARNING_OBJECTIVE_HEADER_V0 = [
    STANDARD_NODE_ID_KEY,
    ID_KEY,
    LEARNING_OBJECTIVE_TEXT_KEY,
    LEARNING_OBJECTIVE_KIND_KEY,
]

def learning_objective_to_rowdict(learning_objective):
    datum = {
        STANDARD_NODE_ID_KEY: learning_objective.node_id,
        ID_KEY: learning_objective.id,
        LEARNING_OBJECTIVE_TEXT_KEY: learning_objective.text,
        LEARNING_OBJECTIVE_KIND_KEY: learning_objective.kind,
    }
    return datum

def export_learning_objectives(learning_objectives, csvfilepath):
    """
    Writes the learning objectives data to the CSV file at `csvfilepath`.
    """
    with open(csvfilepath, 'w') as csv_file:
        csvwriter = csv.DictWriter(csv_file, LEARNING_OBJECTIVE_HEADER_V0)
        csvwriter.writeheader()    
        for learning_objective in learning_objectives:
            rowdict = learning_objective_to_rowdict(learning_objective)
            csvwriter.writerow(rowdict)
    return csvfilepath



# HUMAN JUDGMENT CSV EXPORT FORMAT
################################################################################
# ID_KEY = 'id'
NODE1_KEY = 'node1_id'
NODE2_KEY = 'node2_id'
RATING_KEY = 'rating'
CONFIDENCE_KEY = 'confidence'
MODE_KEY = 'mode'
# UI_NAME_KEY = 'ui_name'
# UI_VERSION_HASH_KEY = 'ui_version_hash'
# USER_ID_KEY = 'user_id'
# CREATED_KEY = 'created'
# EXTRA_FIELDS_KEY = 'extra_fields', 

HUMAN_JUDGMENTS_HEADER_V0 = [
    ID_KEY,
    NODE1_KEY,
    NODE2_KEY,
    RATING_KEY,
    CONFIDENCE_KEY,
    MODE_KEY,
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
        EXTRA_FIELDS_KEY: json.dumps(human_judgment.extra_fields),
    }
    return datum

def export_human_judgments(human_judgments, csvfilepath):
    """
    Writes the human judgements data to the CSV file at `csvfilepath`.
    """
    with open(csvfilepath, 'w') as csv_file:
        csvwriter = csv.DictWriter(csv_file, HUMAN_JUDGMENTS_HEADER_V0)
        csvwriter.writeheader()    
        for human_judgment in human_judgments:
            rowdict = human_judgment_to_rowdict(human_judgment)
            csvwriter.writerow(rowdict)
    return csvfilepath
