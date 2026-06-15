from .author import AuthorSerializer
from .book import BookListSerializer, BookDetailSerializer, BookCreateSerializer
from .chapter import ChapterSerializer, ChapterDetailSerializer
from .comment import CommentSerializer
from .music import MusicRecommendationSerializer, PlaylistSerializer, PlaylistTrackSerializer
from .notification import NotificationSerializer
from .user import UserSerializer, UserUpdateSerializer, RegisterSerializer

__all__ = [
    "AuthorSerializer",
    "BookListSerializer",
    "BookDetailSerializer",
    "BookCreateSerializer",
    "ChapterSerializer",
    "ChapterDetailSerializer",
    "CommentSerializer",
    "MusicRecommendationSerializer",
    "PlaylistSerializer",
    "PlaylistTrackSerializer",
    "NotificationSerializer",
    "UserSerializer",
    "UserUpdateSerializer",
    "RegisterSerializer",
]
