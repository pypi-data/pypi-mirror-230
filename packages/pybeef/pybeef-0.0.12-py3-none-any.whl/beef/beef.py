import functools
import contextvars
import contextlib
import uuid
from enum import Enum
import inspect
import json
from typing import Callable, Awaitable, Any, Optional, NoReturn, Tuple, List, Dict
import aio_pika
import aiormq
import sys
import asyncio
from .pool import Pool

AsyncFunction = Callable[..., Awaitable[Any]]
TaskID = str

class TaskNotFoundError(RuntimeError):
    pass

class TaskCanceledError(RuntimeError):
    pass

class TaskFailedError(RuntimeError):
    pass


class State(Enum):
    def __new__(cls, value, is_final=False):
        self = object.__new__(cls)
        self._value_ = value
        self._name_ = value
        self.is_final = is_final
        return self

    WORKING  = ('WORKING', False)
    SUCCESS  = ('SUCCESS', True)
    FAILURE  = ('FAILURE', True)
    CANCELED = ('CANCELED', True)

FINAL_STATES = { e.value for e in State if e.is_final }

class Status:
    def __init__(self, task_id: TaskID, state: State, body: Any = None):
        self.task_id = task_id
        self.state = state
        self.body = body

    @property
    def is_final(self):
        return self.state.is_final

    def __repr__(self):
        return f'Status({self.task_id}, {self.state}, {self.body})'

    @classmethod
    def success(self, task_id: TaskID, result: Any):
        return Status(task_id, State.SUCCESS, result)

    @classmethod
    def failure(self, task_id: TaskID, error: Optional[str] = None):
        return Status(task_id, State.FAILURE, error)

    @classmethod
    def canceled(self, task_id: TaskID, message: Optional[str] = None):
        return Status(task_id, State.CANCELED, message)

    @classmethod
    def progress(self, task_id: TaskID, steps: int, progress=0, message: Optional[str] = None):
        body = {
            'steps': steps,
            'progress': progress,
        }
        if message is not None:
            body['message'] = message
        return Status(task_id, State.WORKING, body)

def beef(*av, **kw) -> 'Beef':
        if len(av) == 1 and len(kw) == 0 and inspect.isfunction(av[0]):
            # direct wrapper: @beef
            fn = av[0]
            return functools.wraps(fn)(Beef(fn))
        elif len(av) == 0:
            # wrapper with arguments: @beef(queue_name="foo")
            def wrapper(fn: AsyncFunction):
                return functools.wraps(fn)(Beef(fn, **kw))
            return wrapper
        else:
            raise ValueError('@beef decorator only accepts keyword arguments. E.g. @beef, or @beef(queue_name="foo")')


DEFAULT_REPLY_EXPIRATION_MILLIS = 1000 * 60 * 30  # 30 minutes

class Beef:
    def __init__(self,
        fn: AsyncFunction,
        *,
        queue_name: Optional[str] = None,
        reply_expiration_millis = DEFAULT_REPLY_EXPIRATION_MILLIS,
        fast_forward_limit=1000,
    ):
        if not inspect.iscoroutinefunction(fn):
            raise ValueError('beef can only wrap async functions')
        self.fn = fn
        self._pool = contextvars.ContextVar('pool')
        self._task_id = contextvars.ContextVar('task_id')
        self._queue_name = queue_name
        self._reply_expiration_millis = reply_expiration_millis
        self._fast_forward_limit = fast_forward_limit

    @property
    def name(self) -> str:
        if self._queue_name is None:
            self._queue_name = inspect.getmodule(self.fn).__name__ + '.' + self.fn.__name__
        return self._queue_name

    @name.setter
    def name(self, value) -> None:
        self._queue_name = value

    @contextlib.contextmanager
    def with_name(self, new_name) -> None:
        old_name = self.name
        self.name = new_name
        try:
            yield
        finally:
            self.name = old_name

    async def __call__(self, *av, **kaw) -> Any:
        return await self.fn(*av, **kaw)

    async def submit(self, *av, **kw) -> TaskID:
        '''
        Submit a task to be executed in background

        This method requires active connection. see :meth:`connect`.

        :param av: positional arguments
        :param kw: keyword arguments

        :return: task id
        '''
        async with self._acquire_channel() as channel:
            await channel.declare_queue(self.name, durable=True)
            task_id = str(uuid.uuid4())
            await channel.declare_queue(task_id, durable=True, arguments={'x-expires': self._reply_expiration_millis})
            await self._set_status(channel, Status.progress(task_id=task_id, steps=0, progress=-1))
            await channel.default_exchange.publish(
                _work_request_to_message(task_id, *av, **kw),
                routing_key=self.name,
            )
            return task_id

    async def get_status(self, *, task_id: Optional[TaskID] = None) -> Status:
        '''
        Get status of a task (fast)
        '''
        if task_id is None:
            task_id = self._get_task_id()

        async with self._acquire_channel() as channel, self._acquire_reply_queue(channel, task_id) as queue:
            last = None
            for _ in range(self._fast_forward_limit):
                msg = await queue.get(fail=False, no_ack=False)
                if msg is None:
                    break
                if last:
                    await last.ack()
                last = msg
                if msg.headers.get('x-state') in FINAL_STATES:
                    break
            else:
                raise RuntimeError('fast forward limit exceeded')

            if last is None:
                raise TaskNotFoundError(f'task {task_id} not found')

            await last.nack()
            return _message_to_status(last)

    async def set_progress(self, *, task_id: Optional[TaskID] = None, steps: int, progress: int = 0, message: Optional[str] = None) -> None:
        '''
        Set progress of a task.

        :param task_id: task id - can be omitted if called from withing the worker function
        :param steps: total number of steps
        :param progress: progress of the task
        :param message: optional string describing progress
        '''
        if task_id is None:
            task_id = self._get_task_id()
        status = Status.progress(task_id=task_id, steps=steps, progress=progress, message=message)
        async with self._acquire_channel() as channel:
            await self._set_status(channel, status)

    async def cancel(self, *, task_id: Optional[TaskID] = None, message: Optional[str] = None) -> None:
        '''
        Cancel a task

        :param task_id: task id - can be omitted if called from within the worker function
        :param message: optional message of the cancellation reason
        '''
        if task_id is None:
            task_id = self._get_task_id()
        status = Status.canceled(task_id=task_id, message=message)
        async with self._acquire_channel() as channel:
            await self._set_status(channel, status)

    async def cleanup(self, *, task_id: Optional[TaskID] = None) -> None:
        '''
        Cleanup resources

        :param task_id: task id - can be omitted if called from within the worker function
        '''
        if task_id is None:
            task_id = self._get_task_id()
        async with self._acquire_channel() as channel:
            queue = await channel.declare_queue(task_id, durable=True, arguments={'x-expires': self._reply_expiration_millis})
            await queue.delete(if_empty=False, if_unused=False)

    async def result(self, *, task_id: Optional[TaskID] = None) -> Any:
        '''
        Get result of a task (blocks)

        :param task_id: task id - can be omitted if called from within the worker function
        '''
        if task_id is None:
            task_id = self._get_task_id()
        async with self._acquire_channel() as channel, self._acquire_reply_queue(channel, task_id) as queue:
            last = None
            async with queue.iterator(no_ack=False) as queue_iter:
                async for msg in queue_iter:
                    if last:
                        await last.ack()
                    last = msg
                    if msg.headers.get('x-state') in FINAL_STATES:
                        await msg.nack()
                        break

            status = _message_to_status(msg)
            if status.state == State.CANCELED:
                raise TaskCanceledError(f'task {task_id} was canceled with message {status.body}')
            if status.state == State.FAILURE:
                raise TaskFailedError(f'task {task_id} failed with remote exception {status.body}')
            if status.state == State.SUCCESS:
                return status.body
            raise RuntimeError(f'Unexpected final state {status}')

    async def serve(self) -> NoReturn:
        '''
        Worker that executes the task.

        This call block forever, waiting for incoming requests.
        '''
        while True:
            with contextlib.suppress(asyncio.TimeoutError):
                # need this loop with timeout and suppressed TimeoutError, because
                # queue iterator does not exit on connection/channel close
                # we want this loop to break if connection to AMQP server is lost, hence
                # the looping with timeout hack
                async with self._acquire_channel() as channel:
                    await channel.set_qos(prefetch_count=1)
                    queue = await channel.declare_queue(self.name, durable=True)
                    async with queue.iterator(no_ack=False, timeout=10) as queue_iter:
                        async for msg in queue_iter:
                            try:
                                task_id, av, kw = _message_to_work_request(msg)
                                self._task_id.set(task_id)
                                result = await self.fn(*av, **kw)
                                status = Status.success(task_id=task_id, result=result)
                            except Exception as e:
                                import traceback
                                traceback.print_exc(file=sys.stderr)
                                status = Status.failure(task_id=task_id, error=repr(e))
                            finally:
                                self._task_id.set(None)

                            await self._set_status(channel, status)
                            await msg.ack()

    @contextlib.asynccontextmanager
    async def connect(self, url: str, max_channels=10) -> Pool:
        '''
        Opens a (single) connection to AMQP server at :url: and creates a pool of channels
        '''
        connection = await aio_pika.connect(url)
        async with connection:
            pool = Pool(connection, max_items=max_channels)
            async with pool:
                async with self.pool(pool):
                    yield pool

    @contextlib.asynccontextmanager
    async def pool(self, pool: Pool) -> None:
        '''
        Uses external connection pool. Can be used to share a single connection among several workers.

        Example:
        connection = await aio_pika.connect(url)
        async with connection:
            pool = Pool(connection, max_items=max_channels)

        '''
        if self._pool.get(None) is not None:
            raise RuntimeError('Connection context is already present')
        self._pool.set(pool)
        try:
            yield pool
        finally:
            self._pool.set(None)

    @contextlib.asynccontextmanager
    async def _acquire_channel(self) -> aio_pika.abc.AbstractRobustChannel:
        pool = self._pool.get(None)
        if pool is None:
            raise RuntimeError('Connection context is missing. Did you forget to wrap this call in "async with beef.connect(...)"?')
        async with pool.acquire() as channel:
            yield channel

    @contextlib.asynccontextmanager
    async def _acquire_reply_queue(self, channel: aio_pika.abc.AbstractRobustChannel, task_id: TaskID) -> aio_pika.abc.AbstractQueue:
        await channel.set_qos(prefetch_count=1000)
        try:
            queue = await channel.declare_queue(task_id, passive=True)
            yield queue
        except aiormq.exceptions.ChannelNotFoundEntity as e:
            raise TaskNotFoundError(f'Task "{task_id}" not found')

    def _get_task_id(self) -> TaskID:
        task_id = self._task_id.get(None)
        if task_id is None:
            raise RuntimeError('Could not find task_id in the context. You can only omit task_id parameter when calling this method from worker function.')
        return task_id

    @staticmethod
    async def _set_status(channel, status: Status) -> None:
        await channel.default_exchange.publish(
            _status_to_message(status),
            routing_key=status.task_id,
        )

def _status_to_message(status) -> aio_pika.Message:
    return aio_pika.Message(
        body=json.dumps(status.body).encode(),
        headers={
            'content-type': 'application/json',
            'x-task-id': status.task_id,
            'x-state': status.state.value,
        },
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
    )


def _message_to_status(message: aio_pika.Message) -> Status:
    return Status(
        task_id=message.headers.get('x-task-id'),
        state=State(message.headers.get('x-state')),
        body=json.loads(message.body.decode()),
    )

def _work_request_to_message(task_id: TaskID, *av, **kw) -> aio_pika.Message:
    return aio_pika.Message(
        body=json.dumps(dict(av=av, kw=kw)).encode(),
        headers={
            'content-type': 'application/json',
            'x-task-id': task_id,
        },
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
    )

def _message_to_work_request(message: aio_pika.Message) -> Tuple[TaskID, List, Dict]:
    task_id = message.headers.get('x-task-id')
    body = json.loads(message.body.decode())
    return task_id, body['av'], body['kw']
