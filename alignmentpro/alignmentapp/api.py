from django.contrib.auth.models import User
from django.conf.urls import url, include
from rest_framework import serializers, viewsets
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.reverse import reverse
from .models import CurriculumDocument, StandardNode, HumanRelevanceJudgment


class CurriculumDocumentSerializer(serializers.ModelSerializer):
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
    queryset = CurriculumDocument.objects.all()
    serializer_class = CurriculumDocumentSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset
        else:
            return self.queryset.filter(is_draft=False)


BASE_NODE_FIELDS = [
    "id",
    "url",
    "identifier",
    "kind",
    "title",
    "sort_order",
    "depth",
    "time_units",
    "notes",
    "extra_fields",
]


class BaseStandardNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StandardNode
        fields = BASE_NODE_FIELDS


class StandardNodeSerializer(BaseStandardNodeSerializer):
    ancestors = BaseStandardNodeSerializer(source="get_ancestors", many=True)
    children = BaseStandardNodeSerializer(source="get_children", many=True)
    earlier_siblings = BaseStandardNodeSerializer(
        source="get_earlier_siblings", many=True
    )
    later_siblings = BaseStandardNodeSerializer(source="get_later_siblings", many=True)
    judgments = serializers.SerializerMethodField()
    document = CurriculumDocumentSerializer()

    def get_judgments(self, obj):
        result = [
            reverse(
                "humanrelevancejudgment-detail",
                args=[jud.id],
                request=self.context["request"],
            )
            for jud in obj.judgments.filter(is_test_data=False)
        ]
        return result

    class Meta:
        model = StandardNode
        fields = BASE_NODE_FIELDS + [
            "document",
            "ancestors",
            "children",
            "earlier_siblings",
            "later_siblings",
            "judgments",
        ]


class StandardNodeViewSet(viewsets.ModelViewSet):
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


class HumanRelevanceJudgmentSerializer(serializers.ModelSerializer):
    node1 = BaseStandardNodeSerializer()
    node2 = BaseStandardNodeSerializer()

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
            "user_id",
            "created",
            "is_test_data",
        ]


class HumanRelevanceJudgmentViewSet(viewsets.ModelViewSet):
    queryset = HumanRelevanceJudgment.objects.all()
    serializer_class = HumanRelevanceJudgmentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset
        else:
            return self.queryset.filter(is_test_data=False)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id"]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
