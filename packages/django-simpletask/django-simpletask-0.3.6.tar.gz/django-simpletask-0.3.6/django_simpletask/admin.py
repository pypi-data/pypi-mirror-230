from django.contrib import admin
from django.contrib import messages
from django.utils.translation import ngettext
from django.utils.translation import ugettext
from .models import SimpleTask

def action_reset_task(modeladmin, request, queryset):
    reseted = 0
    for item in queryset.all():
        item.reset(save=True)
        reseted += 1
    modeladmin.message_user(request, ngettext(
        '%d task has been reset.',
        '%d tasks have been reset.',
        reseted,
    ) % reseted, messages.SUCCESS)
action_reset_task.allowed_permissions = ("reset",)
action_reset_task.short_description = ugettext("Reset Selected Tasks: %(verbose_name_plural)s")


def action_do_task(modeladmin, request, queryset):
    ok = 0
    failed = 0
    for item in queryset.all():
        try:
            item.do_task_force("admin:action")
            ok += 1
        except Exception as error:
            failed += 1
            modeladmin.message_user(request, ugettext("Do task {id} failed, error_message={error_message}").format(id=item.id, error_message=str(error)), messages.ERROR)
    modeladmin.message_user(request, ngettext(
        '%d task done success',
        '%d tasks done success',
        ok,
    ) % ok, messages.SUCCESS)
action_do_task.allowed_permissions = ("do",)
action_do_task.short_description = ugettext("Do Selected Tasks: %(verbose_name_plural)s")


class SimpleTaskAdmin(admin.ModelAdmin):

    list_display = ["add_time", "mod_time", "status"]
    list_filter = ["status"]
    readonly_fields = [] + SimpleTask.SIMPLE_TASK_FIELDS

    def has_do_permission(self, request, obj=None):
        info = {
            "app_label": self.model._meta.app_label,
            "model_name": self.model._meta.model_name,
        }
        return request.user.has_perm("{app_label}.do_{model_name}".format(**info), obj)
    
    def has_reset_permission(self, request, obj=None):
        info = {
            "app_label": self.model._meta.app_label,
            "model_name": self.model._meta.model_name,
        }
        return request.user.has_perm("{app_label}.reset_{model_name}".format(**info), obj)


    actions = [
        action_do_task,
        action_reset_task,
    ]
