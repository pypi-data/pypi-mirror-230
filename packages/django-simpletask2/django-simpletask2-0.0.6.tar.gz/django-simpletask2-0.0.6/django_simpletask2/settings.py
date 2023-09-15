from django.conf import settings


DJANGO_SIMPLETASK2_CHANNEL_NAME_TEMPLATE = getattr(settings, "DJANGO_SIMPLETASK2_CHANNEL_NAME_TEMPLATE", "django-simpletask2:channels:{channel}")
DJANGO_SIMPLETASK2_CHANNEL_NAME_STRIP_REGEX = getattr(settings, "DJANGO_SIMPLETASK2_CHANNEL_NAME_STRIP_REGEX", "^django-simpletask2:channels:(?P<channel>.*)$")
DJANGO_SIMPLETASK2_CHANNEL_FLAGS_TEMPLATE = getattr(settings, "DJANGO_SIMPLETASK2_CHANNEL_FLAGS_TEMPLATE", "django-simpletask2:channel-flags:{channel}")
DJANGO_SIMPLETASK2_TASK_WAIT_TIMEOUT_KEY_TEMPLATE = getattr(settings, "DJANGO_SIMPLETASK2_TASK_WAIT_TIMEOUT_KEY_TEMPLATE", "django-simpletask2:task-wait-timeout:{channel}")
DJANGO_SIMPLETASK2_DO_TASK_TIMEOUT_KEY_TEMPLATE = getattr(settings, "DJANGO_SIMPLETASK2_DO_TASK_TIMEOUT_KEY_TEMPLATE", "django-simpletask2:do-task-timeout:{channel}")
DJANGO_SIMPLETASK2_TASK_LOCK_NAME_TEMPLATE = getattr(settings, "", "django-simpletask2:locks:{app_label}.{model_name}:{task_id}")
DJANGO_SIMPLETASK2_TASK_PULL_TIMEOUT = getattr(settings, "DJANGO_SIMPLETASK2_TASK_PULL_TIMEOUT", 5)
DJANGO_SIMPLETASK2_REDIS_NAME = getattr(settings, "DJANGO_SIMPLETASK2_REDIS_NAME", "default")
DJANGO_SIMPLETASK2_ACLKEY = getattr(settings, "DJANGO_SIMPLETASK2_ACLKEY", settings.SECRET_KEY)
