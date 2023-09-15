# django-readedit-switch-admin

Read item detail first, and click the Edit switch button to turn to edit view.


## Install

```shell
pip install django-readedit-switch-admin
```

## Usage

**pro/settings.py**

```python

INSTALLED_APPS = [
    ...
    'django_readedit_switch_admin',
    ...
]
```

**app/admin.py**

```python
from django.contrib import admin
from .models import Category
from .models import Book

from django_readedit_switch_admin.admin import DjangoReadEditSwitchAdmin


class BookInline(admin.TabularInline):
    model = Book

class CategoryAdmin(DjangoReadEditSwitchAdmin, admin.ModelAdmin):
    list_display = ["pk", "name"]
    list_editable = ["name"]
    inlines = [
        BookInline
    ]

admin.site.register(Category, CategoryAdmin)

```

## Releases

### v0.1.0

- First release.

### v0.1.1

- Fix add/change/delete permission problem in changelist view. Changelist view should obey the real permission.

### v0.1.2

- Don't check is_edit_view in getting add and delete permissions.

### v0.2.0

- App rename to django_readedit_switch_admin.

### v0.3.0

- Fix django_readedit_switch_admin.apps' verbose_name.
- Rename DjangoReadEditSwitchAdminMixin to DjangoReadEditSwitchAdmin. It's NOT good to add mixin suffix.

### v0.4.0

- Rename django_readedit_switch_admin.html to change_form.html, so that it can be override by other applications.

### v0.4.1

- Fix problem for all NONE DjangoReadeditSwitchAdmins.

### v0.4.2

- Fix block.super spell mistake.

### v0.4.3

- Use jquery.js shipped with django, and control js loading order.

### v0.4.4

- Fix edit problem with _changelist_filters.

### v0.4.5

- Fix has_add_permission problem.
- Test in Django 3.2.

### v0.4.6

- Doc update.
