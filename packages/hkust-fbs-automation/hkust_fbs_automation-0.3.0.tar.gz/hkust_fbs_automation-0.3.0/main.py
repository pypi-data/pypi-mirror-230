import argparse
import logging
from typing import List

from fbs import Facility


def print_facilities(facilities: List[Facility]):
    id_max_len = max([len("ID")] + [len(str(x.id)) for x in facilities])
    name_max_len = max([len("Location")] + [len(str(x.name)) for x in facilities])
    location_max_len = max([len("Name")] + [len(str(x.location)) for x in facilities])
    format_string = (
        f"{{0: >{id_max_len}}} {{2: <{location_max_len}}} {{1: <{name_max_len}}}"
    )
    facilities = sorted(facilities, key=lambda x: x.id)
    logging.info(format_string.format("ID", "Name", "Location"))
    logging.info("-" * (id_max_len + name_max_len + location_max_len))
    for x in facilities:
        logging.info(format_string.format(x.id, x.name, x.location))


def list_handler(args):
    from fbs import Client
    fbs = Client((args.username, args.password))
    print_facilities(fbs.list_facilities())


def book_handler(args):
    from fbs import Client
    fbs = Client((args.username, args.password))
    fbs.auto_book(args.ids, args.timeslot_date, args.start_time, args.end_time)


def main():
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s: %(message)s",
        level=logging.INFO
    )

    parser = argparse.ArgumentParser("HKUST FBS Automation")
    parser.add_argument(
        "--username",
        help="Your ITSC username, without the '@connect.ust.hk'."
    )
    parser.add_argument(
        "--password",
        help="Your ITSC password."
    )

    subparsers = parser.add_subparsers(required=True)

    parser_list = subparsers.add_parser(
        "list", help="List all available facilities for you."
    )
    parser_list.set_defaults(func=list_handler)

    parser_book = subparsers.add_parser(
        "book",
        help="Book the specified facility for you. "
             "If the specified timeslot cannot be booked yet, "
             "the script will wait until it become bookable (nearly, since login also needs time).",
    )
    parser_book.add_argument(
        "ids",
        metavar="ID(s)",
        nargs="*",
        help="The facility ID(s) you want to book. "
             "If more than one ID is specified, separate them with a space inbetween."
             "The ID(s) can be found by the 'list' subcommand.",
    )
    parser_book.add_argument(
        "start_time",
        help="The start time of the timeslots you want to book. "
             "All timeslots inbetween the start_time and end_time will try to be booked. "
             "Example: '12:34', '23:45', etc. ",
    )
    parser_book.add_argument(
        "end_time",
        help="The end time of the timeslot you want to book. "
             "All timeslots inbetween the start_time and end_time will try to be booked."
             "Example: '12:34', '23:45', etc. ",
    )
    parser_book.add_argument(
        "timeslot_date",
        help="The date of the timeslot you want to book. "
             "If the timeslot is currently un-bookable, the script will wait until it becomes bookable.",
    )
    parser_book.set_defaults(func=book_handler)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
