import logging

from fastapi import APIRouter

from eventix.exceptions import NoTaskFound
from eventix.functions.task import task_post, task_next_scheduled, task_by_unique_key
from eventix.pydantic.task import TaskModel
from pydantic_db_backend.backend import Backend

log = logging.getLogger(__name__)

router = APIRouter(tags=["task"])


@router.post("/task")
async def route_task_post(task: TaskModel) -> TaskModel:
    return task_post(task)


@router.get("/task/{uid}")
async def route_task_get(uid: str) -> TaskModel:
    # noinspection PyTypeChecker
    return Backend.get_instance(TaskModel, uid)


@router.delete("/task/{uid}")
async def route_task_delete(uid: str) -> None:
    return Backend.delete_uid(TaskModel, uid)


@router.get("/task/by_unique_key/{unique_key}")
async def route_task_(unique_key: str) -> TaskModel:
    return task_by_unique_key(unique_key=unique_key)


@router.delete("/task/by_unique_key/{unique_key}")
async def route_task_(unique_key: str) -> None:
    uid = task_by_unique_key(unique_key=unique_key).uid
    return Backend.delete_uid(TaskModel, uid)


@router.put("/task/{uid}")
async def route_task_put(uid: str, task: TaskModel) -> TaskModel:
    task.uid = uid  # overwrite uid
    # noinspection PyTypeChecker
    return Backend.put_instance(task)
