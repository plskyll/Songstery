from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class ApprovedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_approved=True)


class Book(models.Model):
    creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_books',
        verbose_name='Added by',
    )
    verified_author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='authored_books',
        verbose_name='Verified author',
    )
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    year = models.IntegerField()
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='books/covers/', blank=True, null=True)
    cover_url = models.URLField(blank=True)
    genre = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    views_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Book'
        verbose_name_plural = 'Books'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} — {self.author}'

    def get_cover(self):
        if self.cover_image:
            return self.cover_image.url
        return self.cover_url or None

    def get_absolute_url(self):
        return reverse('core:book_detail', kwargs={'pk': self.pk})

    @property
    def average_rating(self):
        from django.db.models import Avg
        result = self.ratings.aggregate(avg=Avg('score'))
        return round(result['avg'] or 0, 1)


class Chapter(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=255)
    number = models.IntegerField()
    description = models.TextField(blank=True)
    mood_tags = models.CharField(max_length=200, blank=True)
    is_approved = models.BooleanField(default=False)

    objects = models.Manager()
    approved = ApprovedManager()

    class Meta:
        verbose_name = 'Chapter'
        verbose_name_plural = 'Chapters'
        ordering = ['number']

    def __str__(self):
        return f'Ch.{self.number}: {self.title}'

    def get_absolute_url(self):
        return reverse(
            'core:chapter_detail',
            kwargs={'book_id': self.book.id, 'chapter_num': self.number},
        )
