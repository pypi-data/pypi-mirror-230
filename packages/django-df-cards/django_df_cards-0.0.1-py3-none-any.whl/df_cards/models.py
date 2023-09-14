from django.db import models

from df_cards.fields import (
    AvatarImageField,
    FullImageField,
    IconImageField,
    ThumbnailImageField,
)


class BaseCard(models.Model):
    class Meta:
        abstract = True

    description = models.TextField(blank=True, default="")
    sequence = models.PositiveIntegerField(default=0)


class NamedCard(BaseCard):
    class Meta:
        abstract = True

    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class TitledCard(BaseCard):
    class Meta:
        abstract = True

    title = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.title


class ThumbnailMixin(models.Model):
    class Meta:
        abstract = True

    thumbnail = ThumbnailImageField()


class IconMixin(models.Model):
    class Meta:
        abstract = True

    icon = IconImageField()


class FullImageMixin(models.Model):
    class Meta:
        abstract = True

    full_image = FullImageField()


class AvatarMixin(models.Model):
    class Meta:
        abstract = True

    avatar = AvatarImageField()
