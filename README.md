# bw-file-resubmit

**bw-file-resubmit** is a drop-in replacement for [**django-file-resubmit**](https://github.com/un1t/django-file-resubmit), maintained by the BookWyrm project.

In a Django project you may have forms using `FileField` or `ImageField`. Everything works great, but
when a `ValidationError` is raised, or you want to add some other check before finally submitting the form, you have to reselect all files and images again. This is because HTML `<input type="file">` fields cannot be prepopulated with data due to basic browser security.

**bw-file-resubmit** solves this problem by caching the file and adding it again in the background. It works with `FileField`, `ImageField` and `sorl.thumbnail.ImageField` (see [sorl-thumbnail](https://github.com/jazzband/sorl-thumbnail)).

## How does it work?

Special widgets can be used to replace `FileField` and `ImageField`. When you submit files, every widget saves its file to the cache. When a `ValidationError` is raised, the widgets restore files from cache so the user doesn't have to upload them again.

* `ResubmitFileWidget` can be used in place of `ClearableFileInput`
* `ResubmitImageWidget` can be used in place of `ClearableFileInput`
* `AdminResubmitImageWidget` can be used in place of `AdminFileWidget` (Django) or `AdminImageWidget` (sorl-thumbnail)
* `AdminResubmitMixin` will apply the appropriate widget for all `FileField`s and `ImageField`s

## Installation

```sh
pip install bw-file-resubmit
```

## Configuration

Add `"file_resubmit"` to `INSTALLED_APPS`:

```py
INSTALLED_APPS = {
    ...
    'file_resubmit',
    ...
}
```

Setup cache in settings.py:

```py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    "file_resubmit": {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        "LOCATION": '/tmp/file_resubmit/'
    },
}
```

## Examples

models.py

```py
from django.db import models
from django.db.models import ImageField
# or if you use sorl-thumbnail:
from sorl.thumbnail.fields import ImageField

class Page(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    image =  ImageField(upload_to='whatever1')
```

### Form widgets

#### Ordinary form

forms.py

```py
from django.forms import ModelForm
from file_resubmit.widgets import ResubmitImageWidget, ResubmitFileWidget
from .models import Page

class PageModelForm(forms.ModelForm)

    class Meta:
        model = MyModel
        widgets = {
            'picture': ResubmitImageWidget,
            'file': ResubmitFileWidget,
        }

class Book(forms.Form):
    form = PageModelForm

```

#### Admin form

admin.py

**NOTE:** `admin.AdminResubmitFileWidget` has been dropped from `bw-file-resubmit`. If you need to update a legacy `django-file-resubmit` project, use `widgets.ResubmitFileWidget` instead.

```py
from django.forms import ModelForm
from file_resubmit.admin import AdminResubmitImageWidget,
from file_resubmit.widgets import ResubmitFileWidget
from .models import Page

class PageModelForm(forms.ModelForm)

    class Meta:
        model = MyModel
        widgets = {
            'picture': AdminResubmitImageWidget,
            'file': ResubmitFileWidget,
        }

class PageAdmin(admin.ModelAdmin):
    form = PageModelForm

admin.site.register(Page, PageAdmin)
```

### Use as a model mixin in admin

admin.py

```py
from django.contrib import admin
from file_resubmit.admin import AdminResubmitMixin
from .models import Page

class PageAdmin(AdminResubmitMixin, admin.ModelAdmin):
    pass

admin.site.register(Page, PageAdmin)
```

# Licensing

`bw-file-resubmit` is free software under terms of the MIT License
