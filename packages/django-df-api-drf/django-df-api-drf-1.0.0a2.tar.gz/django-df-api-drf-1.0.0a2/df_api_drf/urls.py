from collections import defaultdict
from typing import Dict

from django.apps import apps
from django.conf import settings
from django.conf.urls import include
from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from .settings import api_settings

app_name = "df_api_drf"

urlpatterns = []

namespaces: Dict[str, Dict[str, str]] = defaultdict(dict)

for app in apps.get_app_configs():
    if df_meta := getattr(app, "DFMeta", None):
        if api_path := df_meta.api_path:
            for namespace, urls in getattr(
                df_meta,
                "api_drf_namespaces",
                {api_settings.DEFAULT_NAMESPACE: f"{app.name}.drf.urls"},
            ).items():
                namespaces[namespace][api_path] = urls

for namespace, app_urls in namespaces.items():
    namespace_patterns = [
        path(
            "schema/",
            SpectacularAPIView.as_view(
                api_version=namespace,
                custom_settings={
                    "SCHEMA_PATH_PREFIX": settings.SPECTACULAR_SETTINGS.get(
                        "SCHEMA_PATH_PREFIX", "/api/"
                    )
                    + namespace
                    + "/"
                },
            ),
            name="schema",
        ),
        path(
            "",
            SpectacularRedocView.as_view(url_name=f"df_api_drf:{namespace}:schema"),
            name="redoc",
        ),
        path(
            "swagger/",
            SpectacularSwaggerView.as_view(url_name=f"df_api_drf:{namespace}:schema"),
            name="swagger-ui",
        ),
    ]
    for api_path, urls in app_urls.items():
        namespace_patterns += [path(api_path, include((urls, api_path.strip("/"))))]
    urlpatterns += [
        path(
            f"{namespace}/",
            include((namespace_patterns, namespace), namespace=namespace),
        )
    ]
