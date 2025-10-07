"""
URL configuration for prompts_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django_prometheus import exports
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle
from rest_framework.decorators import api_view, permission_classes, throttle_classes

@api_view(["GET"])
@permission_classes([AllowAny])
@throttle_classes([])
def schema_view(request):
    view = SpectacularAPIView.as_view()
    return view(request)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("users.urls")),
    path("api/", include("prompts.urls")),
    path("metrics/", exports.ExportToDjangoView, name="metrics"),

    path(
        "schema/",
        SpectacularAPIView.as_view(
            permission_classes=[AllowAny],
            authentication_classes=[],
            throttle_classes=[],
        ),
        name="schema",
    ),

    # Swagger UI
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),

    path(
        "redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
