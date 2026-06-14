from rest_framework import serializers

from core.models import Comment


class CommentReplySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "username", "text", "created_at")
        read_only_fields = ("id", "username", "created_at")


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    replies = CommentReplySerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = (
            "id",
            "username",
            "text",
            "book",
            "chapter",
            "playlist",
            "parent",
            "replies",
            "created_at",
        )
        read_only_fields = ("id", "username", "replies", "created_at")

    def validate(self, attrs: dict) -> dict:
        targets = [attrs.get("book"), attrs.get("chapter"), attrs.get("playlist")]
        if not any(targets):
            raise serializers.ValidationError(
                "A comment must be attached to a book, chapter, or playlist."
            )
        return attrs
