
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
    country = models.CharField(max_length=200, help_text="Country")
    digitization_method = models.CharField(choices=DIGITIZATION_METHODS, max_length=200, help_text="Digitization method")
    source_url = models.CharField(max_length=200, help_text="URL of source used for this document")
    # root = reverse relation on StandardNode.document
    created = models.DateTimeField(auto_now_add=True)
    #? modified = models.DateTimeField(auto_now=True)
    is_draft = models.BooleanField(default=True,
        help_text="True for draft version of the curriculum data.")




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
    kind = models.CharField(max_length=20, choices=NODE_KINDS, default='unit')
    title = models.CharField(max_length=400)
    sort_order = models.IntegerField(default=1)
    node_order_by = ['sort_order']  # the order of children within parent node
    # learning_objectives = reverse relation on LearningObjective.node

    # domain-specific 
    time_units = models.FloatField(blank=True, null=True,
        help_text="A numeric value ~ to the hours of instruction for this unit")
    notes = models.TextField(help_text="Additional notes and modification attributes.")
    extra_fields = JSONField(blank=True, null=True)  # basic model extensibility w/o changing base API


    # Human relevance jugments on edges between nodes
    @property
    def judgments(self):
        return HumanRelevanceJudgment.objects.filter(Q(node1=self) | Q(node2=self))

    def __repr__(self):
        return '<StandardNode: {} {}>'.format(self.identifier, self.title)


class LearningObjective(MP_Node):
    """
    Individual learning objectives statements associated with a curriculum unit,
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

    rating = models.FloatField()  # min = 0.0 (not relevant at all), max = 1.0 (highly relevant)
    confidence = models.FloatField(blank=True, null=True) # 1.0= 100% confident, 50% depends, 0% just guessing (or null)
    extra_fields = JSONField(blank=True, null=True)  # additional context and comments about verdict

    mode = models.CharField(max_length=30)       # (manually added  vs.  rapid feedback)
    ui_name = models.CharField(max_length=100)   # name of frontend within forntends/ ~= team name
    ui_version_hash = models.CharField(max_length=100) # hash of the js bundle of the rapid feedback UI that was used

    user = models.ForeignKey(User, related_name='judgments', null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    is_test_data = models.BooleanField(blank=True, null=True, help_text="True for held out test data.")

    def __repr__(self):
        return '<HumanRelevanceJudgment: {} <--{}--> {}>'.format(repr(self.node1), self.rating, repr(self.node2))



# FEATURES CACHE
################################################################################

class MachineLearningModel(models.Model):
    """
    Stores metadata for a particular instance of ML model (code and training data).
    """
    # id = auto-incrementing integet primary key
    model_name = models.CharField(max_length=50)    # foldername/   /api?model=foldername
    model_version = models.IntegerField()           # get automatically? from git somehow e.g. count # commits that affect the folder for that ML model
    git_hash = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)


class StandardNodeFeatureVector(models.Model):
    """
    Store arbitrary-length feature vector that represets `node` in a given `model`.
    """
    # id = auto-incrementing integet primary key
    mlmodel = models.ForeignKey('MachineLearningModel', related_name='feature_vectors', on_delete=models.CASCADE) 
    node = models.ForeignKey('StandardNode', related_name='features', on_delete=models.CASCADE)
    data = ArrayField(models.FloatField())  # An arbitrary-length feature vector



# DATA EXPORT METADATA
################################################################################

# TODO: add model for export policy
#   is_test_proportion = models.FloatField()   # e.g. 0.15 => 0.15 prob of assigning to test dataset
#   created = models.DateTimeField(auto_now_add=True)
#   modified = models.DateTimeField(auto_now=True)

class DataExport(models.Model):
    curriculum_data_version = models.CharField(max_length=50)
    feedback_data_version = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    exportdir = models.CharField(max_length=400)

    # train_data = models.FileField
    # test_data = models.FileField    

    # def export(self):
    #     new_feedback_data = HumanRelevanceJudgment.filter(is_test_data=None)
    #     for feedback_datum in new_feedback_data:
    #         istestdata = random addignmnt from ExportPolicy
    #         if istestdata:
    #             feedback_datum.is_test_data = True
    #             test_data.append(feedback_datum)
    #         else:
    #             feedback_datum.is_test_data = False
    #             train_data.append(feedback_datum)

