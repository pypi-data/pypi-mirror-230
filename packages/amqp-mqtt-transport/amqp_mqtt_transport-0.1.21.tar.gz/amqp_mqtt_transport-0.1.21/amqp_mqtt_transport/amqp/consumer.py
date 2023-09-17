from . import AMQPController, BindingsParams, QueueParams, ExchangeParams, setup_queue
import typing
import logging
import aio_pika
from amqp_mqtt_transport.abc import Consumer

__all__ = ['AMQPConsumer']
logger = logging.getLogger(__name__)


class AMQPConsumer(Consumer):
    def __init__(self, channel: typing.Union[aio_pika.abc.AbstractChannel, None]):
        self._channel = channel

    @property
    def queue_name(self) -> str:
        return self._binding_params.queue_params.name

    @property
    def queue_params(self) -> QueueParams:
        return self._binding_params.queue_params

    @property
    def exchange_params(self) -> ExchangeParams:
        return self._binding_params.exchange_params

    @property
    def routing_key(self) -> str:
        return self._binding_params.routing_key

    def set_up_binding_params(self, binding_params: BindingsParams):
        self._binding_params = binding_params

    async def create_queue(self):
        if self._binding_params is None:
            raise ValueError(
                'Configuration needed to setup queue is not exist, call set_up_binding_params(BindingsParams) with queue configuration')
        if self._channel is None:
            raise ValueError(
                'Channel is not set')
        # Binding queue and exchange
        self._exchange, self._queue = await setup_queue(self._binding_params, self._channel)

    async def replace_channel(self, channel: aio_pika.abc.AbstractChannel):
        if channel is not None:
            await self._channel.close()
        self._channel = channel
        self._queue.channel = self._channel.channel
        # await self.create_queue()
        # await self.subscribe(self._message_handler)

    async def subscribe(self, message_handler: typing.Callable, **kwargs):
        # can accept kwargs to pass them to AbstractQueue.consume()
        self._message_handler = message_handler
        await self._queue.consume(self._message_handler, **kwargs)
