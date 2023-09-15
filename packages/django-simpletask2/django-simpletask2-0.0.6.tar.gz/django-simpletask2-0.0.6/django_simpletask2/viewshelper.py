
import json
import functools

from django.apps import apps
from django.http import JsonResponse

from .exceptions import DjangoSimpleTask2Error
from .settings import *

def get_task_instance(task_info):
    try:
        task_class_name, task_id = task_info.split(":")
        task_id = int(task_id)
    except Exception:
        message = "bad formatted task_info: {task_info}.".format(task_info=task_info)
        raise DjangoSimpleTask2Error(2910005, message)
    try:
        TaskModel = apps.get_model(task_class_name)
    except LookupError:
        message = "simple task model {task_class_name} not exists.".format(task_class_name=task_class_name)
        raise DjangoSimpleTask2Error(2910006, message)
    try:
        task_instance = TaskModel.objects.get(pk=task_id)
    except TaskModel.DoesNotExist:
        message = "got an already deleted task {task_info}, you may ignore this and continue.".format(task_info=task_info)
        raise DjangoSimpleTask2Error(2910004, message)
    return task_instance

def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return JsonResponse({
                "success": True,
                "result": result,
                "error": {
                    "code": 0,
                    "message": "OK",
                },
            })
        except DjangoSimpleTask2Error as error:
            return JsonResponse({
                "success": False,
                "result": None,
                "error": {
                    "code": error.code,
                    "message": error.message,
                },
            })
        except Exception as error:
            return JsonResponse({
                "success": False,
                "result": None,
                "error": {
                    "code": 2910000,
                    "message": "system error.",
                }
            })
    return functools.wraps(func)(wrapper)

def get_payload(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        raise DjangoSimpleTask2Error(2910001, "please send request parameters in PAYLOAD format.")
    return payload

def aclkey_check(payload):
    aclkey = payload.get("aclkey", None)
    if not aclkey:
        raise DjangoSimpleTask2Error(2910002, "`aclkey` field is required.")
    if aclkey != DJANGO_SIMPLETASK2_ACLKEY:
        raise DjangoSimpleTask2Error(2910003, "aclkey is wrong and access denied.")
    return True
