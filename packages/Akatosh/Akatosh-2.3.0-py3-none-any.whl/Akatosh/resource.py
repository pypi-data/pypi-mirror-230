from __future__ import annotations

from typing import Callable, List, Tuple

from .logger import logger
from .universe import Mundus


class Resource:
    def __init__(
        self,
        capacity: int | float | Callable,
        initial_amount: int | float | Callable | None = None,
        label: str | None = None,
    ) -> None:
        """Resource is a class that represents a resource with capacity and amount, any object can use this resource by calling distribute() and return by calling collect() methods.

        Args:
            capacity (int | float | Callable): the capacity of the resource.
            initial_amount (int | float | Callable | None, optional): the initial amount of the resource. Defaults to capacity.
            label (str | None, optional): short description of the resource. Defaults to None.

        Raises:
            ValueError: raise if initial amount is greater than capacity.
        """
        if callable(capacity):
            self._capacity = capacity()
        else:
            self._capacity = capacity
        if initial_amount:
            if callable(initial_amount):
                if initial_amount() > self.capacity:
                    raise ValueError("Initial amount is greater than capacity.")
                else:
                    self._amount = initial_amount()
            else:
                if initial_amount > self.capacity:
                    raise ValueError("Initial amount is greater than capacity.")
                else:
                    self._amount = initial_amount
        else:
            self._amount = self.capacity
        self._label = label
        self._user_records: List[
            Tuple[object, int | float]
        ] = list()  # (user, amount) tracking the usage of individual user
        self._usage_records: List[
            Tuple[int | float, int | float]
        ] = list()  # (time, amount) tracking the usage of the resource over time

    def get(self, amount: int | float) -> None:
        """Get the amount of resource from the resource.

        Args:
            amount (int | float): the amount of resource to get.

        Raises:
            ValueError: raise if amount is greater than the current available amount of resource.
        """
        if amount > self.amount:
            raise ValueError(f"Not enough amount in Resource {self.label}.")
        else:
            self._amount -= amount
            self.usage_records.append((Mundus.now, self.amount))

    def put(self, amount: int | float) -> None:
        """Put the amount of resource back to the resource.

        Args:
            amount (int | float): the amount of resource to put.

        Raises:
            ValueError: raise if amount is greater than the current used amount of resource.
        """
        if amount > self.occupied:
            raise ValueError(f"Not enough capacity in Resource {self.label}.")
        else:
            self._amount += amount
            self.usage_records.append((Mundus.now, self.amount))

    def distribute(self, user: object, amount: int | float) -> None:
        """Distribute the amount of resource to the user.

        Args:
            user (object): the user of the resource.
            amount (int | float): the amount of resource to distribute.

        Raises:
            ValueError: raise if amount is greater than the current available amount of resource.
        """
        if amount > self.amount:
            raise ValueError(f"Not enough amount in Resource {self.label}.")
        else:
            self._amount -= amount
            if user in self.users:
                for index, record in enumerate(self.user_records):
                    if record[0] is user:
                        self.user_records[index] = (user, record[1] + amount)
                        break
            else:
                self.user_records.append((user, amount))
            self.usage_records.append((Mundus.now, self.amount))
            logger.debug(f"Resource {self.label} distributed {amount} to {user}.")

    def collect(self, user: object, amount: int | float | None = None) -> None:
        """Collect the amount of resource from the user.

        Args:
            user (object): the user of the resource.
            amount (int | float | None, optional): the amount of resource to collect. Defaults to None means collecting all resource used by the user.

        Raises:
            ValueError: raise if user is not using the resource or amount is greater than the current used amount of resource.
        """
        if user not in self.users:
            raise ValueError(f"User {user} is not using Resource {self.label}.")
        if amount is None:
            for index, record in enumerate(self.user_records):
                if record[0] is user:
                    self._amount += record[1]
                    self.usage_records.append((Mundus.now, self.amount))
                    logger.debug(
                        f"Resource {self.label} collected {record[1]} from {user}."
                    )
                    break
        else:
            for index, record in enumerate(self.user_records):
                if record[0] is user:
                    if record[1] < amount:
                        raise ValueError(
                            f"{user} occupied {record[1]} of Resource {self.label}, less than {amount}."
                        )
                    else:
                        self.user_records[index] = (user, record[1] - amount)
                        if self.user_records[index][1] == 0:
                            self.user_records.pop(index)
                        self._amount += amount
                        self.usage_records.append((Mundus.now, self.amount))
                        logger.debug(
                            f"Resource {self.label} collected {amount} from {user}."
                        )
                        break

    def utilization(self, duration: int | float | Callable | None = None):
        """Return the utilization ( occupied amount / capacity ) of the resource in the duration.

        Args:
            duration (int | float | Callable | None, optional): the duration to trace back in time. Defaults to None.
        """
        if duration:
            if callable(duration):
                after = Mundus.now - duration()
            else:
                after = Mundus.now - duration
            if after < 0:
                after = 0
            usage_records = [
                usage_record
                for usage_record in self.usage_records
                if usage_record[0] >= after
            ]
            if len(usage_records) == 0:
                return 1 - (self.amount / self.capacity)
            else:
                if usage_records[-1][0] - after == 0:
                    return 1 - (usage_records[-1][1] / self.capacity)
                else:
                    weighted_overall_amount = 0
                    for index, record in enumerate(usage_records):
                        if index == 0:
                            weighted_overall_amount += record[1] * (record[0] - after)
                        elif index == len(usage_records) - 1:
                            weighted_overall_amount += record[1] * (
                                Mundus.now - usage_records[index - 1][0]
                            )
                        else:
                            weighted_overall_amount += record[1] * (
                                record[0] - usage_records[index - 1][0]
                            )
                    return (
                        1
                        - (weighted_overall_amount / (usage_records[-1][0] - after))
                        / self.capacity
                    )
        else:
            return 1 - (self.amount / self.capacity)

    def usage(self, duration: int | float | Callable | None = None):
        """Return the usage ( occupied amount ) of the resource in the duration.

        Args:
            duration (int | float | Callable | None, optional): the duration to trace back in time. Defaults to None.
        """
        return self.capacity * self.utilization(duration)

    @property
    def amount(self) -> int | float:
        """Return the current available amount of the resource."""
        return self._amount

    @property
    def capacity(self) -> int | float:
        """Return the capacity of the resource."""
        return self._capacity

    @property
    def occupied(self) -> int | float:
        """Return the current occupied amount of the resource."""
        return self.capacity - self.amount

    @property
    def label(self) -> str | None:
        """Return the label of the resource."""
        return self._label

    @property
    def user_records(self) -> List[Tuple[object, int | float]]:
        """Return the usage records of the resource per user."""
        return self._user_records

    @property
    def usage_records(self) -> List[Tuple[int | float, int | float]]:
        """Return the usage records of the resource, for calculating the usage of the resource in a duration."""
        return self._usage_records

    @property
    def users(self) -> List[object]:
        """Return the users of the resource."""
        return [record[0] for record in self._user_records]
