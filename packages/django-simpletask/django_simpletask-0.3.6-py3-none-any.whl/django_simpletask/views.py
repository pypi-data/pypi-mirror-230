
import logging
import typing

import bizerror
from fastutils import sysutils
from fastutils import randomutils
from fastutils import threadutils

from django.urls import path
from django.utils import timezone
from django.db.models import Q
from django.conf import settings

from django_apiview.views import apiview
from django_db_lock.client import DjangoDbLock
from django_db_lock.client import get_default_lock_service

logger = logging.getLogger(__name__)

class SimpleTaskViews(object):
    def __init__(self, *models, aclkey=None, lock_service=None):
        self.models = models
        self.models_mapping = {}
        for model in models:
            app_label = model._meta.app_label
            model_name = model._meta.model_name
            self.models_mapping["{}.{}".format(app_label, model_name)] = model
        self.models_number = len(models)
        self.lock_service = lock_service or get_default_lock_service()
        self.aclkey = aclkey or getattr(settings, "DJANGO_SIMPLETASK_ACLKEY", None)
        self.counter = threadutils.Counter()

    def get_urls(self):
        return [
            path("getReadyTasks", self.get_ready_tasks_view()),
            path("doTask", self.do_task_view()),
            path("postProxyResult", self.post_proxy_result_view()),
            path("reportError", self.report_error_view()),
        ]

    def get_ready_tasks_view(self):
        @apiview
        def get_ready_tasks(aclkey:str, executorName:str, batchSize:int=5, channel=None):
            if not self.aclkey:
                raise bizerror.MissingConfigItem(item="DJANGO_SIMPLETASK_ACLKEY")
            if aclkey != self.aclkey:
                raise bizerror.AppAuthFailed()
            tasks = []
            counter = self.counter.incr()
            for index in range(counter, counter+self.models_number):
                index = index % self.models_number
                model = self.models[index]
                # get ready tasks
                app_label = model._meta.app_label
                model_name = model._meta.model_name
                lock_name = model.GET_READY_TASKS_LOCK_NAME_TEMPLATE.format(app_label=app_label, model_name=model_name, channel=channel)
                timeout = model.GET_READY_TASKS_LOCK_TIMEOUT
                with DjangoDbLock(self.lock_service, lock_name, str(randomutils.uuid4()), timeout) as locked:
                    if locked:
                        queryset = self.get_ready_tasks_queryset(model, channel)
                        for task in queryset[:batchSize]:
                            task.start(executorName, save=True)
                            info = task.get_task_info()
                            tasks.append(info)
                            logger.debug("task app_label={app_label}, model_name={model_name}, channel={channel}, task_id={task_id}, info={info} have been fetched and will be handled soon...".format(app_label=app_label, model_name=model_name, channel=channel, task_id=task.pk, info=info))
                        if tasks:
                            return tasks
            return tasks
        return get_ready_tasks

    def get_model(self, app_label, model_name):
        return self.models_mapping.get("{}.{}".format(app_label, model_name), None)

    def get_ready_tasks_queryset(self, model, channel=None):
        now = timezone.now()
        queryset = model.objects
        queryset = queryset.filter(status=model.READY)
        queryset = queryset.filter(ready_time__lte=now)
        queryset = queryset.filter(Q(expire_time=None) | Q(expire_time__gte=now))
        queryset = queryset.order_by("mod_time")

        prefetch_related = getattr(model, "prefetch_related", None)
        if prefetch_related:
            queryset = queryset.prefetch_related(*prefetch_related)

        channel_field = getattr(model, "channel_field", None)
        if channel_field and channel:
            queryset = queryset.filter(**{channel_field: channel})

        return queryset

    def do_task_view(self):
        @apiview
        def do_task(aclkey:str, task:dict, executorName:str):
            if not self.aclkey:
                raise bizerror.MissingConfigItem(item="DJANGO_SIMPLETASK_ACLKEY")
            if aclkey != self.aclkey:
                raise bizerror.AppAuthFailed()
            app_label = task["app_label"]
            model_name = task["model_name"]
            taskId = task["taskId"]
            model = self.get_model(app_label, model_name)
            if not model:
                raise bizerror.BadParameter("task model {}.{} not registered.".format(app_label, model_name))
            get_task_filter = {
                model.task_id_field: taskId,
            }
            task = model.objects.get(**get_task_filter)
            return task.do_task(executorName)
        return do_task

    def get_task_info_view(self):
        @apiview
        def get_task_info(aclkey:str, task:dict):
            if not self.aclkey:
                raise bizerror.MissingConfigItem(item="DJANGO_SIMPLETASK_ACLKEY")
            if aclkey != self.aclkey:
                raise bizerror.AppAuthFailed()
            app_label = task["app_label"]
            model_name = task["model_name"]
            taskId = task["taskId"]
            model = self.get_model(app_label, model_name)
            if not model:
                raise bizerror.BadParameter("task model {}.{} not registered.".format(app_label, model_name))
            task = model.objects.get(pk=taskId)
            return self.get_task_info(task)
        return get_task_info

    def post_proxy_result_view(self):
        @apiview
        def post_proxy_result(aclkey:str, task:dict, worker, responseData):
            if not self.aclkey:
                raise bizerror.MissingConfigItem(item="DJANGO_SIMPLETASK_ACLKEY")
            if aclkey != self.aclkey:
                raise bizerror.AppAuthFailed()
            app_label = task["app_label"]
            model_name = task["model_name"]
            taskId = task["taskId"]
            model = self.get_model(app_label, model_name)
            if not model:
                raise bizerror.BadParameter("task model {}.{} not registered.".format(app_label, model_name))
            get_task_filter = {
                model.task_id_field: taskId,
            }
            task = model.objects.get(**get_task_filter)
            try:
                result = task.post_proxy_result(worker, responseData, save=True)
                if result is True:
                    task.report_success(worker, result, save=True)
            except Exception as error:
                error = bizerror.BizError(error)
                task.report_error(worker, error.code, error.message, save=True)
            return result
        return post_proxy_result

    def report_success_view(self):
        @apiview
        def report_success(aclkey:str, task:dict, worker, result_message):
            if not self.aclkey:
                raise bizerror.MissingConfigItem(item="DJANGO_SIMPLETASK_ACLKEY")
            if aclkey != self.aclkey:
                raise bizerror.AppAuthFailed()
            app_label = task["app_label"]
            model_name = task["model_name"]
            taskId = task["taskId"]
            model = self.get_model(app_label, model_name)
            if not model:
                raise bizerror.BadParameter("task model {}.{} not registered.".format(app_label, model_name))
            get_task_filter = {
                model.task_id_field: taskId,
            }
            task = model.objects.get(**get_task_filter)
            task.report_success(worker, result_message, save=True)
            return True
        return report_success

    def report_error_view(self):
        @apiview
        def report_error(aclkey:str, task:dict, worker, error_code, error_message):
            if not self.aclkey:
                raise bizerror.MissingConfigItem(item="DJANGO_SIMPLETASK_ACLKEY")
            if aclkey != self.aclkey:
                raise bizerror.AppAuthFailed()
            app_label = task["app_label"]
            model_name = task["model_name"]
            taskId = task["taskId"]
            model = self.get_model(app_label, model_name)
            if not model:
                raise bizerror.BadParameter("task model {}.{} not registered.".format(app_label, model_name))
            get_task_filter = {
                model.task_id_field: taskId,
            }
            task = model.objects.get(**get_task_filter)
            task.report_error(worker, error_code, error_message, save=True)
            return True
        return report_error
    
    def get_task_info(self, task):
        return task.get_task_info()


class SimpleTaskViews(object):

    def __init__(self, *models, aclkey=None):
        self.models = models
        self.models_mapping = {}
        for model in models:
            app_label = model._meta.app_label
            model_name = model._meta.model_name
            self.models_mapping["{}.{}".format(app_label, model_name)] = model
        self.aclkey = aclkey or settings.DJANGO_SIMPLETASK_ACLKEY

    def get_urls(self):
        return [
            path("doTask", self.do_task_view()),
        ]

    def get_model(self, app_label, model_name):
        return self.models_mapping.get("{}.{}".format(app_label, model_name), None)

    def do_task_view(self):
        @apiview
        def do_task(aclkey:str, task:dict, executorName:str, data:typing.Any=None):
            if not self.aclkey:
                raise bizerror.MissingConfigItem(item="DJANGO_SIMPLETASK_ACLKEY")
            if aclkey != self.aclkey:
                raise bizerror.AppAuthFailed()
            app_label = task["app_label"]
            model_name = task["model_name"]
            taskId = task["taskId"]
            model = self.get_model(app_label, model_name)
            if not model:
                raise bizerror.BadParameter("Task model {}.{} not registered.".format(app_label, model_name))
            get_task_filter = {
                model.task_id_field: taskId,
            }
            task = model.objects.get(**get_task_filter)
            task.do_task(executorName, data)
            return True
        return do_task
