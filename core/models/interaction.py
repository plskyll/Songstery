from django.db import models
from django.contrib.auth.models import User
from .book import Book, Chapter
from .music import MusicRecommendation, Playlist


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    music_recommendation = models.ForeignKey(
        MusicRecommendation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='likes',
    )
    playlist = models.ForeignKey(
        Playlist,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='likes',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['user', 'music_recommendation'], ['user', 'playlist']]

    def __str__(self):
        target = self.music_recommendation or self.playlist
        return f'{self.user.username} likes {target}'


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, null=True, blank=True, related_name='comments'
    )
    chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE, null=True, blank=True, related_name='comments'
    )
    playlist = models.ForeignKey(
        Playlist, on_delete=models.CASCADE, null=True, blank=True, related_name='comments'
    )
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username}: {self.text[:40]}'


class SavedBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'book']

    def __str__(self):
        return f'{self.user.username} saved {self.book.title}'


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['follower', 'following']

    def __str__(self):
        return f'{self.follower.username} -> {self.following.username}'


class BookRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='ratings')
    score = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ['user', 'book']

    def __str__(self):
        return f'{self.user.username} rated {self.book.title} {self.score}/5'
