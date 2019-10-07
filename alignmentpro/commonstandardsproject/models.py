from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField
from django.db import models


class Jurisdictions(models.Model):
    # id
    csp_id = models.CharField(max_length=200, blank=True, null=True)
    document = JSONField(blank=True, null=True)  # This field type is a guess.
    title = models.CharField(max_length=200, blank=True, null=True)
    type = models.CharField(max_length=200, blank=True, null=True)

    def get_roots(self, **kwargs):
        return Standards.objects.filter(jurisdiction=self, parent_ids=[], **kwargs)

    def __unicode__(self):
        return "<Jurisdictions %s: %s>" % (self.id, self.title)

    def __repr__(self):
        return self.__unicode__()

    class Meta:
        managed = False
        db_table = "jurisdictions"


class Standards(models.Model):
    # id
    jurisdiction = models.ForeignKey(Jurisdictions, models.DO_NOTHING)
    csp_id = models.CharField(max_length=200, blank=True, null=True)
    parent_ids = ArrayField(models.IntegerField())  # This field type is a guess.
    education_levels = ArrayField(
        models.CharField(max_length=200)
    )  # This field type is a guess.
    title = models.CharField(max_length=200, blank=True, null=True)
    subject = models.CharField(max_length=200, blank=True, null=True)
    document = JSONField(blank=True, null=True)  # This field type is a guess.
    indexed = models.BooleanField()
    child_count = models.IntegerField(blank=True, null=True)

    def get_parent(self):
        if len(self.parent_ids) > 1:
            return Standards.objects.get(id=self.parent_ids[-1])
        else:
            return None  # root node

    def get_children(self):
        return Standards.objects.filter(parent_ids=self.parent_ids + [self.id])

    def get_descendants(self):
        return Standards.objects.filter(
            parent_ids__contains=self.parent_ids + [self.id]
        )

    def __unicode__(self):
        return "<Standards %s: %s>" % (self.id, self.title)

    def __repr__(self):
        return self.__unicode__()

    class Meta:
        managed = False
        db_table = "standards"
