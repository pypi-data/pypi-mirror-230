import re
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.apps import apps

from .models import SimpleTask
from .viewshelper import get_task_instance
from .viewshelper import error_handler
from .viewshelper import aclkey_check
from .viewshelper import get_payload
from .exceptions import DjangoSimpleTask2Error
from .settings import *

logger = logging.getLogger(__name__)

@csrf_exempt
@error_handler
def do_auto_reset(request):
    payload = get_payload(request)
    aclkey_check(payload)

    infos = {}
    for ModelClass in apps.get_models():
        if issubclass(ModelClass, SimpleTask):
            model_class_name = "{app_label}.{model_name}".format(
                app_label=ModelClass._meta.app_label,
                model_name=ModelClass._meta.model_name,
            )
            number = ModelClass.do_auto_reset()
            infos[model_class_name] = number
    return infos

@csrf_exempt
@error_handler
def do_task(request):
    payload = get_payload(request)
    aclkey_check(payload)

    task_info = payload.get("task_info", None)
    if not task_info:
        raise DjangoSimpleTask2Error(2910015, "`task_info` field is required.")

    try:
        task_instance = get_task_instance(task_info)
    except DjangoSimpleTask2Error as error:
        raise error
    except Exception as error:
        message = "get task instance {task_info} failed with error: {error}.".format(task_info=task_info, error=str(error))
        logger.warning(message)
        return JsonResponse({
            "success": False,
            "result": None,
            "error": {
                "code": 2910016,
                "message": message,
            }
        })

    try:
        result =  task_instance.do_task(payload)
        return result
    except DjangoSimpleTask2Error as error:
        logger.info("do task got failed: {error}".format(error=str(error)))
        raise error
    except Exception as error:
        logger.error("system error: {error}".format(error=str(error)))
        raise error

@csrf_exempt
@error_handler
def get_a_task(request):
    payload = get_payload(request)
    aclkey_check(payload)

    channels = payload.get("channels", "default")
    redis_conn = SimpleTask.get_redis_conn()
    channels = [DJANGO_SIMPLETASK2_CHANNEL_NAME_TEMPLATE.format(channel=channel) for channel in channels.split(",")]
    task = redis_conn.blpop(channels, timeout=DJANGO_SIMPLETASK2_TASK_PULL_TIMEOUT)
    if not task:
        logger.debug("got NO task whiling pulling task from channels: {channels}".format(channels=channels))
        return None
    else:
        logger.debug("got task {task}.".format(task=task))
    channel_fullname, task_info = task
    try:
        channel = re.match(DJANGO_SIMPLETASK2_CHANNEL_NAME_STRIP_REGEX, channel_fullname).groupdict()["channel"]
        channel_flags = DJANGO_SIMPLETASK2_CHANNEL_FLAGS_TEMPLATE.format(channel=channel)
        result = redis_conn.srem(channel_flags, task_info)
        if result != 1:
            logger.warning("clean task flag failed: channel_flags={channel_flags}, task_info={task_info}.".format(channel_flags=channel_flags, task_info=task_info))
    except Exception as error:
        logger.warning("clean task flag got unknown exception: channel_flags={channel_flags}, task_info={task_info}, error={error}".format(
            channel_flags=channel_flags,
            task_info=task_info,
            error=str(error),
        ))
    return task_info
