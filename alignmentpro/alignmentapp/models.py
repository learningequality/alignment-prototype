from django.contrib.auth.models import User
from django.db import models
from treebeard.mp_tree import MP_Node



# CURRICULUM DOCUMENTS
################################################################################

DIGITIZATION_METHODS = [
    ('manual_entry', 'Manual data entry'),
    ('scan_manual', 'Scan Aligned to'),
    ('automated_scan', 'Automated stucture extraction'),
]

class CurriculumDocument(models.Model):
    """
    Stores the metadata for a curriculum document, e.g. the CCSSM.
    """
    # id = auto-created integet primary key
    title = models.CharField(max_length=200)
    country = models.CharField("Country", max_length=200)
    digitization_method = models.CharField("Digitization method", choices=DIGITIZATION_METHODS, max_length=200)
    version = models.IntegerField("Document version", default=1)
    # root = reverse relation on StandardNode.document




# CURRICULUM STANDARD ENTRIES
################################################################################

NODE_KINDS = [
    ('root', 'Root node'),                  # the root node for the document (self.title == self.document.title)
    ('secion', 'Section or subsection'),    # structural elements (sections and subsections)
    ('entry', 'Standard entry'),            # entries with LOs or content fields
    ('listitem', 'List item'),              # sub-entry list items
]

class StandardNode(MP_Node):
    """
    An standard entry.
    """
    document = models.ForeignKey('CurriculumDocument', related_name='root', on_delete=models.CASCADE)
    kind = models.CharField(max_length=20, choices=NODE_KINDS, default='entry')
    sort_order = models.FloatField(default=1.0)
    title = models.CharField(max_length=200)
    learning_objectives = models.TextField()
    content = models.TextField()
    list_id = models.CharField(max_length=20)
    notes = models.TextField()
    
    # Alignment edges
    alignments = models.ManyToManyField('self',
        through='AlignmentEdge',
        through_fields=('source', 'target'),
        symmetrical=False)

    node_order_by = ['sort_order']

    def __unicode__(self):
        return '<StandardNode: %s>' % self.title

    class Meta:
        unique_together = ['document', 'path']




# ALIGNMENT EDGES
################################################################################

class AlignmentEdge(models.Model):
    """
    Represents a `(source)--relevantfor-->(target)` edges.
    Note the edge is not symmetic.
    """
    # id = auto-created integet primary key
    source = models.ForeignKey(StandardNode, related_name='relevantfor', on_delete=models.CASCADE)
    target = models.ForeignKey(StandardNode, related_name='related', on_delete=models.CASCADE)
    kind = models.CharField(max_length=20, default='relevantfor')

    def __unicode__(self):
        return '<AlignmentEdge ' + self.source.title + '--relevantfor-->' + self.target.title + '>'




# ML MODEL PREDICTIONS
################################################################################

class AlignmentEdgePrediction(models.Model):
    """
    Stores the alignment edge predicted by a ML model.
    """
    alignment_edge = models.ForeignKey(AlignmentEdge, related_name='predictions', on_delete=models.CASCADE)
    similarity_score = models.FloatField(default=1.0)
    model_name = models.CharField(max_length=50)
    model_version = models.CharField(max_length=50)
    data_version = models.CharField(max_length=50)




# HUMAN JUDGMENTS
################################################################################

RELEVANCE_LEVELS = [
    ('relevant', 'Manual data entry'),
    ('somewhat_relevant', 'Scan Aligned to'),
    ('not_relevant', 'Automated stucture extraction'),
]

class AlignmentEdgeRelevanceFeedback(models.Model):
    """
    Stores human feedback about relevance for an `AlignmentEdge` between two nodes.
    """
    alignment_edge = models.ForeignKey(AlignmentEdge, related_name='feedback', on_delete=models.CASCADE)
    verdict = models.CharField(max_length=30, choices=RELEVANCE_LEVELS, default='relevant')
    method = models.CharField(max_length=30) # (manually added  vs.  rapid feedback)
    user = models.ForeignKey(User, related_name='feedbacks', null=True, on_delete=models.SET_NULL)
    ui_version = models.CharField(max_length=30) # which verison of the rapid feedback UI was used
    confidence =  models.FloatField(default=1.0) # 1.0= 100% confident, 50% depends, 0% just guessing
    comment = models.TextField() # provide additional context about verdict as free form text

