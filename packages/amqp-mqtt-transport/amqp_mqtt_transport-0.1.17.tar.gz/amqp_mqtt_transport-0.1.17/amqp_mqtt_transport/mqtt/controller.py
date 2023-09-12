import gmqtt

import logging
import tenacity
import tenacity.stop
import tenacity.wait
import functools
from amqp_mqtt_transport.abc import Controller
import uuid


__all__ = ['MQTTController', 'reconnect']

logger = logging.getLogger(__name__)


def reconnect():
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(manager, *args, **kwargs):
            if not manager.connected():
                await manager.connect()
            try:
                return await func(manager, *args, **kwargs)
            except Exception as e:
                await manager.close()
                raise e
        return wrapped
    return wrapper


class MQTTController(Controller):
    def __init__(self, host: str, port: int,
                 login: str, password: str,
                 ssl: bool):
        self._host = host
        self._port = port
        self._login = login
        self._password = password
        # All methods that exec using _connection should be used with @reconnect decorator, or use property
        self._connection: gmqtt.Client = None  # type: ignore
        self._connected = 0
        self._ssl: bool = ssl

    async def connect(self):
        @tenacity.retry(stop=tenacity.stop.stop_after_attempt(3), wait=tenacity.wait.wait_fixed(3))
        async def wrapper():
            if self._connection is None:
                self._connection = mqtt.Client(str(uuid.uuid1()))
                self._connection.on_connect = self.on_connect
                self._connection.on_message = self.on_message
                self._connection.on_disconnect = self.on_disconnect
                self._connection.on_subscribe = self.on_subscribe
                self._connection.set_auth_credentials(self._login, self._password)
                await self._connection.connect(self._host, self._port)
        try:
            await wrapper()
        except Exception as e:
            logging.error(e, exc_info=True)
            logger.error(f"Failed mqtt broker connection after 3 attempts")

    def on_message(self, client, topic, payload, qos, properties):
        pass

    async def on_connect(self, client, flags, rc, properties):
        logger.info('Connected with mqtt broker')
        self._connected = True

    async def on_disconnect(self, client, packet, exc=None):
        logger.warning(f"Disconnected from mqtt broker")
        self._connected = False

    def on_subscribe(self, client, mid, qos, properties):
        pass

    def connected(self) -> bool:
        return self._connection is not None and self._connected

    async def check_connection(self) -> bool:
        if not self.connected():
            await self.connect()
            return self.connected()
        else:
            return True

    async def close(self):
        if self.connected():
            try:
                await self._connection.disconnect()
            except Exception:
                pass
        self._connection = None  # type: ignore

    @reconnect()
    async def publish(self, queue_name: str, body: bytes):
        self._connection.publish(queue_name, payload=body)
