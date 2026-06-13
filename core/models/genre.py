from django.db import models

from .language import Language


class Genre(models.Model):
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Genre"
        verbose_name_plural = "Genres"
        ordering = ["slug"]

    def __str__(self) -> str:
        return self.slug

    def get_name(self, lang: str = "uk") -> str:
        translation = self.translations.filter(language__code=lang).first()
        if translation:
            return translation.name
        fallback = self.translations.first()
        return fallback.name if fallback else self.slug


class GenreTranslation(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name="translations")
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ["genre", "language"]
        verbose_name = "Genre translation"
        verbose_name_plural = "Genre translations"

    def __str__(self) -> str:
        return f"{self.genre.slug} [{self.language.code}] → {self.name}"
