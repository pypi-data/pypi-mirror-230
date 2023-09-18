from django.conf import settings


SECRET_KEY = settings.SECRET_KEY
DJANGO_SAFE_FIELD_PASSWORDS = {
    "django_crontab_manager.Server.variables_data": SECRET_KEY,
    "django_crontab_manager.Server.aclkey": SECRET_KEY,
    "django_crontab_manager.Schedule.script": SECRET_KEY,
    "django_crontab_manager.Schedule.success_determination_config_data": SECRET_KEY,
    "django_crontab_manager.Result.stdout": SECRET_KEY,
    "django_crontab_manager.Result.stderr": SECRET_KEY,
}
DJANGO_SAFE_FIELD_PASSWORDS.update(getattr(settings, "DJANGO_SAFE_FIELD_PASSWORDS", {}))
