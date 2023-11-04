"""Preserve files in Django forms during form validation errors."""
# pylint: disable=import-error
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


if "file_resubmit" not in settings.CACHES:
    raise ImproperlyConfigured("CACHES['file_resubmit'] is not defined in settings.py")
