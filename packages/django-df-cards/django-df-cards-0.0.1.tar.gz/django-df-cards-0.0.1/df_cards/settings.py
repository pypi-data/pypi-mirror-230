from typing import Any, Dict

from django.conf import settings
from rest_framework.settings import APISettings

DEFAULTS: Dict[str, Any] = {
    "ICON_IMAGE_SPEC": "df_cards.specs.IconImageSpec",
    "THUMBNAIL_IMAGE_SPEC": "df_cards.specs.ThumbnailImageSpec",
    "AVATAR_IMAGE_SPEC": "df_cards.specs.AvatarImageSpec",
    "FULL_IMAGE_SPEC": "df_cards.specs.FullImageSpec",
}

api_settings = APISettings(getattr(settings, "DF_CARDS", None), DEFAULTS)
