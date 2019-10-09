from django.contrib import admin

from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from alignmentapp.models import (
    CurriculumDocument,
    StandardNode,
    HumanRelevanceJudgment,
    MachineLearningModel,
    Parameter,
    DataExport,
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


@admin.register(MachineLearningModel)
class MachineLearningModelAdmin(admin.ModelAdmin):
    model = MachineLearningModel




@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    model = Parameter


@admin.register(DataExport)
class DataExportAdmin(admin.ModelAdmin):
    model = DataExport
