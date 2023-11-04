"""Widgets to use in form fields"""
# pylint: disable=import-error
import os
import uuid

from django import forms
from django.forms.widgets import FILE_INPUT_CONTRADICTION
from django.forms import ClearableFileInput
from django.utils.safestring import mark_safe

from .cache import FileCache


class ResubmitBaseWidget(ClearableFileInput):
    """base widget, based on ClearableFileInput"""

    def __init__(self, attrs=None, field_type=None):
        super().__init__(attrs=attrs)
        self.field_type = field_type
        self.input_name = None
        self.cache_key = None

    def value_from_datadict(self, data, files, name):
        """override value_from_datadict to return the cached value instead"""
        upload = super().value_from_datadict(data, files, name)
        if upload == FILE_INPUT_CONTRADICTION:
            return upload

        self.input_name = f"{name}_cache_key"
        self.cache_key = data.get(self.input_name, "")

        if name in files:
            self.cache_key = random_key()[:10]
            upload = files[name]
            FileCache().set(self.cache_key, upload)
        elif self.cache_key:
            restored = FileCache().get(self.cache_key, name)
            if restored:
                upload = restored
                files[name] = upload
        return upload

    def output_extra_data(self, value):
        """filename and hidden field element to add to form"""
        output = ""
        if value and self.cache_key:
            output += " " + filename_from_value(value)
        if self.cache_key:
            output += forms.HiddenInput().render(
                self.input_name,
                self.cache_key,
                {},
            )
        return output


class ResubmitFileWidget(ResubmitBaseWidget):
    """resubmit widget for files in ordinary forms"""

    template_with_initial = getattr(ClearableFileInput, "template_with_initial", "")
    template_with_clear = getattr(ClearableFileInput, "template_with_clear", "")

    def render(
        self, name, value, attrs=None, **kwargs
    ):  # pylint: disable=unused-argument
        """override render function to add hidden input"""
        output = ClearableFileInput.render(self, name, value, attrs)
        output += self.output_extra_data(value)
        return mark_safe(output)


class ResubmitImageWidget(ResubmitFileWidget):
    """resubmit widget for image files in ordinary forms"""

    pass  # pylint: disable=unnecessary-pass


def random_key():
    """create and return a uuid"""
    return uuid.uuid4().hex


def filename_from_value(value):
    """get just the filename from a file value"""
    return os.path.split(value.name)[-1] if value else None
