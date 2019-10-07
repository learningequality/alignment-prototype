from django.contrib.auth.models import User
from django.conf.urls import url, include
from rest_framework import serializers, viewsets
from .models import (
    CurriculumDocument,
    StandardNode,
    LearningObjective,
    HumanRelevanceJudgment,
)


class CurriculumDocumentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CurriculumDocument
        fields = [
            "id",
            "source_id",
            "title",
            "country",
            "digitization_method",
            "source_url",
            "created",
        ]


class CurriculumDocumentViewSet(viewsets.ModelViewSet):
    serializer_class = CurriculumDocumentSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return CurriculumDocument.objects.all()
        else:
            return CurriculumDocument.objects.filter(is_draft=False)


class StandardNodeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = StandardNode
        fields = [
            "id",
            "identifier",
            "document",
            "kind",
            "title",
            "sort_order",
            "time_units",
            "notes",
            "extra_fields",
        ]


class StandardNodeViewSet(viewsets.ModelViewSet):
    queryset = StandardNode.objects.all()
    serializer_class = StandardNodeSerializer


class LearningObjectiveSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = LearningObjective
        fields = ["id", "node", "text", "kind"]


class LearningObjectiveViewSet(viewsets.ModelViewSet):
    queryset = LearningObjective.objects.all()
    serializer_class = LearningObjectiveSerializer


class HumanRelevanceJudgmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HumanRelevanceJudgment
        fields = [
            "node1",
            "node2",
            "rating",
            "confidence",
            "extra_fields",
            "mode",
            "ui_name",
            "ui_version_hash",
            "user",
            "created",
            "is_test_data",
        ]


class HumanRelevanceJudgmentViewSet(viewsets.ModelViewSet):
    serializer_class = HumanRelevanceJudgmentSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return HumanRelevanceJudgment.objects.all()
        else:
            return HumanRelevanceJudgment.objects.filter(is_test_data=False)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["id"]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
