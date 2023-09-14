from typing import Any

from django.utils.module_loading import import_string
from imagekit.models import ProcessedImageField

from df_cards.settings import api_settings


class ResizedImageField(ProcessedImageField):
    spec_class: str

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        spec = import_string(self.spec_class)

        kwargs.setdefault("blank", True)
        kwargs.setdefault("null", True)
        kwargs.setdefault("spec", spec)
        super().__init__(
            *args,
            **kwargs,
        )


class IconImageField(ResizedImageField):
    spec_class = api_settings.ICON_IMAGE_SPEC


class ThumbnailImageField(ResizedImageField):
    spec_class = api_settings.THUMBNAIL_IMAGE_SPEC


class AvatarImageField(ResizedImageField):
    spec_class = api_settings.AVATAR_IMAGE_SPEC


class FullImageField(ResizedImageField):
    spec_class = api_settings.FULL_IMAGE_SPEC
