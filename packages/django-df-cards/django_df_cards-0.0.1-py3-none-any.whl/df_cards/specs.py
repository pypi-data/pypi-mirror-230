from imagekit import ImageSpec
from imagekit.processors import ResizeToFill


class IconImageSpec(ImageSpec):
    processors = [ResizeToFill(50, 50)]
    format = "PNG"
    options = {"quality": 100}


class ThumbnailImageSpec(ImageSpec):
    processors = [ResizeToFill(150, 150)]
    format = "JPEG"
    options = {"quality": 80}


class AvatarImageSpec(ImageSpec):
    processors = [ResizeToFill(256, 256)]
    format = "JPEG"
    options = {"quality": 80}


class FullImageSpec(ImageSpec):
    processors = [ResizeToFill(1024, 1024)]
    format = "JPEG"
    options = {"quality": 80}
