from django.core.exceptions import ValidationError


def validate_file_type(value):
    if not value.name.endswith(("jpg", "jpeg", "png")):
        raise ValidationError("Only jpg, jpeg, png files are allowed.")
