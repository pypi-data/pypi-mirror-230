import os
from abc import ABCMeta
from typing import Optional
from collections.abc import Callable
import asyncio
import uuid
from concurrent.futures import ThreadPoolExecutor
from navconfig import config
from navconfig.logging import logging
from navigator.types import WebApp
from navigator.applications.base import BaseApplication
from .responses import TriggerResponse
from ..actions import AbstractAction


class BaseHook(metaclass=ABCMeta):
    # Signal for startup method for this Hook (useful for starting connections)
    on_startup: Optional[Callable] = None
    on_shutdown: Optional[Callable] = None

    """BaseHook.

        Base class for all Triggers in FlowTask.
    """
    def __init__(self, *args, actions: list = None, **kwargs):
        self.trigger_id = kwargs.pop('id', uuid.uuid4())
        # self.description = description
        self._args = args
        self._kwargs = kwargs
        self.app: WebApp = None
        self.logger = logging.getLogger(
            f"Hooks.{self.__class__.__name__}"
        )
        self._response: TriggerResponse = None
        self._environment = config
        self._actions: list[AbstractAction] = actions

    def setup(self, app: WebApp) -> None:
        """setup.

            Configuration of Trigger when started.
        Args:
            app (aiohttp.web.Application): Web Application.
        """
        if isinstance(app, BaseApplication):  # migrate to BaseApplication (on types)
            self.app = app.get_app()
        elif isinstance(app, WebApp):
            self.app = app  # register the app into the Extension
        else:
            raise TypeError(
                f"Invalid type for Application Setup: {app}:{type(app)}"
            )
        # startup operations over extension backend
        if callable(self.on_startup):
            app.on_startup.append(self.on_startup)

        if callable(self.on_shutdown):
            app.on_shutdown.append(self.on_shutdown)

    def get_env_value(self, key, default: str = None):
        if val := os.getenv(key):
            return val
        elif val := self._environment.get(key, default):
            return val
        else:
            return key

    def add_action(self, action: AbstractAction):
        self._actions.append(action)

    async def run_actions(self, *args, **kwargs):
        result = None
        if self._actions:
            for action in self._actions:
                try:
                    result = await action.run(*args, **kwargs)
                finally:
                    await action.close()
            return result
        else:
            logging.warning(
                f'Trigger {self.__class__.__name__}: No actions were found to be executed.'
            )

    def call_actions(self):
        # Run the actions in a thread pool
        _new = False
        try:
            loop = asyncio.get_event_loop()
            _new = False
        except RuntimeError:
            loop = asyncio.new_event_loop()
            _new = True
        try:
            with ThreadPoolExecutor() as executor:
                future = executor.submit(
                    loop.run_until_complete, self.run_actions())
                future.result()
        finally:
            if _new is True:
                loop.stop()
