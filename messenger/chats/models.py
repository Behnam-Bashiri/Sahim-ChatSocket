from django.db import models
from accounts.models import UserProfile
from .validators import validate_file_type


class Chat(models.Model):
    participants = models.ManyToManyField(UserProfile, related_name="chats")
    created_at = models.DateTimeField(auto_now_add=True)
    chat_name = models.CharField(max_length=100, blank=True, null=True)
    chat_type = models.CharField(
        max_length=20,
        choices=[("private", "Private"), ("group", "Group")],
        default="private",
    )
    last_message = models.ForeignKey(
        "Message",
        related_name="last_message",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return f"Chat between {', '.join([user.phone_number for user in self.participants.all()])}"


class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(
        UserProfile, related_name="sent_messages", on_delete=models.CASCADE
    )
    content = models.TextField()
    message_type = models.CharField(
        max_length=20,
        choices=[("text", "Text"), ("image", "Image"), ("file", "File")],
        default="text",
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender.phone_number} at {self.timestamp}"


class FileMessage(models.Model):
    chat = models.ForeignKey(
        Chat, related_name="file_messages", on_delete=models.CASCADE
    )
    sender = models.ForeignKey(
        UserProfile, related_name="sent_files", on_delete=models.CASCADE
    )
    file = models.FileField(upload_to="chat_files/", validators=[validate_file_type])
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File from {self.sender.phone_number} at {self.timestamp}"
