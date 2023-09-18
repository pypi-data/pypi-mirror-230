import aio_pika

import logging
import tenacity
import tenacity.stop
import tenacity.wait
import typing
from amqp_mqtt_transport.abc import Controller


__all__ = [
    'AMQPController',
    'ConnectionParams',
    'ExchangeParams',
    'QueueParams',
    'BindingsParams',
    'setup_queue']

logger = logging.getLogger(__name__)


class ConnectionParams(typing.NamedTuple):
    """Data struct to hold parameters needed to initialise amqp connection"""
    login: str
    password: str
    virtual_host: str
    host: str = "localhost"
    port: int = 5672
    ssl: bool = False


class ExchangeParams(typing.NamedTuple):
    """Data struct to hold parameters needed to initialise exchange (PS: add more if needed)"""
    name: str
    auto_delete: bool
    durable: bool
    exchange_type: aio_pika.ExchangeType


class QueueParams(typing.NamedTuple):
    """Data struct to hold parameters needed to initialise queue (PS: add more if needed)"""
    name: str
    auto_delete: bool
    durable: bool
    arguments: typing.Union[typing.Dict[str, typing.Any], None] = None


class BindingsParams(typing.NamedTuple):
    """Basic data struct to hold data needed to init queue and exchange"""
    exchange_params: ExchangeParams
    queue_params: QueueParams
    routing_key: str = ""


class AMQPController(Controller):
    def __init__(self, connection_params: ConnectionParams):
        self._host = connection_params.host
        self._port = connection_params.port
        self._login = connection_params.login
        self._password = connection_params.password
        self._virtual_host = connection_params.virtual_host
        self._ssl: bool = connection_params.ssl
        # All methods that exec using _connection should be used with @reconnect decorator, or use property
        self._connection: aio_pika.abc.AbstractRobustConnection = None  # type: ignore

    async def connect(self):
        @tenacity.retry(stop=tenacity.stop.stop_after_attempt(3), wait=tenacity.wait.wait_fixed(3))
        async def wrapper():
            if self._connection is None:
                self._connection = await aio_pika.connect_robust(
                    host=self._host,
                    port=self._port,
                    login=self._login,
                    password=self._password,
                    virtualhost=self._virtual_host,
                    ssl=self._ssl,
                    reconnect_interval=10
                )
                self.on_connect(self._connection)
                self._connection.close_callbacks.add(self.on_disconnect)
                self._connection.reconnect_callbacks.add(self.on_connect)
        try:
            await wrapper()

        except Exception as e:
            logging.error(e, exc_info=True)
            logger.error(f"Failed amqp broker connection after 3 attempts")

    def connected(self) -> bool:
        return self._connection is not None and self._connection.connected  # type: ignore

    async def check_connection(self) -> bool:
        if not self.connected():
            await self.connect()
            return self.connected()
        else:
            return True

    async def close(self):
        if self.connected():
            try:
                await self._connection.close()
                self.on_disconnect(self._connection, None)
            except Exception:
                pass
        self._connection = None  # type: ignore

    def on_connect(self, connection: aio_pika.abc.AbstractRobustConnection):
        logger.info(f'Connected with amqp broker: {connection}')

    async def on_disconnect(self, connection: aio_pika.abc.AbstractRobustConnection, ex: typing.Union[Exception, None]):
        logger.warning(f"Disconnected from amqp broker: {connection} | {ex or 'No error'}")

    @tenacity.retry(stop=tenacity.stop.stop_after_attempt(3), wait=tenacity.wait.wait_fixed(3))
    async def get_channel(self) -> aio_pika.abc.AbstractChannel:
        chan = await self._connection.channel()
        return chan


async def setup_queue(binding_params: BindingsParams, channel: aio_pika.abc.AbstractChannel) -> typing.Tuple[aio_pika.abc.AbstractExchange, aio_pika.abc.AbstractQueue]:
    ex_param = binding_params.exchange_params
    q_param = binding_params.queue_params
    routing_key = binding_params.routing_key
    exchange = await channel.declare_exchange(name=ex_param.name,
                                              auto_delete=ex_param.auto_delete,
                                              durable=ex_param.durable)
    # Declaring queue
    queue = await channel.declare_queue(name=q_param.name,
                                        auto_delete=q_param.auto_delete,
                                        durable=q_param.durable,
                                        arguments=q_param.arguments)
    # Binding queue and exchange
    try:
        await queue.bind(exchange, routing_key)
    except aio_pika.exceptions.ChannelInvalidStateError:
        pass
        # TODO: uncomment this if program hangs
        # logger.error("Caught channel exception, programm can't continue...")
        # os.kill(os.getpid(), signal.SIGTERM)
    return (exchange, queue)
