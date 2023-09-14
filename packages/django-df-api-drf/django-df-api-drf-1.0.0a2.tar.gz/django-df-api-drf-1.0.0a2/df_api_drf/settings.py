from typing import Any, Dict

from django.conf import settings
from rest_framework.settings import APISettings

DEFAULTS: Dict[str, Any] = {"DEFAULT_NAMESPACE": "v1"}

api_settings = APISettings(getattr(settings, "DF_API_DRF", None), DEFAULTS)
