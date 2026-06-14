from rest_framework import serializers

from core.models import Book
from .author import AuthorSerializer
from .chapter import ChapterSerializer
from .mixins import LangMixin
from .music import PlaylistSerializer


class BookListSerializer(LangMixin, serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()
    genre = serializers.SerializerMethodField()
    cover_url = serializers.SerializerMethodField()
    avg_rating = serializers.FloatField(source="average_rating", read_only=True)
    chapters_count = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = (
            "slug",
            "title",
            "author_name",
            "cover_url",
            "genre",
            "avg_rating",
            "chapters_count",
            "year",
            "created_at",
        )

    def get_title(self, obj: Book) -> str:
        return obj.get_title(self._lang())

    def get_author_name(self, obj: Book) -> str:
        return obj.get_author_name(self._lang())

    def get_genre(self, obj: Book) -> str:
        return obj.get_genre_name(self._lang())

    def get_cover_url(self, obj: Book) -> str | None:
        return obj.get_cover()

    def get_chapters_count(self, obj: Book) -> int:
        return obj.chapters.filter(is_approved=True).count()


class BookDetailSerializer(LangMixin, serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()
    genre = serializers.SerializerMethodField()
    cover_url = serializers.SerializerMethodField()
    avg_rating = serializers.FloatField(source="average_rating", read_only=True)
    chapters = ChapterSerializer(many=True, read_only=True)
    playlists = PlaylistSerializer(many=True, read_only=True)
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Book
        fields = (
            "slug",
            "title",
            "description",
            "author",
            "author_name",
            "cover_url",
            "genre",
            "year",
            "isbn",
            "open_library_id",
            "is_approved",
            "views_count",
            "avg_rating",
            "created_at",
            "chapters",
            "playlists",
        )

    def get_title(self, obj: Book) -> str:
        return obj.get_title(self._lang())

    def get_description(self, obj: Book) -> str:
        return obj.get_description(self._lang())

    def get_author_name(self, obj: Book) -> str:
        return obj.get_author_name(self._lang())

    def get_genre(self, obj: Book) -> str:
        return obj.get_genre_name(self._lang())

    def get_cover_url(self, obj: Book) -> str | None:
        return obj.get_cover()


class BookCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Book
        fields = (
            "title",
            "description",
            "year",
            "cover_url",
            "isbn",
        )

    def validate_year(self, value: int) -> int:
        if value < 0 or value > 2100:
            raise serializers.ValidationError("Invalid year.")
        return value
