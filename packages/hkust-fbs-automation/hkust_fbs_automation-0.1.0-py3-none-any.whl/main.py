import argparse
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import NamedTuple, List

import requests
from requests import Session, HTTPError

import auth
from auth import TLSAdapter


def sleep_until(target):
    now = datetime.now()
    delta = target - now
    if delta > timedelta(0):
        time.sleep(delta.total_seconds())


def raise_for_status(resp: requests.Response):
    resp.raise_for_status()
    if 'status' in resp.json() and 'message' in resp.json():
        http_error_msg = None
        if 400 <= int(resp.json()['status']) < 500:
            http_error_msg = (
                f"{int(resp.json()['status'])} Error: {int(resp.json()['message'])} for url: {resp.url}"
            )
        elif 500 <= int(resp.json()['status']) < 600:
            http_error_msg = (
                f"{int(resp.json()['status'])} Error: {int(resp.json()['message'])} for url: {resp.url}"
            )
        if http_error_msg:
            raise HTTPError(http_error_msg, response=resp)


class Facility(NamedTuple):
    id: int
    name: str
    location: str

    # noinspection PyPep8Naming
    @staticmethod
    def from_dict(facilityID: int, facilityName: str, location: str):
        return Facility(facilityID, facilityName, location)


def list_facilities(client: Session):
    resp = client.get('https://w5.ab.ust.hk/msapi/fbs/facilities')
    raise_for_status(resp)
    return [Facility.from_dict(**k) for k in resp.json()['facility']]


def print_facilities(facilities: List[Facility]):
    id_max_len = max([len("ID")] + [len(str(x.id)) for x in facilities])
    name_max_len = max([len("Location")] + [len(str(x.name)) for x in facilities])
    location_max_len = max([len("Name")] + [len(str(x.location)) for x in facilities])
    format_string = f"{{0: >{id_max_len}}} {{2: <{location_max_len}}} {{1: <{name_max_len}}}"
    facilities = sorted(facilities, key=lambda x: x.id)
    print(format_string.format("ID", "Name", "Location"))
    print("-" * (id_max_len + name_max_len + location_max_len))
    for x in facilities:
        print(format_string.format(x.id, x.name, x.location))


def book(client: Session, facility_id: str, start_time: str, end_time: str, timeslot_date: str, cancel: str = None):
    params = {
        'facilityID': str(facility_id),
        'startTime': start_time,
        'endTime': end_time,
        'timeslotDate': timeslot_date,
        'cancelInd': 'N'
    }
    if cancel is not None:
        params['cancelInd'] = 'Y'
        params['bookingRef'] = cancel

    resp = client.post('https://w5.ab.ust.hk/msapi/fbs/book', params=params)
    raise_for_status(resp)
    return resp.json()


def create_client(credentials=None, use_cache=False):
    tokens_path = Path('./tokens.json')
    if (
            use_cache and
            tokens_path.exists() and
            datetime.fromtimestamp(tokens_path.stat().st_mtime) - datetime.now() < timedelta(hours=6)
    ):
        access_token, id_token, student_id = json.loads(tokens_path.read_text())
    else:
        tokens = auth.auth(credentials)
        access_token, id_token, student_id = tokens
        tokens_path.write_text(json.dumps(tokens))

    client = requests.session()
    client.mount("https://", TLSAdapter())
    client.headers['authorization'] = f'Bearer {id_token}'
    client.params = {'userType': '01', 'ustID': student_id}
    return client


def list_handler(args):
    credentials = None
    if args.username and args.password:
        credentials = (args.username, args.password)
    client = create_client(credentials=credentials, use_cache=args.use_cache)
    facilities = list_facilities(client)
    print_facilities(facilities)


def book_handler(args):
    sleep_until(datetime.now().replace(hour=7, minute=59, second=0, microsecond=0))
    credentials = None
    if args.username and args.password:
        credentials = (args.username, args.password)
    client = create_client(credentials=credentials, use_cache=args.use_cache)

    sleep_until(datetime.now().replace(hour=8, minute=0, second=0, microsecond=0))
    book_result = book(client, args.id, args.start_time, args.end_time, args.timeslot_date)
    print(json.dumps(book_result, indent=4))


def main():
    parser = argparse.ArgumentParser("HKUST FBS Automation")
    parser.add_argument("--use-cache", action='store_true')
    parser.add_argument("--username")
    parser.add_argument("--password")

    subparsers = parser.add_subparsers(required=True)

    parser_list = subparsers.add_parser("list")
    parser_list.set_defaults(func=list_handler)

    parser_book = subparsers.add_parser("book")
    parser_book.set_defaults(func=list_handler)
    parser_book.add_argument('--id')
    parser_book.add_argument('--start-time')
    parser_book.add_argument('--end-time')
    parser_book.add_argument('--timeslot-date')

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
