from django.apps import AppConfig


class DjangoFastadminConfig(AppConfig):
    name = 'django_fastadmin'

    def ready(self):
        self.django_admin_global_media_inject()

    def django_admin_global_media_inject(self):
        from .admin import DjangoAdminGlobalMedia
        DjangoAdminGlobalMedia.inject()
