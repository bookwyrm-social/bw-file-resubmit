"""Admin widgets and mixins"""

from django.db import models
from django.utils.safestring import mark_safe

try:
    from sorl.thumbnail.fields import ImageField
    from sorl.thumbnail.admin.current import AdminImageWidget as BaseWidget
except ImportError:
    # pylint: disable=ungrouped-imports
    from django.forms import ImageField
    from django.contrib.admin.widgets import AdminFileWidget as BaseWidget

from .widgets import ResubmitBaseWidget



class AdminResubmitImageWidget(ResubmitBaseWidget, BaseWidget):
    """Image widget with render override"""
    def render(self, name, value, attrs=None, renderer=None):
        output = super().render(name, value, attrs)
        output += self.output_extra_data(value)
        return mark_safe(output)


class AdminResubmitMixin():
    """Admin mixin"""

    def formfield_for_dbfield(self, db_field, **kwargs):
        """return the relevant formfield"""

        if isinstance(db_field, (ImageField, models.ImageField)):
            return db_field.formfield(widget=AdminResubmitImageWidget)

        if isinstance(db_field, models.FileField):
            return db_field.formfield(widget=ResubmitBaseWidget)

        return super().formfield_for_dbfield(
            db_field, **kwargs
        )
