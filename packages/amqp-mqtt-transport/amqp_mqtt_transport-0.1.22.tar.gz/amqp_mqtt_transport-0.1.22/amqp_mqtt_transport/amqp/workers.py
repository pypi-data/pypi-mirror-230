import aio_pika
import abc
import asyncio
import logging
import aiormq
import signal
from typing import List, Dict, Awaitable
from amqp_mqtt_transport.amqp import BindingsParams, ConnectionParams, AMQPController, AMQPConsumer
from functools import lru_cache

__all__ = ['Workforce', 'Worker']
logger = logging.getLogger(__name__)

class Worker(abc.ABC):
    """Abstract worker class that should be inherited when creating custom workers,
    override methods setup_queue to setup queue and on_message for actions on recieving message
    """
    
    @abc.abstractmethod
    async def setup_worker(self, channel: aio_pika.abc.AbstractChannel):
        """ Abstract method used to setup queue and exchange for it and bind them\n
         Channel that can be recived beforehand from connection_controller.\n
         Before method exit, call self._setup_queue()"""
        ...
        
    async def _setup_queue(self, channel: aio_pika.abc.AbstractChannel, binding_params: BindingsParams, **kwargs):
        # can accept kwargs to pass them to AbstractQueue.consume()
        self._consumer = AMQPConsumer(channel)
        self._consumer.set_up_binding_params(binding_params)
        await self._consumer.create_queue()
        await self._consumer.subscribe(self.on_message, **kwargs)

    @abc.abstractmethod
    async def on_message(self, message: aio_pika.IncomingMessage):
        """Handler for messages recieved from amqp

        Args:
            message (aio_pika.IncomingMessage): Amqp message, should be acknoledged or not acknoledged before method return
        """
        ...
    

class Workforce():

    def __init__(self, amqp_connection_params : ConnectionParams) -> None:
        self._amqp_controller = AMQPController(amqp_connection_params)
        self._workers : List[Worker] = []
        self._supervisor : Dict[Worker, Awaitable] = {}
        self._stop_flag: bool = False
    
    @lru_cache
    def __repr__(self) -> str:
        unique_classes = []
        for worker in self._workers:
            if worker.__class__.__name__ not in unique_classes:
                unique_classes.append(worker.__class__.__name__)
        return f"[{self.__class__.__name__}] with workers {unique_classes}"
   
    def add_worker(self, worker : Worker):
        self._workers.append(worker)
    
    async def _rally_workers(self, channel):
        for worker in self._workers:
            await worker.setup_worker(channel)
            
    async def stop(self):
        logger.debug(f"|{self}| Stopping...")
        await self._channel.close()
        self._stop_flag = True
    
    async def run_loop(self):
        while not self._stop_flag:
            await asyncio.sleep(1)
            
    async def shutdown(self, sig : signal.Signals, loop):
        logger.info(f'Workforce caught {sig.name} signal')
        await self.stop()
        tasks = [task for task in asyncio.all_tasks() if task is not
                asyncio.tasks.current_task()]
        list(map(lambda task: task.cancel(), tasks))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        logger.info('finished awaiting cancelled tasks, results: {0}'.format(results))
        loop.stop()
        
    async def _run(self):
        logger.debug(f"|{self}| Starting...")
        while not self._amqp_controller.connected():
            try:
                await self._amqp_controller.connect()
            except aiormq.exceptions.AMQPConnectionError:
                wait_period_sec = 10
                logger.debug(f"Couldn't connect to rabbitmq broker, sleeping for {wait_period_sec} seconds.")
                await asyncio.sleep(wait_period_sec)
        self._channel = await self._amqp_controller.get_channel()
        await self._channel.set_qos(prefetch_count=10)
        await self._rally_workers(self._channel)
        await self.run_loop()
        logger.debug(f"|{self}| Succesfully stopped.")

    async def start(self):
        """Entry point for class to start its work"""
        loop = asyncio.get_event_loop()
        # setting up termination signals
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda sig=sig: asyncio.ensure_future(self.shutdown(sig, loop)))
        try:
            await self._run()
        except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
            await self.stop()
        # finally:
        #     loop.close()
