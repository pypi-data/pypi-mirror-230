
import logging
import typing
import amqp_mqtt_transport.abc
import asyncio

__all__ = ['MessageSheduler']
logger = logging.getLogger(__name__)


class ScheduledPublisherWrapper(typing.NamedTuple):
    """Basic data struct to hold ScheduledPublisher instance with future assigned to it"""
    id: str
    scheduled_publisher: amqp_mqtt_transport.ScheduledPublisher
    task: asyncio.Task


class MessageSheduler():
    """Class manager for list of amqp_controller.ScheduledPublisher
    """

    def __init__(self) -> None:
        self._publishers: typing.Dict[str, ScheduledPublisherWrapper] = {}

    async def add_sheduled_publisher(self, id: str,
                                     messages: typing.List[typing.Dict],
                                     interval_seconds: float,
                                     publisher: amqp_mqtt_transport.abc.Publisher,
                                     delay_seconds: float = 0,
                                     stop_after_n_runs: int = -1):
        if id in self._publishers:
            logger.error(f'Publisher with id={id} already exists')
            return
        sh_publisher = amqp_mqtt_transport.ScheduledPublisher(publisher)
        for msg in messages:
            sh_publisher.add_message_to_list(msg)
        sh_publisher.interval_seconds = interval_seconds
        sh_publisher.sleep(delay_seconds)
        if stop_after_n_runs >= 0:
            sh_publisher.stop_after_n_runs = stop_after_n_runs
        task = asyncio.create_task(sh_publisher.run())
        sch_wrapper = ScheduledPublisherWrapper(id, sh_publisher, task)
        self._publishers[id] = sch_wrapper

        logger.debug(f"Created scheduled publisher with id={id}, queue_name={publisher.queue_name}")

    async def run(self):
        while len(self._publishers):
            for id, sch_wrapper in self._publishers.items():
                if not sch_wrapper.task.cancelled():
                    logger.debug(f'scheduled publisher with id={id} is alive')
                else:
                    logger.warning(f'scheduled publisher with id={id} was canceled')
            await asyncio.sleep(60 * 10)
