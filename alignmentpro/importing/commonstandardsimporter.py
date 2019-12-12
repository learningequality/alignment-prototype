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

from commonstandardsproject.models import Jurisdictions, Standards
from alignmentapp.models import CurriculumDocument, StandardNode


# SHARED
################################################################################


def join_standards(standard_ids, identifier, title, notes=""):
    """
    Combine multiple standards subtrees into a single dict tree.
    """
    data = dict(
        identifier=identifier,
        kind="document",
        title=title,
        notes=notes,
        extra_fields={},
    )
    root = dict(data=data, children=[])
    for standard_id, identifier in standard_ids:
        standard = Standards.objects.get(id=standard_id)
        source_identifier = standard.document.get("statementNotation", None)
        if source_identifier:
            print("Replacing source_identifier", source_identifier)
        standard.document["statementNotation"] = identifier
        root["children"].append(standard.to_dicttree())
    return root


def standard_to_standardnode(standard):
    doc = standard.document
    # find title
    if standard.title:
        title = standard.title
    else:
        title = doc.get("description", "no description").replace("\n", " ")
    # find kind
    kind = doc.get("statementLabel", "no statementLabel")
    if kind is None:
        kind = "statementLabel is None"
    # find identifier
    identifier = doc.get("statementNotation", "no identifier")
    if identifier is None:
        identifier = "identifier is None"
    standardnode = dict(kind=kind, identifier=identifier, title=title, extra_fields={})
    extra_props = ["listId", "title", "subject"]
    for extra_prop in extra_props:
        if doc.get(extra_prop):
            standardnode["extra_fields"][extra_prop] = doc.get(extra_prop)
    return standardnode


def transform_subtree(subtree):
    standard = subtree["data"]
    if isinstance(standard, Standards):
        node = standard_to_standardnode(standard)
    else:
        node = standard
    transformed_children = []
    for child in subtree["children"]:
        transformed_child = transform_subtree(child)
        transformed_children.append(transformed_child)
    node["children"] = transformed_children
    return node


def print_commonstandards_tree(root, display_len_limit=None):
    print("COMMON STANDARDS TREE")

    def print_subtree(subtree, indent=0):
        # print(subtree)
        title = subtree["title"]
        if display_len_limit:
            title = title[0:display_len_limit]
        print(
            "   " * indent + " - ",
            "(" + subtree["kind"] + ")",
            "[" + subtree["identifier"] + "]",
            title,
            subtree["extra_fields"],
        )
        for child in subtree["children"]:
            print_subtree(child, indent=indent + 1)

    print_subtree(root)


def drop_titles(tree, titles_to_drop):
    """
    Walk the tree and drop any nodes whose titles are in `titles_to_drop`.
    """

    def _drop_titles(subtree):
        new_children = []
        for child in subtree["children"]:
            if child["title"] in titles_to_drop:
                continue
            else:
                new_child = _drop_titles(child)
                new_children.append(child)
        subtree["children"] = new_children
        return subtree

    return _drop_titles(tree)

# RM unnecessay intermediate nodes
def hoist_unnecessary_tree_nodes(subtree, hoist_titles):
    new_children = []
    for child in subtree["children"]:
        if child["title"] in hoist_titles:
            new_children.extend(child["children"])
        else:
            new_children.append(child)
            hoist_unnecessary_tree_nodes(child, hoist_titles=hoist_titles)
    subtree["children"] = new_children

# Common Core State Standards for Mathematics
################################################################################

COMMON_CORE_JURISDICTION_ID = 62
COMMON_CORE_MATH_ROOTS = [  # pairs of (Standard.id, identifier)
    ("156639", "CCSSM.K"),  # Grade K Common Core Mathematics
    ("154978", "CCSSM.1"),  # Grade 1 Common Core Mathematics
    ("155776", "CCSSM.2"),  # Grade 2 Common Core Mathematics
    ("156415", "CCSSM.3"),  # Grade 3 Common Core Mathematics
    ("155828", "CCSSM.4"),  # Grade 4 Common Core Mathematics
    ("155961", "CCSSM.5"),  # Grade 5 Common Core Mathematics
    ("155177", "CCSSM.6"),  # Grade 6 Common Core Mathematics
    ("156348", "CCSSM.7"),  # Grade 7 Common Core Mathematics
    ("154300", "CCSSM.8"),  # Grade 8 Common Core Mathematics
    (
        "154361",
        "CCSSM.HSN",
    ),  # High School — Number and Quantity Common Core Mathematics
    ("156688", "CCSSM.HSA"),  # High School — Algebra Common Core Mathematics
    ("155892", "CCSSM.HSF"),  # High School — Functions Common Core Mathematics
    ("154902", "CCSSM.HSG"),  # High School — Geometry Common Core Mathematics
    (
        "157364",
        "CCSSM.HSS",
    ),  # High School — Statistics and Probability Common Core Mathematics
    # CCSSM.9-12 is redundant since High-School topics above include the same
    # ("154416", "CCSSM.9-12"),  # Grades 9, 10, 11, 12 Common Core Mathematics
]

CCSSM_DROP_TITLES = ["Standards for Mathematical Practice"]

CCSSM_TO_NODE_KIND_MAPPING = {
    "Domain": "topic",
    "Cluster": "topic",
    "Standard": "unit",
    "Component": "learning_objective",
}

CCSSM_DOCUMENT_ATTRIBUTES = {
    "source_id": "CCSSM",
    "title": "Common Core State Standards for Mathematics",
    "country": "USA",
    "digitization_method": "data_import",
    "source_url": "http://www.corestandards.org/Math/",
    "is_draft": False,
}


def extract_ccssm():
    tree = join_standards(
        COMMON_CORE_MATH_ROOTS,
        identifier="CCSSM",
        title="Common Core State Standards for Mathematics",
    )
    return tree


def infer_ccssm_domain_identifier_from_first_child(subtree):
    if subtree["kind"] == "Domain" and subtree["identifier"] == "no identifier":
        first_child = subtree["children"][0]
        split_identifier = first_child["identifier"].split(".")
        subtree["identifier"] = ".".join(split_identifier[0:-1])
    for child in subtree["children"]:
        infer_ccssm_domain_identifier_from_first_child(child)


def transform_ccssm(tree):
    # convert from {data=Standard, children=[..] } to regular dict tree
    tree2 = transform_subtree(tree)

    # set grade level
    for grade_level in tree2["children"]:
        grade_level["kind"] = "level"

    # Drop repeating 'Standards for Mathematical Practice' (focus on Content)
    tree3 = drop_titles(tree2, CCSSM_DROP_TITLES)

    infer_ccssm_domain_identifier_from_first_child(tree3)

    return tree3


def load_ccssm(transformed_tree):
    try:
        document = CurriculumDocument.objects.get(
            source_id=CCSSM_DOCUMENT_ATTRIBUTES["source_id"]
        )
        document.delete()
    except CurriculumDocument.DoesNotExist:
        pass
    document = CurriculumDocument.objects.create(**CCSSM_DOCUMENT_ATTRIBUTES)

    root = StandardNode.add_root(
        identifier=transformed_tree["identifier"],
        title=transformed_tree["title"],
        kind=transformed_tree["kind"],
        document=document,
    )

    def _add_children_to_parent(parent, children):
        for i, child in enumerate(children):
            sort_order = i + 1
            source_kind = child["kind"]
            if source_kind in CCSSM_TO_NODE_KIND_MAPPING:
                kind = CCSSM_TO_NODE_KIND_MAPPING[source_kind]
            else:
                kind = source_kind
            node = parent.add_child(
                document=parent.document,
                title=child["title"],
                identifier=child["identifier"],
                sort_order=sort_order,
                kind=kind,
            )
            _add_children_to_parent(node, child["children"])

    _add_children_to_parent(root, transformed_tree["children"])


def import_ccssm():
    tree = extract_ccssm()
    transformed_tree = transform_ccssm(tree)
    # print_commonstandards_tree(transformed_tree, display_len_limit=None)
    load_ccssm(transformed_tree)
    print("Finished importing CCSSM")


# Next Generation Science Standards
################################################################################

NEXT_GENERATION_SCIENCE_JURISDICTION_ID = 181
NEXT_GENERATION_SCIENCE_ROOTS = [  # pairs of (Standard.id, identifier)
    ("506764", "NGSS.K"),  #  Grade K Science
    ("505846", "NGSS.1"),  #  Grade 1 Science
    ("505606", "NGSS.2"),  #  Grade 2 Science
    ("506630", "NGSS.3"),  #  Grade 3 Science
    ("505708", "NGSS.4"),  #  Grade 4 Science
    ("506865", "NGSS.5"),  #  Grade 5 Science
    ("506303", "NGSS.MS"),  #  Grades 6, 7, 8 Science
    ("505934", "NGSS.HS"),  #  Grades 9, 10, 11, 12 Science
    ("507222", "NGSS.MS-LS"),  #  Middle School Life Science
    ("506992", "NGSS.MS-PS"),  #  Middle School Physical Science
    ("507105", "NGSS.NG"),  #  Middle school science Science Practices
    ("507165", "NGSS.SEP"),  #  High School Science Science and Engineering Practices
    # ("507019", "NGSS.SCIENCE"),  #   Science
    # ("507090", "NGSS.CC"),  #  Middle School Crosscutting Concepts
    # ("507082", "NGSS.CC"),  #  Crosscutting Concepts Science
    # ("507054", "NGSS.LIFE"),  #  Life Sciences Science
    # ("507073", "NGSS.PRACTICES"),  #   Science Practices
]
NGSS_TO_NODE_KIND_MAPPING = {}

NGSS_DOCUMENT_ATTRIBUTES = {
    "source_id": "NGSS",
    "title": "Next Generation Science Standards",
    "country": "USA",
    "digitization_method": "data_import",
    "source_url": "https://www.nextgenscience.org/sites/default/files/NGSS%20DCI%20Combined%2011.6.13.pdf",
    "is_draft": False,
}

NGSS_DROP_TITLES = [  # these repeat in many places in the hierarchy
    "Science and Engineering Practices",
    "Crosscutting Concepts",
]

NGSS_HOIST_TITLES = [
    "Students who demonstrate understanding can:",
    "Disciplinary Core Ideas",
]


def extract_ngss():
    tree = join_standards(
        NEXT_GENERATION_SCIENCE_ROOTS,
        identifier="NGSS",
        title="Next Generation Science Standards",
    )
    return tree


def transform_ngss(tree):
    # convert from {data=Standard, children=[..] } to regular dict tree
    tree2 = transform_subtree(tree)
    tree3 = drop_titles(tree2, NGSS_DROP_TITLES)

    hoist_unnecessary_tree_nodes(tree3, hoist_titles=NGSS_HOIST_TITLES)

    # Auto assign kinds based on depth in tree
    for grade in tree3["children"]:
        grade["kind"] = "level"
        for topic in grade["children"]:
            if topic["kind"] in ["no statementLabel", "statementLabel is None"]:
                topic["kind"] = "topic"
                for i, lo in enumerate(topic["children"]):
                    if lo["kind"] in ["no statementLabel", "statementLabel is None"]:
                        lo["kind"] = "learning_objective"
                    if lo["identifier"] == "no identifier":
                        lo["identifier"] = topic["identifier"] + "." + str(i + 1)

    return tree3


def load_ngss(transformed_tree):
    try:
        document = CurriculumDocument.objects.get(
            source_id=NGSS_DOCUMENT_ATTRIBUTES["source_id"]
        )
        document.delete()
    except CurriculumDocument.DoesNotExist:
        pass
    document = CurriculumDocument.objects.create(**NGSS_DOCUMENT_ATTRIBUTES)

    root = StandardNode.add_root(
        identifier=transformed_tree["identifier"],
        title=transformed_tree["title"],
        kind=transformed_tree["kind"],
        document=document,
    )

    def _add_children_to_parent(parent, children):
        for i, child in enumerate(children):
            sort_order = i + 1
            source_kind = child["kind"]
            if source_kind in NGSS_TO_NODE_KIND_MAPPING:
                kind = NGSS_TO_NODE_KIND_MAPPING[source_kind]
            else:
                kind = source_kind
            node = parent.add_child(
                document=parent.document,
                title=child["title"],
                identifier=child["identifier"],
                sort_order=sort_order,
                kind=kind,
            )
            _add_children_to_parent(node, child["children"])

    _add_children_to_parent(root, transformed_tree["children"])


def import_ngss():
    tree = extract_ngss()
    transformed_tree = transform_ngss(tree)
    # print_commonstandards_tree(transformed_tree, display_len_limit=90)
    load_ngss(transformed_tree)
    print("Finished importing NGSS")




# CALIFORNIA VOCATIONAL
################################################################################

CALIFORNIA_JURISDICTION_ID = 49
CALIFORNIA_VOCATIONAL_ROOTS = [  # pairs of (Standard.id, identifier)
    # ("116094", "49-116094"),  # Agriculture and Natural Resources
    # ("113743", "49-113743"),  #CTE: Arts, Media, and Entertainment
    # ("116651", "49-116651"),  #CTE: Building and Construction Trades
    ("121067", "bizfinance"),  # CTE: Business and Finance
    # ("115293", "49-115293"),  #CTE: Education, Child Development, and Family Services
    # ("118232", "49-118232"),  #CTE: Energy, Environment, and Utilities
    # ("121690", "49-121690"),  #CTE: Engineering and Architecture
    # ("117571", "49-117571"),  #CTE: Fashion and Interior Design
    # ("122209", "49-122209"),  #CTE: Health Science and Medical Technology
    # ("123466", "49-123466"),  #CTE: Hospitality, Tourism, and Recreation
    ("124793", "infocomtech"),  # CTE: Information and Communication Technologies
    # ("124144", "49-124144"),  #CTE: Manufacturing and Product Development
    # ("122879", "49-122879"),  #CTE: Marketing, Sales, and Service
    # ("125540", "49-125540"),  #CTE: Public Services
    # ("123188", "49-123188"),  #CTE: Transportation
]

CALIFORNIA_VOCATIONAL_HOIST_TITLES = [
    "Knowledge and Performance",
    "Pathway Standards",
]

CALIFORNIA_VOCATIONAL_DOCUMENT_ATTRIBUTES = {
    "source_id": "CA-CTE",
    "title": "California Career Technical Education",
    "country": "USA",
    "digitization_method": "data_import",
    "source_url": "https://www.cde.ca.gov/ci/ct/",
    "is_draft": False,
}

def import_california():
    j = Jurisdictions.objects.get(id=CALIFORNIA_JURISDICTION_ID)
    root_tuples = CALIFORNIA_VOCATIONAL_ROOTS
    tree = join_standards(
        root_tuples,
        identifier="CTE",
        title="California Career Technical Education",
    )

    transformed_tree = transform_subtree(tree)

    # drop empty folders
    transformed_tree = drop_titles(transformed_tree, ['Academics'])

    # set subjects
    for child in transformed_tree['children']:
        child['title'] = child['extra_fields']['subject']

    # set some identifiers
    def _set_identifier_from_listId(subtree):
        if subtree['identifier'] == 'no identifier' and 'listId' in subtree['extra_fields']:
            subtree['identifier'] = subtree['extra_fields']['listId']
        for child in subtree['children']:
            _set_identifier_from_listId(child)
    _set_identifier_from_listId(transformed_tree)

    # hoist non-useful headings
    hoist_unnecessary_tree_nodes(transformed_tree, hoist_titles=CALIFORNIA_VOCATIONAL_HOIST_TITLES)

    # set kinds
    for subject in transformed_tree['children']:
        if subject['kind'] == 'no statementLabel':
            subject['kind'] = 'subject'
        for topic in subject['children']:
            if topic['kind'] == 'no statementLabel':
                topic['kind'] = 'topic'

    print_commonstandards_tree(transformed_tree, display_len_limit=90)
    # return transformed_tree

    try:
        document = CurriculumDocument.objects.get(
            source_id=CALIFORNIA_VOCATIONAL_DOCUMENT_ATTRIBUTES["source_id"]
        )
        document.delete()
    except CurriculumDocument.DoesNotExist:
        pass
    document = CurriculumDocument.objects.create(**CALIFORNIA_VOCATIONAL_DOCUMENT_ATTRIBUTES)

    root = StandardNode.add_root(
        identifier=transformed_tree["identifier"],
        title=transformed_tree["title"],
        kind=transformed_tree["kind"],
        document=document,
    )

    def _add_children_to_parent(parent, children):
        for i, child in enumerate(children):
            sort_order = i + 1
            node = parent.add_child(
                document=parent.document,
                title=child["title"],
                identifier=child["identifier"],
                sort_order=sort_order,
                kind=child["kind"],
            )
            _add_children_to_parent(node, child["children"])

    _add_children_to_parent(root, transformed_tree["children"])
    print("Finished importing California vocational standards")


