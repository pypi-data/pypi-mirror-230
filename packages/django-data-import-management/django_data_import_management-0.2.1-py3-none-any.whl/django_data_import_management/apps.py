from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class DjangoDataImportManagementConfig(AppConfig):
    name = 'django_data_import_management'
    verbose_name = _("Django Data Import Management")
