# django-tabbed-changeform-admin

Group fieldsets or inlinegroups into tabs for django admin's changeform.

## Install

```shell
pip install django-tabbed-changeform-admin
```

## Usgae

**pro/settings.py**

**Note:**

- We used jquery and jquery-ui's static files, so we MUST add django_static_jquery_ui in INSTALLED_APPS.
- We override admin/change_form.html, so we MUST add django_tabbed_changeform_admin in INSTALLED_APPS.

```python
INSTALLED_APPS = [
    ....
    'django_static_jquery_ui',
    'django_tabbed_changeform_admin',
    ...
]
```

**app/admin.py**

**Note:**

- Create ModelAdmin based on DjangoTabbedChangeformAdmin.
- Add *a sepcial class name* to every fieldset or inline group.
- Add `tabs` property to admin. It's a list of (Tab-Name, Content-Class-Names) pair.
- You can get `tabs` dynamically by overriding method `get_tabs(self, request, object_id, form_url, extra_context)`.

```python
from django.contrib import admin
from django_tabbed_changeform_admin.admin import DjangoTabbedChangeformAdmin
from .models import Book
from .models import Character


class CharacterInline(admin.TabularInline):
    model = Character
    extra = 0
    classes = ["tab-character-inline"]

class BookAdmin(DjangoTabbedChangeformAdmin, admin.ModelAdmin):
    save_on_top = True
    list_display = ["name", "published_time", "publisher"]
    fieldsets = [
        (None, {
            "fields": ["name"],
            "classes": ["tab-basic"],
        }),
        ("Publish Information", {
            "fields": ["published_time", "publisher"],
            "classes": ["tab-publish-info"],
        })
    ]
    inlines = [
        CharacterInline,
    ]

    tabs = [
        ("Basic Information", ["tab-basic", "tab-publish-info"]),
        ("Characters", ["tab-character-inline"]),
    ]

admin.site.register(Book, BookAdmin)
```

## Releases




### v0.1.0 2020/03/17

- First releases.

### v0.1.1 2020/03/18

- Set property tabs' default value to empty list. `tabs = []`.
- Use `django_tabbed_changeform_admin_tabs` for the context variable, so it will NOT conflict with other applications.

### v0.1.2 2020/03/18

- Fix template problem while checking context variable `django_tabbed_changeform_admin_tabs` exists or not.

### v0.1.3 2020/03/21

- Do deep copy in `get_tabs`, so that it will NOT chaos the original `tabs` setting.

### v0.1.4 2020/09/23

- Fix django_static_jquery3 upgrade problem.
- Add app_requires.
- Add LICENSE file.

### v0.1.5 2020/09/23

- Remove django-static-jquery3 depends, using django vendor jquery.js instead.
    - Tips: put your js between "admin/js/vendor/jquery/jquery.js" and "admin/js/jquery.init.js".

### v0.1.6 2020/09/23

- doc fix.

### v0.1.7 2023/09/15

- Doc update.
