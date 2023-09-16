import logging
from datetime import datetime, timedelta, date, time
from typing import List, NamedTuple, Tuple, Optional

import requests

import auth


def sleep_until(target):
    import time

    now = datetime.now()
    delta = target - now
    if delta > timedelta():
        time.sleep(delta.total_seconds())
        return True
    else:
        return False


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
    status: str = "Available"

    def __str__(self) -> str:
        return f"{self.start_time_str()}-{self.end_time_str()}"

    def __repr__(self) -> str:
        return self.__str__()

    def date_str(self):
        return self.date.strftime("%Y-%m-%d")

    def start_time_str(self):
        return self.start_time.strftime("%H:%M")

    def end_time_str(self):
        return self.end_time.strftime("%H:%M")


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
    def __init__(self, username: Optional[str], password: Optional[str]) -> None:
        self.client = self.create_client(username, password)

    @staticmethod
    def create_client(username: Optional[str], password: Optional[str]):
        if username is None or password is None:
            logging.info("Logging in manually...")
            tokens = auth.auth()
        else:
            logging.info(f"Logging in using credentials of {username}...")
            tokens = auth.auth((username, password))
        access_token, id_token, student_id = tokens

        client = requests.session()
        client.mount("https://", auth.TLSAdapter())
        client.headers["authorization"] = f"Bearer {id_token}"
        client.params = {"userType": "01", "ustID": student_id}

        logging.debug(f"Created a new FBS client {client.__dict__}.")
        logging.info("Logged in.")
        return client

    def auto_book(self, ids: List[str], timeslot_date: str, start_time: str, end_time: str, no_confirm: bool = False):
        ids = [int(x) for x in ids]
        timeslot_date = date.fromisoformat(timeslot_date)
        timeslot_start_time = time.fromisoformat(start_time)
        timeslot_end_time = time.fromisoformat(end_time)

        close_time = time.fromisoformat("00:00")
        open_time = time.fromisoformat("08:00")

        if close_time <= datetime.now().time() < open_time:
            target_time = datetime.combine(datetime.now(), open_time)
            logging.info(f"The FBS is closed. "
                         f"Waiting until {target_time.isoformat()}...")
            if not no_confirm:
                logging.warning("Since we are going to wait, "
                                "the booking will be made without confirmation to ensure the booking can be made ASAP.")
                no_confirm = True
            sleep_until(target_time)

        facilities_timeslots = {
            facility_id: self.list_facility_timeslots(
                facility_id,
                timeslot_date,
                timeslot_date,
                timeslot_start_time,
                timeslot_end_time
            )
            for facility_id in ids
        }

        if not no_confirm:
            facilities_id_obj = {x.id: x for x in self.list_facilities()}
            logging.info("The following facilities and timeslots are going to be booked:")
            for facility_id, timeslots in facilities_timeslots.items():
                logging.info(f"\t")
                logging.info(f"\tFacility ID: {facility_id}")
                logging.info(f"\tFacility Location: {facilities_id_obj[facility_id].location}")
                logging.info(f"\tFacility Name: {facilities_id_obj[facility_id].name}")
                logging.info(f"\tTimeslot Date: {timeslot_date}")
                logging.info("\tTimeslot(s):")
                for timeslot in timeslots:
                    logging.info(f"\t\t{timeslot}")
            logging.info(f"\t")
            logging.info("Please confirm the booking. (y/N)")
            if input().lower() != "y":
                logging.critical("The booking is cancelled.")
                return

        available_time = datetime.combine(timeslot_date - timedelta(days=7), open_time)
        if close_time <= datetime.now().time() < open_time or datetime.now() < available_time:
            target_time = max(datetime.combine(datetime.now(), open_time), available_time)
            logging.info(f"The FBS is closed or the specified timeslot date has not become available yet. "
                         f"Waiting until {target_time.isoformat()}...")
            sleep_until(target_time)

        for facility_id in ids:
            for timeslot in facilities_timeslots[facility_id]:
                try:
                    self.book(facility_id, timeslot)
                    # Break if booked successfully.
                    # Because only one timeslot for one day and one facility is allowed.
                    break
                except BookingError:
                    logging.warning(f"Couldn't book the timeslot {timeslot} of the facility {facility_id}.",
                                    exc_info=True)

    def book(
            self,
            facility_id: int,
            timeslot: Timeslot
    ):
        logging.info(f"Booking the timeslot {timeslot} of the facility {facility_id}...")

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
                result = BookingResult(
                    resp_obj["ustID"],
                    result["facilityID"],
                    result["timeslotDate"],
                    result["startTime"],
                    result["endTime"],
                    result["bookingRef"],
                )
                logging.info(f"Booked the timeslot {timeslot} of the facility {facility_id}.")
                logging.info(f"Booking result: {result}")
                return result
            case _:
                raise BookingError(f"({resp_obj['status']}) {resp_obj['message']}")

    def list_facilities(self):
        logging.info("Retrieving the facilities...")
        resp = self.client.get("https://w5.ab.ust.hk/msapi/fbs/facilities")
        resp.raise_for_status()
        facilities = [Facility.from_dict(**k) for k in resp.json()["facility"]]
        logging.info(f"Retrieved {len(facilities)} facilities.")
        return facilities

    def list_facility_timeslots(self,
                                facility_id: int,
                                start_date: date,
                                end_date: date,
                                start_time: time = time.min,
                                end_time: time = time.max):
        logging.info(f"Retrieving the timeslots of the facility {facility_id}...")
        params = {
            "facilityID": str(facility_id),
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
        }
        resp = self.client.get("https://w5.ab.ust.hk/msapi/fbs/facilityTimeslot", params=params)
        resp.raise_for_status()
        resp_obj = resp.json()
        timeslots = [
            Timeslot(
                date.fromisoformat(k["timeslotDate"]),
                time.fromisoformat(k["startTime"]),
                time.fromisoformat(k["endTime"]),
                k["timeslotStatus"],
            )
            for k in resp_obj["timeslot"]
        ]
        timeslots = [x for x in timeslots if start_time <= x.start_time and x.end_time <= end_time]
        logging.info(f"Retrieved the timeslots {timeslots} of the facility {facility_id}.")
        return timeslots
