from typing import Annotated, List, Dict, Any

from fastapi import Body
from pydantic import BaseModel


class PaginationParametersModel(BaseModel):
    skip: int | None = 0
    limit: int | None = 25
    sort: List[Dict] | None = None


class PaginationResultModel(PaginationParametersModel):
    data: Any
    max_results: int | None = 0


async def dep_pagination_parameters(
    skip: Annotated[int, Body()] = None,
    limit: Annotated[int, Body()] = None,
    sort: Annotated[List[Dict], Body()] = None
):
    return PaginationParametersModel(
        skip=skip,
        limit=limit,
        sort=sort,
    )
