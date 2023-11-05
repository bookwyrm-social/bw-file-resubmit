"""For admin views"""
# pylint: disable=ungrouped-imports,import-error

from django.db import models
from django.utils.safestring import mark_safe

try:
    from sorl.thumbnail.fields import ImageField
    from sorl.thumbnail.admin.current import AdminImageWidget as BaseWidget
except ImportError:
    from django.forms import ImageField
    from django.contrib.admin.widgets import AdminFileWidget as BaseWidget

from .widgets import ResubmitBaseWidget, ResubmitFileWidget


class AdminResubmitImageWidget(ResubmitBaseWidget, BaseWidget):
    """Image widget with render override"""

    def render(
        self, name, value, attrs=None, **kwargs
    ):  # pylint: disable=unused-argument
        """override render function to add hidden input"""
        output = super().render(name, value, attrs)
        output += self.output_extra_data(value)
        return mark_safe(output)


class AdminResubmitMixin:  # pylint: disable=too-few-public-methods
    """Admin mixin"""

    def formfield_for_dbfield(self, db_field, **kwargs):
        """return the relevant formfield"""

        if isinstance(db_field, (ImageField, models.ImageField)):
            return db_field.formfield(widget=AdminResubmitImageWidget)

        if isinstance(db_field, models.FileField):
            return db_field.formfield(widget=ResubmitFileWidget)

        return super().formfield_for_dbfield(db_field, **kwargs)
