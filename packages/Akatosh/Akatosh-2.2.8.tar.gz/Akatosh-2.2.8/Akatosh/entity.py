from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable
from math import inf
from typing import Callable, Iterable, List
from uuid import uuid4

from Akatosh.universe import Mundus

from .event import ContinuousEvent, Event, InstantEvent
from .logger import logger
from .resource import Resource
from .states import State


class Entity:
    def __init__(
        self,
        label: str | None = None,
        create_at: int
        | float
        | Callable[..., int]
        | Callable[..., float]
        | None = None,
        terminate_at: int
        | float
        | Callable[..., int]
        | Callable[..., float]
        | None = None,
        precursor: Entity | List[Entity] | None = None,
    ) -> None:
        """Create a entity.

        Args:
            label (str | None, optional): short description of the entity. Defaults to None.
            create_at (int | float | Callable | None, optional): when the life cycle of this entity should start. Defaults to 0, then must call create() method manually.
            terminate_at (int | float | Callable | None, optional): when the life cycle of this entity should end. Defaults to inf, then must call terminate() method manually.
        """
        self._id = uuid4().int
        self._label = label
        self._state: List[str] = list()
        self._occupied_resources: List[Resource] = list()
        self._registered_lists: List[EntityList] = list()
        self._creation: InstantEvent = None  # type: ignore
        self._termination: InstantEvent = None  # type: ignore
        self._destruction: InstantEvent = None  # type: ignore
        self._events: List[Event] = list()

        # assign precursor and followers
        if isinstance(precursor, list):
            self._precursor = precursor
        elif precursor is None:
            self._precursor = []
        else:
            self._precursor = [precursor]
        self._followers: List[Entity] = []
        for event in self.precursor:
            event._followers.append(self)

        # assign create_at and terminate_at
        if create_at is not None:
            if callable(create_at):
                self._create_at = round(create_at(), Mundus.resolution)
            else:
                self._create_at = round(create_at, Mundus.resolution)
        else:
            self._create_at = 0
        self._created_at = float()

        if terminate_at is not None:
            if callable(terminate_at):
                self._terminate_at = round(terminate_at(), Mundus.resolution)
            else:
                self._terminate_at = round(terminate_at, Mundus.resolution)
        else:
            self._terminate_at = inf
        self._terminated_at = float()

        # create the entity if no precursor
        if create_at is not None and len(self.precursor) == 0:
            self.create(self.create_at)

    def create(self, at: int | float, force=False) -> None:
        """The creation of the entity."""
        if self.created:
            logger.warning(f"Entity {self.label} is already created.")
            return

        # check if the entity is already over due
        if at > self.terminate_at:
            logger.debug(f"Entity {self.label} passed due time.")
            return

        # call back function for creation
        def _create():
            self._created_at = Mundus.now
            self._state.append(State.CREATED)
            self.on_creation()
            logger.debug(f"Entity {self.label} created at {at}")

        # force creation if force is True, regardless of the precursor and the time
        if force:
            self._creation = InstantEvent(
                at=self.create_at if self.create_at > at else at,
                action=_create,
                label=f"Creation of {self.label}",
                priority=-2,
            )
            self.terminate(self.terminate_at)
        else:
            # check if all precursors are terminated, if so, create the entity
            if len(self.precursor) != 0:
                if all(p.terminated for p in self.precursor):
                    self._creation = InstantEvent(
                        at=self.create_at if self.create_at > at else at,
                        action=_create,
                        label=f"Creation of {self.label}",
                        priority=-2,
                    )
                    self.terminate(self.terminate_at)
            # no precursor, create the entity
            else:
                self._creation = InstantEvent(
                    at=self.create_at if self.create_at > at else at,
                    action=_create,
                    label=f"Creation of {self.label}",
                    priority=-2,
                )
                self.terminate(self.terminate_at)

    @abstractmethod
    def on_creation(self):
        """Callback function upon creation of the entity"""
        pass

    def terminate(self, at: int | float) -> None:
        """The termination of the entity. This will release all occupied resource, remove the entity from all entity lists, and cancel all unfinished events."""

        if self.terminated:
            logger.warning(f"Entity {self.label} is already terminated.")
            return

        def _terminate():
            self._terminated_at = Mundus.now
            self._state.append(State.TERMINATED)
            self.release_resources()
            self.unregister_from_lists()
            self.cancel_unfinished_events()
            self.on_termination()
            logger.debug(f"Entity {self.label} terminated at {Mundus.now}")
            for entity in self._followers:
                entity.create(Mundus.now)
        
        # check if a earlier termination is scheduled
        if self._terminate_at > at:
            self._terminate_at = at
            
        if self._termination is not None:
            self._termination.cancel()

        self._termination = InstantEvent(
            at=self.terminate_at,
            action=_terminate,
            label=f"Termination of {self.label}",
            priority=-2,
        )

    @abstractmethod
    def on_termination(self):
        """Callback function upon termination of the entity"""
        pass
    
    def destory(self, at: int | float) -> None:
        """The Destruction of the entity. This will release all occupied resource, remove the entity from all entity lists, and cancel all unfinished events. This will not trigger the creation of followers."""

        if self.terminated:
            logger.warning(f"Entity {self.label} is already terminated.")
            return

        def _destroy():
            self._terminated_at = Mundus.now
            self._state.append(State.TERMINATED)
            self.release_resources()
            self.unregister_from_lists()
            self.cancel_unfinished_events()
            self.on_destruction()
            logger.debug(f"Entity {self.label} destoried at {Mundus.now}")

        if self._destruction is not None:
            self._destruction.cancel()

        self._destruction = InstantEvent(
            at=self.terminate_at if self.terminate_at < at else at,
            action=_destroy,
            label=f"Destruction of {self.label}",
            priority=-2,
        )

    @abstractmethod
    def on_destruction(self):
        """Callback function upon destruction of the entity"""
        pass

    def get(
        self, resource: Resource, amount: int | float | Callable | None = None
    ) -> None:
        """Consume certain amout from a resource. if no amount is specified, consume all."""

        if not self.created:
            raise RuntimeError(
                f"Entity {self} is not created yet, can not interact with any resource."
            )

        if self.terminated:
            raise RuntimeError(
                f"Entity {self} is already terminated, can not interact with any resource."
            )

        if amount:
            if callable(amount):
                resource.distribute(self, amount())
                self.ocupied_resources.append(resource)
            else:
                resource.distribute(self, amount)
                self.ocupied_resources.append(resource)
        else:
            resource.distribute(self, resource.amount)

    def put(
        self, resource: Resource, amount: int | float | Callable | None = None
    ) -> None:
        """Return certain amout to a resource. if no amount is specified, return all."""
        if not self.created:
            raise RuntimeError(
                f"Entity {self} is not created yet, can not interact any resource."
            )

        if self.terminated:
            raise RuntimeError(
                f"Entity {self} is already terminated, can not interact any resource."
            )

        if amount:
            if callable(amount):
                resource.collect(self, amount())
                if self not in resource.users:
                    self.ocupied_resources.remove(resource)
            else:
                resource.collect(self, amount)
                if self not in resource.users:
                    self.ocupied_resources.remove(resource)
        else:
            resource.collect(self)

    def release_resources(self):
        """Release all occupied resources."""
        for res in self.ocupied_resources:
            res.collect(self)

    def unregister_from_lists(self):
        """Remove this entity from all registered entity lists."""
        for list in self.registered_lists[:]:
            list.remove(self)

    def cancel_unfinished_events(self):
        """Cancel all unfinished events."""
        for event in self.events:
            if not event.ended:
                event.cancel()

    def continuous_event(
        self,
        at: int | float | Callable,
        interval: int | float | Callable,
        duration: int | float | Callable,
        precursor: Event | List[Event] | None = None,
        priority: int | float | Callable = 0,
        label: str | None = None,
        **kwargs,
    ):
        """A decorator for creating continous event engaged by this entity.

        Args:
            at (int | float | Callable): when the continuous event starts.
            interval (int | float | Callable): how frequent the event happens.
            duration (int | float | Callable): the duration of the event.
            precursor (Event | List[Event] | None, optional): the precursors for this event. Defaults to None.
            priority (int | float | Callable, optional): the priority for this event. Defaults to 0.
            label (str | None, optional): short description of the event. Defaults to None.
        """

        def _continous_event(func: Callable):
            # define a function that validate the entity state first, then create the event
            def __continous_event():
                if not self.created:
                    raise RuntimeError(
                        f"Entity {self} is not created yet, can not engage in any event."
                    )
                if self.terminated:
                    raise RuntimeError(
                        f"Entity {self} is already terminated, can not engage in any event."
                    )
                self.events.append(
                    ContinuousEvent(
                        at=at,
                        interval=interval,
                        duration=duration,
                        precursor=precursor,
                        action=func,
                        priority=priority,
                        label=label,
                        **kwargs,
                    )
                )

            # create the instant event that will validate the entity state first, then create the continuous event
            InstantEvent(
                at=at,
                action=__continous_event,
                priority=-1,
                label=f"Engagement: {label}",
            )

        return _continous_event

    def instant_event(
        self,
        at: int | float | Callable,
        precursor: Event | List[Event] | None = None,
        priority: int | float | Callable = 0,
        label: str | None = None,
        **kwargs,
    ):
        """Decorator for creating instant event.

        Args:
            at (int | float | Callable): When the event happens.
            precursor (Event | List[Event] | None, optional): The precursor events. Defaults to None.
            priority (int | float | Callable, optional): The priority of the event. Defaults to 0.
            label (str | None, optional): Short description of the event. Defaults to None.
        """

        def _instant_event(func: Callable):
            def __instant_event():
                if not self.created:
                    raise RuntimeError(
                        f"Entity {self} is not created yet, can not engage in any event."
                    )
                if self.terminated:
                    raise RuntimeError(
                        f"Entity {self} is already terminated, can not engage in any event."
                    )

                self.events.append(
                    InstantEvent(
                        at=at,
                        precursor=precursor,
                        action=func,
                        priority=priority,
                        label=label,
                        **kwargs,
                    )
                )

            # create the instant event that will validate the entity state first, then create the event
            InstantEvent(
                at=at, action=__instant_event, priority=-1, label=f"Engagement: {label}"
            )

        return _instant_event

    @property
    def label(self):
        """Return the label of the entity."""
        return self._label

    @property
    def state(self):
        """Return the state(s) of the entity."""
        return self._state

    @property
    def created(self):
        """Return True if the entity is created."""
        return State.CREATED in self.state

    @property
    def create_at(self):
        """Return the time when the entity should be created."""
        return self._create_at

    @property
    def created_at(self):
        """Return the time when the entity is created."""
        return self._created_at

    @property
    def terminated(self):
        """Return True if the entity is terminated."""
        return State.TERMINATED in self.state

    @property
    def terminate_at(self):
        """Return the time when the entity should be terminated."""
        return self._terminate_at

    @property
    def terminated_at(self):
        """Return the time when the entity is terminated."""
        return self._terminated_at

    @property
    def ocupied_resources(self):
        """Return the resources occupied by the entity."""
        return self._occupied_resources

    @property
    def registered_lists(self):
        """Return the entity lists contains the entity."""
        return self._registered_lists

    @property
    def events(self):
        """Return the events engaged by the entity."""
        return self._events

    @property
    def precursor(self):
        """Return the precursor(s) of the entity."""
        return self._precursor


class EntityList(list):
    """Customized list for entities. This list ensures all items are entities and unique. When an entity is terminated, it will be removed from all entity lists automatically."""

    def __init__(self, iterable: Iterable[Entity] = [], label: str | None = None):
        """Create a list for entities, with optional label.

        Args:
            iterable (Iterable[Entity]): Iterable of entities.
        """
        super().__init__(item for item in iterable if isinstance(item, Entity))
        self._label = label

    def insert(self, __index: int, __object: Entity) -> None:
        """Insert an entity to the list.

        Args:
            __index (SupportsIndex): the index to insert the entity.
            __object (Entity): the entity to be inserted.
        """
        if __object not in self:
            super().insert(__index, __object)
            if self not in __object.registered_lists:
                __object.registered_lists.append(self)
            logger.debug(
                f"Entity {__object.label} is inserted to {self.label if self.label else self} at {__index}."
            )

    def append(self, __object: Entity) -> None:
        """Append an entity to the list.

        Args:
            __object (Entity): the entity to be appended.
        """
        if __object not in self:
            super().append(__object)
            if self not in __object.registered_lists:
                __object.registered_lists.append(self)
            logger.debug(
                f"Entity {__object.label} is appended to {self.label if self.label else self}."
            )

    def remove(self, __object: Entity) -> None:
        """Remove an entity from the list.

        Args:
            __object (Entity): the entity to be removed.
        """
        super().remove(__object)
        if self in __object.registered_lists:
            __object.registered_lists.remove(self)
        logger.debug(
            f"Entity {__object.label} is removed from {self.label if self.label else self}."
        )

    def pop(self, __index: int = ...) -> Entity:
        """Pop an entity from the list.

        Args:
            __index (int, optional): the index. Defaults to ... (the last one).

        Returns:
            Entity: return the poped entity.
        """
        __object: Entity = super().pop(__index)
        __object.registered_lists.remove(self)
        logger.debug(
            f"Entity {__object.label} is poped from {self.label if self.label else self} at {__index}."
        )
        return __object

    def clear(self) -> None:
        """Clear the list."""
        for item in self:
            item.registered_lists.remove(self)
        super().clear()
        logger.debug(f"{self.label if self.label else self} is cleared.")

    def extend(self, __iterable: Iterable[Entity]) -> None:
        """Extend the list with an iterable of entities.

        Args:
            __iterable (Iterable[Entity]): the iterable of entities.
        """
        for item in __iterable:
            if item not in self:
                super().append(item)
        for item in __iterable:
            if self not in item.registered_lists:
                item.registered_lists.append(self)
        logger.debug(
            f"{self.label if self.label else self} is extended with {__iterable}."
        )

    @property
    def label(self):
        """Return the label of the entity list."""
        return self._label
