import logging

from fastapi import APIRouter

from eventix.exceptions import NoTaskFound
from eventix.functions.task import task_post, task_next_scheduled
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


@router.put("/task/{uid}")
async def route_task_put(uid: str, task: TaskModel) -> TaskModel:
    task.uid = uid  # overwrite uid
    # noinspection PyTypeChecker
    return Backend.put_instance(task)

