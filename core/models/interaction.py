from django.db import models
from django.contrib.auth.models import User
from .book import Book, Chapter
from .music import MusicRecommendation, Playlist

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    music_recommendation = models.ForeignKey(MusicRecommendation, on_delete=models.CASCADE, null=True, blank=True, related_name='likes')
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, null=True, blank=True, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['user', 'music_recommendation'], ['user', 'playlist']]

class Comment(models.Model):
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'book']