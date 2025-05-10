from rest_framework import serializers
from .models import Chat, Message
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

    class Meta:
        model = Message
        fields = ["id", "chat", "sender", "content", "timestamp", "media"]
