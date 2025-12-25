from django.contrib import admin
from modern_django_admin.admin import modern_admin_site
from .models import Chat, Message, FileMessage


class ChatAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "chat_name",
        "chat_type",
        "created_at",
        "get_participants",
        "last_message",
    )
    search_fields = ("chat_name",)
    list_filter = ("chat_type", "created_at")

    def get_participants(self, obj):
        return ", ".join([user.phone_number for user in obj.participants.all()])

    get_participants.short_description = "Participants"


class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "chat",
        "sender",
        "message_type",
        "timestamp",
        "is_read",
        "is_deleted",
    )
    list_filter = ("message_type", "is_read", "is_deleted", "timestamp")
    search_fields = ("content", "sender__phone_number")


class FileMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "chat", "sender", "file", "timestamp")
    search_fields = ("sender__phone_number",)
    list_filter = ("timestamp",)


modern_admin_site.register(Chat, ChatAdmin)
modern_admin_site.register(Message, MessageAdmin)
modern_admin_site.register(FileMessage, FileMessageAdmin)
