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
