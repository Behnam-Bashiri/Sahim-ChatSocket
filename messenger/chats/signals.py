from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FileMessage
from .tasks import compress_chat_file


@receiver(post_save, sender=FileMessage)
def handle_file_upload(sender, instance, created, **kwargs):
    if created and instance.file:
        file_name = instance.file.name.lower()
        if file_name.endswith((".jpg", ".jpeg", ".png")):
            compress_chat_file.delay(instance.id)
