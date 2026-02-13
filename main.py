import os
import sys
import traceback
from datetime import date, datetime, time, timedelta
from time import sleep

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from core import (fill_event_registration_form, form_has_loaded,
                  show_submission_menu)
from eventform import EventForm

load_dotenv()


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


def main():
    FORM_URL = os.environ['FORM_URL']

    start_time = next_saturday(date.today() + timedelta(days=14))
    start_time = datetime.combine(start_time, time(hour=15, minute=45))
    end_time = datetime.combine(start_time, time(hour=18, minute=45))

    data = EventForm.from_yaml(
        'config.yml',
        overrides={
            'start_time': format_datetime(start_time),
            'end_time': format_datetime(end_time)
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

    print('Waiting for form to be ready... ', end='', flush=True)
    while not form_has_loaded(driver):
        sleep(1)
    print('done')

    try:
        fill_event_registration_form(driver, data)
        show_submission_menu(driver)
    except Exception:
        traceback.print_exc()
    except KeyboardInterrupt:
        print('interrupted')

    print()
    print('==== Entering Debugger ====')
    print()
    __import__('pdb').set_trace()


if __name__ == '__main__':
    main()
