from django.contrib import admin

from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from alignmentapp.models import (
    CurriculumDocument,
    StandardNode,
    LearningObjective,
    HumanRelevanceJudgment,
    MachineLearningModel,
)


@admin.register(CurriculumDocument)
class CurriculumDocumentAdmin(admin.ModelAdmin):
    model = CurriculumDocument


class LearningObjectiveInline(admin.TabularInline):
    model = LearningObjective
    fields = ("text",)


@admin.register(StandardNode)
class StandardNodeAdmin(TreeAdmin):
    list_filter = ("document__country", "document")
    search_fields = ["identifier", "title", "learning_objectives__text", "notes"]
    form = movenodeform_factory(StandardNode)
    inlines = [LearningObjectiveInline]


@admin.register(HumanRelevanceJudgment)
class HumanRelevanceJudgmentAdmin(admin.ModelAdmin):
    model = HumanRelevanceJudgment


@admin.register(MachineLearningModel)
class MachineLearningModelAdmin(admin.ModelAdmin):
    model = MachineLearningModel
