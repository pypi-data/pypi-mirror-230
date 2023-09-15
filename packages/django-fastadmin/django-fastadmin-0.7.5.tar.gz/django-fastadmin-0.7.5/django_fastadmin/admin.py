import uuid
import copy
import time
import json
import urllib
from functools import update_wrapper
from django.http.response import HttpResponse, JsonResponse


from fastutils import listutils
from fastutils import funcutils
from magic_import import import_from_string

from django.db import models
from django import forms
from django.forms import Textarea
from django.template.loader import render_to_string
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render

from django.contrib import admin
from django.contrib.admin.options import BaseModelAdmin
from django.contrib.admin.options import InlineModelAdmin
from django.contrib.admin.options import csrf_protect_m
from django.contrib.admin.options import TO_FIELD_VAR
from django.contrib.admin.options import unquote
from django.contrib import messages

from django_middleware_global_request.middleware import get_request

from .utils import jquery_plugins


class UuidFieldSearchableAdmin(admin.ModelAdmin):
    """Enable search by uuid string with dashes.
    """
    def get_search_results(self, request, queryset, search_term):
        try:
            search_term_new = search_term
            if isinstance(search_term_new, str):
                search_term_new = search_term_new.strip()
            search_term_new = uuid.UUID(search_term_new).hex
        except ValueError:
            search_term_new = search_term
        result = super().get_search_results(request, queryset, search_term_new)
        return result

class InlineBooleanFieldsAllowOnlyOneCheckedMixin(InlineModelAdmin):
    """Admin inline formset has a boolean field, so that there are many checkboxes of that field, make sure that only one checkbox is checked.
    """

    special_class_name = "inline-boolean-fields-allow-only-one-checked-mixin"
    field_name_prefix = special_class_name + "-"

    class Media:
        js = jquery_plugins([
            "jquery/plugins/jquery.utils.js",
            "fastadmin/admins/inline-boolean-fields-allow-only-one-checked-mixin/ibfaoocm.js",
        ])

class InlineUniqueChoiceFieldsMixin(InlineModelAdmin):
    """ @todo
    """
    special_class_name = "with-inline-unique-choice-fields"
    field_name_prefix = special_class_name + "-"

    class Media:
        js = jquery_plugins([
            "jquery/plugins/jquery.utils.js",
            "fastadmin/admins/with-inline-unique-choice-fields.js",
        ])

class DisableInlineEditingInAddingMixin(BaseModelAdmin):
    """Disable inline editing in main object adding step.
    """
    def get_inline_instances(self, request, obj=None):
        if not obj or not obj.pk:
            return []
        else:
            return super().get_inline_instances(request, obj)

class InlineEditingHideOriginalMixin(BaseModelAdmin):
    """Hide original part in inline editing.
    """
    class Media:
        css = {
            "all": [
                "fastadmin/admins/inline-editing-hide-original-mixin/inline-editing-hide-original-mixin.css",
            ]
        }

class DisableDeleteActionMixin(BaseModelAdmin):
    """Disable delete action for all user.
    """
    DELETE_ACTION_ENABLE_FOR_SUPERUSER = False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if request.user and request.user.is_superuser and self.DELETE_ACTION_ENABLE_FOR_SUPERUSER:
            pass
        else:
            if "delete_selected" in actions:
                del actions["delete_selected"]
        return actions

class DisableAddPermissionMixin(BaseModelAdmin):
    ADD_PERMISSION_ENABLE_FOR_SUPERUSER = False

    def has_add_permission(self, request, obj=None):
        """Fix InlineModelAdmin.has_add_permission(...) has obj paramter in Django 3.2 problem.
        """
        if not request.user:
            return False
        if not request.user.is_superuser:
            return False
        if not self.ADD_PERMISSION_ENABLE_FOR_SUPERUSER:
            return False
        return True

class DisableDeletePermissionMixin(BaseModelAdmin):
    DELETE_PERMISSION_ENABLE_FOR_SUPERUSER = False

    def has_delete_permission(self, request, obj=None):
        if not request.user:
            return False
        if not request.user.is_superuser:
            return False
        if not self.DELETE_PERMISSION_ENABLE_FOR_SUPERUSER:
            return False
        return True

class DisableChangePermissionMixin(BaseModelAdmin):
    CHANGE_PERMISSION_ENABLE_FOR_SUPERUSER = False

    def has_change_permission(self, request, obj=None):
        if not request.user:
            return False
        if not request.user.is_superuser:
            return False
        if not self.CHANGE_PERMISSION_ENABLE_FOR_SUPERUSER:
            return False
        return True

class MarkPermissionsMixin(BaseModelAdmin):

    def get_changing_object(self, request, object_id):
        if not object_id:
            return None
        else:
            to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
            obj = self.get_object(request, unquote(object_id), to_field)
            return obj

    @csrf_protect_m
    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        obj = self.get_changing_object(request, object_id)
        extra_context = extra_context or {}
        has_add_permission = self.has_add_permission(request)
        has_view_permssion = self.has_view_permission(request, obj)
        has_change_permission = self.has_change_permission(request, obj)
        has_delete_permission = self.has_delete_permission(request, obj)
        setattr(request, "has_add_permission", has_add_permission)
        setattr(request, "has_view_permssion", has_view_permssion)
        setattr(request, "has_change_permission", has_change_permission)
        setattr(request, "has_delete_permission", has_delete_permission)
        extra_context.update({
            "has_add_permission": has_add_permission,
            "has_view_permssion": has_view_permssion,
            "has_change_permission": has_change_permission,
            "has_delete_permission": has_delete_permission,
        })
        return super().changeform_view(request, object_id, form_url, extra_context)

class TextFieldAutoHeightMixin(BaseModelAdmin):
    class Media:
        js = jquery_plugins([
            "fastadmin/admins/text-field-auto-height-mixin/text-field-auto-height-mixin.js",
        ])

class TextFieldSetRowColumnMixin(BaseModelAdmin):
    TEXT_AREA_ROW = 1
    TEXT_AREA_COLS = 80

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if models.TextField in self.formfield_overrides:
            self.formfield_overrides[models.TextField]["widget"] = Textarea(attrs={'rows': self.TEXT_AREA_ROW, 'cols': self.TEXT_AREA_COLS})

class DisplayField(object):

    template_name = None
    css = {}
    js = []

    def __init__(self, field_name, short_description, help_text=None):
        self.field_name = field_name
        self.short_description = short_description
        self.help_text = help_text

    def __call__(self, obj):
        request = get_request()
        templates = self.get_templates(request, obj)
        context = self.get_context(request, obj)
        return render_to_string(templates, context)

    def get_templates(self, request, obj):
        app_label = obj._meta.app_label
        model_name = obj._meta.model_name
        templates = [
            "admin/{}/{}/{}".format(app_label, model_name, self.template_name),
            "admin/{}/{}".format(app_label, self.template_name),
            "admin/{}".format(self.template_name),
        ]
        return templates

    def get_context(self, request, obj=None):
        add = request.path.endswith("/add/")
        app_label = obj._meta.app_label
        model_name = obj._meta.model_name
        context = {
            "request": request,
            "obj": obj,
            "field_name": self.field_name,
            "short_description": self.short_description,
            "help_text": self.help_text,
            "add": add,
            "has_change_permission": request.has_change_permission,
            "value": getattr(obj, self.field_name),
        }
        return context

class WithDisplayFieldsMixin(MarkPermissionsMixin):

    def get_display_fields_map(self):
        fields_map = {}
        for name in dir(self):
            if name in ["media"]:
                continue
            field = getattr(self, name)
            if isinstance(field, DisplayField):
                fields_map[field.field_name] = name
        return fields_map

    def get_fieldsets(self, request, obj=None):
        fields_map = self.get_display_fields_map()
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets = copy.deepcopy(fieldsets)
        if request.method != 'POST':
            for block in fieldsets:
                fields = listutils.replace(block[1]["fields"], fields_map)
                block[1]["fields"] = fields
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        fields_map = self.get_display_fields_map()
        fields = list(super().get_readonly_fields(request, obj))
        fields = copy.deepcopy(fields)
        for field_old, field_new in fields_map.items():
            if not field_new in fields:
                fields.append(field_new)
        return fields

    @property
    def media(self):
        resource = super().media
        fields_map = self.get_display_fields_map()
        for _, display_field_name in fields_map.items():
            field = getattr(self, display_field_name)
            resource += forms.Media(css=field.css, js=field.js)
        return resource
    
class HideShowField(DisplayField):
    template_name = "hide_show_field.html"
    css = {
        "all": [
            "fastadmin/admins/hide-show-field/hide-show-field.css",
        ]
    }
    js = jquery_plugins([
        "fastadmin/admins/hide-show-field/hide-show-field.js",
    ])

class EditablePasswordField(DisplayField):

    template_name = "fastadmin/admins/editable-password-field/editable-password-field.html"
    css = {
        "all": [
            "fastadmin/admins/editable-password-field/editable-password-field.css",
        ]
    }
    js = jquery_plugins([
        "fastadmin/admins/editable-password-field/editable-password-field.js",
    ])

class ResetToRandomPasswordField(object):

    template_name = "fastadmin/admins/reset-to-random-password-field/reset-to-random-password-field.html"
    css = {
        "all": [
            "fastadmin/admins/reset-to-random-password-field/reset-to-random-password-field.css",
        ]
    }
    js = jquery_plugins([
        "fastadmin/admins/reset-to-random-password-field/reset-to-random-password-field.js",
    ])

    def __init__(self, field_name, get_password_url, short_description, help_text=None, params=None):
        super().__init__(field_name, short_description, help_text)
        self.get_password_url = get_password_url
        self.params = params

    def get_context(self, request, obj=None):
        context = super().get_context(request, obj)
        context.update({
            "get_password_url": reverse(self.get_password_url),
            "params": self.params,
            "params_json": json.dumps(self.params),
        })
        return context

ModelAdminProperties = dir(admin.ModelAdmin)

class ExtraViewsAdmin(admin.ModelAdmin):
    """With this extenstion, you can add an admin view by following simple code:
    ```
    extra_views = [{
        "name": "admin_view_name_suffix",
        "view": "admin_view_function_name_or_function_itself",
        "url": "<path:object_id>/some-action-name/"
    }]  

    def admin_view_function_name_or_function_itself(self, request, object_id):
        pass
    ```                                                                                                                                                                                                                                                                11111111111111111111                
    """

    admin_site_namespace = "admin"

    def get_urls(self):
        urlpatterns = self.get_extra_views()
        urlpatterns += super().get_urls()
        return urlpatterns

    def get_extra_views(self):
        urlpatterns = []

        extra_views_configs = self.get_extra_views_configs()
        for admin_view_config in extra_views_configs:
            urlpatterns.append(self.make_urlpattern(admin_view_config))

        for key in dir(self):
            if key in ModelAdminProperties:
                continue
            if key in [
                    "admin_site_namespace",
                    "get_urls",
                    "get_extra_admin_views",
                    "get_extra_admin_view_configs",
                    "admin_view_wrap",
                    "get_admin_view_name",
                    "get_admin_view_name_full",
                    "make_urlpattern",
                    "get_url_final",
                    ]:
                continue
            value = getattr(self, key, None)
            if value and callable(value) and getattr(value, "extra_view", False):
                view = value
                view_name = getattr(view, "name", key)
                is_object_view = getattr(view, "is_object_view", False)
                url = getattr(view, "url", None)
                if not url:
                    if is_object_view:
                        url = "<path:object_id>/{0}/".format(view_name)
                    else:
                        url = view_name
                urlpatterns.append(self.make_urlpattern({
                    "name": self.get_admin_view_name(view_name),
                    "view": self.admin_view_wrap(view),
                    "url": url,
                }))

        return urlpatterns

    def get_extra_views_configs(self):
        return getattr(self, "extra_views", [])

    def admin_view_response_handler(self, view):
        def wrapper(*args, **kwargs):
            result = view(*args, **kwargs)
            if isinstance(result, HttpResponse):
                return result
            elif result is None:
                request = get_request()
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
            elif isinstance(result, str):
                return HttpResponseRedirect(result)
            else:
                return JsonResponse(result)
        return wrapper

    def admin_view_wrap(self, view):
        def wrapper(*args, **kwargs):
            result = self.admin_site.admin_view(self.admin_view_response_handler(view))(*args, **kwargs)
            return result
        wrapper.model_admin = self
        return update_wrapper(wrapper, view)

    def get_admin_view_name(self, view_name):
        if not isinstance(view_name, str):
            view_name = getattr(view_name, "name", view_name.__name__)
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        return "{app_label}_{model_name}_{view_name}".format(app_label=app_label, model_name=model_name, view_name=view_name)

    def get_admin_view_name_full(self, view_name):
        view_name = self.get_admin_view_name(view_name)
        view_name_full = "{namespace}:{view_name}".format(namespace=self.admin_site_namespace, view_name=view_name)
        return view_name_full

    def make_urlpattern(self, config):
        from django.urls import path

        name = config.get("name", None)
        view = config["view"]
        url = config["url"]

        if isinstance(view, str):
            view = getattr(self, view, None)
            if view is None:
                view = import_from_string(view)
        
        extra_params = {}
        if name:
            extra_params["name"] = name
        return path(url, self.admin_view_wrap(view), **extra_params)

    def get_view_url(self, view, object_id=None):
        view_name_full = self.get_admin_view_name_full(view)
        is_object_view = getattr(view, "is_object_view", False)
        if is_object_view:
            return reverse(view_name_full, kwargs={"object_id": object_id})
        else:
            return reverse(view_name_full)

    def is_extra_view(self, view):
        return getattr(view, "extra_view", False)

class ToggleFieldStateAdmin(ExtraViewsAdmin, admin.ModelAdmin):
    

    def get_toggle_field_state_view_name(self, field_name):
        return "toggle_" + field_name

    def get_extra_admin_view_configs(self):
        configs = super().get_extra_admin_view_configs()
        for field_name, field_config in self.get_toggle_field_state_configs().items():
            configs.append({
                "name": self.get_admin_view_name(self.get_toggle_field_state_view_name(field_name)),
                "view": self.toggle_field_state,
                "url": "<path:object_id>/toggle-field-state/<path:field_name>/",
            })
        return configs

    def toggle_field_state(self, request, object_id, field_name):
        obj = self.get_object(request, object_id)
        if self.has_toggle_field_state_permission(request, obj, field_name):
            method_name = "toggle_{0}_state".format(field_name)
            if hasattr(obj, method_name):
                getattr(obj, method_name)(request)
                obj.save()
            else:
                if getattr(obj, field_name, None):
                    setattr(obj, field_name, False)
                else:
                    setattr(obj, field_name, True)
                obj.save()
            messages.success(request, _("Toggle state success."))
        else:
            messages.error(request, _("You have NO permission to change the state of the instance."))
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    def has_toggle_field_state_permission(self, request, obj, field_name):
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        return request.user.has_perm("{app_label}.change_{model_name}".format(app_label=app_label, model_name=model_name))

    def get_toggle_field_state_configs(self):
        return getattr(self, "toggle_field_state_configs", {})

    def field_state(self, obj, field_name):
        return getattr(obj, field_name, None)

    @staticmethod
    def make_toggle_field_state_button(field_name_config_name):
        def toggle_field_state_button(self, obj):
            field_name = getattr(self, field_name_config_name, field_name_config_name)
            href = reverse("{namespace}:{view_name}".format(
                namespace=self.admin_site_namespace,
                view_name= self.get_admin_view_name(self.get_toggle_field_state_view_name(field_name))),
                args=[obj.pk, field_name],
            )
            button_config = self.get_toggle_field_state_configs()[field_name]
            if self.field_state(obj, field_name):
                icon = button_config.get("toggle_button_icon_state_on", "")
                title = button_config.get("toggle_button_title_turn_off", _("Turn Off"))
            else:
                icon = button_config.get("toggle_button_icon_state_off", "")
                title = button_config.get("toggle_button_title_turn_on", _("Turn On"))
            return {
                "href": href,
                "icon": icon,
                "title": title,
                "help_text": button_config.get("toggle_button_help_text", ""),
            }
        return toggle_field_state_button

class SetTopModelAdmin(ToggleFieldStateAdmin, admin.ModelAdmin):

    is_top_field_name = "is_top"

    toggle_top_setting_button_title_turn_on = _("Set Top")
    toggle_top_setting_button_title_turn_off = _("Cancel Top")
    toggle_top_setting_button_icon_state_on = "fa fa-compress-arrows-alt"
    toggle_top_setting_button_icon_state_off = "fa fa-arrow-up"
    toggle_top_setting_button_help_text = _("Set item to display top or cancel the top setting.")

    def get_toggle_field_state_configs(self):
        configs = super().get_toggle_field_state_configs()
        configs[self.is_top_field_name] = {
            "toggle_button_title_turn_on": self.toggle_top_setting_button_title_turn_on,
            "toggle_button_title_turn_off": self.toggle_top_setting_button_title_turn_off,
            "toggle_button_icon_state_on": self.toggle_top_setting_button_icon_state_on,
            "toggle_button_icon_state_off": self.toggle_top_setting_button_icon_state_off,
            "toggle_button_help_text": self.toggle_top_setting_button_help_text,
        }
        return configs

    toggle_top_setting_button = ToggleFieldStateAdmin.make_toggle_field_state_button("is_top_field_name")

class DjangoAdminGlobalMedia(object):
    
    def __init__(self):
        self.global_media = []
    
    def register(self, media):
        self.global_media.append(media)
    
    def inject(self):
        django_admin_global_media_instance = self
        from django.contrib.admin import ModelAdmin
        ModelAdmin.__django_admin_global_media_old_media = ModelAdmin.media

        @property
        def media(self):
            result_media = self.__django_admin_global_media_old_media
            for media in django_admin_global_media_instance.global_media:
                if callable(media):
                    media = media(self)
                if media:
                    result_media += media
            return result_media

        ModelAdmin.media = media

DjangoAdminGlobalMedia = DjangoAdminGlobalMedia()

class DjangoWithExtraContextAdmin(admin.ModelAdmin):
    
    add_django_with_extra_context_admin_view_name = True
    django_with_extra_context_admin_view_name = "django_with_extra_context_admin_view_name"

    def get_extra_context(self, request, **kwargs):
        return {}

    def get_changeform_view_extra_context(self, request, object_id=None, form_url='', extra_context=None):
        return self.get_extra_context(request, object_id=object_id, form_url=form_url, extra_context=extra_context)
    
    def get_changelist_view_extra_context(self, request, extra_context=None):
        return self.get_extra_context(request, extra_context=extra_context)
    
    def get_delete_view_extra_context(self, request, object_id, extra_context=None):
        return self.get_extra_context(request, object_id=object_id, extra_context=extra_context)

    def get_history_view_extra_context(self, request, object_id, extra_context=None):
        return self.get_extra_context(request, object_id=object_id, extra_context=extra_context)

    def get_add_view_extra_context(self, request, form_url, extra_context=None):
        return self.get_extra_context(request, form_url=form_url, extra_context=extra_context)

    def get_change_view_extra_context(self, request, object_id, form_url='', extra_context=None):
        return self.get_extra_context(request, object_id=object_id, form_url=form_url, extra_context=extra_context)

    @csrf_protect_m
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        if self.add_django_with_extra_context_admin_view_name and not self.django_with_extra_context_admin_view_name in extra_context:
            extra_context[self.django_with_extra_context_admin_view_name] = "changeform_view"
        extra_context.update(self.get_changeform_view_extra_context(request, object_id=object_id, form_url=form_url, extra_context=extra_context))
        return super().changeform_view(request, object_id, form_url, extra_context)

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        if self.add_django_with_extra_context_admin_view_name and not self.django_with_extra_context_admin_view_name in extra_context:
            extra_context[self.django_with_extra_context_admin_view_name] = "changelist_view"
        extra_context.update(self.get_changelist_view_extra_context(request, extra_context=extra_context))
        return super().changelist_view(request, extra_context)

    @csrf_protect_m
    def delete_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or {}
        if self.add_django_with_extra_context_admin_view_name and not self.django_with_extra_context_admin_view_name in extra_context:
            extra_context[self.django_with_extra_context_admin_view_name] = "delete_view"
        extra_context.update(self.get_delete_view_extra_context(request, object_id=object_id, extra_context=extra_context))
        return super().delete_view(request, object_id, extra_context)

    def history_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or {}
        if self.add_django_with_extra_context_admin_view_name and not self.django_with_extra_context_admin_view_name in extra_context:
            extra_context[self.django_with_extra_context_admin_view_name] = "history_view"
        extra_context.update(self.get_history_view_extra_context(request, object_id=object_id, extra_context=extra_context))
        return super().history_view(request, object_id, extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        if self.add_django_with_extra_context_admin_view_name and not self.django_with_extra_context_admin_view_name in extra_context:
            extra_context[self.django_with_extra_context_admin_view_name] = "add_view"
        extra_context.update(self.get_add_view_extra_context(request, form_url=form_url, extra_context=extra_context))
        return super().add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        if self.add_django_with_extra_context_admin_view_name and not self.django_with_extra_context_admin_view_name in extra_context:
            extra_context[self.django_with_extra_context_admin_view_name] = "change_view"
        extra_context.update(self.get_change_view_extra_context(request, object_id=object_id, form_url=form_url, extra_context=extra_context))
        return super().change_view(request, object_id, form_url, extra_context)

class DjangoDynamicMediaAdmin(ExtraViewsAdmin, admin.ModelAdmin):

    @staticmethod
    def get_dynamic_media(model_admin):
        params = {}
        django_dynamic_media_get_js_urls = getattr(model_admin, "django_dynamic_media_get_js_urls", None)
        django_dynamic_media_get_css_urls = getattr(model_admin, "django_dynamic_media_get_css_urls", None)
        if django_dynamic_media_get_js_urls:
            params["js"] = django_dynamic_media_get_js_urls()
        if django_dynamic_media_get_css_urls:
            params["css"] = {"all": django_dynamic_media_get_css_urls()}
        if params:
            return forms.Media(**params)
        else:
            return None

    def django_dynamic_media_get_js_urls(self):
        view_name = self.get_admin_view_name("dynamic_media_js")
        full_view_name = "{namespace}:{view_name}".format(namespace=self.admin_site_namespace, view_name=view_name)
        return [reverse(full_view_name) + "?_=" + str(time.time())]
    
    def django_dynamic_media_get_css_urls(self):
        view_name = self.get_admin_view_name("dynamic_media_css")
        full_view_name = "{namespace}:{view_name}".format(namespace=self.admin_site_namespace, view_name=view_name)
        return [reverse(full_view_name) + "?_=" + str(time.time())]

    def get_extra_admin_view_configs(self):
        configs = super().get_extra_admin_view_configs()
        configs += [{
            "name": self.get_admin_view_name("dynamic_media_css"),
            "view": self.django_dynamic_media_css_view,
            "url": "dynamic-media-css/",
        },{
            "name": self.get_admin_view_name("dynamic_media_js"),
            "view": self.django_dynamic_media_js_view,
            "url": "dynamic-media-js/",
        }]
        return configs

    def django_dynamic_media_css_view(self, request, **kwargs):
        return render(request, "fastadmin/admins/django-dynamic-media-admin/css.template.html", {
            "css_segments": self.get_css_segments(request, **kwargs),
        }, content_type="text/css; charset=utf-8")

    def django_dynamic_media_js_view(self, request, **kwargs):
        return render(request, "fastadmin/admins/django-dynamic-media-admin/js.template.html", {
            "js_segments": self.get_js_tuples(request, **kwargs),
        }, content_type="application/x-javascript")

    def get_js_tuples(self, request, **kwargs):
        result = []
        segments = self.get_js_segments(request, **kwargs)
        for segment in segments:
            if not isinstance(segment, (tuple, list)):
                segment = (";(function(){", segment, "})();")
            result.append(segment)
        return result
    
    def make_jquery_tuple(self, segment):
        return (";(function($){", segment, "})(jQuery);")

    def get_css_segments(self, request, **kwargs):
        return []
    
    def get_js_segments(self, request, **kwargs):
        return []

DjangoAdminGlobalMedia.register(DjangoDynamicMediaAdmin.get_dynamic_media)

class HiddenFieldsAdmin(DjangoDynamicMediaAdmin):
    """
    extra admin settings:
        hidden_fields = [...]
    """

    def get_hidden_fields(self):
        fields = getattr(self, "hidden_fields", [])
        return fields

    def make_hidden_field_css(self, field_name):
        return """.field-{}{{display:none;}}""".format(field_name)

    def get_css_segments(self, request, **kwargs):
        css_segments = [] + super().get_css_segments(request, **kwargs)
        for field in self.get_hidden_fields():
            css = self.make_hidden_field_css(field)
            css_segments.append(css)
        return css_segments

class HideShowFieldsOnValueAdmin(HiddenFieldsAdmin):
    """
    extra admin settings:
        hide_show_mapping = {
            "target_field": {
                "": ["show_field1", "show_field2"],
                "value1": ["show_field1", "show_field3"],
            }
        }
    """

    def get_hide_show_mapping(self):
        return getattr(self, "hide_show_mapping", {})

    def get_hidden_fields(self):
        fields = super().get_hidden_fields()
        for field_name, field_settings in self.get_hide_show_mapping().items():
            for value, show_field_names in field_settings.items():
                fields += show_field_names
        fields = list(set(fields))
        fields.sort()
        return fields

    def make_hide_show_css(self, target_field_name, value, show_field_names):
        lines = ""
        for show_field_name in show_field_names:
            lines += ".hide-show-fields-on-value-admin-{}-{} .field-{}{{display:block;}}\n""".format(target_field_name, value, show_field_name)
        return lines

    def make_hide_show_js(self, target_field_name):
        return self.make_jquery_tuple("""
        $(document).ready(function(){{
            $("#id_{field_name}").set_form_class_on_field_value_changes("hide-show-fields-on-value-admin-");
        }});
        """.format(field_name=target_field_name))
    
    def django_dynamic_media_get_js_urls(self):
        return jquery_plugins([
            "fastadmin/admins/hide-show-fields-on-value-admin/jquery.set-form-class-on-field-value-changes.js",
        ] + super().django_dynamic_media_get_js_urls())

    def get_css_segments(self, request, **kwargs):
        css_segments = super().get_css_segments(request, **kwargs)
        for field_name, field_settings in self.get_hide_show_mapping().items():
            for value, show_field_names in field_settings.items():
                css = self.make_hide_show_css(field_name, value, show_field_names)
                css_segments.append(css)
        return css_segments

    def get_js_segments(self, request, **kwargs):
        js_segments = super().get_js_segments(request, **kwargs)
        for field_name in self.get_hide_show_mapping().keys():
            js = self.make_hide_show_js(field_name)
            js_segments.append(js)
        return js_segments

class Button(object):

    def __init__(self, href, title, target="", klass="", icon="", help_text=""):
        self.href = href
        self.title = title
        self.target = target
        self.klass = klass
        self.icon = icon
        self.help_text = help_text

    @classmethod
    def from_dict(cls, data):
        item = cls(**data)
        return item

class DjangoObjectToolbarAdmin(ExtraViewsAdmin, admin.ModelAdmin):

    @csrf_protect_m
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        django_object_toolbar_changeform_buttons_setting_name = "django_object_toolbar_buttons"
        if hasattr(self, "django_object_toolbar_changeform_buttons"):
            django_object_toolbar_changeform_buttons_setting_name = "django_object_toolbar_changeform_buttons"
        extra_context = extra_context or {}
        if object_id:
            to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
            obj = self.get_object(request, unquote(object_id), to_field)
            extra_context["django_object_toolbar_changeform_buttons"] = self.get_django_object_toolbar_buttons(django_object_toolbar_changeform_buttons_setting_name, obj)
        return super().changeform_view(request, object_id, form_url, extra_context)

    def django_object_toolbar(self, obj):
        return self.get_django_object_toolbar("django_object_toolbar_buttons", obj)
    django_object_toolbar.short_description = _("Django Object Toolbar")

    def get_django_object_toolbar(self, buttons_property, obj):
        buttons = self.get_django_object_toolbar_buttons(buttons_property, obj)
        return render_to_string("fastadmin/admins/django-object-toolbar-admin/object-toolbar.html", {
            "buttons": buttons,
        })

    def get_django_object_toolbar_buttons(self, buttons_property, obj):
        buttons = []
        object_toolbar_buttons = getattr(self, buttons_property, [])
        for button in object_toolbar_buttons:
            buttons.append(self.make_django_object_toolbar_button(button, obj))
        return buttons

    def make_django_object_toolbar_button(self, button, obj):
        if isinstance(button, Button):
            return button
        if isinstance(button, str):
            button_function = getattr(self, button, None)
            if self.is_extra_view(button_function):
                button = self.get_view_url(button_function, obj.pk)
            else:
                if button_function:
                    button = button_function(obj)
                else:
                    button_function = getattr(obj, button, None)
                    if button_function:
                        button = button_function()
                    else:
                        raise RuntimeError("make_django_object_toolbar_button failed: {0}".format(button))
        if isinstance(button, dict):
            return Button.from_dict(button)
        if isinstance(button, str):
            href = button
            title = getattr(button_function, "title", href)
            target = getattr(button_function, "target", "")
            klass = getattr(button_function, "klass", "")
            icon = getattr(button_function, "icon", "")
            help_text = getattr(button_function, "help_text", "")
            return Button(href, title, target, klass, icon, help_text)
        if isinstance(button, Button):
            return button
        else:
            raise RuntimeError("make_django_object_toolbar_button failed: {0}".format(button))

    class Media:
        css = {
            "all": [
                "fontawesome/css/all.min.css",
            ]
        }

class DjangoSortableAdmin(DjangoObjectToolbarAdmin, ExtraViewsAdmin, admin.ModelAdmin):

    django_sort_field = "display_order"
    django_sort_delta = 100
    django_sort_start = 10000

    def django_sortable_toolbar(self, obj):
        return self.get_django_object_toolbar("django_sortable_toolbar_buttons", obj)
    django_sortable_toolbar.short_description = _("Django Sortable Toolbar")

    django_sortable_toolbar_buttons = [
        "move_up",
        "move_down",
    ]

    def reset_order(self):
        objs = self.model.objects.all()
        index = self.django_sort_start
        for obj in objs:
            setattr(obj, self.django_sort_field, index)
            index += self.django_sort_delta
        return self.model.objects.bulk_update(objs, [self.django_sort_field])

    def move_up(self, request, object_id):
        object_id = int(object_id)
        obj = self.get_object(request, object_id)
        values = self.get_queryset(request).values_list("id", self.django_sort_field)
        prev_value = None
        for index, value in enumerate(values):
            if obj.pk == value[0]:
                if index == 0:
                    prev_id = None
                    prev_value = None
                else:
                    prev_id = values[index-1][0]
                    prev_value = values[index-1][1]
        if prev_id is None:
            messages.error(request, _("This item is already the first."))
        else:
            obj_value = getattr(obj, self.django_sort_field)
            if prev_value != obj_value:
                prev = self.model.objects.get(pk=prev_id)
                setattr(obj, self.django_sort_field, prev_value)
                setattr(prev, self.django_sort_field, obj_value)
                self.model.objects.bulk_update([obj, prev], [self.django_sort_field])
            else:
                self.reset_order()
                obj = self.model.objects.get(pk=object_id)
                prev = self.model.objects.get(pk=prev_id)
                obj_value = getattr(obj, self.django_sort_field)
                prev_value = getattr(prev, self.django_sort_field)
                setattr(obj, self.django_sort_field, prev_value)
                setattr(prev, self.django_sort_field, obj_value)
                self.model.objects.bulk_update([obj, prev], [self.django_sort_field])
            messages.success(request, _("Item move up done!"))
    move_up.extra_view = True
    move_up.is_object_view = True
    move_up.name = "move-up"
    move_up.title = _("Up")
    move_up.icon = "fa fa-arrow-up"

    def move_down(self, request, object_id):
        object_id = int(object_id)
        obj = self.get_object(request, object_id)
        values = self.get_queryset(request).values_list("id", self.django_sort_field)
        next_value = None
        for index, value in enumerate(values):
            if obj.pk == value[0]:
                if index == len(values) - 1:
                    next_id = None
                    next_value = None
                else:
                    next_id = values[index+1][0]
                    next_value = values[index+1][1]
        if next_id is None:
            messages.error(request, _("This item is already the last."))
        else:
            obj_value = getattr(obj, self.django_sort_field)
            if next_value != obj_value:
                next = self.model.objects.get(pk=next_id)
                setattr(obj, self.django_sort_field, next_value)
                setattr(next, self.django_sort_field, obj_value)
                self.model.objects.bulk_update([obj, next], [self.django_sort_field])
            else:
                self.reset_order()
                obj = self.model.objects.get(pk=object_id)
                next = self.model.objects.get(pk=next_id)
                obj_value = getattr(obj, self.django_sort_field)
                next_value = getattr(next, self.django_sort_field)
                setattr(obj, self.django_sort_field, next_value)
                setattr(next, self.django_sort_field, obj_value)
                self.model.objects.bulk_update([obj, next], [self.django_sort_field])
            messages.success(request, _("Item move down done!"))
    move_down.extra_view = True
    move_down.is_object_view = True
    move_down.name = "move-down"
    move_down.title = _("Down")
    move_down.icon = "fa fa-arrow-down"

class AddAdminViewHelper(ExtraViewsAdmin):
    """Renamed, keep it for old apps.
    """
    pass
