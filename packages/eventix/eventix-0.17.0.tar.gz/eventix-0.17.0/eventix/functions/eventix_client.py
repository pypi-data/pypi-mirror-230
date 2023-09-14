from __future__ import annotations

from typing import Any

import requests
from requests import Session, Response

import logging

log = logging.getLogger(__name__)


# class EventixClientSession(Session):
#     def __init__(self, base_url: str = None) -> None:
#         self.base_url = base_url
#         self.keep_alive = False
#         super().__init__()
#
#     def request(
#         self,
#         method: str | bytes,
#         url: str | bytes,
#         *args,
#         **kwargs
#     ) -> Response:  # pragma: no cover
#         # kwargs['headers'] = kwargs.get('headers', {}) | {"Connection": "close"}
#         return super().request(
#             method,
#             f"{self.base_url}{url}",
#             *args,
#             **kwargs
#         )

class EventixClientSession(Session):
    def __init__(self, base_url: str = None) -> None:
        self.base_url = base_url
        super().__init__()

    def request(
        self,
        method,
        url,
        *args,
        **kwargs
    ) -> Response:  # pragma: no cover
        return requests.request(
            method,
            f"{self.base_url}{url}",
            *args,
            **kwargs
        )


def get_session():
    s = EventixClientSession()
    s.headers["Connection"] = "close"
    return s


class EventixClient:
    # interface: Any | None = EventixClientSession()
    interface: Any | None = get_session()
    namespace: str | None = None

    @classmethod
    def set_base_url(cls, base_url):
        if isinstance(cls.interface, EventixClientSession):
            log.info(f"Setting EventixClient base_url: {base_url}")
            cls.interface.base_url = base_url
