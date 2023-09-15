import logging
import json
import time
from urllib import parse as urlparse

import bizerror
import requests
from fastutils import sysutils
from fastutils import threadutils
from fastutils import threadutils

from django_apiview.pack import SimpleJsonResultPacker

logger = logging.getLogger(__name__)

class SimpleTaskProducer(threadutils.SimpleProducer):

    default_batch_size = 5

    def __init__(self,
            task_server_url,
            task_server_aclkey,
            executorName,
            channel=None,
            batch_size=None,
            api_url_get_ready_tasks=None,
            response_packer=None,
            **kwargs):
        self.task_server_url = task_server_url
        self.task_server_aclkey = task_server_aclkey
        self.executorName = executorName
        self.channel = channel
        self.batch_size = batch_size or self.default_batch_size
        self.api_url_get_ready_tasks = api_url_get_ready_tasks or urlparse.urljoin(self.task_server_url, "./getReadyTasks")
        self.response_packer = response_packer or SimpleJsonResultPacker()
        super().__init__(**kwargs)

    def produce(self):
        logger.debug("SimpleTaskProducer do produce...")
        try:
            params = {
                "aclkey": self.task_server_aclkey,
                "executorName": self.executorName,
                "batchSize": self.batch_size,
                "channel": self.channel,
                "ts": time.time(),
            }
            logger.debug("SimpleTaskProducer calling get_ready_tasks api: url={0}, params={1}".format(self.api_url_get_ready_tasks, params))
            response = requests.get(self.api_url_get_ready_tasks, params)
            logger.debug("SimpleTaskProducer calling get_ready_tasks api got response: content={0}".format(response.content))
            tasks = self.response_packer.unpack(response.content)
            if tasks:
                logger.info("SimpleTaskProducer calling get_ready_tasks api parse the response and got the tasks: {0}".format(tasks))
            else:
                logger.debug("SimpleTaskProducer calling get_ready_tasks api parse the response and got NO tasks...")
            return tasks
        except Exception as error:
            logger.exception("SimpleTaskProducer produce tasks failed: {0}".format(str(error)))
            return []

class SimpleTaskConsumer(threadutils.SimpleConsumer):
    
    default_task_id_field_name = "id"

    def __init__(self,
            task_server_url,
            task_server_aclkey,
            executorName,
            task_id_field_name=None,
            api_url_do_task=None,
            api_url_get_task_info=None,
            api_url_post_proxy_result=None,
            api_url_report_success=None,
            api_url_report_error=None,
            response_packer=None,
            **kwargs):
        self.task_server_url = task_server_url
        self.task_server_aclkey = task_server_aclkey
        self.executorName = executorName
        self.task_id_field_name = task_id_field_name or self.default_task_id_field_name
        self.api_url_do_task = api_url_do_task or urlparse.urljoin(self.task_server_url, "./doTask")
        self.api_url_get_task_info = api_url_get_task_info or urlparse.urljoin(self.task_server_url, "./getTaskInfo")
        self.api_url_post_proxy_result = api_url_post_proxy_result or urlparse.urljoin(self.task_server_url, "./postProxyResult")
        self.api_url_report_success = api_url_report_success or urlparse.urljoin(self.task_server_url, "./reportSuccess")
        self.api_url_report_error = api_url_report_error or urlparse.urljoin(self.task_server_url, "./reportError")
        self.response_packer = response_packer or SimpleJsonResultPacker()
        super().__init__(**kwargs)

    def consume(self, task):
        logger.info("SimpleTaskConsumer do consume task: {0}".format(str(task)))
        is_proxy_task = task.get("isProxyTask", False)
        if is_proxy_task:
            return self.do_proxy_consume(task)
        else:
            return self.do_simple_consume(task)
    
    def do_simple_consume(self, task):
        logger.debug("SimpleTaskConsumer do simple consume task: {0}".format(str(task)))
        try:
            params = {
                "ts": time.time(),
            }
            data = {
                "task": task,
                "aclkey": self.task_server_aclkey,
                "executorName": self.executorName,
            }
            logger.debug("SimpleTaskConsumer calling do_task api: url={0}, params={1}".format(self.api_url_do_task, params))
            response = requests.post(self.api_url_do_task, params=params, json=data)
            logger.debug("SimpleTaskConsumer calling do_task api got response: content={0}".format(response.content))
            result = self.response_packer.unpack(response.content)
            logger.debug("SimpleTaskConsumer unpack response content and got result={0}".format(result))
            result
        except Exception as error:
            logger.exception("SimpleTaskConsumer do simple consume task failed: error_message={0}".format(str(error)))
            return False

    def do_proxy_consume(self, task):
        logger.debug("SimpleTaskConsumer do proxy consume task: {0}".format(str(task)))
        try:
            post_proxy_result_response = {}
            proxy_settings = task.get("proxy-settings", {})
            while proxy_settings:
                result = self.do_proxy_request(task, proxy_settings)
                post_proxy_result_response = self.post_proxy_result(task, result)
                if isinstance(post_proxy_result_response, dict):
                    proxy_settings = post_proxy_result_response.get("proxy-settings", None)
                else:
                    proxy_settings = None
        except Exception as error:
            logger.exception("SimpleTaskConsumer do proxy consume task failed: error_message={0}".format(str(error)))
            error = bizerror.BizError(error)
            try:
                self.report_error(task, error.code, error.message)
            except Exception as error:
                logger.exception("SimpleTaskConsumer report error failed: error_message={0}".format(str(error)))

    def do_proxy_request(self, task, settings):
        logger.debug("SimpleTaskConsumer do proxy request, settings={0}".format(settings))
        settings = settings or {}
        settings.setdefault("method", "GET")
        logger.debug("SimpleTaskConsumer do proxy request calling requests.request, settings={0}".format(settings))
        response = requests.request(**settings)
        logger.debug("SimpleTaskConsumer do proxy request get response data: {0}".format(response.text))
        return response.text

    def post_proxy_result(self, task, response_data):
        logger.debug("SimpleTaskConsumer post proxy result response...")
        params = {
            "ts": time.time(),
        }
        data = {
            "task": task,
            "aclkey": self.task_server_aclkey,
            "worker": self.executorName,
            "responseData": response_data,
        }
        logger.debug("SimpleTaskConsumer calling post_proxy_result api: url={0}, params={1}, json={2}".format(self.api_url_post_proxy_result, params, data))
        response = requests.post(self.api_url_post_proxy_result, params=params, json=data)
        logger.debug("SimpleTaskConsumer calling post_proxy_result api got response: content={0}".format(response.text))
        result = self.response_packer.unpack(response.text)
        logger.debug("SimpleTaskConsumer unpack response content and got result={0}".format(result))
        return result

    def get_task_info(self, task):
        logger.debug("SimpleTaskConsumer doing get_task_info...")
        params = {
            "ts": time.time(),
        }
        data = {
            "task": task,
            "aclkey": self.task_server_aclkey,
        }
        logger.debug("SimpleTaskConsumer calling get_task_info api: url={0}, params={1}".format(self.api_url_get_task_info, params))
        response = requests.post(self.api_url_get_task_info, params=params, json=data)
        logger.debug("SimpleTaskConsumer calling get_task_info api got response: content={0}".format(response.text))
        result = self.response_packer.unpack(response.text)
        logger.debug("SimpleTaskConsumer unpack response content and got result={0}".format(result))
        return result

    def report_success(self, task, result_message):
        logger.debug("SimpleTaskConsumer doing report_success...")
        params = {
            "ts": time.time(),
        }
        data = {
            "task": task,
            "aclkey": self.task_server_aclkey,
            "worker": self.executorName,
            "result_message": result_message,
        }
        logger.debug("SimpleTaskConsumer calling report_success api: url={0}, params={1}, data={2}".format(self.api_url_report_success, params, data))
        response = requests.post(self.api_url_report_success, params=params, json=data)
        logger.debug("SimpleTaskConsumer calling report_success api got response: content={}".format(response.text))
        result = self.response_packer.unpack(response.text)
        logger.debug("SimpleTaskConsumer unpack response content and got result={0}".format(result))
        return result

    def report_error(self, task, error_code, error_message):
        logger.debug("SimpleTaskConsumer doing report error...")
        params = {
            "ts": time.time(),
        }
        data = {
            "task": task,
            "aclkey": self.task_server_aclkey,
            "worker": self.executorName,
            "error_code": error_code,
            "error_message": error_message,
        }
        logger.debug("SimpleTaskConsumer calling report_error api: url={0}, params={1}, data={2}".format(self.api_url_report_error, params, data))
        response = requests.post(self.api_url_report_error, params=params, json=data)
        logger.debug("SimpleTaskConsumer calling report_error api got response: content={0}".format(response.text))
        result = self.response_packer.unpack(response.text)
        logger.debug("SimpleTaskConsumer unpack response content and got resul={0}".format(result))
        return result

class SimpleTaskService(threadutils.SimpleProducerConsumerServer):

    def __init__(self, **kwargs):
        executorName = sysutils.get_worker_id(self.__class__.__name__)
        producer_class_init_kwargs = kwargs.get("producer_class_init_kwargs", {})
        consumer_class_init_kwargs = kwargs.get("consumer_class_init_kwargs", {})
        kwargs["producer_class_init_kwargs"] = producer_class_init_kwargs
        kwargs["consumer_class_init_kwargs"] = consumer_class_init_kwargs
        producer_class_init_kwargs["executorName"] = executorName
        consumer_class_init_kwargs["executorName"] = executorName
        super().__init__(**kwargs)

    default_producer_class = SimpleTaskProducer
    default_consumer_class = SimpleTaskConsumer
