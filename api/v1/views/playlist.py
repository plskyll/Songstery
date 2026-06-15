from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Like, Playlist, PlaylistTrack
from api.v1.serializers.music import PlaylistSerializer, PlaylistTrackSerializer


class PlaylistDetailView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request: Request, slug: str) -> Response:
        playlist = get_object_or_404(Playlist, slug=slug)
        serializer = PlaylistSerializer(playlist, context={"request": request})
        return Response(serializer.data)


class PlaylistLikeView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request: Request, slug: str) -> Response:
        playlist = get_object_or_404(Playlist, slug=slug)
        like, created = Like.objects.get_or_create(user=request.user, playlist=playlist)
        if created:
            Playlist.objects.filter(pk=playlist.pk).update(likes_count=F("likes_count") + 1)
        else:
            like.delete()
            Playlist.objects.filter(pk=playlist.pk).update(likes_count=F("likes_count") - 1)
        playlist.refresh_from_db(fields=["likes_count"])
        return Response({"liked": created, "likes_count": playlist.likes_count})


class PlaylistTracksView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request: Request, slug: str) -> Response:
        playlist = get_object_or_404(Playlist, slug=slug)
        if request.user != playlist.creator:
            return Response(
                {"detail": "Only the creator can add tracks."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = PlaylistTrackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        last = playlist.tracks.order_by("-order").first()
        order = (last.order + 1) if last else 1
        serializer.save(playlist=playlist, order=order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
