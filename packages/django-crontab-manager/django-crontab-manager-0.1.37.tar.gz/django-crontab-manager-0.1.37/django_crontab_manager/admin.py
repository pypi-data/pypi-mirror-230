
from fastutils import strutils

from django.contrib import admin
from django.utils.translation import ugettext as _
from django.forms import ModelForm

from django_fastadmin.widgets import AceWidget
from django_simple_export_admin.admin import DjangoSimpleExportAdmin

from .models import Server
from .models import Schedule
from .models import Result

from .actions import redo_success_determination
from .actions import recompute_schedule_code

class ServerAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "uid", "enable", "last_updated_time", "alive"]
    list_filter = ["enable"]
    search_fields = ["name", "description", "uid"]
    readonly_fields = ["last_updated_time"]

class ScheduleForm(ModelForm):
    class Meta:
        model = Schedule
        fields = "__all__"
        widgets = {
            "script": AceWidget(ace_options={
                "mode": "ace/mode/sh",
                "theme": "ace/theme/twilight",
            }),
            "success_determination_config_data": AceWidget(ace_options={
                "mode": "ace/mode/yaml",
                "theme": "ace/theme/twilight",
            }),
        }

class ScheduleAdmin(DjangoSimpleExportAdmin, admin.ModelAdmin):
    form = ScheduleForm
    list_filter = ["server", "enable"]
    list_display = ["title", "server", "uid", "schedule", "enable"]
    search_fields = ["title", "description", "uid", "schedule", "user", "script", "code"]
    readonly_fields = ["uid", "code"]

    actions = [
        recompute_schedule_code,
    ]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related("server")
        return queryset

    django_simple_export_admin_exports = {
        "filtered-books": {
            "label": _("Export Schedules"),
            "icon": "fas fa-clock",
            "filename": "schedules.xlsx",
            "fields": [
                {"field": "forloop.counter1", "label": _("Index")},
                {"field": "server__name", "label": _("Server Name")},
                {"field": "server__uid", "label": _("Server Uid")},
                {"field": "uid", "render": str, "label": _("Uid")},
                {"field": "title"},
                {"field": "description"},
                {"field": "schedule"},
                {"field": "user"},
                {"field": "script"},
                {"field": "enable"},
                {"field": "get_success_determination_rule_code", "label": _("Success Determination Rule Code")},
                {"field": "success_determination_rule"},
                {"field": "success_determination_config_data"},
            ],
            "export-filtered": True,
            "permissions": ["django_crontab_manager.export_filtered_schedules"],
        }
    }

class ResultAdmin(admin.ModelAdmin):
    list_display = ["id", "schedule", "run_time", "success", "code"]
    list_filter = ["schedule", "run_time", "success", "code"]
    readonly_fields = ["schedule", "run_time", "success", "code"]
    actions = [
        redo_success_determination,
    ]

    def stdout_display(self, obj):
        return obj.stdout and strutils.text_display_shorten(obj.stdout, 20) or "-"
    stdout_display.short_description = _("Stdout")

    def stderr_display(self, obj):
        return obj.stderr and strutils.text_display_shorten(obj.stderr, 20) or "-"
    stderr_display.short_description = _("Stderr")

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related("schedule")
        return queryset


admin.site.register(Server, ServerAdmin)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Result, ResultAdmin)
