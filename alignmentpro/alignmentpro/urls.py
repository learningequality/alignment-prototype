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
from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path
from rest_framework import permissions
from rest_framework import routers

from alignmentapp.api import (
    CurriculumDocumentViewSet,
    StandardNodeViewSet,
    HumanRelevanceJudgmentViewSet,
    UserViewSet,
)

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Semi-Automated Alignment API",
        default_version="v1",
        description="APIs for semi-automated alignment prototype",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


router = routers.DefaultRouter()
router.register(r"document", CurriculumDocumentViewSet)
router.register(r"node", StandardNodeViewSet)
router.register(r"judgment", HumanRelevanceJudgmentViewSet)
router.register(r"user", UserViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    url(r"^api/", include(router.urls)),
    url(r"^api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    url(
        r"^api-docs/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
]
