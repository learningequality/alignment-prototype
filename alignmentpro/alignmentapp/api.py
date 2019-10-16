import json
import os
import re
import shutil
import urllib.request

from django.contrib.auth.models import User
from django.conf import settings
from django.conf.urls import url, include
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import serializers, viewsets, status, response
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .models import CurriculumDocument, StandardNode, HumanRelevanceJudgment
from .schedulers import prob_weighted_random


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

    def list(self, request):
        queryset = self.queryset
        scheduler = self.request.query_params.get("scheduler", None)
        if scheduler:
            if scheduler == "fullyrandom":
                queryset = queryset.order_by("?")[:2]
            elif scheduler == "random":
                gamma = float(self.request.query_params.get("gamma", 2.0))
                relevance, queryset = prob_weighted_random(
                    queryset, model_name="baseline", gamma=gamma
                )
            else:
                raise APIException("Unknown scheduler!")
        else:
            return super().list(request)
        serializer = StandardNodeSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response(
            {
                "count": 2,
                "next": None,
                "previous": None,
                "relevance": relevance,
                "results": serializer.data,
            }
        )


class HumanRelevanceJudgmentSerializer(serializers.ModelSerializer):
    node1 = serializers.PrimaryKeyRelatedField(queryset=StandardNode.objects.all())
    node2 = serializers.PrimaryKeyRelatedField(queryset=StandardNode.objects.all())

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


class TrainedModelSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    notebook_url = serializers.URLField(max_length=200)
    team_members = serializers.CharField(max_length=200)
    file = serializers.FileField(max_length=200, allow_empty_file=False, use_url=False)
    folder_url = serializers.SerializerMethodField()

    def get_folder_url(self, data):
        return "http://alignmentapp.learningequality.org/files/models/" + data["name"]


class TrainedModelViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    serializer_class = TrainedModelSerializer

    def list(self, request):
        base_dir = os.path.join(settings.MEDIA_ROOT, "models")
        model_dirs = os.listdir(base_dir)
        data = []
        for name in model_dirs:
            with open(os.path.join(base_dir, name, "metadata.json")) as f:
                data.append(json.load(f))
        serializer = TrainedModelSerializer(data=data, many=True)
        serializer.is_valid()
        return response.Response(serializer.data, status=200)

    @csrf_exempt
    def create(self, request):
        serializer = TrainedModelSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data

            # save the file
            file = request.FILES["file"]
            export_base_dir = os.path.join(settings.MEDIA_ROOT, "models", data["name"])
            exportdirname = timezone.localtime().strftime("%Y%m%d-%H%M%S")
            exportpath = os.path.join(export_base_dir, exportdirname)
            if not os.path.exists(exportpath):
                os.makedirs(exportpath)
            with open(os.path.join(exportpath, file.name), "wb+") as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            data["file"] = None

            # download the notebook
            NOTEBOOK_URL_PATTERN = "https://colab.research.google.com/drive/([^#]+)"
            match = re.match(NOTEBOOK_URL_PATTERN, data["notebook_url"])
            if not match:
                raise Exception("Not a valid notebook URL")
            notebook_id = match.group(1)
            download_url = "https://drive.google.com/uc?id=" + notebook_id
            urllib.request.urlretrieve(
                download_url, os.path.join(exportpath, "model.ipynb")
            )

            # create the metadata.json file
            with open(os.path.join(exportpath, "metadata.json"), "w") as f:
                json.dump(data, f)

            # copy the contents of the timestamped folder into parent folder
            src_files = os.listdir(exportpath)
            for file_name in src_files:
                full_file_name = os.path.join(exportpath, file_name)
                if os.path.isfile(full_file_name):
                    shutil.copy(full_file_name, os.path.join(exportpath, ".."))

            with open(os.path.join(exportpath, "..", "dirty"), "w") as f:
                f.write("dirty")

            return response.Response(data, status=201)
        else:
            data = serializer.data
            data["file"] = None
            return response.Response(data, status=400)

    # def retrieve(self, request, pk=None):
    # base_dir = os.path.join(settings.MEDIA_ROOT, "models")
    # model_dirs = os.listdir(base_dir)
    # data = []
    # for name in model_dirs:
    #     with open(os.path.join(base_dir, name, "metadata.json")) as f:
    #         data.append(json.load(f))
    # serializer = TrainedModelSerializer(data=[], many=True)
    # return response.Response(data, status=200)
