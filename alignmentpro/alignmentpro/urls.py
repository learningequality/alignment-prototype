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
from rest_framework import routers

from alignmentapp.api import (
    CurriculumDocumentViewSet,
    StandardNodeViewSet,
    HumanRelevanceJudgmentViewSet,
    UserViewSet,
)

from alignmentapp import views

router = routers.DefaultRouter()
router.register(r"document", CurriculumDocumentViewSet)
router.register(r"node", StandardNodeViewSet)
router.register(r"judgment", HumanRelevanceJudgmentViewSet)
router.register(r"user", UserViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    url(r"^api/", include(router.urls)),
    url(r"^api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path('accounts/', include('allauth.urls')),
    path('', views.Home.as_view(), name='home'),
]
