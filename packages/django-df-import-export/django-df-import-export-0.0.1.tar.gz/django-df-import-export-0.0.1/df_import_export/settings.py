from typing import Any, Dict

from django.conf import settings
from rest_framework.settings import APISettings

DEFAULTS: Dict[str, Any] = {}

api_settings = APISettings(getattr(settings, "DF_IMPORT_EXPORT", None), DEFAULTS)
