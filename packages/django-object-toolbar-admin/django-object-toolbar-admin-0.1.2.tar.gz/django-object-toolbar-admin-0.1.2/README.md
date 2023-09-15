# django-object-tools-admin

Add toolbar in every item line in django's changelist view, and on top of django's changeform view.

## Install

```
pip install django-object-toolbar-admin
```

## Usage

**pro/settings.py**

```
INSTALLED_APPS = [
    ...
    'django_static_fontawesome',
    'django_object_toolbar_admin',
    ...
]
```

- Add django_static_fontawesome and django_object_toolbar_admin applications in INSTALLED_APPS.

**app/admin.py**

```
from django.contrib import admin
from django_object_toolbar_admin.admin import DjangoObjectToolbarAdmin
from .models import Category

class CategoryAdmin(DjangoObjectToolbarAdmin, admin.ModelAdmin):
    list_display = ["name", "django_object_toolbar", "my_toolbar"]

    django_object_toolbar_changeform_buttons = [
        "print",
        "export",
        "bye",
    ]
    # define default toolbar
    django_object_toolbar_buttons = [
        "print",
        "export",
        'bye',
    ]

    def print(self, obj):
        return "/print"
    print.icon = "fas fa-print"
    print.title = "Print"
    print.help_text = "Print the object information..."
    
    def export(self, obj):
        return "/export"
    export.icon = "fas fa-save"
    export.title = "Export"

    # define my toolbar
    def my_toolbar(self, obj):
        return self.get_django_object_toolbar("my_toolbar_buttons", obj)
    my_toolbar.short_description = "My Toolbar"

    my_toolbar_buttons = [
        "delete",
        "say_hi",
    ]

    def delete(self, obj):
        return "/delete"
    delete.icon = "fas fa-trash"
    delete.title = "Delete"

    def say_hi(self, obj):
        return "javascript:alert('hi {}');".format(obj.pk)
    say_hi.icon = "fas fa-music"
    say_hi.title = "Say Hi!"

admin.site.register(Category, CategoryAdmin)
```

- Buttons in `django_object_toolbar_changeform_buttons` will display on top of changeform view.
- Buttons in `django_object_toolbar_buttons` or `my_toolbar_buttons` will display in every line in changelist view. You need to put `django_object_toolbar` or `my_toolbar` in `list_display`.
- A button can be a method of admin or a method of model instance.
- A button method returns the link of the button.
- A button method tasks extra configs:
    - button.title
    - button.icon
    - button.help_text
    - button.target
    - button.klass

## Releases

### v0.1.0

- First release.

### v0.1.1

- Fix Button.from_dict calling problem.
- Add i18n.
- Add app_requires.

### v0.1.2

- Doc update.
