import logging
from typing import List, Annotated

from fastapi import APIRouter, Body, Depends

from eventix.exceptions import NoTaskFound
from eventix.functions.task import task_post, task_next_scheduled, tasks_by_status
from eventix.pydantic.pagination import dep_pagination_parameters, PaginationParametersModel, PaginationResultModel
from eventix.pydantic.task import TaskModel
from pydantic_db_backend.backend import Backend

log = logging.getLogger(__name__)

router = APIRouter(tags=["tasks"])


@router.get("/tasks/next_scheduled")
async def route_tasks_next_scheduled_get(worker_id: str, namespace: str) -> TaskModel:
    t = task_next_scheduled(worker_id, namespace)
    if t is None:
        raise NoTaskFound(namespace=namespace)
    return t


class RouterTasksByStatusResponseModel(PaginationResultModel):
    data: List[TaskModel]


@router.put("/tasks/by_status")
async def router_tasks_by_status_put(
    status: Annotated[str, Body()] = None,
    namespace: Annotated[str, Body()] = None,
    pagination: PaginationParametersModel = Depends(dep_pagination_parameters)
) -> RouterTasksByStatusResponseModel:
    data, max_results = tasks_by_status(
        status=status,
        namespace=namespace,
        pagination=pagination
    )
    return RouterTasksByStatusResponseModel(
        data=data,
        max_results=max_results,
        **pagination.dict()
    )
