from celery import shared_task
from PIL import Image
import os
from django.conf import settings
from .models import UserProfile


@shared_task
def compress_profile_image(user_id):
    try:
        user = UserProfile.objects.get(id=user_id)
        if not user.profile_picture:
            return

        print(
            f"Found user {user_id} with profile picture at {user.profile_picture.path}"
        )

        image_path = user.profile_picture.path
        img = Image.open(image_path)

        # بررسی فرمت مجاز
        if img.format not in ["JPEG", "JPG", "PNG"]:
            print(f"Unsupported image format: {img.format}")
            return

        # کاهش کیفیت
        img = img.convert("RGB")
        img.save(image_path, "JPEG", quality=70, optimize=True)

        print(f"Image compressed and saved for user {user_id}")

    except Exception as e:
        print(f"Image compression error: {e}")
