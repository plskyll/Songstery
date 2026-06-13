from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models
from slugify import slugify

if TYPE_CHECKING:
    pass


def generate_unique_slug(model: type[models.Model], text: str, slug_field: str = "slug") -> str:
    """
    Transliterate *text* to an ASCII slug and ensure uniqueness within *model*
    by appending -2, -3, … on collisions.

    Args:
        model:      Django model class to check uniqueness against.
        text:       Source string (any language).
        slug_field: Name of the slug field on the model (default: "slug").

    Returns:
        A unique slug string.
    """
    base = slugify(text, allow_unicode=False) or "item"
    slug = base
    counter = 2

    qs = model._default_manager.all()
    while qs.filter(**{slug_field: slug}).exists():
        slug = f"{base}-{counter}"
        counter += 1

    return slug
