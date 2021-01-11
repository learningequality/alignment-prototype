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

import json
import os
import re
import shutil
import urllib.request

from django.contrib.auth.models import User
from django.conf import settings
from django.conf.urls import url, include
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers, viewsets, views, status, response
from rest_framework.authentication import SessionAuthentication
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .models import (
    CurriculumDocument,
    DocumentSection,
    StandardNode,
    HumanRelevanceJudgment,
    UserAction,
)
from .schedulers import prob_weighted_random
from .recommenders import recommend_top_ranked


class CurriculumDocumentSerializer(serializers.ModelSerializer):
    root_node_id = serializers.SerializerMethodField()
    root_node_url = serializers.SerializerMethodField()

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
            "official",
            "root_node_id",
            "root_node_url",
        ]

    def get_root_node_id(self, obj):
        try:
            return StandardNode.objects.get(depth=1, document_id=obj.id).id
        except:
            return None

    def get_root_node_url(self, obj):
        root_node_id = self.get_root_node_id(obj)
        return "http://alignmentapp.learningequality.org/api/node/{}".format(
            root_node_id
        )


def LargeResultsSetPagination(size=100):
    class CustomPagination(PageNumberPagination):
        page_size = size
        page_size_query_param = "page_size"
        max_page_size = page_size * 10

    return CustomPagination


class CurriculumDocumentViewSet(viewsets.ModelViewSet):
    queryset = CurriculumDocument.objects.all()
    serializer_class = CurriculumDocumentSerializer
    pagination_class = LargeResultsSetPagination(100)

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
    "numchild",
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
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["document", "depth"]

    def list(self, request):
        queryset = self.get_queryset()
        params = self.request.query_params
        scheduler = params.get("scheduler", None)
        left = params.get("left", None)
        right = params.get("right", None)
        relevance, probability, distribution = -1, -1, -1

        if scheduler:
            if scheduler == "fullyrandom":
                queryset = queryset.order_by("?")[:2]
            elif scheduler == "random":
                gamma = float(params.get("gamma", 20.0))
                left_root_id = int(params.get("left_root_id", 0)) or None
                right_root_id = int(params.get("right_root_id", 0)) or None
                allow_same_doc = bool(params.get("allow_same_doc", False))
                include_nonleaf_nodes = bool(params.get("include_nonleaf_nodes", False))
                relevance, probability, distribution, queryset = prob_weighted_random(
                    queryset,
                    model_name="baseline",
                    gamma=gamma,
                    left_root_id=left_root_id,
                    right_root_id=right_root_id,
                    allow_same_doc=allow_same_doc,
                    include_nonleaf_nodes=include_nonleaf_nodes,
                )
            else:
                raise APIException("Unknown scheduler!")
        elif left and right:
            queryset = queryset.filter(id=left) | queryset.filter(id=right)
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
                "probability": probability,
                "distribution": distribution,
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

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        return self.queryset.filter(pk=self.request.user.pk)


class TrainedModelSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    notebook_url = serializers.URLField(max_length=200)
    team_members = serializers.CharField(max_length=200)
    file = serializers.FileField(max_length=200, allow_empty_file=False, use_url=False)
    folder_url = serializers.SerializerMethodField()
    scores = serializers.SerializerMethodField()

    def get_folder_url(self, data):
        return "http://alignmentapp.learningequality.org/files/models/" + data["name"]

    def get_scores(self, data):
        scores_path = os.path.join(
            settings.MEDIA_ROOT, "models", data["name"], "scores.json"
        )
        if os.path.exists(scores_path):
            with open(scores_path) as f:
                return json.load(f)
        else:
            return {}


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

            scores_path = os.path.join(exportpath, "..", "scores.json")
            if os.path.exists(scores_path):
                os.unlink(scores_path)

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


class LeaderboardView(views.APIView):
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        return Response(
            User.objects.exclude(username="khan_academy_org")
            .annotate(number_of_judgments=Count("judgments"))
            .order_by("-number_of_judgments")
            .values("username", "number_of_judgments")
        )


class StandardNodeRecommendationSerializer(BaseStandardNodeSerializer):
    ancestors = BaseStandardNodeSerializer(source="get_ancestors", many=True)
    document = CurriculumDocumentSerializer()
    # relevance = serializers.SerializerMethodField()

    class Meta:
        model = StandardNode
        fields = BASE_NODE_FIELDS + ["document", "ancestors"]

    # def get_relevance(self, obj):
    #     return obj.relevance


class StandardNodeRecommendationViewSet(viewsets.ModelViewSet):
    queryset = StandardNode.objects.all()
    serializer_class = StandardNodeRecommendationSerializer

    def list(self, request):
        queryset = self.get_queryset()
        params = self.request.query_params
        target = params.get("target")
        assert target, "Needs a target param with node ID"
        threshold = params.get("threshold")
        count = params.get("count", None if threshold else 10)
        model = params.get("model", "baseline")
        target_node = StandardNode.objects.get(id=int(target))
        relevances, results = recommend_top_ranked(
            queryset=queryset,
            target_node=target_node,
            threshold=threshold,
            count=count,
            model=model,
        )
        serializer = StandardNodeRecommendationSerializer(
            results, many=True, context={"request": request}
        )

        return Response(
            {
                "count": len(results),
                "next": None,
                "previous": None,
                "target_node": StandardNodeRecommendationSerializer(
                    target_node, context={"request": request}
                ).data,
                "relevances": relevances,
                "results": serializer.data,
            }
        )


@api_view(["GET", "POST"])
@authentication_classes((TokenAuthentication, SessionAuthentication))
@permission_classes((IsAuthenticated,))
def review_section(request):
    """
    Backend http://localhost:8000/api/section-review/ for the Thursday hacksession
    for frontend see http://localhost:8000/#/curriculum_review
    POST to this URL to save human review edits for a section
    GET this URL to load the next available topic (is_draft=True + reviewed_by=None)
    """
    # POST
    if request.method == "POST":
        data = json.loads(request.body)
        section = DocumentSection.objects.get(pk=data["section_id"])
        section.text = data["section_text"]
        section.reviewed_by = request.user
        # TODO: Add a 'Finalize' button to the UI, so that if they need to stop, they can
        # save and come back to finish later. We may also want to only allow finalizing after a review.
        points = 5
        resp_data = {"success": True}
        if "finalize" in data and data["finalize"]:
            section.is_draft = False
            UserAction.objects.create(
                user=request.user, action="reviewed_section", points=points
            )
            resp_data["points"] = 5
            # TODO: Add UserAction points for this.
        # TODO: Add a 'Abandon/Cancel' button to the UI so that users users can
        # put back section into available pile for another user to continue
        if "abandon" in data and data["abandon"]:
            section.reviewed_by = None
        section.save()
        return Response(resp_data)
    # GET
    else:
        user = request.user
        # First check if user already has a section they are currently reviewing
        section = user.section_reviews.filter(is_draft=True).first()
        if section is None:
            # Otherwise assign next available section
            section = DocumentSection.get_section_for_review()
        if section is None:
            return Response(
                {
                    "error": "No document sections currently available for review. Please check back again later."
                }
            )

    # first chunk image (API v0 Oct29)
    image_url = "{}scans/{}/{}".format(
        settings.MEDIA_URL,
        section.get_section_dir(),
        section.name + "_chunk001_lowres.png",
    )

    # all chunks images (API v1 > Oct30)
    rel_path = section.get_section_dir()
    full_path = os.path.join(settings.SCANS_ROOT, rel_path)
    lowres_chunk_filanames = [f for f in os.listdir(full_path) if "lowres" in f]
    image_urls = []
    for lowres_chunk_filaname in lowres_chunk_filanames:
        image_url = "{}scans/{}/{}".format(
            settings.MEDIA_URL, section.get_section_dir(), lowres_chunk_filaname
        )
        image_urls.append(image_url)

    text = section.text
    if not "<p>" in text:
        text = "<p>" + section.text.replace("\n", "</p><p>") + "</p>"

    vars = {
        "document": {
            "title": section.document.title,
            "country": section.document.country,
        },
        "section_id": section.pk,
        "image_url": image_url,  # still available, but deprecated
        "image_urls": sorted(
            image_urls
        ),  # list of URLs of chunk images in this section
        "section_text": text,
        "section_name": section.name,
        "ancestors": section.get_ancestors().values_list("name", flat=True),
    }

    return Response(vars)


@api_view(["GET"])
@authentication_classes((TokenAuthentication, SessionAuthentication))
@permission_classes((IsAuthenticated,))
def get_user_points(request):
    points = UserAction.objects.filter(user=request.user).aggregate(Sum("points"))[
        "points__sum"
    ]
    if points is None:
        points = 0

    return Response({"points": points})
