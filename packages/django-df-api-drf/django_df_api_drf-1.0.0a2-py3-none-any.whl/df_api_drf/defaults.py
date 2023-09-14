REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "df_api_drf.exceptions.errors_formatter_exception_handler",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "ALLOWED_VERSIONS": ["v1", "v2"],
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",
    "COERCE_DECIMAL_TO_STRING": False,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "PAGE_SIZE": 100,
    "TIME_FORMAT": "%H:%M",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "DEFAULT_THROTTLE_RATES": {"anon": "100/min", "user": "1000/min"},
    "DEFAULT_SCHEMA_CLASS": "df_api_drf.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Project API",
    "DESCRIPTION": "description",
    "VERSION": "0.0.1",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    "SCHEMA_PATH_PREFIX": "/api/",
    "COMPONENT_SPLIT_REQUEST": True,
    "COMPONENT_NO_READ_ONLY_REQUIRED": True,
    "ENUM_ADD_EXPLICIT_BLANK_NULL_CHOICE": False,
}

DF_API_DRF_INSTALLED_APPS = [
    "rest_framework",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "df_api_drf",
]
