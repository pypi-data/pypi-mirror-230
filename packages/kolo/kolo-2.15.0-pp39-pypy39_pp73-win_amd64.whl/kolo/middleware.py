from __future__ import annotations

import logging
import os
import sys
import threading
from typing import Awaitable, Callable

from asgiref.sync import iscoroutinefunction
from django.conf import settings
from django.http import HttpRequest, HttpResponse

from .config import load_config
from .db import setup_db
from .profiler import KoloProfiler
from .serialize import monkeypatch_queryset_repr

logger = logging.getLogger("kolo")

DjangoView = Callable[[HttpRequest], HttpResponse]
DjangoAsyncView = Callable[[HttpRequest], Awaitable[HttpResponse]]


class KoloMiddleware:
    sync_capable = True
    async_capable = True

    def __init__(self, get_response: DjangoView | DjangoAsyncView) -> None:
        self._is_coroutine = iscoroutinefunction(get_response)
        self._get_response = get_response
        self.config = load_config()
        self.enabled = self.should_enable()
        if self.enabled:
            self.db_path = setup_db(wal_mode=self.config.get("wal_mode", True))

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if self._is_coroutine:
            get_response = self.aget_response
        else:
            get_response = self.get_response  # type: ignore

        # WARNING: Because Django's runserver uses threading, we need
        # to be careful about thread safety here.
        if not self.enabled or self.check_for_third_party_profiler():
            return get_response(request)  # type: ignore

        filter_config = self.config.get("filters", {})
        ignore_request_paths = filter_config.get("ignore_request_paths", [])
        for path in ignore_request_paths:
            if path in request.path:
                return get_response(request)  # type: ignore

        # Don't store the KoloProfiler on self to avoid threadsafety
        # bugs. If a different thread gets this instance of KoloProfiler
        # at the wrong time, we lose the original profiler's trace.
        profiler = KoloProfiler(
            self.db_path, config=self.config, source="kolo.middleware.KoloMiddleware"
        )

        monkeypatch_queryset_repr()
        if self._is_coroutine:
            return self.aprofile_response(request, profiler)
        else:
            return self.profile_response(request, profiler)

    def profile_response(self, request, profiler):
        with profiler:
            response = self.get_response(request)
        self.save_trace(profiler)
        return response

    async def aprofile_response(self, request, profiler):
        with profiler:
            response = await self.aget_response(request)
        self.save_trace(profiler)
        return response

    async def aget_response(self, request: HttpRequest) -> HttpResponse:
        response = await self._get_response(request)  # type: ignore
        return response

    def get_response(self, request: HttpRequest) -> HttpResponse:
        response = self._get_response(request)
        return response  # type: ignore

    @staticmethod
    def save_trace(profiler):
        name = "kolo-save_request_in_db"
        threading.Thread(target=profiler.save_request_in_db, name=name).start()

    def check_for_third_party_profiler(self) -> bool:
        profiler = sys.getprofile()
        if profiler:
            logger.warning("Profiler %s is active, disabling KoloMiddleware", profiler)
            return True
        if self.config.get("threading", False):
            try:
                profiler = threading.getprofile()  # type: ignore[attr-defined]
            except AttributeError:
                profiler = threading._profile_hook
            if profiler:  # pragma: no branch
                logger.warning(
                    "Profiler %s is active, disabling KoloMiddleware", profiler
                )
                return True
        return False

    def should_enable(self) -> bool:
        if settings.DEBUG is False:
            logger.debug("DEBUG mode is off, disabling KoloMiddleware")
            return False

        if os.environ.get("KOLO_DISABLE", "false").lower() not in ["false", "0"]:
            logger.debug("KOLO_DISABLE is set, disabling KoloMiddleware")
            return False

        if self.check_for_third_party_profiler():
            return False

        return True
