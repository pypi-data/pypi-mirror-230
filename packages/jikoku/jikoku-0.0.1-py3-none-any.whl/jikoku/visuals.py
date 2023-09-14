"""
Module for printing & visualizing Jikoku object data.
"""
import itertools
import logging

from jikoku.models import *
from jikoku.scheduler import schedule
from tests.test_scheduler_basic import get_basic_schedule

Log = logging.getLogger(__name__)


def pretty_print_schedule(schedule: Schedule) -> str:
    to_print = f"\nPrinting Schedule'{schedule.name}'\n"
    # sort schedule by train:
    sorted_trips = sorted(schedule.trips, key=lambda t: t.train.name)

    # group schedule by train
    for train, trips in itertools.groupby(sorted_trips, key=lambda t: t.train.name):
        to_print += f"{train}\n"
        for trip in trips:
            to_print += f"\t{trip.service.start_time} - {trip.service.end_time}: {trip.service.first_stop.name} => {trip.service.last_stop.name}\n"

    return to_print


if __name__ == "__main__":
    loglevel = logging.DEBUG
    logging.basicConfig(
        level=loglevel,
        format="%(asctime)s - %(levelname)s@%(module)s:%(lineno)d - %(message)s",
        datefmt="[%H:%M:%S]",
    )

    s = schedule(get_basic_schedule())
    Log.info(pretty_print_schedule(s))
