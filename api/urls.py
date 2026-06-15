from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from api.v1.views.auth import RegisterView, LoginView, LogoutView
from api.v1.views.book import BookViewSet
from api.v1.views.chapter import ChapterDetailView, ChapterMusicView, MusicLikeView, MusicDeleteView
from api.v1.views.author import AuthorDetailView, AuthorFollowView
from api.v1.views.comment import CommentCreateView, CommentDeleteView
from api.v1.views.playlist import PlaylistDetailView, PlaylistLikeView, PlaylistTracksView
from api.v1.views.search import MusicSearchView, BookSearchView
from api.v1.views.verification import AuthorVerificationView
from api.v1.views.profile import (
    ProfileMeView,
    ProfileSavedView,
    ProfilePlaylistsView,
    ProfileRecommendationsView,
    ProfileNotificationsView,
    ProfileNotificationsReadView,
)

router = DefaultRouter()
router.register(r"books", BookViewSet, basename="book")

urlpatterns = [
    path(
        "v1/",
        include([
            path("", include(router.urls)),
            path("chapters/<int:pk>/", ChapterDetailView.as_view()),
            path("chapters/<int:pk>/music/", ChapterMusicView.as_view()),
            path("music/<int:pk>/like/", MusicLikeView.as_view()),
            path("music/<int:pk>/", MusicDeleteView.as_view()),
            path("authors/<slug:slug>/", AuthorDetailView.as_view()),
            path("authors/<slug:slug>/follow/", AuthorFollowView.as_view()),
            path("playlists/<slug:slug>/", PlaylistDetailView.as_view()),
            path("playlists/<slug:slug>/like/", PlaylistLikeView.as_view()),
            path("playlists/<slug:slug>/tracks/", PlaylistTracksView.as_view()),
            path("comments/", CommentCreateView.as_view()),
            path("comments/<int:pk>/", CommentDeleteView.as_view()),
            path("search/music/", MusicSearchView.as_view()),
            path("search/books/", BookSearchView.as_view()),
            path("author-verification/", AuthorVerificationView.as_view()),
            path("auth/register/", RegisterView.as_view()),
            path("auth/login/", LoginView.as_view()),
            path("auth/logout/", LogoutView.as_view()),
            path("auth/refresh/", TokenRefreshView.as_view()),
            path("profile/me/", ProfileMeView.as_view()),
            path("profile/saved/", ProfileSavedView.as_view()),
            path("profile/playlists/", ProfilePlaylistsView.as_view()),
            path("profile/recommendations/", ProfileRecommendationsView.as_view()),
            path("profile/notifications/", ProfileNotificationsView.as_view()),
            path("profile/notifications/read/", ProfileNotificationsReadView.as_view()),
        ]),
    ),
]