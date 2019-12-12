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

from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField
from django.db import models

from django.db.models.expressions import RawSQL


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
        return Standards.objects.filter(
            parent_ids=self.parent_ids + [self.id]
        ).order_by(RawSQL("document->>%s", ("position",)))

    def get_descendants(self):
        return Standards.objects.filter(
            parent_ids__contains=self.parent_ids + [self.id]
        )

    def to_dicttree(self):
        self_dict = dict(data=self, children=[])
        for child in self.get_children():
            self_dict["children"].append(child.to_dicttree())
        return self_dict

    def __str__(self):
        return "%s: %s" % (self.id, self.title)

    class Meta:
        managed = False
        db_table = "standards"
