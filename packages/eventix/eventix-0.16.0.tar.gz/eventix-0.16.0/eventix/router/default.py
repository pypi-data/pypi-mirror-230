import logging

from fastapi import APIRouter

from eventix.functions.tools import version

log = logging.getLogger(__name__)

router = APIRouter(prefix="")


@router.get("/healthz")
async def router_healthz_get():
    return {"status": "healthy"}


@router.get("/version")
async def router_version_get():
    return {"version": version()}
