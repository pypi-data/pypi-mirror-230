import arrow
import csv
import datetime
from enum import Enum
import ics.icalendar
import json
import logging
import pathlib
import os
import sys
import typer
from typing_extensions import Annotated

from nytid.signup import hr
from nytid.signup import sheets
import operator

from nytid.cli import courses as coursescli
from nytid.cli.signupsheets import SIGNUPSHEET_URL_PATH
from nytid import courses as courseutils
from nytid import schedules as schedutils
from nytid.signup import hr
from nytid.signup import sheets

import appdirs

try:
    import canvasapi
    import canvaslms.cli

    dirs_canvas = appdirs.AppDirs("canvaslms", "dbosk@kth.se")

    canvaslms_config = canvaslms.cli.read_configuration(
        f"{dirs_canvas.user_config_dir}/config.json"
    )

    CANVAS_SERVER, CANVAS_TOKEN = canvaslms.cli.login.load_credentials(canvaslms_config)

    if CANVAS_SERVER and CANVAS_TOKEN:
        canvas_session = canvasapi.Canvas(
            os.environ["CANVAS_SERVER"], os.environ["CANVAS_TOKEN"]
        )
    else:
        canvas_session = None
        logging.warning("Can't load Canvas credentials, run `canvaslms login`")
except ImportError as err:
    logging.warning(f"Can't import Canvas: {err}")
    canvas_session = None
except Exception as err:
    logging.warning(f"Can't load Canvas credentials: {err}")
    canvas_session = None
try:
    import ladok3
    import ladok3.cli

    dirs_ladok = appdirs.AppDirs("ladok", "dbosk@kth.se")

    LADOK_INST, LADOK_VARS = ladok3.cli.load_credentials(
        "f{dirs_ladok.user_config_dir}/config.json"
    )

    if LADOK_INST and LADOK_VARS:
        ladok_session = ladok3.LadokSession(LADOK_INST, LADOK_VARS)
    else:
        ladok_session = None
        logging.warning("Can't load LADOK credentials, run `ladok login`")
except ImportError as err:
    logging.warning(f"Can't import ladok3, not using LADOK data: {err}")
    ladok_session = None
except Exception as err:
    logging.warning(f"Can't load LADOK credentials: {err}")
    ladok_session = None
import cachetools
from nytid.signup import sheets
from nytid.signup import utils
from nytid.signup import hr
import re
import typerconf

AMANUENSIS_CONTRACT_PATH = "amanuensis.contract_path"

cli = typer.Typer(name="hr", help="Manage sign-up sheets for teaching")


@cachetools.cached(cache={})
def get_canvas_courses(course_regex):
    """
    Returns a list of Canvas course objects matching the given course_regex.
    """
    courses = list(canvaslms.cli.courses.filter_courses(canvas_session, course_regex))
    return courses


@cachetools.cached(cache={})
def get_canvas_users(username_regex, course_regex):
    """
    Returns a list of Canvas user objects matching the given username_regex.
    Searches for username_regex in the courses matching course_regex.
    """
    courses = get_canvas_courses(course_regex)
    users = list(canvaslms.cli.users.filter_users(courses, username_regex))
    return users


def get_canvas_user(username, course_regex):
    """
    Takes a username and returns a Canvas user object.
    Searches for username in the courses matching course_regex.
    """
    users = get_canvas_users(".*", course_regex)
    username = username.strip()
    for user in users:
        if user.login_id.split("@")[0] == username or user.login_id == username:
            return user
    raise ValueError(f"Can't find {username} in Canvas")


def get_ladok_user(canvas_user):
    """
    Takes a Canvas user object and returns a LADOK student object.
    """
    try:
        return ladok_session.get_student(canvas_user.integration_id)
    except KeyError as err:
        raise KeyError(f"can't look up {canvas_user} in LADOK: {err}")


def to_hours(td):
    return td.total_seconds() / 60 / 60


def push_forward(start, end, push_start):
    """
    Takes a start and end date and pushes them forward so that start becomes
    push_start.
    """
    if push_start > start:
        end += push_start - start
        start = push_start

    return start, end


try:
    default_username = os.environ["USER"]
except KeyError:
    default_username = None

username_opt = typer.Option(
    help="Username to filter sign-up sheet for, "
    "defaults to logged in user's username."
)
detailed_opt = typer.Option(help="Output detailed user data.")
user_regex_opt = typer.Option(
    "--user", help="Regex to match TAs' usernames that " "should be included."
)
start_date_opt = typer.Option(
    help="The start date (inclusive, <=), "
    "when unset includes "
    "everything in the sign-up sheet. "
    "Set this to decide what to include from "
    "the sign-up sheet.",
    formats=["%Y-%m-%d"],
)
end_date_opt = typer.Option(
    help="The end date (not inclusive, <), "
    "when unset includes "
    "everything in the sign-up sheet. "
    "Set this to decide what to include from "
    "the sign-up sheet.",
    formats=["%Y-%m-%d"],
)
push_start_opt = typer.Option(
    help="Push the dates of the contract so that it "
    "starts at this date. "
    "This keeps the same percentage.",
    formats=["%Y-%m-%d"],
)
set_start_opt = typer.Option(
    help="Force the start date of the contract to "
    "this date. Might modify percentage.",
    formats=["%Y-%m-%d"],
)
set_end_opt = typer.Option(
    help="Force the end date of the contract to " "this date. Might modify percentage.",
    formats=["%Y-%m-%d"],
)


@cli.command()
def users(
    course_regex: Annotated[str, coursescli.course_arg_regex],
    register: Annotated[str, coursescli.register_opt_regex] = coursescli.MINE,
    detailed: Annotated[bool, detailed_opt] = False,
):
    """
    Prints the list of all usernames booked on the course.
    """
    registers = coursescli.registers_regex(register)
    courses = {}
    for course_reg in coursescli.courses_regex(course_regex, registers):
        try:
            courses[course_reg] = courseutils.get_course_config(*course_reg)
        except KeyError as err:
            logging.warning(err)
        except PermissionError as err:
            course, register = course_reg
            logging.warning(f"You don't have access to {course} in {register}: {err}")
    if not courses:
        sys.exit(1)

    booked = []
    for (course, register), config in courses.items():
        url = config.get(SIGNUPSHEET_URL_PATH)
        if "docs.google.com" in url:
            url = sheets.google_sheet_to_csv_url(url)
        booked += sheets.read_signup_sheet_from_url(url)

    for user in hr.hours_per_TA(booked):
        user_obj = user

        if detailed:
            try:
                user_obj = get_canvas_user(user, course_regex)
            except Exception as err:
                logging.warning(f"Can't look up {user} in Canvas: {err}")
            else:
                try:
                    user_obj = get_ladok_user(user_obj)
                except Exception as err:
                    logging.warning(
                        f"Can't look up {user} ({user_obj}) in LADOK: {err}"
                    )
                    pass
        print(user_obj)


@cli.command()
def time(
    course_regex: Annotated[str, coursescli.course_arg_regex],
    register: Annotated[str, coursescli.register_opt_regex] = coursescli.MINE,
    detailed: Annotated[bool, detailed_opt] = False,
):
    """
    Summarizes the time spent on teaching the course(s).
    """
    registers = coursescli.registers_regex(register)
    courses = {}
    for course_reg in coursescli.courses_regex(course_regex, registers):
        try:
            courses[course_reg] = courseutils.get_course_config(*course_reg)
        except KeyError as err:
            logging.warning(err)
        except PermissionError as err:
            course, register = course_reg
            logging.warning(f"You don't have access to {course} in {register}: {err}")
    if not courses:
        sys.exit(1)

    booked = []
    for (course, register), config in courses.items():
        url = config.get(SIGNUPSHEET_URL_PATH)
        if "docs.google.com" in url:
            url = sheets.google_sheet_to_csv_url(url)
        booked += sheets.read_signup_sheet_from_url(url)

    h_per_student = hr.hours_per_student(booked)

    for event, hours in h_per_student.items():
        print(f"{event}: {to_hours(hours):.2f} h/student")

    print(
        f"Booked: {to_hours(hr.total_hours(booked)):.2f} h "
        f"({to_hours(hr.max_hours(booked)):.2f} h)\n"
    )

    print("# Amanuenser")

    amanuensis = hr.compute_amanuensis_data(booked)

    for user, data in amanuensis.items():
        if not user:
            continue
        user_obj = user

        if detailed:
            try:
                user_obj = get_canvas_user(user, course_regex)
            except Exception as err:
                logging.warning(f"Can't look up {user} in Canvas: {err}")
            else:
                try:
                    user_obj = get_ladok_user(user_obj)
                except Exception as err:
                    logging.warning(
                        f"Can't look up {user} ({user_obj}) in LADOK: {err}"
                    )
                    pass
        print(user_obj, end="")
        print(
            f": {data[2]:.2f} h, "
            f"{100*hr.compute_percentage(*data):.1f}%: "
            f"{data[0].format('YYYY-MM-DD')}--{data[1].format('YYYY-MM-DD')}"
        )

    print()
    print("# Hourly")

    for user, hours in hr.hours_per_TA(booked).items():
        if not user or user in amanuensis:
            continue
        user_obj = user

        if detailed:
            try:
                user_obj = get_canvas_user(user, course_regex)
            except Exception as err:
                logging.warning(f"Can't look up {user} in Canvas: {err}")
            else:
                try:
                    user_obj = get_ladok_user(user_obj)
                except Exception as err:
                    logging.warning(
                        f"Can't look up {user} ({user_obj}) in LADOK: {err}"
                    )
                    pass
        print(user_obj, end="")
        print(f": {to_hours(hours):.2f} h")


amanuensis = typer.Typer(name="amanuensis", help="Manage amanuensis employment")
cli.add_typer(amanuensis)


@amanuensis.command(name="create")
def amanuens_cmd(
    user_regex: Annotated[str, user_regex_opt] = ".*",
    start: Annotated[datetime.datetime, start_date_opt] = None,
    end: Annotated[datetime.datetime, end_date_opt] = None,
    push_start: Annotated[datetime.datetime, push_start_opt] = None,
    set_start: Annotated[datetime.datetime, set_start_opt] = None,
    set_end: Annotated[datetime.datetime, set_end_opt] = None,
    course_regex: Annotated[str, coursescli.course_arg_regex] = ".*",
    register: Annotated[str, coursescli.register_opt_regex] = coursescli.MINE,
):
    """
    Computes amanuensis data for a TA.
    """
    if start:
        start = start.astimezone()
    if push_start:
        push_start = push_start.astimezone()
    if set_start:
        set_start = set_start.astimezone()
    if set_end:
        set_end = set_end.astimezone()
    registers = coursescli.registers_regex(register)
    courses = {}
    for course_reg in coursescli.courses_regex(course_regex, registers):
        try:
            courses[course_reg] = courseutils.get_course_config(*course_reg)
        except KeyError as err:
            logging.warning(err)
        except PermissionError as err:
            course, register = course_reg
            logging.warning(f"You don't have access to {course} in {register}: {err}")
    if not courses:
        sys.exit(1)

    booked = []
    for (course, register), config in courses.items():
        url = config.get(SIGNUPSHEET_URL_PATH)
        if "docs.google.com" in url:
            url = sheets.google_sheet_to_csv_url(url)
        booked += sheets.read_signup_sheet_from_url(url)

    booked = sheets.filter_events_by_date(booked, start, end)

    amanuensis = hr.compute_amanuensis_data(booked, begin_date=start, end_date=end)

    user_pattern = re.compile(user_regex)
    first_print = True
    path = pathlib.Path("./")
    try:
        path = pathlib.Path(typerconf.get(AMANUENSIS_CONTRACT_PATH))
    except KeyError as err:
        logging.warning(
            f"Can't find {AMANUENSIS_CONTRACT_PATH} in config, "
            f"storing contract data in `{path}`. Set by running "
            f"`nytid config {AMANUENSIS_CONTRACT_PATH} -s <path>`."
        )
    for user in amanuensis:
        if not user_pattern.match(user):
            continue
        if first_print:
            first_print = False
        else:
            print("\n")

        data = amanuensis[user]

        start = data[0]
        end = data[1]
        hours = data[2]
        if push_start:
            push_start = arrow.Arrow(push_start.year, push_start.month, push_start.day)
            start, end = push_forward(start, end, push_start)
        data = list(data)
        if set_start:
            start = data[0] = set_start
        if set_end:
            end = data[1] = set_end

        print(
            f"{user}: {hours:.2f} h, "
            f"{round(100*hr.compute_percentage(*data))}%: "
            f"{start.date()}--{end.date()}"
        )

        events = sheets.filter_events_by_TA(user, booked)
        events = filter(lambda x: user in sheets.get_booked_TAs_from_csv(x)[0], booked)
        events = list(
            map(lambda x: x[0 : len(sheets.SIGNUP_SHEET_HEADER)] + [user], events)
        )
        for event, hours in hr.hours_per_event(events).items():
            print(f"{event}: {to_hours(hours)}")

        filename = f"{user}.{datetime.datetime.now().isoformat()}.json"

        path.mkdir(parents=True, exist_ok=True)

        with open(path / filename, "w") as outfile:
            json.dump(
                {
                    "user": user,
                    "start": start.isoformat() if start else None,
                    "set_start": set_start.isoformat() if set_start else None,
                    "push_start": push_start.isoformat() if push_start else None,
                    "end": end.isoformat() if end else None,
                    "set_end": set_end.isoformat() if set_end else None,
                    "events": events,
                },
                outfile,
                indent=2,
            )
