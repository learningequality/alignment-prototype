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

from django.contrib import admin

from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from alignmentapp.models import (
    CurriculumDocument,
    StandardNode,
    HumanRelevanceJudgment,
    Parameter,
    DataExport,
    SubjectArea,
    UserAction,
    UserProfile,
    DocumentSection
)


@admin.register(CurriculumDocument)
class CurriculumDocumentAdmin(admin.ModelAdmin):
    list_display = ["country", "title", "source_id"]
    list_filter = ("country", "digitization_method", "is_draft")
    search_fields = ["source_id", "title"]
    model = CurriculumDocument


@admin.register(StandardNode)
class StandardNodeAdmin(TreeAdmin):
    # list_display = ["title"]
    list_filter = ("document__country", "document")
    search_fields = ["identifier", "title", "notes"]
    form = movenodeform_factory(StandardNode)


@admin.register(HumanRelevanceJudgment)
class HumanRelevanceJudgmentAdmin(admin.ModelAdmin):
    model = HumanRelevanceJudgment


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    model = Parameter


@admin.register(DataExport)
class DataExportAdmin(admin.ModelAdmin):
    model = DataExport


@admin.register(SubjectArea)
class SubjectAreaAdmin(admin.ModelAdmin):
    model = SubjectArea


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    model = UserProfile


@admin.register(UserAction)
class UserActionAdmin(admin.ModelAdmin):
    model = UserAction


@admin.register(DocumentSection)
class DocumentSectionAdmin(TreeAdmin):
    model = DocumentSection
    list_filter = ("document__country", "document")
    search_fields = ["name"]
    form = movenodeform_factory(DocumentSection)
