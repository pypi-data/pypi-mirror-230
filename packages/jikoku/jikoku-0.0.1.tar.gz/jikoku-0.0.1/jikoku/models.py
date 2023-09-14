from dataclasses import dataclass
from datetime import time, timedelta
from typing import Self

from jikoku.time import TimePoint
from jikoku.utils import add_times, subtract_times


@dataclass
class Stop:
    name: str
    stop_time: TimePoint

    def __add__(self, other):
        return Stop(self.name, self.stop_time.plus(other))

    def __sub__(self, other):
        return Stop(self.name, self.stop_time.minus(other))

    def __le__(self, other):
        pass


@dataclass
class Service:
    """
    This is a test api documentation
    """

    name: str
    stops: list[Stop]

    @classmethod
    def from_stops(cls, name: str, stops: list[Stop]) -> Self:
        return cls(name, stops)

    @property
    def start_time(self) -> TimePoint:
        return self.stops[0].stop_time

    @property
    def first_stop(self) -> Stop:
        return self.stops[0]

    @property
    def last_stop(self) -> Stop:
        return self.stops[-1]

    @property
    def end_time(self) -> TimePoint:
        return self.stops[-1].stop_time

    def __add__(self, other: TimePoint):
        new_name = self.name + "_shift_by_" + str(other)
        return Service(
            new_name,
            [stop + other for stop in self.stops],
        )

    def __sub__(self, other: TimePoint):
        new_name = self.name + "_shift_by_minus" + str(other)
        return Service(
            new_name,
            [stop - other for stop in self.stops],
        )


@dataclass
class Train:
    # TODO this should be unique, any way to enforce?
    name: str


@dataclass
class Trip:
    service: Service
    train: Train


@dataclass
class Schedule:
    name: str
    trips: list[Trip]

    @property
    def number_of_trains(self):
        return len({t.train.name for t in self.trips})
