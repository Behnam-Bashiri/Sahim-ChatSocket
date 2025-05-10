from rest_framework import serializers
from .models import Chat, Message, FileMessage
from accounts.models import UserProfile


class ChatSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.all(), many=True
    )

    class Meta:
        model = Chat
        fields = ["id", "participants", "created_at"]


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all())
    chat = serializers.PrimaryKeyRelatedField(queryset=Chat.objects.all())
    media = serializers.FileField(source="file_message.file", required=False)

    class Meta:
        model = Message
        fields = ["id", "chat", "sender", "content", "timestamp", "media"]


class FileMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileMessage
        fields = ["id", "chat", "sender", "file", "timestamp"]
