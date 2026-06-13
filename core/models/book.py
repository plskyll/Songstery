from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_approved=True)


class ApprovedChapterManager(models.Manager):
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
    title = models.CharField(max_length=255, verbose_name='Title')
    author = models.CharField(max_length=255, verbose_name='Author')
    year = models.IntegerField(verbose_name='Year')
    description = models.TextField(blank=True, verbose_name='Description')
    cover_image = models.ImageField(
        upload_to='books/covers/',
        blank=True,
        null=True,
        verbose_name='Cover file',
    )
    cover_url = models.URLField(blank=True, verbose_name='Cover URL')
    genre = models.CharField(max_length=100, blank=True, verbose_name='Genre')
    is_approved = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='Approved',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    views_count = models.IntegerField(default=0)

    objects = models.Manager()
    published = PublishedManager()

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

    def is_visible_to(self, user):
        if self.is_approved:
            return True
        return user.is_authenticated and (
            user == self.creator or user.is_staff
        )

    @property
    def average_rating(self):
        from django.db.models import Avg
        result = self.ratings.aggregate(avg=Avg('score'))
        return round(result['avg'] or 0, 1)


class Chapter(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=255, verbose_name='Title')
    number = models.IntegerField(verbose_name='Number')
    description = models.TextField(blank=True, verbose_name='Description')
    mood_tags = models.CharField(max_length=200, blank=True)
    is_approved = models.BooleanField(default=False, verbose_name='Approved')

    objects = models.Manager()
    approved = ApprovedChapterManager()

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
