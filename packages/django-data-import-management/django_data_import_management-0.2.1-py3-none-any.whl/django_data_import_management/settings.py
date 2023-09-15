
from django.conf import settings

DJANGO_DATA_IMPORT_MANAGEMENT_DATA_FILE_UPLOAD_TO = getattr(settings, "DJANGO_DATA_IMPORT_MANAGEMENT_DATA_FILE_UPLOAD_TO", "django-data-import/")


DJANGO_DATA_IMPORT_MANAGEMENT_SECRET_KEY = getattr(settings, "DJANGO_DATA_IMPORT_MANAGEMENT_SECRET_KEY", settings.SECRET_KEY)
SAFE_FIELD_PASSWORDS = {
    "django_data_import_management.DjangoDataImportCase.title": DJANGO_DATA_IMPORT_MANAGEMENT_SECRET_KEY,
    "django_data_import_management.DjangoDataImportCase.import_workflow": DJANGO_DATA_IMPORT_MANAGEMENT_SECRET_KEY,
    "django_data_import_management.DjangoDataImportCase.parse_error": DJANGO_DATA_IMPORT_MANAGEMENT_SECRET_KEY,
    "django_data_import_management.DjangoDataImportCase.import_error": DJANGO_DATA_IMPORT_MANAGEMENT_SECRET_KEY,
    "django_data_import_management.DjangoDataImportItem.info": DJANGO_DATA_IMPORT_MANAGEMENT_SECRET_KEY,
    "django_data_import_management.DjangoDataImportItem.json_data": DJANGO_DATA_IMPORT_MANAGEMENT_SECRET_KEY,
    "django_data_import_management.DjangoDataImportItem.import_error": DJANGO_DATA_IMPORT_MANAGEMENT_SECRET_KEY,
}
SAFE_FIELD_PASSWORDS.update(getattr(settings, "SAFE_FIELD_PASSWORDS", {}))
