from os import stat_result
import re
from typing import Tuple
import uuid
import json
import logging

import yaml
from fastutils import hashutils
from fastutils import strutils
from fastutils import dictutils
from fastutils import typingutils
from fastutils import fsutils

from xlsxhelper import load_data_from_workbook

from django.db import models
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save

from django_safe_fields.fields import SafeTextField
from django_safe_fields.fields import SafeCharField
from django_data_import_management.models import DjangoDataImportWorkflow
from django_data_import_management.models import DjangoSimpleExportedDataImportWorkflow
from django_data_import_management.models import ParsedItem


from . import settings as app_settings

DJANGO_CRONTAB_MANAGER_OFFLINE_SECONDS = getattr(settings, "DJANGO_CRONTAB_MANAGER_OFFLINE_SECONDS", 60*5)
DJANGO_CRONTAB_MANAGER_COPY_IMPORTED_DATAFILE = getattr(settings, "DJANGO_CRONTAB_MANAGER_COPY_IMPORTED_DATAFILE", False)

logger = logging.getLogger(__name__)

def uuidstr():
    return str(uuid.uuid4())

class Server(models.Model):
    name = models.CharField(max_length=64, verbose_name=_("Name"))
    uid = models.CharField(max_length=128, default=uuidstr, unique=True, verbose_name=_("UUID"))
    aclkey = SafeCharField(max_length=128, default=uuidstr, password=app_settings.DJANGO_SAFE_FIELD_PASSWORDS["django_crontab_manager.Server.aclkey"], verbose_name=_("Acl Key"))
    description = models.TextField(null=True, blank=True, verbose_name=_("Description"))
    add_time = models.DateTimeField(auto_now_add=True, verbose_name=_("Add Time"))
    modify_time = models.DateTimeField(auto_now=True, verbose_name=_("Modify Time"))
    last_updated_time = models.DateTimeField(null=True, blank=True, verbose_name=_("Last Updated Time"), help_text=_("It's the latest time that the agent installed on that server got schedule settings."))
    enable = models.BooleanField(default=True, verbose_name=_("Enable"))
    variables_data = SafeTextField(null=True, blank=True, password=app_settings.DJANGO_SAFE_FIELD_PASSWORDS["django_crontab_manager.Server.variables_data"], verbose_name=_("Variables"), help_text=_("Set variables in yml format."))

    class Meta:
        verbose_name = _("Server")
        verbose_name_plural = _("Servers")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = uuid.uuid4()
        return super().save(*args, **kwargs)

    def alive(self):
        if not self.last_updated_time:
            return None
        delta = timezone.now() - self.last_updated_time
        seconds = delta.total_seconds()
        if seconds <= DJANGO_CRONTAB_MANAGER_OFFLINE_SECONDS:
            return True
        else:
            return False
    alive.short_description = _("Alive")
    alive.boolean = True

    def get_variables(self):
        if not self.variables_data:
            return {}
        try:
            return yaml.safe_load(self.variables_data)
        except Exception:
            return {}
    
    def set_variables(self, value):
        self.variables_data = yaml.safe_dump(value)

    variables = property(get_variables, set_variables)


def zero_exit_code_means_success(schedule, result):
    if result.code is None:
        return None
    elif result.code == 0:
        return True
    else:
        return False

def stdout_icontains(schedule, result):
    keyword = schedule.success_determination_config.get("keyword", None)
    if keyword is None:
        return None
    return keyword.lower() in result.stdout.lower()

def stdout_not_icontains(schedule, result):
    keyword = schedule.success_determination_config.get("keyword", None)
    if keyword is None:
        return None
    return not keyword.lower() in result.stdout.lower()

def stdout_regex_match(schedule, result):
    pattern = schedule.success_determination_config.get("pattern", None)
    if pattern is None:
        return None
    if re.findall(pattern, result.stdout):
        return True
    else:
        return False

class Schedule(models.Model):
    ZERO_EXIT_CODE_MEANS_SUCCESS = 0
    STDOUT_ICONTAINS = 10
    STDOUT_NOT_ICONTAINS = 20
    STDOUT_REGEX_MATCH = 30

    SUCCESS_RULES = [
        (ZERO_EXIT_CODE_MEANS_SUCCESS, _("An 0 exit code is considered successful")),
        (STDOUT_ICONTAINS, _("Stdout contains given keyword is considered successful")),
        (STDOUT_NOT_ICONTAINS, _("Stdout NOT contains given keyword is considered successful")),
        (STDOUT_REGEX_MATCH, _("Stdout matchs the regex pattern is considered successful"))
    ]
    SUCCESS_RULE_FUNCTIONS = {
        ZERO_EXIT_CODE_MEANS_SUCCESS: zero_exit_code_means_success,
        STDOUT_ICONTAINS: stdout_icontains,
        STDOUT_NOT_ICONTAINS: stdout_not_icontains,
        STDOUT_REGEX_MATCH: stdout_regex_match,
    }

    schedule_help_text = _("""Linux crontab schedule settings, e.g. * * * * *""")
    code_help_text = _("MD5 code of the schedule settings. It will be auto computed.")

    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name="schedules", verbose_name=_("Server"))
    uid = models.UUIDField(null=True, blank=True, default=uuid.uuid4, verbose_name=_("UUID"))
    title = models.CharField(max_length=128, verbose_name=_("Title"), help_text=_("Describe the scheduled task, so that we know what it is."))
    description = models.TextField(null=True, blank=True, verbose_name=_("Description"))
    schedule = models.CharField(max_length=256, default="* * * * *", verbose_name=_("Schedule Settings"), help_text=schedule_help_text)
    user = models.CharField(max_length=64, default="root", verbose_name=_("Running User"))
    script = SafeTextField(null=True, blank=True, password=app_settings.DJANGO_SAFE_FIELD_PASSWORDS["django_crontab_manager.Schedule.script"], verbose_name=_("Shell Script"))
    enable = models.BooleanField(default=True, verbose_name=_("Enable"))
    code = models.CharField(max_length=32, null=True, blank=True, verbose_name=_("Setting Code"), help_text=code_help_text)

    add_time = models.DateTimeField(auto_now_add=True, verbose_name=_("Add Time"))
    modify_time = models.DateTimeField(auto_now=True, verbose_name=_("Modify Time"))

    success_determination_rule = models.IntegerField(choices=SUCCESS_RULES, default=ZERO_EXIT_CODE_MEANS_SUCCESS, verbose_name=_("Success Determination Rule"))
    success_determination_config_data = SafeTextField(null=True, blank=True, password=app_settings.DJANGO_SAFE_FIELD_PASSWORDS["django_crontab_manager.Schedule.success_determination_config_data"], verbose_name=_("Success Determination Rule Settings"))

    class Meta:
        verbose_name = _("Schedule")
        verbose_name_plural = _("Schedules")
        permissions = [
            ("export_filtered_schedules", _("Export Filtered Schedules"))
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = uuid.uuid4()
        self.script = self.script and self.script.replace("\r\n", "\n") or ""
        self.code = self.get_code()
        return super().save(*args, **kwargs)

    def get_success_determination_rule_code(self):
        return self.success_determination_rule

    def get_script(self):
        return self.script.format(**self.server.variables)

    def get_core_info(self):
        return {
            "uid": str(self.uid),
            "title": self.title,
            "description": self.description,
            "schedule": self.schedule,
            "user": self.user,
            "script": self.get_script(),
            "enable": self.enable,
            "add_time": str(self.add_time),
            "mod_time": str(self.modify_time),
        }
    
    def get_code(self):
        info = self.get_core_info()
        info_str = json.dumps(info)
        return hashutils.get_md5_hexdigest(info_str)
    
    def info(self):
        info = self.get_core_info()
        info["code"] = self.code
        return info

    def get_success_determination_config(self):
        if not self.success_determination_config_data:
            return {}
        try:
            return yaml.safe_load(self.success_determination_config_data)
        except:
            return {}
    
    def set_success_determination_config(self, value):
        self.success_determination_config_data = yaml.safe_dump(value)
    
    success_determination_config = property(get_success_determination_config, set_success_determination_config)

    def success_determination(self, result):
        return self.SUCCESS_RULE_FUNCTIONS.get(self.success_determination_rule)(self, result)

class Result(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, verbose_name=_("Schedule"))
    run_time = models.DateTimeField(verbose_name=_("Run Time"))
    success = models.NullBooleanField(verbose_name=_("Success"))
    code = models.IntegerField(null=True, blank=True, verbose_name=_("Script Exit Code"))
    stdout = SafeTextField(null=True, blank=True, password=app_settings.DJANGO_SAFE_FIELD_PASSWORDS["django_crontab_manager.Result.stdout"], verbose_name=_("Stdout Message"))
    stderr = SafeTextField(null=True, blank=True, password=app_settings.DJANGO_SAFE_FIELD_PASSWORDS["django_crontab_manager.Result.stderr"], verbose_name=_("Stderr Message"))

    class Meta:
        verbose_name = _("Result")
        verbose_name_plural = _("Results")

    def __str__(self):
        return str(self.pk)

    def success_determination(self, save=False):
        self.success = self.schedule.success_determination(self)
        if save:
            self.save()
        return self.success



@receiver(post_save, sender=Server)
def do_update_schedules_code(sender, **kwargs):
    from .services import update_schedules_code
    instance = kwargs.get("instance", None)
    if instance:
        changed_items = update_schedules_code(instance.schedules.all())
        for item in changed_items:
            logger.info("Schedule id={} title={} update code after server settings changed.".format(item.pk, item.title))


class ScheduleImportWorkflow(DjangoDataImportWorkflow):

    def do_parse(self):
        if DJANGO_CRONTAB_MANAGER_COPY_IMPORTED_DATAFILE:
            temp_datafile_instance = fsutils.TemporaryFile(content=self.datafile_field.read(), filename_suffix=".xlsx")
            datafile = temp_datafile_instance.filepath
        else:
            datafile = self.datafile
            
        items = []
        try:
            rows = load_data_from_workbook(datafile, rows="2-")
        except Exception as error:
            raise RuntimeError(_("Load excel file failed: {0}").format(str(error)))

        schedule_mapping = {}
        for s in Schedule.objects.prefetch_related("server").all():
            schedule_mapping[str(s.uid)] = s

        server_uids = [str(x.uid) for x in Server.objects.all()]

        for row in rows:
            item = ParsedItem()
            data = {
                "server__uid": row[2],
                "uid": row[3],
                "title": row[4],
                "description": row[5],
                "schedule": row[6],
                "user": row[7],
                "script": row[8],
                "enable": typingutils.cast_bool(row[9]),
                "success_determination_rule": row[10],
                "success_determination_config_data": row[12],
            }

            uid = row[3]
            if not uid:
                item.mark_failed(_("Imported row has no Uid field"), data)
                items.append(item)
                continue
    
            server_uid = row[2]
            if not server_uid in server_uids:
                item.mark_failed(_("Imported row's server uid is not exists"), data)
                items.append(item)
                continue

            if uid in schedule_mapping:
                schedule = schedule_mapping[uid]
                schedule.uid = str(schedule.uid)
                schedule.add_time = str(schedule.add_time)
                schedule.modify_time = str(schedule.modify_time)
                field_names =  ["uid", "title", "description", "schedule", "user", "script", "enable", "success_determination_rule", "success_determination_config_data"]
                changed, changed_keys = dictutils.changes(schedule, data, field_names, return_changed_keys=True, do_update=False, ignore_empty_value=True)
                if str(schedule.server.uid) != data["server__uid"]:
                    changed_keys.append("server__uid")
                    changed = True
                if changed:
                    item.mark_success(_("Imported row will update an exists schedule, title={title}, changed fields: {changed_fields}").format(title=data.get("title", ""), changed_fields=", ".join(changed_keys)), data)
                    items.append(item)
                    continue
                else:
                    item.mark_success(_("Imported row is the same with an exists schedule"), data)
                    items.append(item)
                    continue
            else:
                item.mark_success(_("Imported row will create a new schedule"), data)
                items.append(item)
                continue
        return items

    
    def do_import(self, import_items):

        server_mapping = {}
        for server in Server.objects.all():
            server_mapping[str(server.uid)] = server
        
        schedule_mapping = {}
        for s in Schedule.objects.prefetch_related("server").all():
            schedule_mapping[str(s.uid)] = s
        
        for item in import_items:
            try:
                server__uid = item.data["server__uid"]
                if not server__uid in server_mapping:
                    item.mark_failed(_("Server with uid={uid} not exists.").format(uid=server__uid))
                    continue
                server = server_mapping[server__uid]

                uid = item.data["uid"]
                create_flag = False
                if uid in schedule_mapping:
                    schedule = schedule_mapping[uid]
                else:
                    schedule = Schedule()
                    schedule.server = server
                    schedule.uid = uid
                    create_flag = True

                field_names =  ["title", "description", "schedule", "user", "script", "enable", "add_time", "modify_time", "success_determination_rule", "success_determination_config_data"]
                changed, changed_fields = dictutils.changes(schedule, item.data, keys=field_names, return_changed_keys=True, ignore_empty_value=True)
                if schedule.server.pk != server.pk:
                    changed = True
                    changed_fields.append("server")
                    schedule.server = server

                if changed or create_flag:
                    schedule.save()

                if changed and create_flag:
                    item.mark_success(_("Schedule uid={uid} created success").format(uid=uid))
                elif changed:
                    item.mark_success(_("Schedule uid={uid} updated success, changed_fields={changed_fields}").format(uid=uid, changed_fields=", ".join(changed_fields)))
                else:
                    item.mark_success(_("Schedule uid={uid} NOTHING changed.").format(uid=uid))

            except Exception as error:
                item.mark_failed(_("Import failed, error_message={error_message}").format(error_message=str(error)))

class ScheduleImportWorkflow(DjangoSimpleExportedDataImportWorkflow):
    model = Schedule
    keyfield = "uid"
    field_cols = {
        "server": 2,
        "uid": 3,
        "title": 4,
        "description": 5,
        "schedule": 6,
        "user": 7,
        "script": 8,
        "enable": 9,
        "success_determination_rule": 10,
        "success_determination_config_data": 12,
    }
    foreignkey_settings = {
        "server": {
            "keyfield": "uid",
            "model": Server,
        }
    }
