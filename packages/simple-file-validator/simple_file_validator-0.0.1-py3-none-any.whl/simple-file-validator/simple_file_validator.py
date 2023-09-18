import os
from django.core.exceptions import ValidationError

def validate_file_extension(value, valid_extensions):
    ext = os.path.splitext(value.name)[1]  # Get the file extension

    if not ext.upper() in valid_extensions:
        raise ValidationError(f"Unsupported file extension. Supported extensions are: {', '.join(valid_extensions)}")
    