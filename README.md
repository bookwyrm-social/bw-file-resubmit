# bw-file-resubmit

**NOTE: this repository is still being set up and the code is most probably currently broken!**

In a Django project you may have forms using `FileField` or `ImageField`. Everything works great, but
when a ValidationError is raised, or you want to add some other check before finally submitting the form, you have to reselect all files and images again because HTML `<input type="file">` fields cannot be prepopulated with data due to basic browser security concerns.

**bw-file-resubmit** solves this problem by caching the file and adding it again in the background. It works with `FileField`, `ImageField` and `sorl.thumbnail.ImageField`.

**bw-file-resubmit** is a drop-in replacement for [**django-file-resubmit**](https://github.com/un1t/django-file-resubmit), which appears to be abandoned.

## How does it work?

Special widgets can be used to replace `FileField` and `ImageField`. When you submit files, every widget saves its file to the cache. When a `ValidationError` is raised, the widgets restore files from cache so the user doesn't have to upload them again.

## Compatible with sorl-thumbnails

It is compatible with `sorl-thumbnail <https://github.com/jazzband/sorl-thumbnail>`_.

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

# Use as a model mixin

admin.py

```py
from django.contrib import admin
from file_resubmit.admin import AdminResubmitMixin
from .models import Page

class PageAdmin(AdminResubmitMixin, admin.ModelAdmin):
    pass

admin.site.register(Page, PageAdmin)
```

## Use as a form widget

admin.py

```py
from django.forms import ModelForm
from file_resubmit.admin import AdminResubmitImageWidget, AdminResubmitFileWidget
from .models import Page

class PageModelForm(forms.ModelForm)

    class Meta:
        model = MyModel
        widgets = {
            'picture': AdminResubmitImageWidget,
            'file': AdminResubmitFileWidget,
        }

class PageAdmin(admin.ModelAdmin):
    form = PageModelForm

admin.site.register(Page, PageAdmin)
```


# Licensing

`bw-file-resubmit` is free software under terms of the MIT License

**Copyright (C) 2011-2023 Ilya Shalyapin**, ishalyapin@gmail.com
**Copyright (C) 2023- BookWyrm contributors**

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
