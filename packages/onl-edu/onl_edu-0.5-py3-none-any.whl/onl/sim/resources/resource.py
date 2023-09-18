from types import TracebackType
from typing import TYPE_CHECKING, Any, List, Optional, Type

from ..core import BoundClass, Environment, SimTime
from ..events import Process
from .base import Get, Put, BaseResource


class Request(Put):
    """Request usage of the resource. The event is triggered once access is
    granted.

    If the maximum capacity of users has not yet been reached, the request is
    triggered immediately. If the maximum capacity has been reached, the
    request is triggered once an earlier usage request on the resource is
    released.

    """

    resource: 'Resource'

    #: The time at which the request succeeded.
    usage_since: Optional[SimTime] = None

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        super().__exit__(exc_type, exc_value, traceback)
        # Don't release the resource on generator cleanups. This seems to
        # create unclaimable circular references otherwise.
        if exc_type is not GeneratorExit:
            self.resource.release(self)
        return None


class Release(Get):
    """Releases the usage of *resource* granted by request. This event is
    triggered immediately.

    """

    def __init__(self, resource: 'Resource', request: Request):
        self.request = request
        """The request (:class:`Request`) that is to be released."""
        super().__init__(resource)


class Resource(BaseResource):
    """Resource with capacity of usage slots that can be requested by
    processes.

    If all slots are taken, requests are enqueued. Once a usage request is
    released, a pending request will be triggered.
    """

    def __init__(self, env: Environment, capacity: int = 1):
        if capacity <= 0:
            raise ValueError('"capacity" must be > 0.')

        super().__init__(env, capacity)

        self._users: List[Request] = []
        self._queue = self.put_queue

    @property
    def count(self) -> int:
        """Number of users currently using the resource."""
        return len(self._users)

    @property
    def users(self):
        """List of Request events for the processes that are currently using
        the resource."""
        return self._users

    @property
    def queue(self):
        """Queue of pending Request events. """
        return self._queue

    if TYPE_CHECKING:

        def request(self) -> Request:
            """Request a usage slot."""
            return Request(self)

        def release(self, request: Request) -> Release:
            """Release a usage slot."""
            return Release(self, request)

    else:
        request = BoundClass(Request)
        release = BoundClass(Release)

    def _do_put(self, event: Request) -> bool:
        if len(self._users) < self.capacity:
            self._users.append(event)
            event.usage_since = self._env.now
            event.succeed()
            return True
        else:
            return False

    def _do_get(self, event: Release) -> bool:
        try:
            self._users.remove(event.request)  # type: ignore
        except ValueError:
            pass
        event.succeed()
        return True


class PriorityRequest(Request):
    """Request the usage of resource with a given priority. If the
    resource supports preemption and preempt is True other usage
    requests of the resource may be preempted."""

    def __init__(
        self, resource: 'Resource', priority: int = 0, preempt: bool = True
    ):
        self.priority = priority
        """The priority of this request. A smaller number means higher
        priority."""

        self.preempt = preempt
        """Indicates whether the request should preempt a resource user or not"""

        self.time = resource._env.now
        """The time at which the request was made."""

        self.key = (self.priority, self.time, not self.preempt)
        """Key for sorting events. Consists of the priority (lower value is
        more important), the time at which the request was made (earlier
        requests are more important) and finally the preemption flag (preempt
        requests are more important)."""

        super().__init__(resource)


class SortedQueue(list):
    """Queue for sorting events by their key attributes."""

    def __init__(self, maxlen: Optional[int] = None):
        super().__init__()
        self.maxlen = maxlen

    def append(self, item: Any) -> None:
        if self.maxlen is not None and len(self) >= self.maxlen:
            raise RuntimeError('Cannot append event. Queue is full.')

        super().append(item)
        super().sort(key=lambda e: e.key)


class PriorityResource(Resource):
    """Use SortedQueue to hold all the pending requests. The requests are
    ordered by their (priority, time, not preempted) attribute"""

    PutQueue = SortedQueue
    GetQueue = list

    def __init__(self, env: Environment, capacity: int = 1):
        super().__init__(env, capacity)

    if TYPE_CHECKING:

        def request(
            self, priority: int = 0, preempt: bool = True
        ) -> PriorityRequest:
            """Request a usage slot with the given *priority*."""
            return PriorityRequest(self, priority, preempt)

        def release(
            self, request: PriorityRequest
        ) -> Release:
            """Release a usage slot."""
            return Release(self, request)

    else:
        request = BoundClass(PriorityRequest)
        release = BoundClass(Release)


class Preempted:
    def __init__(
        self,
        by: Optional[Process],
        usage_since: Optional[SimTime],
        resource: 'Resource',
    ):
        self.by = by
        """The preempting :class:`sim.events.Process`."""
        self.usage_since = usage_since
        """The simulation time at which the preempted process started to use
        the resource."""
        self.resource = resource
        """The resource which was lost, i.e., caused the preemption."""


class PreemptiveResource(PriorityResource):
    """If a request is preempted, the process of that request will receive an
    Interrupt with a Preempted instance as cause."""

    users: List[PriorityRequest]  # type: ignore

    def _do_put(self, event: PriorityRequest) -> bool:
        if len(self.users) >= self.capacity and event.preempt:
            # Check if we can preempt another process
            preempt = sorted(self.users, key=lambda e: e.key)[-1]
            if preempt.key > event.key:
                self.users.remove(preempt)
                preempt.proc.interrupt(  # type: ignore
                    Preempted(
                        by=event.proc,
                        usage_since=preempt.usage_since,
                        resource=self,
                    )
                )

        return super()._do_put(event)
