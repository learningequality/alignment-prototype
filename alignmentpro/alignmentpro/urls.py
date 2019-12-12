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

"""alignmentpro URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from rest_framework import routers
from rest_framework.authtoken import views as rest_auth_views

from alignmentapp.api import (
    CurriculumDocumentViewSet,
    StandardNodeViewSet,
    HumanRelevanceJudgmentViewSet,
    UserViewSet,
    TrainedModelViewSet,
    LeaderboardView,
    StandardNodeRecommendationViewSet,
    review_section,
    get_user_points
)

from alignmentapp import views

router = routers.DefaultRouter()
router.register(r"document", CurriculumDocumentViewSet)
router.register(r"node", StandardNodeViewSet)
router.register(r"judgment", HumanRelevanceJudgmentViewSet)
router.register(r"user", UserViewSet)
router.register(r"model", TrainedModelViewSet, basename="model")
router.register(r"recommend", StandardNodeRecommendationViewSet, basename="recommend")

urlpatterns = [
    path("admin/", admin.site.urls),
    url(r"^api-token-auth/", rest_auth_views.obtain_auth_token),
    url(r"^register/$", views.register, name="register"),
    url(
        r"^api/",
        include(
            router.urls
            + [path("leaderboard", LeaderboardView.as_view(), name="leaderboard"),
               path("section-review/", review_section, name="review_section"),
               path("user-points/", get_user_points, name="user_points"),
               ]
        ),
    ),
    url(r"^api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", views.HomeView.as_view(), name="home"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
