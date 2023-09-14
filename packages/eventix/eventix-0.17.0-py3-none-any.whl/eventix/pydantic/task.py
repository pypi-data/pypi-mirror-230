from __future__ import annotations

import datetime
from typing import Any, Dict, Self, Literal

from pydantic import Field
from pydantic_db_backend_common.indexes import SortingIndex, AggregationIndex

from pydantic_db_backend_common.pydantic import BackendModel
from pydantic_db_backend_common.utils import utcnow

task_model_status = Literal["scheduled", "processing", "done", "error", "retry"]


class TaskModel(BackendModel):
    unique_key: str | None = None
    eta: datetime.datetime | None = Field(default_factory=utcnow)
    scheduled: datetime.datetime | None = Field(default_factory=utcnow)
    status: task_model_status | None = "scheduled"
    priority: int | None = 0  # lower value -> higher priority, because of sorting
    namespace: str | None = "default"
    task: str
    args: tuple | None = Field(default_factory=tuple)
    kwargs: Dict[str, Any] | None = Field(default_factory=dict)

    worker_id: str | None = None
    worker_expires: datetime.datetime | None = None

    retry: bool = True
    max_retries: int | None = None  # None forever, positive value gets decremented until 0
    error_eta_inc: int = 15
    error_eta_max: int = 300
    store_result: bool = True

    result: Any = None

    # Expirations will keep the task in the db.
    # If there is one with None it will keep forever.
    # Otherwise the expiration is set to the one with the longest duration
    # depending which ones are applicable.

    error_expires: int | None = None  # keep forever on error
    result_expires: int | None = 604800  # 7 days

    expires: datetime.datetime | None = None

    def unique_update_from(self, task: Self):
        self.eta = min([task.eta, self.eta])
        self.priority = min([task.priority, self.priority])
        self.args = task.args
        self.kwargs = task.kwargs

        self.status = task.status  # from retry to scheduled
        self.error_eta_inc: task.error_eta_inc  # reset retry inc


    class Config:
        backend_indexes = [
            SortingIndex("priority_eta", [{"priority": "asc"}, {"eta": "asc"}]),
            AggregationIndex("status_sum", {"status": "_sum"})
        ]

    # sort order
    # priority-, eta-

    # 9    0
    # 9    1
    # 9    2
    # 9    3
    # 8    1
    # 8    2
    # 5    4
