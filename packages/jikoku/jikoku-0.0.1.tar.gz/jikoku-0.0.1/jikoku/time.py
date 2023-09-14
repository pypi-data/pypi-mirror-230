from abc import ABC, abstractmethod
from typing import Self

# FIXME: the abstract class should have some notion of adding a few minutes to an existing timepoint!


class TimePoint(ABC):
    @abstractmethod
    def plus(self, other: Self) -> Self:
        pass

    @abstractmethod
    def minus(self, other: Self) -> Self:
        pass

    @abstractmethod
    def same_time(self, other: Self) -> bool:
        pass

    @abstractmethod
    def earlier_than(self, other: Self) -> bool:
        pass

    def __add__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(
                "Can only add a TimePoint of the same type to another TimePoint!"
            )

        return self.plus(other)

    def __sub__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(
                "Can only subtract a TimePoint of the same type to another TimePoint!"
            )

        return self.minus(other)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError("Can only compare Timepoints of the same type!")

        return self.same_time(other)

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError("Can only compare Timepoints of the same type!")

        return self.same_time(other)

    @abstractmethod
    def __str__(self):
        """Forces child classes to implement __str__ method"""
        pass


class DailyTimePoint(TimePoint, ABC):
    def __init__(
        self, hour: int = 0, minute: int = 0, day: int = 0, previous: Self = None
    ):
        self._t = day * 24 * 60 + hour * 60 + minute

    def plus(self, other: Self) -> Self:
        return DailyTimePoint(hour=0, minute=self._t + other._t)

    def minus(self, other: Self) -> Self:
        return DailyTimePoint(hour=0, minute=self._t - other._t)

    def same_time(self, other: Self) -> bool:
        return self._t == other._t

    def earlier_than(self, other: Self) -> bool:
        return self._t <= other._t

    def __str__(self):
        date, total_min = divmod(self._t, 24 * 60)
        hours, minutes = divmod(total_min, 60)

        if date == 0:
            return f"{hours:02}:{minutes:02}"
        elif date == 1:
            return f"Tomorrow at {hours:02}:{minutes:02}"
        elif date == -1:
            return f"Yesterday at {hours:02}:{minutes:02}"
        elif date >= 2:
            return f"In {date} days at {hours:02}:{minutes:02}"
        elif date <= -2:
            return f"{abs(date)} days ago at {hours:02}:{minutes:02}"


class WeeklyTimePoint(TimePoint):
    pass
