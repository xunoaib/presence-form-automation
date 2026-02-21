import json
import os
import sys
import traceback
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Iterable

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from core import fill_event_registration_form, show_submission_menu
from eventform import EventForm

load_dotenv()


DATE_FILE = Path('submitted_dates.json')
START_TIME = time(hour=15, minute=45)
END_TIME = time(hour=18, minute=45)


def next_saturday(from_date=None):
    if from_date is None:
        from_date = date.today()

    days_ahead = (5 - from_date.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7

    return datetime.combine(from_date + timedelta(days=days_ahead), time.min)


def format_datetime(dt: datetime):
    return dt.strftime('%Y-%m-%d %H:%M')


def get_options(profile_location=None, binary_location=None):
    options = Options()

    if binary_location:
        options.binary_location = binary_location

    if profile_location:
        options.add_argument('-profile')
        options.add_argument(profile_location)

    return options


def get_next_sat_times(submitted_dates: Iterable[str] | None = None):
    submitted_dates = submitted_dates or []

    sat = next_saturday(date.today() + timedelta(days=1))
    while True:
        s = sat.strftime('%Y-%m-%d')
        if s not in submitted_dates:
            break
        sat += timedelta(days=7)

    start_time = datetime.combine(sat, START_TIME)
    end_time = datetime.combine(start_time, END_TIME)

    return start_time, end_time


def main():
    FORM_URL = os.environ['FORM_URL']

    submitted_dates = json.load(
        DATE_FILE.open()) if DATE_FILE.exists() else []
    assert isinstance(submitted_dates, list)

    start_time, end_time = get_next_sat_times(submitted_dates)

    print('Start:', start_time)
    print('End:  ', end_time)

    if (input('\nGood? [Y/n] ').lower() or 'y') != 'y':
        print('exiting')
        return

    data = EventForm.from_yaml(
        'config.yml',
        overrides={
            'start_time': format_datetime(start_time),
            'end_time': format_datetime(end_time),
            'about_html': Path('about.html').read_text(),
        }
    )

    options = get_options(
        profile_location=os.environ.get('FIREFOX_PROFILE_PATH'),
        binary_location=os.environ.get('FIREFOX_BIN_PATH'),
    )

    driver = webdriver.Firefox(options=options)
    driver.get(FORM_URL)

    if '-d' in sys.argv:
        __import__('pdb').set_trace()

    if (
        input('Automate filling out form now (without submitting)? [Y/n] ')
        or 'y'
    ).lower() != 'y':
        return

    choice = None
    try:
        fill_event_registration_form(driver, data)
        choice = show_submission_menu(driver)
    except Exception:
        traceback.print_exc()
    except KeyboardInterrupt:
        print('interrupted')

    print('philled')

    if choice == '1' and (input('\nUpdate dates? [Y/n] ').lower() or 'y') == 'y':
        print('saving')
        submitted_dates.append(start_time.strftime('%Y-%m-%d'))
        with DATE_FILE.open('w') as f:
            json.dump(submitted_dates, f)

    # print()
    # print('==== Entering Debugger ====')
    # print()
    # __import__('pdb').set_trace()


if __name__ == '__main__':
    main()
