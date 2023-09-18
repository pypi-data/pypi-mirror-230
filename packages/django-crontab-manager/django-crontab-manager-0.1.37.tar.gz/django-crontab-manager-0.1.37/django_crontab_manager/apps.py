from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class DjangoCrontabManagerConfig(AppConfig):
    name = 'django_crontab_manager'
    verbose_name = _("Django Crontab Manager")

    def ready(self):
        from django_data_import_management.models import register_django_data_import_workflow
        from .models import ScheduleImportWorkflow

        register_django_data_import_workflow(_("Import Schedules"), ScheduleImportWorkflow)