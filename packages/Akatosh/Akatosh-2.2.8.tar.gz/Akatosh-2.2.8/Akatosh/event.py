from __future__ import annotations

import inspect
from abc import abstractmethod
from typing import Any, Callable, List
from uuid import uuid4
import warnings

from .logger import logger
from .states import State
from .universe import Mundus


class Event:
    def __init__(
        self,
        at: int | float | Callable[..., int] | Callable[..., float],
        precursor: Event | List[Event] | None = None,
        action: Callable | None = None,
        priority: int | float | Callable[..., int] | Callable[..., float] = 0,
        label: str | None = None,
        **kwargs,
    ) -> None:
        """Base class for all events.

        Args:
            at (int | float | Callable[...,int] | Callable[...,float]): the time when the event happens.
            precursor (Event | List[Event] | None, optional): the precursor events. Defaults to None.
            action (Callable | None, optional): the actual action of the event, must be defined. Defaults to None.
            priority (int | float | Callable[...,int] | Callable[...,float], optional): the priority of the event. When multiple event happen at the same time, the event with lower priority value will happen first. Defaults to 0.
            label (str | None, optional): Short descirption of the event. Defaults to None.
        """
        self._id = uuid4().int
        # set the time
        if callable(at):
            self._at = round(at(), Mundus.resolution)
        else:
            self._at = round(at, Mundus.resolution)
        # set the target event(s) that this event should wait and follow
        if isinstance(precursor, list):
            self._precursor = precursor
        elif precursor is None:
            self._precursor = []
        else:
            self._precursor = [precursor]
        self._follower: List[Event] = []
        for event in self.precursor:
            event._follower.append(self)
        # set the state
        if len(self.precursor) != 0:
            self.state = State.INACTIVE
        else:
            self.state = State.ACTIVE
        # set the action and the priority
        if action:
            self._action = action
        if callable(priority):
            self._priority = priority()
        else:
            self._priority = priority
        # assign label
        self._label = label
        # add to the universe
        if Mundus.now < self.at:
            Mundus.future_events.append(self)
        elif Mundus.now > self.at:
            raise RuntimeError(f"Event {self.label} tries to alter the past.")
        else:
            Mundus.current_events.append(self)

    def end(self):
        """End the event and activate the follower events if there is any."""
        if self.ended:
            return

        self.state = State.ENDED
        if self in Mundus.future_events:
            Mundus.future_events.remove(self)
        if self in Mundus.current_events:
            Mundus.current_events.remove(self)
        Mundus.past_events.append(self)
        for event in self.follower:
            try:
                event.activate()
            except RuntimeError:
                logger.debug(f"Event {event.label} passed due time.")
        logger.debug(f"Event {self.label} is ended.")

    def activate(self, force: bool = False):
        """Activate the event."""

        # raise error if the event has already ended
        if self.ended:
            raise RuntimeError(f"Event {self.label} has already ended.")

        # raise warning if the event is cancelled
        if self.cancelled:
            warnings.warn(f"Event {self.label} is cancelled.")
            return

        # return if the event is already active
        if self.active:
            return

        if force:
            self.state = State.ACTIVE
            if self._at < Mundus.now:
                self._at = Mundus.now
            logger.debug(f"Event {self.label} is set to active.")
        else:
            if all(e.state == State.ENDED for e in self.precursor):
                self.state = State.ACTIVE
                if self._at < Mundus.now:
                    self._at = Mundus.now
                logger.debug(f"Event {self.label} is set to active.")
            else:
                warnings.warn(f"Event {self.label} is waiting for other events to end.")
                return

    def deactivate(self):
        """Deactivate the event.

        Raises:
            RuntimeError: raise if the event has already ended.
        """

        # raise error if the event has already ended
        if self.ended:
            raise RuntimeError(f"Event {self.label} has already ended.")

        # raise warning if the event is cancelled
        if self.cancelled:
            warnings.warn(f"Event {self.label} is cancelled.")
            return

        # return if the event is already inactive
        if self.inactive:
            return

        self.state = State.INACTIVE

    def cancel(self):
        """Cancel the event. Will not set the follower events to active.

        Raises:
            RuntimeError: raise if the event has already ended.
        """

        # raise error if the event has already ended
        if self.ended:
            raise RuntimeError(f"Event {self.label} has already ended.")

        # return if the event is already cancelled
        if self.cancelled:
            return

        self.state = State.CANCELED
        if self in Mundus.future_events:
            Mundus.future_events.remove(self)
        if self in Mundus.current_events:
            Mundus.current_events.remove(self)
        Mundus.past_events.append(self)
        logger.debug(f"Event {self.label} is cancelled.")

    @abstractmethod
    async def _perform(self):
        """Abstract method for the event to perform its action."""
        pass

    def __eq__(self, _o: Event) -> bool:
        """Determine if two events are the same."""
        return self.id == _o.id

    @property
    def id(self) -> int:
        """Return the unique id of the event."""
        return self._id

    @property
    def label(self) -> str | None:
        """Return the label of the event."""
        return self._label

    @property
    def at(self) -> int | float:
        """Return the time when the event happens."""
        return self._at

    @property
    def precursor(self) -> List[Event]:
        """Return the precursor events."""
        return self._precursor

    @property
    def follower(self) -> List[Event]:
        """Return the follower events."""
        return self._follower

    @property
    def action(self) -> Callable | None:
        """Return the action of the event."""
        return self._action

    @property
    def priority(self) -> int | float:
        """Return the priority of the event."""
        return self._priority

    @property
    def state(self) -> str:
        """Return the state of the event."""
        return self._state

    @state.setter
    def state(self, state: str):
        """Set the state of the event."""
        self._state = state

    @property
    def active(self) -> bool:
        """Return True if the event is active."""
        return State.ACTIVE == self.state

    @property
    def inactive(self) -> bool:
        """Return True if the event is inactive."""
        return State.INACTIVE == self.state

    @property
    def cancelled(self) -> bool:
        """Return True if the event is cancelled."""
        return State.CANCELED == self.state

    @property
    def ended(self) -> bool:
        """Return True if the event is ended."""
        return State.ENDED == self.state


class InstantEvent(Event):
    """Instant event is an event that happens at a specific time and only happens once."""

    def __init__(
        self,
        at: int | float | Callable[..., int] | Callable[..., float],
        precursor: Event | List[Event] | None = None,
        action: Callable[..., Any] | None = None,
        priority: int | float | Callable[..., int] | Callable[..., float] = 0,
        label: str | None = None,
        **kwargs,
    ) -> None:
        """Create a instant event.

        Args:
            at (int | float | Callable[...,int] | Callable[...,float]): the time when the event happens.
            precursor (Event | List[Event] | None, optional): the precursor events. Defaults to None.
            action (Callable | None, optional): the actual action of the event, must be defined. Defaults to None.
            priority (int | float | Callable[...,int] | Callable[...,float], optional): the priority of the event. When multiple event happen at the same time, the event with lower priority value will happen first. Defaults to 0.
            label (str | None, optional): Short descirption of the event. Defaults to None.
        """
        super().__init__(at, precursor, action, priority, label, **kwargs)

    async def _perform(self):
        """Perform the action of the event."""
        if self.state == State.ACTIVE:
            if self.action:
                if inspect.iscoroutinefunction(self.action):
                    await self.action()
                else:
                    self.action()
            Mundus.current_events.remove(self)
            Mundus.past_events.append(self)
            self.end()


def instant_event(
    at: int | float | Callable[..., int] | Callable[..., float],
    precursor: Event | List[Event] | None = None,
    priority: int | float | Callable[..., int] | Callable[..., float] = 0,
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
        return InstantEvent(
            at=at,
            precursor=precursor,
            action=func,
            priority=priority,
            label=label,
            **kwargs,
        )

    return _instant_event


class ContinuousEvent(Event):
    def __init__(
        self,
        at: int | float | Callable[..., int] | Callable[..., float],
        interval: int | float | Callable[..., int] | Callable[..., float],
        duration: int | float | Callable[..., int] | Callable[..., float],
        precursor: Event | List[Event] | None = None,
        action: Callable[..., Any] | None = None,
        priority: int | float | Callable[..., int] | Callable[..., float] = 0,
        label: str | None = None,
        **kwargs,
    ) -> None:
        """Continous event is an event that happens at a specific time and happens multiple times for a specific duration.

        Args:
            at (int | float | Callable[...,int] | Callable[...,float]): when the event happens.
            interval (int | float | Callable[...,int] | Callable[...,float]): the interval between each action repeat.
            duration (int | float | Callable[...,int] | Callable[...,float]): the duration of the event.
            precursor (Event | List[Event] | None, optional): the precursor events, can be both instant events or continous events. Defaults to None.
            action (Callable[..., Any] | None, optional): the actual action of the event. Defaults to None.
            priority (int | float | Callable[...,int] | Callable[...,float], optional): the priority of the event. Defaults to 0.
            label (str | None, optional): short description of the event.. Defaults to None.
        """
        super().__init__(
            at=at,
            precursor=precursor,
            action=action,
            priority=priority,
            label=label,
            **kwargs,
        )

        self._interval = interval
        if callable(duration):
            self._duration = round(duration(), Mundus.resolution)
        else:
            self._duration = round(duration, Mundus.resolution)
        self._till = self.at + self.duration
        self._sub_events: List[InstantEvent] = list()

    async def _perform(self):
        """Perform the action of the event. Compare to instant event, continous event will perform the action multiple times."""
        if self.action:
            self.action()
            if callable(self.interval):
                self._at = round(self.interval() + Mundus.now, Mundus.resolution)
            else:
                self._at = round(self.interval + Mundus.now, Mundus.resolution)
            if self.at <= self.till:
                logger.debug(f"Event {self.label} next step is at {self.at}.")
                Mundus.future_events.append(self)
                Mundus.current_events.remove(self)
            else:
                self.end()

    def activate(self, force: bool = False):
        if Mundus.now > self.till:
            logger.debug(f"Event {self.label} has passed due time.")
            return
        else:
            super().activate(force)

    @property
    def interval(self) -> int | float | Callable[..., Any]:
        """Return the interval between each action repeat."""
        return self._interval

    @property
    def duration(self) -> int | float:
        """Return the duration of the event."""
        return self._duration

    @property
    def till(self) -> int | float:
        """Return the time when the event ends."""
        return self._till

    @property
    def sub_events(self) -> List[InstantEvent]:
        """Return the sub events of the continous event."""
        return self._sub_events


def continuous_event(
    at: int | float | Callable[..., int] | Callable[..., float],
    interval: int | float | Callable[..., int] | Callable[..., float],
    duration: int | float | Callable[..., int] | Callable[..., float],
    precursor: Event | List[Event] | None = None,
    priority: int | float | Callable[..., int] | Callable[..., float] = 0,
    label: str | None = None,
    **kwargs,
):
    """A decorator for creating continous event.

    Args:
        at (int | float | Callable[...,int] | Callable[...,float]): when the continuous event starts.
        interval (int | float | Callable[...,int] | Callable[...,float]): how frequent the event happens.
        duration (int | float | Callable[...,int] | Callable[...,float]): the duration of the event.
        precursor (Event | List[Event] | None, optional): the precursors for this event. Defaults to None.
        priority (int | float | Callable[...,int] | Callable[...,float], optional): the priority for this event. Defaults to 0.
        label (str | None, optional): short description of the event. Defaults to None.
    """

    def _continous_event(func: Callable):
        return ContinuousEvent(
            at=at,
            interval=interval,
            duration=duration,
            precursor=precursor,
            action=func,
            priority=priority,
            label=label,
            **kwargs,
        )

    return _continous_event
