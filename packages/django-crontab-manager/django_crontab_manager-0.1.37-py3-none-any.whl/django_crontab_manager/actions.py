
from django.db.models import query
from django_crontab_manager.settings import SECRET_KEY
from django.utils.translation import ugettext_lazy as _

from .services import update_schedules_code
from .services import update_results_success_determination

def redo_success_determination(modeladmin, request, queryset):
    changed_items = update_results_success_determination(queryset.all())
    msg = _("{count} result items' success value changes").format(count=len(changed_items))
    modeladmin.message_user(request, msg)
redo_success_determination.short_description = _("Redo success determinaion on selected items")


def recompute_schedule_code(modeladmin, request, queryset):
    changed_items = update_schedules_code(queryset.al())
    msg = _("{count} schedule items's code value changed.").format(count=len(changed_items))
    modeladmin.message_user(request, msg)
recompute_schedule_code.short_description = _("Re-compute code value on selected items")
