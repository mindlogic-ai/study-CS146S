from rest_framework import serializers

from .models import ActionItem, Note


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ["id", "title", "content", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ActionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionItem
        fields = ["id", "description", "completed", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
