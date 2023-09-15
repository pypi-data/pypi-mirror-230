import logging
from django.utils.translation import gettext_lazy as _
from django.contrib import messages


logger = logging.getLogger(__name__)


def reset_selected_tasks(modeladmin, request, queryset):
    ok = 0
    failed = 0
    for item in queryset:
        try:
            item.reset()
            item.push_to_mq()
            ok += 1
        except Exception as error:
            logger.warning("doing action:reset_selected_tasks failed on item: task_info={task_info}, error={error}.".format(task_info=item.get_task_info(), error=str(error)))
            failed += 1
    if not failed:
        modeladmin.message_user(request, _("{ok} items have been reset successfully.").format(ok=ok), messages.SUCCESS)
    elif not ok:
        modeladmin.message_user(request, _("{failed} items reset failed.").format(failed=failed), messages.ERROR)
    else:
        modeladmin.message_user(request, _("{ok} items have been reset successfully and {failed} items reset failed.").format(ok=ok, failed=failed), messages.WARNING)

reset_selected_tasks.short_description = _("Reset selected tasks and push them to message queue")

def force_do_selected_tasks(modeladmin, request, queryset):
    ok = 0
    failed = 0
    for item in queryset:
        try:
            item.reset()
            item.do_task(force=True)
            ok += 1
        except Exception as error:
            logger.warning("doing action:force_do_selected_tasks failed on item: task_info={task_info}, error={error}.".format(task_info=item.get_task_info(), error=str(error)))
            failed += 1
    if not failed:
        modeladmin.message_user(request, _("{ok} items have been successfully completed.").format(ok=ok), messages.SUCCESS)
    elif not ok:
        modeladmin.message_user(request, _("{failed} items failed.").format(failed=failed), messages.ERROR)
    else:
        modeladmin.message_user(request, _("{ok} items have been successfully completed and {failed} items failed.").format(ok=ok, failed=failed), messages.WARNING)
force_do_selected_tasks.short_description = _("Force to do selected tasks")

def mark_selected_tasks_done(modeladmin, request, queryset):
    ok = 0
    failed = 0
    for item in queryset:
        try:
            item.done(force=True)
            ok += 1
        except Exception as error:
            logger.warning("doing action:mark_selected_tasks_done failed on item: task_info={task_info}, error={error}.".format(task_info=item.get_task_info(), error=str(error)))
            failed += 1
    if not failed:
        modeladmin.message_user(request, _("{ok} items have been successfully completed.").format(ok=ok), messages.SUCCESS)
    elif not ok:
        modeladmin.message_user(request, _("{failed} items failed.").format(failed=failed), messages.ERROR)
    else:
        modeladmin.message_user(request, _("{ok} items have been successfully completed and {failed} items failed.").format(ok=ok, failed=failed), messages.WARNING)
mark_selected_tasks_done.short_description = _("Force to mark selected tasks done")
