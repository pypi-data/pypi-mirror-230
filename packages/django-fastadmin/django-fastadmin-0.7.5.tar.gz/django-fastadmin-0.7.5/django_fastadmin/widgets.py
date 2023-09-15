import json

from fastutils import dictutils
from fastutils import strutils

from django.forms.widgets import Textarea
from django.forms.widgets import TextInput
from django.forms.widgets import SelectMultiple
from django.urls import reverse

from .utils import jquery_plugins
from .utils import get_url

class AceWidget(Textarea):

    def __init__(self, ace_options=None, attrs=None):
        ace_options = ace_options or {}
        new_attrs = {"width": "600px", "height": "400px"}
        new_attrs.update(attrs or {})
        classes = [x.strip() for x in new_attrs.get("class", "").split()]
        classes.append("django-fastadmin-ace-widget")
        new_attrs["class"] = " ".join(classes)
        new_attrs["ace-widget-options"] = json.dumps(ace_options)
        super().__init__(new_attrs)

    class Media:
        css = {
            "screen": [
                "fastadmin/widgets/ace-widget/ace-widget.css",
            ]
        }
        js = jquery_plugins([
            "ace-builds/ace.js",
            "jquery/plugins/jquery.utils.js",
            "fastadmin/widgets/ace-widget/ace-widget.js",
        ])


class TitleToCodeWidget(TextInput):

    def __init__(self, from_field,
            api_title_to_code_url="django_fastadmin.titleToCode",
            api_request_delay=500,
            attrs=None):
        self.from_field = from_field
        self.api_title_to_code_url = api_title_to_code_url
        self.api_request_delay = api_request_delay

        attrs = attrs or {}
        classes = dictutils.touch(attrs, "class", "")
        classes = strutils.html_element_css_append(classes, "django-fastadmin-title-to-code")
        classes = strutils.html_element_css_append(classes, "vTextField")
        attrs["class"] = classes
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        attrs = attrs or {}
        context = super().get_context(name, value, attrs)
        context["widget"]["attrs"]["django-fastadmin-title-to-code-options"] = json.dumps({
            "from": self.from_field,
            "api_title_to_code_url": get_url(self.api_title_to_code_url),
            "api_request_delay": self.api_request_delay,
        })
        return context

    class Media:
        js = jquery_plugins([
            "jquery/plugins/jquery.utils.js",
            "fastadmin/django-admin.utils.js",
            "fastadmin/widgets/title-to-code/title-to-code.js",
        ])


class CategoriedSelectMultiple(SelectMultiple):

    def __init__(self, get_category_url, get_items_url, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.get_category_url = get_category_url
        self.get_items_url = get_items_url

    template_name = 'fastadmin/widgets/categoried-select-multiple/categoried-select-multiple.html'

    class Media:
        css = {
            "all": [
                "fastadmin/widgets/categoried-select-multiple/categoried-select-multiple.css",
            ]
        }
        js = [
            "fastadmin/widgets/categoried-select-multiple/categoried-select-multiple.js"
        ]
