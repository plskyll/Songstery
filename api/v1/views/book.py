from django.db.models import F, QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.models import Book, BookRating, Chapter, Language, MusicRecommendation, SavedBook
from core.models.book import BookTranslation, ChapterTranslation
from core.utils.slugs import generate_unique_slug
from api.v1.filters.book import BookFilter
from api.v1.filters.pagination import BookCursorPagination, MusicCursorPagination
from api.v1.filters.permissions import IsOwnerOrStaff
from api.v1.serializers.book import BookCreateSerializer, BookDetailSerializer, BookListSerializer
from api.v1.serializers.chapter import ChapterSerializer
from api.v1.serializers.music import MusicRecommendationSerializer, PlaylistSerializer


class BookViewSet(ModelViewSet):
    pagination_class = BookCursorPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = BookFilter
    ordering_fields = ("created_at", "views_count", "year")
    ordering = ("-created_at",)
    lookup_field = "slug"

    def get_queryset(self) -> QuerySet:
        user = self.request.user
        base_qs = (
            Book.objects
            if (user.is_authenticated and user.is_staff)
            else Book.published
        )
        return base_qs.select_related(
            "author", "genre", "verified_author"
        ).prefetch_related(
            "translations",
            "author__translations",
            "genre__translations",
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BookDetailSerializer
        if self.action in ("create", "partial_update", "update"):
            return BookCreateSerializer
        return BookListSerializer

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        if self.action in ("partial_update", "update"):
            return [IsAuthenticated(), IsOwnerOrStaff()]
        return [IsAuthenticatedOrReadOnly()]

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        session_key = f"api_viewed_book_{instance.pk}"
        if not request.session.get(session_key):
            Book.objects.filter(pk=instance.pk).update(views_count=F("views_count") + 1)
            request.session[session_key] = True
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer: BookCreateSerializer) -> None:
        title = serializer.validated_data.get("title", "")
        slug = generate_unique_slug(Book, title)
        book: Book = serializer.save(creator=self.request.user, slug=slug)

        uk = Language.objects.filter(code="uk").first()
        if uk:
            BookTranslation.objects.create(
                book=book,
                language=uk,
                title=title,
                description=serializer.validated_data.get("description", ""),
            )
            chapter = Chapter.objects.create(book=book, number=1, is_approved=True)
            ChapterTranslation.objects.create(chapter=chapter, language=uk, title="Chapter 1")

    @action(detail=True, methods=["get"], url_path="chapters")
    def chapters(self, request: Request, slug: str | None = None) -> Response:
        book = self.get_object()
        is_privileged = request.user.is_authenticated and (
                request.user == book.creator or request.user.is_staff
        )
        qs = book.chapters.all() if is_privileged else book.chapters.filter(is_approved=True)
        serializer = ChapterSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="playlists")
    def playlists(self, request: Request, slug: str | None = None) -> Response:
        book = self.get_object()
        qs = book.playlists.filter(is_public=True).order_by("-likes_count")
        serializer = PlaylistSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="music")
    def music(self, request: Request, slug: str | None = None) -> Response:
        book = self.get_object()
        qs = (
            MusicRecommendation.objects.filter(chapter__book=book)
            .order_by("-likes_count")
            .select_related("user")[:20]
        )
        serializer = MusicRecommendationSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["post"],
        url_path="save",
        permission_classes=[IsAuthenticated],
    )
    def save(self, request: Request, slug: str | None = None) -> Response:
        book = self.get_object()
        saved, created = SavedBook.objects.get_or_create(user=request.user, book=book)
        if not created:
            saved.delete()
        return Response({"saved": created})

    @action(
        detail=True,
        methods=["post"],
        url_path="rate",
        permission_classes=[IsAuthenticated],
    )
    def rate(self, request: Request, slug: str | None = None) -> Response:
        book = self.get_object()
        try:
            score = int(request.data.get("score", 0))
        except (TypeError, ValueError):
            return Response({"detail": "Invalid score."}, status=status.HTTP_400_BAD_REQUEST)
        if not 1 <= score <= 5:
            return Response(
                {"detail": "Score must be between 1 and 5."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        BookRating.objects.update_or_create(
            user=request.user, book=book, defaults={"score": score}
        )
        return Response({"avg_rating": book.average_rating})
