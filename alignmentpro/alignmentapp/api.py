from django.contrib.auth.models import User
from django.conf.urls import url, include
from rest_framework import serializers, viewsets
from rest_framework.exceptions import APIException
from rest_framework.reverse import reverse
from .models import CurriculumDocument, StandardNode, HumanRelevanceJudgment


class CurriculumDocumentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CurriculumDocument
        fields = [
            "id",
            "url",
            "source_id",
            "title",
            "country",
            "digitization_method",
            "source_url",
            "created",
        ]


class CurriculumDocumentViewSet(viewsets.ModelViewSet):
    """
    API for curriculum documents.

    Contains information about curriculum documents input into the system, including which country's curriculum
    it describes and how the document was digitized.
    """

    queryset = CurriculumDocument.objects.all()
    serializer_class = CurriculumDocumentSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset
        else:
            return self.queryset.filter(is_draft=False)


class StandardNodeSerializer(serializers.HyperlinkedModelSerializer):
    ancestors = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = StandardNode
        fields = [
            "id",
            "url",
            "identifier",
            "document",
            "kind",
            "title",
            "sort_order",
            "depth",
            "time_units",
            "notes",
            "extra_fields",
            "ancestors",
            "children",
        ]

    def get_ancestors(self, obj):
        result = [
            reverse(
                "standardnode-detail", args=[anc.id], request=self.context["request"]
            )
            for anc in obj.get_ancestors()
        ]
        return result

    def get_children(self, obj):
        result = [
            reverse(
                "standardnode-detail", args=[anc.id], request=self.context["request"]
            )
            for anc in obj.get_children()
        ]
        return result


class StandardNodeViewSet(viewsets.ModelViewSet):
    """
    API for curricular standards.

    Each StandardNode corresponds to a single curricular standard found within a curriculum document.
    Each StandardNode must contain a reference to the document it was retrieved from.
    """

    queryset = StandardNode.objects.all()
    serializer_class = StandardNodeSerializer

    def get_queryset(self):
        queryset = self.queryset
        scheduler = self.request.query_params.get("scheduler", None)
        if scheduler:
            if scheduler == "random":
                queryset = queryset.order_by("?")[:2]
            else:
                raise APIException("Unknown scheduler!")
        return queryset


class HumanRelevanceJudgmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HumanRelevanceJudgment
        fields = [
            "id",
            "url",
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
    """
    API for manually determined similarities between nodes.

    In addition to similarties determined by machine learning algorithms, we store
    similarities determined manually via human review. This allows us to compare
    the similarities with those determined by the algorithms.
    """

    queryset = HumanRelevanceJudgment.objects.all()
    serializer_class = HumanRelevanceJudgmentSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset
        else:
            return self.queryset.filter(is_test_data=False)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["id"]


class UserViewSet(viewsets.ModelViewSet):
    """
    API for user information.

    Contains app-specific user information.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
