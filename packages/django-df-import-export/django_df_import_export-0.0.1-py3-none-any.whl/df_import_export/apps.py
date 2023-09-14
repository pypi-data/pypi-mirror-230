from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DFImportExportConfig(AppConfig):
    name = "df_import_export"
    verbose_name = _("DjangoFlow Import Export")
