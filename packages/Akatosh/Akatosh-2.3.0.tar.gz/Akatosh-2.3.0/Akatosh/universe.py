from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, List

from .logger import logger
from .states import State

if TYPE_CHECKING:
    from .event import Event


class Universe:
    def __init__(self) -> None:
        """The Simulation Universe."""
        self._resolution = 15  # the resolution of the time. 1 means minimum time unit is 0.1 second.
        self._now: int | float = -1  # the current time of the simulated universe.
        self._future_events: List[Event] = list()  # the future events queue.
        self._current_events: List[Event] = list()  # the current events queue.
        self._past_events: List[Event] = list()  # the past events queue.
        self._alduin: bool = False  # trigger to stop the simulation.
        self.set_logger(logging.ERROR)  # set the default logger level to ERROR.

    async def akatosh(self, till: int | float | None = None):
        """Akatosh is the god of time in the Elder Scrolls universe. This method is the core of the simulation.

        Args:
            till (int | float | None, optional): the end time of the simulated universe. Defaults to None.

        Raises:
            RuntimeError: raise if the event is in unknown state or being placed in wrong event queue.
        """
        while len(self.future_events) != 0:
            
            # stop simulation if world eater alduin is triggered.
            if self.alduin:
                return

            # update the current time of the simulated universe.
            valid_future_events = [
                event
                for event in self.future_events
                if event.state == State.ACTIVE or event.state == State.INACTIVE
            ]
            if len(valid_future_events) == 0:
                return
            _time = min(event.at for event in valid_future_events)
            if self.now < _time:
                self._now = _time
                
            # stop simulation if the end time is reached.
            if till is not None:
                if self.now > till:
                    return
                
            logger.debug(f"Time: {self.now}")

            logger.debug(
                f"Future active events: {[(event.at, event.label) for event in self.future_events]}"
            )

            self.organise_events()

            logger.debug(
                f"Current events: {[(event.priority, event.label) for event in self.current_events]}"
            )

            await self.execute_current_events()
            
            

    def organise_events(self):
        """Organise the events in the future events queue. Valid event will be moved to the current events queue. Non-valid event will be moved to the past events queue.

        Raises:
            RuntimeError: raise if the event is in unknown state or being placed in wrong event queue.
        """
        for event in self.future_events[:]:
            if event.at <= self.now:
                if event.state == State.ACTIVE or event.state == State.INACTIVE:
                    logger.debug(f"Event {event.label} is triggered.")
                    self.future_events.remove(event)
                    self.current_events.append(event)
                elif event.state == State.CANCELED:
                    raise RuntimeError(
                            f"Event {event.label} is canceled but inside future events queue."
                        )
                elif event.state == State.ENDED:
                    raise RuntimeError(
                            f"Event {event.label} is ended but inside future events queue."
                        )
                else:
                    raise RuntimeError(f"Event {event.label} is in unknown state.")

    async def execute_current_events(self):
        """Execute the current events queue based on priority. The event with the lowest priority will be executed first. The event with the same priority will be executed concurrently.
        """
        while (
            len([event for event in self.current_events if event.state == State.ACTIVE])
            != 0
        ):
            priority = min(
                event.priority
                for event in self.current_events
                if event.state == State.ACTIVE
            )
            logger.debug(
                f"Current Priority: {priority}, Executing events: {[event.label for event in self.current_events if event.priority == priority]}"
            )
            await asyncio.gather(
                *[
                    event._perform()
                    for event in self.current_events
                    if event.priority == priority
                ]
            )

    def simulate(self, till: int | float | None = None):
        """Start the simulation."""
        asyncio.run(self.akatosh(till))

    def set_logger(self, level: int):
        """Set the logger level."""
        logger.setLevel(level)

    @property
    def resolution(self) -> int:
        """Return  the resolution of the time."""
        return self._resolution
    
    @resolution.setter
    def resolution(self, value: int):
        """Set the resolution of the time."""
        if value <= 0:
            raise ValueError("Resolution must be greater than 0.")
        self._resolution = value

    @property
    def now(self) -> int | float:
        """Return the current time of the simulated universe."""
        return self._now

    @property
    def future_events(self) -> List[Event]:
        """Return the future events queue."""
        return self._future_events

    @property
    def current_events(self) -> List[Event]:
        """Return the current events queue."""
        return self._current_events

    @property
    def past_events(self) -> List[Event]:
        """Return the past events queue."""
        return self._past_events

    @property
    def alduin(self) -> bool:
        """Return the trigger to stop the simulation."""
        return self._alduin

    @alduin.setter
    def alduin(self, value: bool):
        """Set the trigger to stop the simulation."""
        self._alduin = value


Mundus = Universe()
