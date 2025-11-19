from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Book(models.Model):
    """Книга"""
    creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Створив"
    )
    title = models.CharField(max_length=255, verbose_name="Назва")
    author = models.CharField(max_length=255, verbose_name="Автор")
    year = models.IntegerField(verbose_name="Рік")
    description = models.TextField(blank=True, verbose_name="Опис")

    # Обкладинки: файл (пріоритет) або посилання
    cover_image = models.ImageField(
        upload_to='books/covers/',
        blank=True,
        null=True,
        verbose_name="Файл обкладинки"
    )
    cover_url = models.URLField(blank=True, verbose_name="Посилання на обкладинку")

    genre = models.CharField(max_length=100, blank=True, verbose_name="Жанр")
    created_at = models.DateTimeField(auto_now_add=True)
    views_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.title} - {self.author}"

    def get_cover(self):
        """Повертає URL обкладинки: пріоритет у завантаженого файлу, потім посилання"""
        if self.cover_image:
            return self.cover_image.url
        if self.cover_url:
            return self.cover_url
        return None

    def get_absolute_url(self):
        return reverse('core:book_detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
        ordering = ['-created_at']


class Chapter(models.Model):
    """Розділ книги"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=255, verbose_name="Назва розділу")
    number = models.IntegerField(verbose_name="Номер")
    description = models.TextField(blank=True, verbose_name="Опис")
    mood_tags = models.CharField(
        max_length=200,
        blank=True,
        help_text="Наприклад: спокій, напруга, епічність"
    )

    # Статус модерації (False = потребує перевірки адміном)
    is_approved = models.BooleanField(default=False, verbose_name="Підтверджено")

    def __str__(self):
        return f"Розділ {self.number}: {self.title}"

    def get_absolute_url(self):
        return reverse('core:chapter_detail', kwargs={
            'book_id': self.book.id,
            'chapter_num': self.number
        })

    class Meta:
        ordering = ['number']
        verbose_name = "Розділ"
        verbose_name_plural = "Розділи"


class MusicRecommendation(models.Model):
    """Музична рекомендація"""
    LINK_TYPES = [
        ('youtube', 'YouTube'),
        ('spotify', 'Spotify'),
        ('soundcloud', 'SoundCloud'),
        ('other', 'Інше'),
    ]

    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name='music_recommendations'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    track_title = models.CharField(max_length=255, verbose_name="Назва треку")
    artist = models.CharField(max_length=255, verbose_name="Виконавець")
    link_type = models.CharField(max_length=20, choices=LINK_TYPES, default='youtube')
    link_url = models.URLField(verbose_name="Посилання")
    embed_code = models.CharField(
        max_length=100,
        blank=True,
        help_text="Для YouTube: ID відео"
    )
    comment = models.TextField(blank=True, verbose_name="Коментар")

    likes_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.track_title} - {self.artist}"

    class Meta:
        verbose_name = "Музична рекомендація"
        verbose_name_plural = "Музичні рекомендації"
        ordering = ['-likes_count', '-created_at']


class Playlist(models.Model):
    """Плейлист"""
    title = models.CharField(max_length=255, verbose_name="Назва")
    description = models.TextField(blank=True, verbose_name="Опис")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='playlists')
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='playlists'
    )
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    mood = models.CharField(max_length=200, blank=True)

    # НОВЕ ПОЛЕ: Зовнішнє посилання
    external_link = models.URLField(blank=True, verbose_name="Посилання на плейлист (YouTube/Spotify)")

    likes_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('core:playlist_detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = "Плейлист"
        verbose_name_plural = "Плейлисти"
        ordering = ['-created_at']


class PlaylistTrack(models.Model):
    """Трек у плейлисті"""
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='tracks')
    track_title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    link_url = models.URLField()
    embed_code = models.CharField(max_length=100, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']


class Like(models.Model):
    """Лайк"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    music_recommendation = models.ForeignKey(
        MusicRecommendation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='likes'
    )
    playlist = models.ForeignKey(
        Playlist,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            ['user', 'music_recommendation'],
            ['user', 'playlist']
        ]


class Comment(models.Model):
    """Коментар"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(verbose_name="Коментар")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True, blank=True, related_name='comments')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, null=True, blank=True, related_name='comments')
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, null=True, blank=True, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class SavedBook(models.Model):
    """Збережена книга"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'book']