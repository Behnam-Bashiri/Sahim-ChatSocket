# chats/tasks.py

from celery import shared_task
from PIL import Image
import os
from django.conf import settings
from .models import FileMessage


@shared_task
def compress_chat_file(file_message_id):
    try:
        file_message = FileMessage.objects.get(id=file_message_id)
        if not file_message.file:
            print("No file found.")
            return

        file_path = file_message.file.path
        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext not in [".jpg", ".jpeg", ".png"]:
            print(f"Skipped non-image file: {file_ext}")
            return

        print(f"Compressing image at {file_path}")

        img = Image.open(file_path)

        if img.format not in ["JPEG", "JPG", "PNG"]:
            print(f"Unsupported image format: {img.format}")
            return

        img = img.convert("RGB")
        img.save(file_path, "JPEG", quality=70, optimize=True)

        print(f"Image compressed for FileMessage {file_message_id}")

    except Exception as e:
        print(f"Compression failed for FileMessage {file_message_id}: {e}")
