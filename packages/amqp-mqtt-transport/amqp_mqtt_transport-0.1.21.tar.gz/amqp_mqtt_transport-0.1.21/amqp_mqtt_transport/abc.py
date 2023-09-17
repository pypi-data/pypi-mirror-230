import abc
import typing

__all__ = ['Controller']


class Controller(abc.ABC):
    @abc.abstractmethod
    async def connect(self, *args, **kwargs) -> typing.Awaitable: ...

    @abc.abstractmethod
    def connected(self) -> typing.Awaitable[bool]: ...

    @abc.abstractmethod
    async def check_connection(self) -> typing.Awaitable[bool]: ...

    @abc.abstractmethod
    async def close(self) -> typing.Awaitable: ...

    @abc.abstractmethod
    def on_connect(self) -> None: ...

    @abc.abstractmethod
    def on_disconnect(self) -> None: ...


class Publisher(abc.ABC):
    @property
    @abc.abstractmethod
    def queue_name(self) -> str: ...

    @abc.abstractmethod
    async def publish(self, body: bytes) -> typing.Awaitable: ...


class Consumer(abc.ABC):
    @property
    @abc.abstractmethod
    def queue_name(self) -> str: ...

    @abc.abstractmethod
    async def subscribe(self, body: bytes) -> typing.Awaitable: ...
