# django-visit-on-site-in-new-window

Turn VISIT-ON-SITE button to open in the new window on Django's admin site.

## Install

```shell
pip install django-visit-on-site-in-new-window
```

## Usage

**pro/settings.py**

```python
INSTALLED_APPS = [
    ...
    'django_static_jquery3',
    'django_visit_on_site_in_new_window',
    ...
]
```

**app/admin.py**

```python
from django.contrib import admin
from django_visit_on_site_in_new_window.admin import DjangoVisitOnSiteInNewWindowAdmin
from .models import Book


class BookAdmin(DjangoVisitOnSiteInNewWindowAdmin, admin.ModelAdmin):
    list_display = ["name", "author"]

admin.site.register(Book, BookAdmin)
```

## Releases

### v0.1.0 2020/03/10

- First release.

### v0.1.1 2023/09/15

- Doc update.
