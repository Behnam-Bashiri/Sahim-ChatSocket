from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile
from .tasks import compress_profile_image


@receiver(post_save, sender=UserProfile)
def compress_image_signal(sender, instance, created, **kwargs):
    if instance.profile_picture:
        compress_profile_image.delay(instance.id)
