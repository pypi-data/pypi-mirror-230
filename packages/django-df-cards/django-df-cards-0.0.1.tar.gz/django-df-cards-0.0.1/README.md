# Django DF Cards

Model mixins to provide image/title/description and other fields to be displayed as cards.

## Installation:

- Install the package

```
pip install django-df-cards
```

## Usage:

```python
from df_cards.models import TitledCard, ThumbnailMixin, FullImageMixin

class Post(TitledCard, ThumbnailMixin, FullImageMixin):
    pass
```

will give you `Post` model with the following fields:

- `title` - CharField
- `description` - TextField
- `thumbnail` - ImageField
- `full_image` - ImageField
- `sequence` - PositiveIntegerField


## Development

Installing dev requirements:

```
pip install -e .[test]
```

Installing pre-commit hook:

```
pre-commit install
```

Running tests:

```
pytest
```
