import aio_pika
from amqp_mqtt_transport.abc import Publisher
import logging
from . import BindingsParams, QueueParams, ExchangeParams, setup_queue

__all__ = ['AMQPPublisher']
logger = logging.getLogger(__name__)


class AMQPPublisher(Publisher):
    @property
    def queue_name(self) -> QueueParams:
        return self._queue

    @property
    def queue_params(self) -> QueueParams:
        return self._q_param

    @property
    def exchange_params(self) -> ExchangeParams:
        return self._ex_param

    @property
    def routing_key(self) -> str:
        return self._routing_key

    async def setup_queue(self, channel: aio_pika.abc.AbstractChannel, binding_params: BindingsParams):
        self._ex_param = binding_params.exchange_params
        self._q_param = binding_params.queue_params
        self._routing_key = binding_params.routing_key
        # Binding queue and exchange
        self._exchange, self._queue = await setup_queue(binding_params, channel)

    async def publish(self, body: bytes):
        try:
            aio_message = aio_pika.Message(body=body, content_type="text/plain")
            await self._exchange.publish(aio_message, self._routing_key)
            logger.info(f"Succesfully published message to topic={self.queue_name}")
        except Exception as e:
            logger.error(e, exc_info=True)
            logger.error(f"Failed publish message to topic={self.queue_name}")
