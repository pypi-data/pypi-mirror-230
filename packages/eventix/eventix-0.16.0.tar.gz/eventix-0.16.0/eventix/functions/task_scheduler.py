import logging
import os
import sys

from eventix.contexts import namespace_context, namespace_context_var
from eventix.exceptions import backend_exceptions
from eventix.functions.errors import raise_errors
from eventix.functions.eventix_client import EventixClient
from eventix.pydantic.task import TaskModel

log = logging.getLogger(__name__)


class TaskScheduler(EventixClient):

    @classmethod
    def schedule(cls, task: TaskModel) -> TaskModel:
        if task.namespace is None:
            with namespace_context() as namespace:
                task.namespace = namespace
        log.debug(f"scheduling task: {task.task} namespace: {task.namespace} uid: {task.uid} eta: {task.eta} unique_key: {task.unique_key} priority: {task.priority}")
        return cls.task_post(task)

    @classmethod
    def task_get(cls, uid: str) -> TaskModel:
        r = cls.interface.get(f'/task/{uid}')
        with raise_errors(r, backend_exceptions):
            return TaskModel.parse_raw(r.content)

    @classmethod
    def task_post(cls, task: TaskModel) -> TaskModel:
        r = cls.interface.post('/task', data=task.json())
        with raise_errors(r, backend_exceptions):
            return TaskModel.parse_raw(r.content)

    @classmethod
    def config(cls, config: dict):
        # Be aware that the namespace context is set direct through
        # the context variable.... so no reset possible

        base_url = os.environ.get("EVENTIX_URL", "")
        if base_url == "":
            log.error("No EVENTIX_URL set.")
            sys.exit()

        cls.set_base_url(base_url)

        namespace = ""
        if "namespace" in config:
            namespace = config['namespace']

        if namespace == "":
            namespace = os.environ.get("EVENTIX_NAMESPACE", "")


        if namespace == "":
            log.error("No EVENTIX_NAMESPACE set.")
            sys.exit()

        namespace_context_var.set(namespace)


