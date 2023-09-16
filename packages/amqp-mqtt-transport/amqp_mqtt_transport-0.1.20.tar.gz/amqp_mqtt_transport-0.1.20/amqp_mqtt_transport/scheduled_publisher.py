import amqp_mqtt_transport
import logging
import typing
import asyncio
import json


__all__ = ['ScheduledPublisher']
logger = logging.getLogger(__name__)


class ScheduledPublisher():
    """Class wrapper for publisher that will publish messages to amqp in time intervals
    NOTE: this relies on asyncio task switching to make delays, so it may be inaccurate if there are tasks that holding onto thread
    """
    @property
    def interval_seconds(self) -> float:
        """Interval between publishing

        Returns:
            float: interval
        """
        return self._interval_sec

    @interval_seconds.setter
    def interval_seconds(self, value: float):
        self._interval_sec = value

    def sleep(self, delay_seconds: float):
        self._delay_sec = delay_seconds

    def __init__(self, publisher: amqp_mqtt_transport.abc.Publisher) -> None:
        self._messages: typing.List[bytes] = []
        self._publisher = publisher  # amqp_controller.Publisher(self._amqp_connection)
        self._interval_sec: float = 0
        self.stop_after_n_runs: int = -1

    def add_message_to_list(self, message: typing.Dict):
        """Appends message to list of messages thats going to be published"""

        self._messages.append(json.dumps(message, indent=2).encode('utf-8'))

    def clear_messages_list(self):
        self._messages.clear()

    async def run(self):
        if self.stop_after_n_runs == 0:
            logger.warning("stop_after_n_runs is set to 0 in config, scheduler won't start (remove key/value for infinite)")
            return
        if self._interval_sec <= 0:
            logger.warning("Interval is not set, scheduler won't start")
            return
        if self._delay_sec:
            logger.debug(f"Sleeping for set delay {self._delay_sec}s")
            await asyncio.sleep(self._delay_sec)
            self._delay_sec = 0
        while (True):
            try:
                if self.stop_after_n_runs == 0:
                    logger.info(f"Scheduler finished publishing all messages, stopped.")
                    break
                else:
                    self.stop_after_n_runs -= 1
                for message in self._messages:
                    await self._publisher.publish(message)
            except Exception as e:
                logger.error(e, exc_info=True)
                logger.error(f"Failed to publish")
            await asyncio.sleep(self._interval_sec)
