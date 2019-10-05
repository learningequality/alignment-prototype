
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Q
from treebeard.mp_tree import MP_Node



# CURRICULUM DOCUMENTS
################################################################################

DIGITIZATION_METHODS = [
    ('manual_entry', 'Manual data entry'),
    ('scan_manual', 'Curriculum manually extracted from OCR'),
    ('automated_scan', 'Automated stucture extraction via OCR'),
    ('website_scrape', 'Curriculum scraped from website'),
    ('data_import', 'Curriculum imported from data'),
]

class CurriculumDocument(models.Model):
    """
    Stores the metadata for a curriculum document, e.g. KICD standards for math.
    """
    # id = auto-incrementing integet primary key
    source_id = models.CharField(max_length=200, help_text="A unique identifier for the source document")
    title = models.CharField(max_length=200)
    country = models.CharField("Country", max_length=200)
    digitization_method = models.CharField(choices=DIGITIZATION_METHODS, max_length=200, help_text="Digitization method")
    source_url = models.CharField(max_length=200, help_text="URL of source used for this document")
    # root = reverse relation on StandardNode.document
    created = models.DateTimeField(auto_now_add=True)
    #? modified = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True,
        help_text="True for most recent version of the curriculum data for a given source_id.")




# CURRICULUM DATA
################################################################################

NODE_KINDS = [
    ('document', 'Curriculum document node'),       # the root node for the document (self.title == self.document.title)
    # ('langauge', 'Language of content '),         # language subdivision
    ('level', 'Grade level or age group'),          # level-based grouping
    ('subject', 'Subject matter'),                  # e.g. Math, Phyiscis, IT, etc.
    ('topic', 'Subject, section, or subsection'),   # structural elements (sections and subsections)
    ('unit', 'Standard entry'),                     # Individual standard entries with LOs
    # ('learning_objective', see node.learning_objectives
]

class StandardNode(MP_Node):
    """
    The individual elements of a curriculum structure.
    """
    # id = auto-incrementing integet primary key
    # path = inherited from MP_Node, e.g. ['0001'] for root node of tree_id 0001
    document = models.ForeignKey('CurriculumDocument', related_name='root', on_delete=models.CASCADE)
    identifier = models.CharField(max_length=20)
    # source_id / source_url ?
    kind = models.CharField(max_length=20, choices=NODE_KINDS, default='entry')
    title = models.CharField(max_length=400)
    sort_order = models.FloatField(default=1.0)
    node_order_by = ['sort_order']  # the order of children within parent node
    # learning_objectives = reverse relation on LearningObjective.node

    # domain-specific 
    time_units = models.FloatField(blank=True, null=True,
        help_text="A numeric value ~ to the hours of instruction for this unit")
    notes = models.TextField(help_text="A numeric value ~ to the hours of instruction for this unit")
    extra_fields = JSONField(blank=True, null=True)  # basic model extensibility w/o changing base API


    # Human relevance jugments on edges between nodes
    def get_judgments(self):
        return HumanRelevanceJudgment.objects.filter(Q(node1=self) | Q(node2=self))
        #   == self._relations.filter(Q(node1=self) | Q(node2=self))
    judgments = property(get_judgments)
    # implementation details
    _relations = models.ManyToManyField('self',
        through='HumanRelevanceJudgment',
        through_fields=('node1', 'node2'),
        symmetrical=False)  # this means a human relatedness jugement edge could
                            # be attached from one end (self==e.node1) the another
                            # (self==e.node2) so we won't access _relations directly

    def __repr__(self):
        return '<StandardNode: {} {}>'.format(self.identifier, self.title)

    class Meta:
        unique_together = ['document', 'path']  # so document 1-to-1 with MP_Node tree


class LearningObjective(MP_Node):
    """
    Individual lerning objectives statements associated with a curriculum unit,
    e.g., "Describe the reaction between a given metal and metal oxide"
    or "solving quadratic equations by completing the square".    
    """
    # id = auto-incrementing integet primary key
    node = models.ForeignKey('StandardNode', related_name='learning_objectives', on_delete=models.CASCADE)
    text = models.CharField(max_length=400, help_text="Text of the statement of the leanring objective.")
    # optional:
    kind = models.CharField(max_length=50, blank=True, null=True)  # system tag, e.g. KUD:Know, KUD:Understand, KUD:Do

    def __repr__(self):
        return '<LearningObjective: {}>'.format(self.text)

# HUMAN JUDGMENTS
################################################################################

class HumanRelevanceJudgment(models.Model):
    """
    Stores human feedback about relevance for an `AlignmentEdge` between two nodes.
    Relevance edges are stored as directed edges but are logically undirected.
    """
    # id = auto-incrementing integet primary key
    node1 = models.ForeignKey(StandardNode, related_name='node1+', on_delete=models.CASCADE)
    node2 = models.ForeignKey(StandardNode, related_name='node2+', on_delete=models.CASCADE)

    rating = models.FloatField()  # min = 0.0  max = 1.0
    confidence = models.FloatField(blank=True, null=True) # 1.0= 100% confident, 50% depends, 0% just guessing
    comment = JSONField(blank=True, null=True)  # provide additional context about verdict as free form text


    mode = models.CharField(max_length=30)      # (manually added  vs.  rapid feedback)
    ui_name = models.CharField(max_length=100)   # name of frontend within forntends/ ~= team name
    ui_version_hash = models.CharField(max_length=100) # hash of page contents w/o data)  # which verison of the rapid feedback UI was used

    user = models.ForeignKey(User, related_name='feedbacks', null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)

    def __repr__(self):
        return '<HumanRelevanceJudgment: {} <--{}--> {}>'.format(repr(self.node1), self.rating, repr(self.node2))



# FEATURES CACHE
################################################################################

class StandardNodeFeatureVector(models.Model):
    """
    Store arbitrary-length feature vector that represets `node` in `model_name:model_version`.
    """
    #
    node = models.ForeignKey('StandardNode', related_name='features', on_delete=models.CASCADE)
    data = ArrayField(models.FloatField())  # An arbitrary-length feature vector

    model_name = models.CharField(max_length=50)    # foldername/   /api?model=foldername
    model_version = models.IntegerField()           # get automatically? from git somehow e.g. count # commits that affect the folder for that ML model
    git_hash = models.CharField(max_length=200)
    # created = models.DateTimeField(auto_now_add=True)




# DATA EXPORT METADATA
################################################################################

class DataExport(models.Model):
    curriculum_data_version = models.CharField(max_length=50)
    feedback_data_version = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    exportdir = models.CharField(max_length=400)

    # train_data = models.FileField
    # test_data = models.FileField    

    # def export(self):
    #     for feedback_datum in feedback_data:
    #         istestdata = random Bool # training vs. test prob 0.85 / 0.15
    #         if istestdata:
    #             test_data.append(feedback_datum)
    #         else:
    #             train_data.append(feedback_datum)


