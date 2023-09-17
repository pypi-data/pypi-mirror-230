# interval.py

from typing import Tuple, Union, Dict, Any, ClassVar
import datetime as dt

from attrs import define

from represent import represent, Modifiers


__all__ = [
    "interval_to_duration",
    "interval_to_time",
    "interval_to_total_time",
    "parts_to_interval",
    "INTERVALS",
    "MINUTES",
    "MONTHS",
    "HOURS",
    "DAYS",
    "YEARS",
    "WEEKS",
    "Interval"
]

MINUTES = "m"
MONTHS = "mo"
HOURS = "h"
DAYS = "d"
YEARS = "y"
WEEKS = "w"

INTERVALS = {
    MINUTES: dt.timedelta(minutes=1),
    HOURS: dt.timedelta(hours=1),
    DAYS: dt.timedelta(days=1),
    WEEKS: dt.timedelta(days=7),
    MONTHS: dt.timedelta(days=30),
    YEARS: dt.timedelta(days=365)
}

@define(slots=False, init=False, repr=False, eq=False, unsafe_hash=True)
@represent
class Interval:
    """
    A class to represent a trading pair.

    This object represents a pair of assets that can be traded.

    attributes:

    - base:
        The asset to buy or sell.

    - quote:
        The asset to use to buy or sell.

    >>> from crypto_screening.interval import Interval
    >>>
    >>> interval = Interval(1, "d")
    """

    __slots__ = "_periods", "_duration"

    __modifiers__ = Modifiers(excluded=["parts"])

    PERIODS: ClassVar[str] = 'periods'
    DURATION: ClassVar[str] = 'duration'

    try:
        from typing import Self

    except ImportError:
        Self = Any
    # end try

    def __init__(self, periods: int, duration: str) -> None:
        """
        Defines the class attributes.

        :param periods: The amount of periods for the interval.
        :param duration: The duration type for the interval.
        """

        self._periods = periods
        self._duration = duration
    # end __init__

    def __eq__(self, other: Any) -> bool:
        """
        Checks if the signatures are equal.

        :param other: The signature to compare.

        :return: The equality value.
        """

        if type(other) is not type(self):
            return NotImplemented
        # end if

        other: Interval

        return (self is other) or (
            (self.periods == other.periods) and
            (self.duration == other.duration)
        )
    # end __eq__

    @property
    def periods(self) -> int:
        """
        Returns the periods property.

        :return: The amount of periods in the interval.
        """

        return self._periods
    # end periods

    @property
    def duration(self) -> str:
        """
        Returns the duration property.

        :return: The duration in the interval.
        """

        return self._duration
    # end duration

    @classmethod
    def load(cls, data: Dict[str, Union[str, int]]) -> Self:
        """
        Creates a pair of assets from the data.

        :param data: The pair data.

        :return: The pair object.
        """

        return cls(
            periods=data[cls.PERIODS],
            duration=data[cls.DURATION]
        )
    # end load

    @property
    def parts(self) -> Tuple[int, str]:
        """
        Returns the property value.

        :return: The symbol.
        """

        return self._periods, self._duration
    # end parts

    def interval(self) -> str:
        """
        Returns the string for the interval.

        :return: The string.
        """

        return f"{self.periods}{self.duration}"
    # end __str__

    def json(self) -> Dict[str, Union[int, str]]:
        """
        Converts the data into a json format.

        :return: The chain of assets.
        """

        return {
            self.PERIODS: self.periods,
            self.DURATION: self.duration
        }
    # end json
# end Interval

def interval_to_duration(interval: str) -> int:
    """
    Extracts the number from the interval.

    :param interval: The interval to extract.

    :return: The number from the interval.
    """

    for kind in tuple(INTERVALS.keys()):
        try:
            return int(interval.replace(kind, ""))

        except (TypeError, EOFError):
            pass
        # end try
    # end for

    raise ValueError(f"Invalid interval value: {interval}.")
# end interval_to_duration

def interval_to_time(interval: str) -> dt.timedelta:
    """
    Extracts the type from the interval.

    :param interval: The interval to extract.

    :return: The type from the interval.
    """

    number = interval_to_duration(interval)

    try:
        return INTERVALS[interval.replace(str(number), "")]

    except KeyError:
        raise ValueError(f"Invalid interval structure: {interval}.")
    # end try
# end interval_to_time

def interval_to_total_time(interval: str) -> dt.timedelta:
    """
    Extracts the type from the interval.

    :param interval: The interval to extract.

    :return: The type from the interval.
    """

    return interval_to_duration(interval) * interval_to_time(interval)
# end interval_to_total_time

def parts_to_interval(increment: str, duration: int) -> str:
    """
    Creates a valid interval from the parameters.

    :param increment: The increment type for the interval.
    :param duration: The duration of the interval.

    :return: The interval.
    """

    if increment not in INTERVALS:
        raise ValueError(
            f"Interval increment must be one of "
            f"{', '.join(INTERVALS.keys())}, not {increment}."
        )
    # end if

    return f"{duration}{increment}"
# end parts_to_interval