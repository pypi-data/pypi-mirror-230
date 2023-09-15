import logging
from datetime import datetime, timedelta, date, time
from typing import List, NamedTuple, Tuple

import requests

import auth

TIME_UPPER_BOUND = time.fromisoformat("09:00")
TIME_LOWER_BOUND = time.fromisoformat("22:00")
TIMESLOT_INTERVAL = timedelta(hours=1)


class Facility(NamedTuple):
    id: int
    name: str
    location: str

    # noinspection PyPep8Naming
    @staticmethod
    def from_dict(facilityID: int, facilityName: str, location: str):
        return Facility(facilityID, facilityName, location)


class Timeslot(NamedTuple):
    date: datetime.date
    start_time: datetime.time
    end_time: datetime.time

    def __str__(self) -> str:
        return f"{self.start_time.isoformat()}-{self.end_time.isoformat()}"

    def __repr__(self) -> str:
        return self.__str__()

    def date_str(self):
        return self.date.strftime("%Y-%m-%d")

    def start_time_str(self):
        return self.start_time.strftime("%H:%M")

    def end_time_str(self):
        return self.end_time.strftime("%H:%M")


def generate_timeslots(d: datetime.date) -> List[Timeslot]:
    def add_time_timedelta(t, delta):
        return (datetime.combine(date.today(), t) + delta).time()

    timeslots = []
    cursor_upper = TIME_UPPER_BOUND
    cursor_lower = add_time_timedelta(cursor_upper, TIMESLOT_INTERVAL)
    while cursor_lower <= TIME_LOWER_BOUND:
        timeslots.append(Timeslot(d, cursor_upper, cursor_lower))
        cursor_upper = cursor_lower
        cursor_lower = add_time_timedelta(cursor_upper, TIMESLOT_INTERVAL)
    return timeslots


def find_timeslots(d: datetime.date, start_time: datetime.time, end_time: datetime.time):
    return [
        x
        for x in generate_timeslots(d)
        if start_time <= x.start_time and x.end_time <= end_time
    ]


def sleep_until(target):
    import time

    now = datetime.now()
    delta = target - now
    if delta > timedelta(0):
        time.sleep(delta.total_seconds())
        return True
    else:
        return False


class BookingError(Exception):
    pass


class BookingResult(NamedTuple):
    ust_id: str
    facility_id: int
    timeslot_date: str
    start_time: str
    end_time: str
    booking_ref: int


class Client:
    def __init__(self, credentials: Tuple[str, str] = None) -> None:
        self.client = self.create_client(credentials)

    @staticmethod
    def create_client(credentials=None):
        tokens = auth.auth(credentials)
        access_token, id_token, student_id = tokens

        client = requests.session()
        client.mount("https://", auth.TLSAdapter())
        client.headers["authorization"] = f"Bearer {id_token}"
        client.params = {"userType": "01", "ustID": student_id}
        return client

    def auto_book(self, ids: List[str], timeslot_date: str, start_time: str, end_time: str):
        timeslot_date = date.fromisoformat(timeslot_date)
        timeslot_start_time = time.fromisoformat(start_time)
        timeslot_end_time = time.fromisoformat(end_time)

        # Wait until the facility become (nearly) bookable.
        bookable_time = datetime.combine(
            timeslot_date - timedelta(weeks=1),
            time.fromisoformat("07:59")
        )
        if datetime.now() < bookable_time:
            logging.info(
                f"The specific timeslot cannot be booked yet. "
                f"Waiting until {bookable_time.isoformat()}..."
            )
            sleep_until(bookable_time)

        close_time = datetime.combine(date.today(), time.fromisoformat("00:00"))
        open_time = datetime.combine(date.today(), time.fromisoformat("08:00"))
        if close_time <= datetime.now() < open_time:
            # Wait for FBS to open.
            logging.info(
                f"The FBS is closed. "
                f"Waiting until {open_time.isoformat()} for its opening..."
            )
            sleep_until(open_time)

        for facility_id in ids:
            for timeslot in find_timeslots(
                    timeslot_date,
                    timeslot_start_time,
                    timeslot_end_time,
            ):
                try:
                    book_result = self.book(facility_id, timeslot)
                    logging.info(f"Booked the timeslot {timeslot} of facility {facility_id}.")
                    logging.info(f"Booking result: {book_result}")
                except BookingError:
                    logging.warning(f"Couldn't book the timeslot {timeslot} of facility {facility_id}.", exc_info=True)

    def book(
            self,
            facility_id: str,
            timeslot: Timeslot
    ):
        params = {
            "facilityID": str(facility_id),
            "timeslotDate": timeslot.date_str(),
            "startTime": timeslot.start_time_str(),
            "endTime": timeslot.end_time_str(),
            "cancelInd": "N",
        }

        resp = self.client.post("https://w5.ab.ust.hk/msapi/fbs/book", params=params)
        resp.raise_for_status()
        resp_obj = resp.json()
        match (resp_obj["status"]):
            case "200":
                result = resp_obj["bookingResult"][0]
                return BookingResult(
                    resp_obj["ustID"],
                    result["facilityID"],
                    result["timeslotDate"],
                    result["startTime"],
                    result["endTime"],
                    result["bookingRef"],
                )
            case _:
                raise BookingError(f"({resp_obj['status']}) {resp_obj['message']}")

    def list_facilities(self):
        resp = self.client.get("https://w5.ab.ust.hk/msapi/fbs/facilities")
        resp.raise_for_status()
        return [Facility.from_dict(**k) for k in resp.json()["facility"]]
