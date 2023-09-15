from django.urls import path
from . import settings
from . import views

urlpatterns = [
]

if settings.ENABLE_WIDGET_API_TITLE_TO_CODE:
    urlpatterns += [
        path('titleToCode', views.titleToCode, name="django_fastadmin.titleToCode"),
    ]
