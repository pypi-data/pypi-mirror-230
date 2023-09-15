# django-fastadmin

django admin extensions.

## Install

```shell
pip install django-fastadmin
```

## Usage

**pro/settings.py**

```
INSTALLED_APPS = [
    ...
    "django_static_jquery3",
    "django_static_ace_builds",
    "django_apiview",
    'django_fastadmin',
    ...
]
```

- Add dependence package names in INSTALLED_APPS.


## Installed Admin Extensions

### Admin extends

- AddAdminViewHelper
- DisableAddPermissionMixin
- DisableChangePermissionMixin
- DisableDeleteActionMixin
- DisableDeletePermissionMixin
- DisableInlineEditingInAddingMixin
- DjangoDynamicMediaAdmin
- DjangoObjectToolbarAdmin
- DjangoSortableAdmin
- DjangoWithExtraContextAdmin
- EditablePasswordField
- ExtraViewsAdmin
- HiddenFieldsAdmin
- HideShowField
- HideShowFieldsOnValueAdmin
- InlineBooleanFieldsAllowOnlyOneCheckedMixin
- InlineEditingHideOriginalMixin
- InlineUniqueChoiceFieldsMixin
- MarkPermissionsMixin
- ResetToRandomPasswordField
- SetTopModelAdmin
- TextFieldAutoHeightMixin
- TextFieldSetRowColumnMixin
- ToggleFieldStateAdmin
- UuidFieldSearchableAdmin
- WithDisplayFieldsMixin

### Widgets

- AceWidget
- TitleToCodeWidget

### Forms

### Filters


## admin.InlineBooleanFieldsAllowOnlyOneCheckedMixin Usage

- `django_static_jquery3` required in INSTALLED_APPS.
- Add this mixin to inline class, and put it before TabularInline.
- Add classes property
    - Add class InlineBooleanFieldsAllowOnlyOneCheckedMixin.special_class_name
    - Add class InlineBooleanFieldsAllowOnlyOneCheckedMixin.field_name_prefix + {field name},
- Example:
    ```
    from django.contrib import admin
    from django_fastadmin.admin import InlineBooleanFieldsAllowOnlyOneCheckedMixin

    from .models import Book
    from .models import Category

    class BookInline(InlineBooleanFieldsAllowOnlyOneCheckedMixin, admin.TabularInline):
        model = Book
        extra = 0
        classes = [
            InlineBooleanFieldsAllowOnlyOneCheckedMixin.special_class_name,
            InlineBooleanFieldsAllowOnlyOneCheckedMixin.field_name_prefix + "is_best_seller",
            ]


    class CategoryAdmin(admin.ModelAdmin):
        inlines = [
            BookInline,
        ]

    admin.site.register(Category, CategoryAdmin)
    ```



## widget.AceWidget Usage

- `django_static_jquery3` and `django_static_ace_builds` required in INSTALLED_APPS.
- Create a model_form, and set the admin's form to the model_form.
- Set the field to use AceWidget in the model_form.
- Example:
```
class BookModelForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = "__all__"
        widgets = {
            "description": AceWidget(ace_options={
                "mode": "ace/mode/yaml",
                "theme": "ace/theme/twilight",
            }),
        }

class BookAdmin(admin.ModelAdmin):
    form = BookModelForm
    list_display = ["title", "published"]

```

## Releases

### v0.1.0

- First release.
- Add UuidFieldSearchableAdmin.
- Add InlineBooleanFieldsAllowOnlyOneCheckedMixin.

### v0.1.1

- Fix jquery.js and jquery.init.js including orders, so that we don't need to change js plugin's source to use django.jQuery.

### v0.2.0

- Add widgets.AceWidget.

### v0.3.0 

- hange the directory structure of static files.
- Add models.SimpleTask. It's an abstract model.
- jQuery and jQuery plugins are moved to django-static-jquery3>=5.0.0.

### v0.3.1

- Rename zh_hans to zh_Hans.
- Depends on django-db-lock>=0.3.1.
- Add django-static-xxx depends.

### v0.3.2

- Add SimpleTaskService.
- Move service functions from model to service.
- Upgrade django_db_lock depends.

### v0.4.0

- Add widgets.TitleToCodeWidget.
- Add models.SimplePublishModel.
- Add many admin mixins.
- Add django-app-requires support.

### v0.5.0

- Add admin.AddAdminViewHelper.
- Add admin.ToggleFieldStateAdmin.
- Add admin.SimplePublishModelAdmin.
- Add admin.SetTopModelAdmin. 

### v0.6.0

- Add admin.DjangoAdminGlobalMedia.
- Add admin.DjangoWithExtraContextAdmin.
- Add admin.DjangoDynamicMediaAdmin.
- Add admin.HiddenFieldsAdmin.
- Add admin.HideShowFieldsOnValueAdmin.
- Add admin.DjangoObjectToolbarAdmin.
- Add admin.DjangoSortableAdmin.
- Add depends.

### v0.6.1

- Upgrade django-db-lock, fix missing requests in setup problem.

### v0.6.2

- Fix DjangoWithExtraContextAdmin problem.

### v0.7.0

- Remove abstract models, so that django_fastadmin can forcus on admin extensions.
- SimpleTask moved to django_simpletask.
- SimplePublishModel and SimplePublishModelAdmin moved to django_simple_publish_model.

### v0.7.1

- Fix missing django-static-ace-builds problem.

### v0.7.2 

- Fix InlineModelAdmin.has_add_permission(...) has obj paramter in Django 3.2 problem.
- Test in Django 3.2.

### v0.7.4

- Rename AddAdminViewHelper to ExtraViewsAdmin.
- ExtraViewsAdmin make define view function easy.
- DjangoObjectToolbarAdmin make define button function easy.
- DjangoSortableAdmin using ExtraViewsAdmin easier way to define move-up and move-down button views.
- We are not care about the version of fastutils, so let the end user to choose.

### v0.7.5

- Doc update.