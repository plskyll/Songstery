from rest_framework import serializers

from core.models import Chapter
from .mixins import LangMixin
from .music import MusicRecommendationSerializer


class ChapterSerializer(LangMixin, serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    mood_tags = serializers.SerializerMethodField()
    music_count = serializers.SerializerMethodField()

    class Meta:
        model = Chapter
        fields = ("id", "number", "title", "mood_tags", "music_count", "is_approved")

    def get_title(self, obj: Chapter) -> str:
        return obj.get_title(self._lang())

    def get_mood_tags(self, obj: Chapter) -> str:
        return obj.get_mood_tags(self._lang())

    def get_music_count(self, obj: Chapter) -> int:
        return obj.music_recommendations.count()


class ChapterDetailSerializer(LangMixin, serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    mood_tags = serializers.SerializerMethodField()
    music_recommendations = MusicRecommendationSerializer(many=True, read_only=True)

    class Meta:
        model = Chapter
        fields = (
            "id",
            "number",
            "title",
            "description",
            "mood_tags",
            "is_approved",
            "music_recommendations",
        )

    def get_title(self, obj: Chapter) -> str:
        return obj.get_title(self._lang())

    def get_description(self, obj: Chapter) -> str:
        return obj.get_description(self._lang())

    def get_mood_tags(self, obj: Chapter) -> str:
        return obj.get_mood_tags(self._lang())
