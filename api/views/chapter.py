from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Chapter, Like, MusicRecommendation
from ..serializers import ChapterDetailSerializer, MusicRecommendationSerializer


class ChapterDetailView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request: Request, pk: int) -> Response:
        chapter = get_object_or_404(Chapter, pk=pk)
        user = request.user
        is_privileged = user.is_authenticated and (
            user == chapter.book.creator or user.is_staff
        )
        if not chapter.is_approved and not is_privileged:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ChapterDetailSerializer(chapter, context={"request": request})
        return Response(serializer.data)


class ChapterMusicView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request: Request, pk: int) -> Response:
        chapter = get_object_or_404(Chapter, pk=pk)
        serializer = MusicRecommendationSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(chapter=chapter, user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MusicLikeView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request: Request, pk: int) -> Response:
        music = get_object_or_404(MusicRecommendation, pk=pk)
        like, created = Like.objects.get_or_create(
            user=request.user, music_recommendation=music
        )
        if created:
            MusicRecommendation.objects.filter(pk=pk).update(
                likes_count=F("likes_count") + 1
            )
        else:
            like.delete()
            MusicRecommendation.objects.filter(pk=pk).update(
                likes_count=F("likes_count") - 1
            )
        music.refresh_from_db(fields=["likes_count"])
        return Response({"liked": created, "likes_count": music.likes_count})


class MusicDeleteView(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request: Request, pk: int) -> Response:
        music = get_object_or_404(MusicRecommendation, pk=pk)
        if music.user != request.user and not request.user.is_staff:
            return Response(
                {"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN
            )
        music.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
