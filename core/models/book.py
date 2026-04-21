from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class ApprovedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_approved=True)

class Book(models.Model):
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Створив")
    title = models.CharField(max_length=255, verbose_name="Назва")
    author = models.CharField(max_length=255, verbose_name="Автор")
    year = models.IntegerField(verbose_name="Рік")
    description = models.TextField(blank=True, verbose_name="Опис")
    cover_image = models.ImageField(upload_to='books/covers/', blank=True, null=True, verbose_name="Файл обкладинки")
    cover_url = models.URLField(blank=True, verbose_name="Посилання на обкладинку")
    genre = models.CharField(max_length=100, blank=True, verbose_name="Жанр")
    created_at = models.DateTimeField(auto_now_add=True)
    views_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.author}"

    def get_cover(self):
        if self.cover_image:
            return self.cover_image.url
        return self.cover_url if self.cover_url else None

    def get_absolute_url(self):
        return reverse('core:book_detail', kwargs={'pk': self.pk})

class Chapter(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=255, verbose_name="Назва розділу")
    number = models.IntegerField(verbose_name="Номер")
    description = models.TextField(blank=True, verbose_name="Опис")
    mood_tags = models.CharField(max_length=200, blank=True)
    is_approved = models.BooleanField(default=False, verbose_name="Підтверджено")

    objects = models.Manager()
    approved = ApprovedManager()

    class Meta:
        verbose_name = "Розділ"
        verbose_name_plural = "Розділи"
        ordering = ['number']

    def __str__(self):
        return f"Розділ {self.number}: {self.title}"

    def get_absolute_url(self):
        return reverse('core:chapter_detail', kwargs={'book_id': self.book.id, 'chapter_num': self.number})