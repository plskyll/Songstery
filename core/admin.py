from django.contrib import admin
from .models import (
    Book, Chapter, MusicRecommendation,
    Playlist, PlaylistTrack, Like, Comment, SavedBook,
    UserProfile, AuthorVerification, Follow, BookRating,
)


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 1
    fields = ['number', 'title', 'mood_tags', 'is_approved']


class MusicRecommendationInline(admin.TabularInline):
    model = MusicRecommendation
    extra = 0
    fields = ['track_title', 'artist', 'link_url', 'mood', 'likes_count']
    readonly_fields = ['likes_count']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'year', 'genre', 'verified_author', 'views_count', 'created_at']
    list_filter = ['genre', 'year']
    search_fields = ['title', 'author']
    raw_id_fields = ['creator', 'verified_author']
    inlines = [ChapterInline]


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['book', 'number', 'title', 'is_approved', 'mood_tags']
    list_filter = ['book', 'is_approved']
    search_fields = ['title', 'book__title']
    inlines = [MusicRecommendationInline]


@admin.register(MusicRecommendation)
class MusicRecommendationAdmin(admin.ModelAdmin):
    list_display = ['track_title', 'artist', 'mood', 'chapter', 'user', 'likes_count', 'created_at']
    list_filter = ['link_type', 'mood', 'created_at']
    search_fields = ['track_title', 'artist']


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['title', 'book', 'creator', 'likes_count', 'is_public', 'created_at']
    list_filter = ['is_public', 'created_at']


@admin.register(PlaylistTrack)
class PlaylistTrackAdmin(admin.ModelAdmin):
    list_display = ['playlist', 'track_title', 'artist', 'order']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'text_preview', 'created_at']

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text

    text_preview.short_description = 'Text'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'music_recommendation', 'playlist', 'created_at']


@admin.register(SavedBook)
class SavedBookAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'created_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'is_verified_author']
    list_filter = ['is_verified_author']
    search_fields = ['user__username', 'user__email']


@admin.register(AuthorVerification)
class AuthorVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'status', 'submitted_at', 'reviewed_at', 'reviewed_by']
    list_filter = ['status']
    readonly_fields = ['submitted_at', 'reviewed_at', 'reviewed_by']
    search_fields = ['user__username', 'book__title']
    actions = ['approve_selected', 'reject_selected']

    def approve_selected(self, request, queryset):
        count = 0
        for verification in queryset.filter(status=AuthorVerification.STATUS_PENDING):
            verification.approve(admin_user=request.user)
            count += 1
        self.message_user(request, f'Approved {count} application(s).')

    approve_selected.short_description = 'Approve selected'

    def reject_selected(self, request, queryset):
        count = 0
        for verification in queryset.filter(status=AuthorVerification.STATUS_PENDING):
            verification.reject(admin_user=request.user, note='Rejected via bulk action.')
            count += 1
        self.message_user(request, f'Rejected {count} application(s).')

    reject_selected.short_description = 'Reject selected'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'created_at']
    search_fields = ['follower__username', 'following__username']


@admin.register(BookRating)
class BookRatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'score']
    list_filter = ['score']
