from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Q, UniqueConstraint
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from treebeard.mp_tree import MP_Node


BACKGROUNDS = [
    ('instructional_designer', 'Instructional Designer'),
    ('curriculum', 'Curriculum Alignment Expert'),
    ('content_expert', "OER Expert"),
    ('teacher', 'Teacher/Coach'),
    ('designer', 'Designer or Frontend Developer'),
    ('developer', 'Technologist and/or Developer'),
    ('data_science', 'Machine Learning and Data Science'),
    ('metadata', 'Metadata'),
    ('other', 'Other')
]


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    background = models.CharField(max_length=50, choices=BACKGROUNDS, help_text="What is your background experience?")
    subject_areas = models.ManyToManyField(
        to='alignmentapp.SubjectArea',
        related_name='user_profiles',
        blank=True,
    )

    def __str__(self):
        return "Profile for {}".format(self.user.username)


class SubjectArea(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# CURRICULUM DOCUMENTS
################################################################################

DIGITIZATION_METHODS = [
    ("manual_entry", "Manual data entry"),
    ("scan_manual", "Curriculum manually extracted from OCR"),
    ("automated_scan", "Automated stucture extraction via OCR"),
    ("website_scrape", "Curriculum scraped from website"),
    ("data_import", "Curriculum imported from data"),
]


class CurriculumDocument(models.Model):
    """
    Stores the metadata for a curriculum document, e.g. KICD standards for math.
    """

    # id = auto-incrementing integet primary key
    source_id = models.CharField(
        unique=True,
        max_length=200,
        help_text="A unique identifier for the source document",
    )
    title = models.CharField(max_length=200)
    country = models.CharField(max_length=200, help_text="Country")
    digitization_method = models.CharField(
        choices=DIGITIZATION_METHODS, max_length=200, help_text="Digitization method"
    )
    source_url = models.CharField(
        max_length=200, blank=True, help_text="URL of source used for this document"
    )
    # root = reverse relation on StandardNode.document
    created = models.DateTimeField(auto_now_add=True)
    # ? modified = models.DateTimeField(auto_now=True)
    is_draft = models.BooleanField(
        default=True, help_text="True for draft version of the curriculum data."
    )

    @property
    def root(self):
        return StandardNode.get_root_nodes().get(document=self)

    def __str__(self):
        return "{}: {} ({})".format(self.country, self.title, self.source_id)


# CURRICULUM DATA
################################################################################


class StandardNode(MP_Node):
    """
    The individual elements of a curriculum structure.
    """

    # id = auto-incrementing integet primary key
    # path = inherited from MP_Node, e.g. ['0001'] for root node of tree_id 0001
    document = models.ForeignKey(
        "CurriculumDocument", related_name="nodes", on_delete=models.CASCADE
    )
    identifier = models.CharField(max_length=300)
    # source_id / source_url ?
    kind = models.CharField(max_length=100)
    title = models.TextField(help_text="Primary text that represents this node.")
    # the order of tree children within parent node
    sort_order = models.FloatField(default=1.0)
    node_order_by = ["sort_order"]

    # domain-specific
    time_units = models.FloatField(
        blank=True,
        null=True,
        help_text="A numeric value ~= to the # hours of instruction for this unit or topic",
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes, description, and supporting text from the source.",
    )
    # basic model extensibility w/o changing base API
    extra_fields = JSONField(default=dict)

    # Human relevance jugments on edges between nodes
    @property
    def judgments(self):
        return HumanRelevanceJudgment.objects.filter(Q(node1=self) | Q(node2=self))

    def __str__(self):
        return "{} {}".format(self.identifier, self.title)

    def add_child(self, **kwargs):
        if "document" not in kwargs:
            kwargs["document"] = self.document
        return super().add_child(**kwargs)

    def get_earlier_siblings(self):
        return self.get_siblings().filter(sort_order__lt=self.sort_order)

    def get_later_siblings(self):
        return self.get_siblings().filter(sort_order__gt=self.sort_order)

    class Meta:
        constraints = [
            UniqueConstraint(  # Make sure every document has at most one tree
                name="single_root_per_document",
                fields=["document", "depth"],
                condition=Q(depth=1),
            )
        ]


# HUMAN JUDGMENTS
################################################################################


class HumanRelevanceJudgment(models.Model):
    """
    Stores human feedback about relevance for an `AlignmentEdge` between two nodes.
    Relevance edges are stored as directed edges but are logically undirected.
    """

    # id = auto-incrementing integet primary key
    node1 = models.ForeignKey(
        StandardNode, related_name="node1+", on_delete=models.CASCADE
    )
    node2 = models.ForeignKey(
        StandardNode, related_name="node2+", on_delete=models.CASCADE
    )

    # Relevnace rating: min = 0.0 (not relevant at all), max = 1.0 (highly relevant)
    rating = models.FloatField()
    # Optional confidence level: 1.0= 100% sure, 50% depends, 0% just guessing
    confidence = models.FloatField(blank=True, null=True)
    extra_fields = JSONField(default=dict)

    mode = models.CharField(max_length=30)  # manually added vs. rapid feedback
    # Save the info about the UI frontend used to provide judgment (team name)
    ui_name = models.CharField(max_length=100)
    ui_version_hash = models.CharField(max_length=100)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="judgments", null=True, on_delete=models.SET_NULL
    )
    created = models.DateTimeField(auto_now_add=True)
    is_test_data = models.BooleanField(
        blank=True, null=True, help_text="True for held out test data."
    )

    def __str__(self):
        return "{} <--{}--> {}".format(
            repr(self.node1_id), self.rating, repr(self.node2_id)
        )


# MACHINE LEARNING
################################################################################


class Parameter(models.Model):
    """
    General-purpse key-value store. Used to store:
      - test_size (float-compatible str): proportion of human judgments to set
        aside for use as the testing set.
    """

    key = models.CharField(max_length=200, unique=True)
    value = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class DataExport(models.Model):
    """
    Keep track when data exports was done and which folder it was saved to.
    """

    exportdirname = models.CharField(max_length=400, blank=True, null=True)
    started = models.DateTimeField(auto_now_add=True)
    finished = models.DateTimeField(blank=True, null=True)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    Make sure we auto-create an auth token for the user qwhenever a new user is created.
    """
    if created:
        Token.objects.create(user=instance)
