import datetime
import functools
import logging
from inspect import signature
from typing import Callable, Dict, Any, _BaseGenericAlias

from pydantic import BaseModel
from pydantic_db_backend_common.utils import str_to_datetime_if_parseable

from eventix.contexts import namespace_context, delay_tasks_context, task_priority_context
from eventix.functions.task_scheduler import TaskScheduler
from eventix.pydantic.task import TaskModel

log = logging.getLogger(__name__)


class EventixTaskBase(object):
    pass


def task(store_result: bool = True, unique_key_generator: Callable = None, retry: bool = True, max_retries: int | None = None, error_expires: int | None = None, result_expires: int | None = 604800):
    # parameters suggested:
    #
    # store_result: bool , wether to store or not to store results
    # unique_uid: ....  having a unique id, which leads to update the task if it is rescheduled.

    # retry: bool, wether to retry failed tasks
    # max_retry: int, maximum retries default 5 ... each retry doubles the time to wait, starting with 30 sec

    is_unique = unique_key_generator is not None

    def inner(f):
        class EventixTask(EventixTaskBase):
            def __init__(self):
                self.func = f
                self.func_name = f.__name__
                self.arg_spec = list(signature(f).parameters.values())
                self.arg_spec_args = [arg.annotation for arg in self.arg_spec]
                self.arg_spec_kwargs = {arg.name: arg.annotation for arg in self.arg_spec}
                assert True

            def get_arg_from_cls(self, cls, arg) -> Any:

                #### commented code is a first start to restructure

                # if isinstance(arg, dict):
                #     if isinstance(cls, _BaseGenericAlias):
                #         cls = cls.__origin__
                #
                # match cls:
                #     case datetime.datetime:
                #         if isinstance(arg, str):
                #             arg = str_to_datetime_if_parseable(arg)
                #     case BaseModel:
                #         if isinstance(arg, dict):
                #             arg = cls.parse_obj(arg)

                match cls:
                    case datetime.datetime:
                        # next line if is for calling task with run. in this case the arg is already a datetime
                        if isinstance(arg, str):
                            arg = str_to_datetime_if_parseable(arg)
                    case _:
                        if isinstance(arg, dict):
                            if isinstance(cls, _BaseGenericAlias):
                                cls = cls.__origin__
                            if issubclass(cls, BaseModel):
                                arg = cls.parse_obj(arg)
                return arg

            def restore_original_types(self, args, kwargs) -> tuple[list[Any], Dict[str, Any]]:
                new_args = []
                for i, arg in enumerate(args):
                    cls = self.arg_spec_args[i]
                    arg = self.get_arg_from_cls(cls=cls, arg=arg)
                    new_args.append(arg)
                new_kwargs = {}
                for kw, arg in kwargs.items():
                    cls = self.arg_spec_kwargs[kw]
                    new_kwargs[kw] = self.get_arg_from_cls(cls=cls, arg=arg)
                return new_args, new_kwargs

            @functools.wraps(f)
            def delay(self, *args, _priority: int | None = None, _eta: datetime.datetime | None = None, **kwargs) -> TaskModel:
                if _priority is None:
                    with task_priority_context() as task_priority:
                        _priority = task_priority
                # priority has to be negated, needed for fixing ascending sort order
                tm = self.make_task_model(args, kwargs, priority=_priority * -1, eta=_eta)
                with delay_tasks_context() as delay:
                    if delay:
                        tm = TaskScheduler.schedule(tm)
                    else:
                        self.run(*args, **kwargs)

                # IDEA: It could be possible to run worker execute with generated task during tests
                return tm

            @functools.wraps(f)
            def run(self, *args, **kwargs):
                args, kwargs = self.restore_original_types(args, kwargs)
                return self.func(*args, **kwargs)

            def make_task_model(self, args, kwargs, priority, eta) -> TaskModel:
                with namespace_context() as namespace:
                    params = dict(
                        task=self.func_name,
                        args=args,
                        kwargs=kwargs,
                        priority=priority,
                        store_result=store_result,
                        retry=retry,
                        max_retries=max_retries,
                        error_expires=error_expires,
                        result_expires=result_expires,
                        namespace=kwargs['namespace'] if "namespace" in kwargs else namespace
                    )
                    if eta is not None:
                        if eta.tzinfo is None:
                            eta.replace(tzinfo=datetime.timezone.utc)
                        params["eta"] = eta

                    if is_unique:
                        unique_key = unique_key_generator(*args, **kwargs)
                        params |= dict(unique_key=unique_key)

                return TaskModel.parse_obj(params)

        return EventixTask()

    return inner
