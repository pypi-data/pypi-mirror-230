from types import TracebackType
from typing import Type
from heaobject.activity import DesktopObjectAction, Status
from heaobject.user import NONE_USER
from heaobject.root import Share, ShareImpl, Permission, DesktopObject
from heaserver.service.oidcclaimhdrs import SUB
from aiohttp.web import Request, Application

from .messagebroker import publish_desktop_object
from typing import Any
from abc import ABC
from collections.abc import Iterable, Callable, Awaitable
from contextlib import AbstractAsyncContextManager
import logging


def default_shares(request: Request) -> tuple[ShareImpl]:
    """
    Default shares are NONE_USER and VIEWER permission.
    """
    share = ShareImpl()
    share.user = request.headers.get(SUB, NONE_USER)
    share.permissions = [Permission.VIEWER]
    return (share,)


class DesktopObjectActionLifecycle(AbstractAsyncContextManager[DesktopObjectAction | None], ABC):
    """
    Abstract base class for querying a database for desktop objects, generating
    desktop object actions, and putting the actions on the message queue.
    """

    def __init__(self, request: Request,
                 code: str,
                 description: str,
                 user_id: str | None = None,
                 shares: Iterable[Share] | None = None,
                 activity_cb: Callable[[Application, DesktopObjectAction], Awaitable[None]] | None = None) -> None:
        if code is None:
            raise ValueError('code cannot be None')
        if description is None:
            raise ValueError('description cannot be None')
        if not isinstance(request, Request):
            raise TypeError(f'request must be a Request but was a {type(request)}')
        self.__request = request
        self.__code = str(code)
        self.__description = str(description)
        self.__activity: DesktopObjectAction | None = None
        self.__user_id = str(user_id) if user_id is not None else request.headers.get(SUB, NONE_USER)
        self.__shares = list(shares) if shares is not None else list(default_shares(request))
        if any(not isinstance(share, Share) for share in self.__shares):
            raise ValueError(f'shares must all be Share objects but were {", ".join(set(str(type(share)) for share in self.__shares))}')
        self.__activity_cb: Callable[[Application, DesktopObjectAction], Awaitable[None]] | None = activity_cb


    async def __aenter__(self) -> DesktopObjectAction:
        self.__activity = DesktopObjectAction()
        self.__activity.generate_application_id()
        self.__activity.code = self.__code
        self.__activity.owner = NONE_USER
        self.__activity.shares = self.__shares
        self.__activity.user_id = self.__user_id
        self.__activity.description = self.__description
        if self.__activity_cb:
            await self.__activity_cb(self.request.app, self.__activity)

        self.__activity.status = Status.IN_PROGRESS
        if self.__activity_cb:
            await self.__activity_cb(self.request.app, self.__activity)

        return self.__activity

    async def __aexit__(self, exc_type: Type[BaseException] | None,
                        exc_value: BaseException | None,
                        traceback: TracebackType | None) -> Any:
        if exc_type is not None:
            self.__activity.status = Status.FAILED
        elif self.__activity.status not in (Status.SUCCEEDED, Status.FAILED):
            if exc_type is None:
                self.__activity.status = Status.SUCCEEDED
            else:
                self.__activity.status = Status.FAILED
        if self.__activity_cb:
            await self.__activity_cb(self.request.app, self.__activity)

    @property
    def request(self) -> Request:
        return self.__request

def augment_desktop_object_action_for_get(action: DesktopObjectAction, request: Request, volume_id: str, obj: DesktopObject):
    action.old_object_id = obj.id
    action.old_object_type_name = obj.type
    action.old_volume_id = volume_id
    action.old_object_uri = request.url
    action.old_object_created = obj.created
    action.old_object_modified = obj.modified
    action.new_object_id = obj.id
    action.new_object_type_name = obj.type
    action.new_volume_id = volume_id
    action.new_object_uri = request.url
