from celery import shared_task
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


@shared_task
def process_and_save_image(chat_id, message_id, image_data):
    from chats.models import Message

    try:
        message = Message.objects.get(id=message_id, chat_id=chat_id)
        img = Image.open(image_data)
        img.thumbnail((800, 800))  # Resize to max 800x800

        # Save image back to memory
        thumb_io = BytesIO()
        img.save(thumb_io, img.format, quality=85)
        new_image = InMemoryUploadedFile(
            thumb_io,
            "ImageField",
            f"{message.id}.{img.format}",
            f"image/{img.format.lower()}",
            sys.getsizeof(thumb_io),
            None,
        )

        message.content = new_image
        message.save()

    except Exception as e:
        print(f"Error processing image: {e}")
