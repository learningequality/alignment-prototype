from commonstandardsproject.models import Jurisdictions, Standards


# SHARED
################################################################################

def join_standards(standard_ids, identifier, title, notes=''):
    """
    Combine multiple standards subtrees into a single dict tree.
    """
    data = dict(
        identifier=identifier,
        kind='document',
        title=title,
        notes=notes,
        extra_fields={},
    )
    root = dict(
        data=data,
        children=[],
    )
    for standard_id, identifier in standard_ids:
        standard = Standards.objects.get(id=standard_id)
        source_identifier = standard.document.get('statementNotation', None)
        if source_identifier:
            print('Replacing source_identifier', source_identifier)
        standard.document['statementNotation'] = identifier
        root['children'].append(standard.to_dicttree())
    return root

def standard_to_standardnode(standard):
    doc = standard.document
    # find title
    if standard.title:
        title = standard.title
    else:
        title = doc.get('description', 'no description').replace('\n', ' ')
    # find kind
    kind = doc.get('statementLabel', 'no statementLabel')
    if kind is None:
        kind = 'statementLabel is None'
    # find identifier
    identifier=doc.get('statementNotation', 'no identifier')
    if identifier is None:
        identifier = 'identifier is None'
    standardnode = dict(
        kind=kind,
        identifier=identifier,
        title=title,
        extra_fields={}
    )
    extra_props = ['listId', 'title']
    for extra_prop in extra_props:
        if doc.get(extra_prop):
            standardnode['extra_fields'][extra_prop]=doc.get(extra_prop)
    return standardnode


def print_commonstandards_tree(root, display_len_limit=None):
    print('COMMON STANDARDS TREE')

    def print_subtree(subtree, indent=0):
        # print(subtree)
        title = subtree['title']
        if display_len_limit:
            title = title[0:display_len_limit]
        print('   '*indent + ' - ',
              '(' + subtree['kind'] + ')',
              '[' + subtree['identifier'] + ']',
              title,
              subtree['extra_fields'],
        )
        for child in subtree['children']:
            print_subtree(child, indent=indent+1)
    print_subtree(root)






# Common Core State Standards for Mathematics
################################################################################

COMMON_CORE_JURISDICTION_ID = 62
COMMON_CORE_MATH_ROOTS = [     # pairs of (Standard.id, identifier)
    ("156639", "CCSSM.K"),  # Grade K Common Core Mathematics
    ("154978", "CCSSM.1"),  # Grade 1 Common Core Mathematics
    ("155776", "CCSSM.2"),  # Grade 2 Common Core Mathematics
    ("156415", "CCSSM.3"),  # Grade 3 Common Core Mathematics
    ("155828", "CCSSM.4"),  # Grade 4 Common Core Mathematics
    ("155961", "CCSSM.5"),  # Grade 5 Common Core Mathematics
    ("155177", "CCSSM.6"),  # Grade 6 Common Core Mathematics
    ("156348", "CCSSM.7"),  # Grade 7 Common Core Mathematics
    ("154300", "CCSSM.8"),  # Grade 8 Common Core Mathematics
    ("154416", "CCSSM.9-12"),  # Grades 9, 10, 11, 12 Common Core Mathematics
    ("154361", "CCSSM.HSN"),  # High School — Number and Quantity Common Core Mathematics
    ("156688", "CCSSM.HSA"),  # High School — Algebra Common Core Mathematics
    ("155892", "CCSSM.HSF"),  # High School — Functions Common Core Mathematics
    ("154902", "CCSSM.HSG"),  # High School — Geometry Common Core Mathematics
    ("157364", "CCSSM.HSS"),  # High School — Statistics and Probability Common Core Mathematics
]


def extract_ccssm():
    tree = join_standards(
        COMMON_CORE_MATH_ROOTS,
        identifier='CCSSM',
        title='Common Core State Standards for Mathematics',
    )
    return tree

def transform_cssm(tree):

    def _transform_subtree(subtree):
        standard = subtree['data']
        if isinstance(standard, Standards):
            node = standard_to_standardnode(standard)
        else:
            node = standard
        transformed_children = []
        for child in subtree['children']:
            transformed_child = _transform_subtree(child)
            transformed_children.append(transformed_child)
        node['children'] = transformed_children
        return node
    
    tree2 = _transform_subtree(tree)

    # set grade level
    for grade_level in tree2['children']:
        grade_level['kind'] = 'level'

    return tree2


def load_cssm(transformed_tree):
    pass

def import_ccssm():
    tree = extract_ccssm()
    transformed_tree = transform_cssm(tree)
    print_commonstandards_tree(transformed_tree, display_len_limit=None)
    load_cssm(transformed_tree)


# Next Generation Science Standards
################################################################################

NEXT_GENERATION_SCIENCE_JURISDICTION_ID = 181
NEXT_GENERATION_SCIENCE_ROOTS = [     # pairs of (Standard.id, identifier)
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




# Common Core English/Language Arts
################################################################################

COMMON_CORE_JURISDICTION_ID = 62
COMMON_CORE_LANGUAGE = [
    # ("157732", ""),  #  Kindergarten Arte Lenguaje en Español
    # ("157494", ""),  #  Primer Grado Arte Lenguaje en Español
    # ("157623", ""),  #  Segundo Grado Arte Lenguaje en Español
    ("156027", " Grade K Common Core English/Language Arts"),  #  Grade K Common Core English/Language Arts
    ("155249", " Grade 1 Common Core English/Language Arts"),  #  Grade 1 Common Core English/Language Arts
    ("155027", " Grade 2 Common Core English/Language Arts"),  #  Grade 2 Common Core English/Language Arts
    ("156181", " Grade 3 Common Core English/Language Arts"),  #  Grade 3 Common Core English/Language Arts
    ("155412", " Grade 4 Common Core English/Language Arts"),  #  Grade 4 Common Core English/Language Arts
    ("156478", " Grade 5 Common Core English/Language Arts"),  #  Grade 5 Common Core English/Language Arts
    ("156951", " Grade 6 Common Core English/Language Arts"),  #  Grade 6 Common Core English/Language Arts
    ("156747", " Grade 7 Common Core English/Language Arts"),  #  Grade 7 Common Core English/Language Arts
    ("157158", " Grade 8 Common Core English/Language Arts"),  #  Grade 8 Common Core English/Language Arts
    ("154699", " Grades 9, 10 Common Core English/Language Arts"),  #  Grades 9, 10 Common Core English/Language Arts
    ("155575", " Grades 11, 12 Common Core English/Language Arts"),  #  Grades 11, 12 Common Core English/Language Arts
    # ("157454", " 6-8 English Language Arts - History/Social Studies"),  #  6-8 English Language Arts - History/Social Studies
    # ("157469", " 6-8 English Language Arts - Writing (History/Social Studies, Science, & Technical Subjects)"),  #  6-8 English Language Arts - Writing (History/Social Studies, Science, & Technical Subjects)
    # ("157438", " 6-8  English Language Arts - Science and Technical Subjects"),  #  6-8  English Language Arts - Science and Technical Subjects
    # ("157423", " Grade 9-10 English Language Arts - Science and Technical Subjects"),  #  Grade 9-10 English Language Arts - Science and Technical Subjects
]

