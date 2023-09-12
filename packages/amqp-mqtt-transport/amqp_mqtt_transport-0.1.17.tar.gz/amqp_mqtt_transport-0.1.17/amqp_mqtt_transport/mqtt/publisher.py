from amqp_mqtt_transport.abc import Publisher
from . import MQTTController
import logging

__all__ = ['MQTTPublisher']
logger = logging.getLogger(__name__)


class MQTTPublisher(Publisher):
    def __init__(self, controller: MQTTController):
        self.__controller = controller

    @property
    def queue_name(self) -> str:
        return self.__queue_name

    async def setup_exchange(self, queue_name: str):
        self.__queue_name = queue_name

    async def publish(self, body: bytes):
        try:
            await self.__controller.publish(self.__queue_name, body)
            logger.info(f"Succesfully published message to topic={self.queue_name}")
        except Exception as e:
            logger.error(e, exc_info=True)
            logger.error(f"Failed publish message to topic={self.queue_name}")
