import datetime
from typing import List, Any

from pydantic import Field, BaseModel

from pydantic_db_backend_common.pydantic import BackendModel


class Schedule(BackendModel):
    schedule: str
    task: str
    name: str | None = None
    args: List[Any] | None = Field(default_factory=list)
    kwargs: dict | None = Field(default_factory=dict)
    last_schedule: datetime.datetime | None = None
    next_schedule: datetime.datetime | None = None
    priority: int | None = 0

    def __init__(__pydantic_self__, **data: Any) -> None:
        if "name" not in data:
            data["name"] = data["task"]
        super().__init__(**data)
