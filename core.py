from functools import partial, wraps
from pathlib import Path
from time import sleep

from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from eventform import EventForm


def xpath(elt: WebElement | WebDriver, xpath: str):
    return elt.find_elements(By.XPATH, xpath)


def retry(max_attempts=3, delay=0.5):
    '''
    Adds retry behavior to functions which might try to click on obscured
    elements before they're ready (i.e. those covered by dropdowns/popups which
    are still closing), causing a ClickIntercepted exception.
    '''

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except ElementClickInterceptedException as e:
                    last_exception = e
                    if attempt == max_attempts:
                        break
                    print(
                        f'ClickIntercepted in {func.__name__!r}. Retrying momentarily...'
                    )
                    sleep(delay)

            if last_exception:
                raise last_exception

        return wrapper

    return decorator


def wait_until_clickable(driver: WebDriver, xpath: str, timeout: float = 5):
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))


def fill_text_field(
    driver: WebDriver,
    search: str,
    fill_value: str,
    exact: bool = False,
):
    print('Filling text', search, fill_value)
    match = f'normalize-space(text())="{search}"' if exact else f'contains(text(),"{search}")'
    elt = wait_until_clickable(driver, f'//*[{match}]/..')
    input = xpath(elt, './/input')[0]
    input.clear()
    input.send_keys(fill_value)


def enter_times(driver: WebDriver, startTime: str, endTime: str):
    startInput, endInput = xpath(driver, '//input[contains(@class,"dpicker")]')
    script = Path('fill_times.js').read_text()
    driver.execute_script(script, startInput, endInput, startTime, endTime)


@retry(max_attempts=3, delay=1)
def select_option(driver: WebDriver, desc_contains: str, option_contains: str):
    print('Selecting', desc_contains, ':', option_contains)

    dropdown = wait_until_clickable(
        driver,
        f'//*[contains(text(),"{desc_contains}")]/../..//*[contains(@class, "chosen-container")]'
    )
    dropdown.click()  # may not trigger
    dropdown.click()

    option = wait_until_clickable(
        driver,
        f"//li[contains(@class,'active-result') and contains(text(),'{option_contains}')]"
    )
    option.click()


def fill_rich_form(driver: WebDriver, contains_str: str, fill_value: str):
    # switch to HTML mode
    buttons = xpath(
        driver,
        f'//*[contains(text(),"{contains_str}")]/..//button[contains(@title,"Toggle html")]'
    )
    assert len(buttons) == 1
    buttons[0].click()

    form, *_ = xpath(
        driver,
        f'//*[contains(text(),"{contains_str}")]/..//textarea[@ng-model="html"]'
    )
    form.clear()
    form.click()
    form.send_keys(fill_value)


@retry(max_attempts=3, delay=1)
def click_input_with_label(
    driver: WebDriver,
    contains_str: str,
    selected_label: str,
):
    print('Clicking', contains_str, '=', selected_label)
    while True:
        elts = xpath(
            driver,
            f'//label[contains(text(),"{contains_str}")]/..//input[@aria-label="{selected_label}"]'
        )
        if elts:
            elts[0].click()
            break

        print(f'Waiting for element... ({contains_str!r}): {selected_label!r}')
        sleep(1)


def form_has_loaded(driver: WebDriver):
    return len(xpath(driver, '//field-group-grid-item')) == 18


def fill_event_registration_form(driver: WebDriver, data: EventForm):
    '''
    Fills out a specific event registration form using the provided form data.
    This can also serve as reference for automating other forms.
    '''

    select = partial(select_option, driver)
    rich = partial(fill_rich_form, driver)
    text = partial(fill_text_field, driver)
    click = partial(click_input_with_label, driver)

    select('Host', data.host)
    rich('About the event', data.about_html)
    text('Event Name', data.event_name)

    enter_times(driver, data.start_time, data.end_time)

    text('Event Location', data.location)
    click('Is this a virtual event?', data.is_virtual)
    click(
        'Is this event being held on campus or off campus?',
        data.on_or_off_campus
    )

    path = str(Path(data.cover_image_file_path).absolute())
    file_input = xpath(
        driver, '//input[@type="file" and contains(@ngf-pattern,".jpg")]'
    )[0]
    file_input.send_keys(path)

    for tag in data.tags:
        select('Tags', tag)

    rich('Event Notes', data.event_notes_html)
    text('Budget', data.budget, exact=True)
    text('Cost', data.cost, exact=True)
    text('Attendance Goal', data.attendance_goal, exact=True)

    click(
        'Department/Office/Program or a Recognized Student Organization?',
        data.event_creator_source
    )

    text('Contact Person', data.contact_person)
    text('Contact Email', data.contact_email)
    text('Primary Phone Number', data.contact_phone)
    text('RSVP Link', data.rsvp_link)

    click(
        'Where will payment for expenses come from?',
        data.payment_expenses_source,
    )

    text('Agency Account Number', data.agency_account_number)

    click('Will you be hiring/paying a speaker', data.hired_speaker)
    click('Will your event be AFTER 2:00', data.after_2pm_or_weekend)
    click(
        'Will you need to access the space before your event?',
        data.need_access_beforehand
    )
    text(
        'What is the estimated attendance for your event?',
        data.estimated_attendance
    )

    to_click = [
        (
            'Are you the person In charge of planning/managing this event for your organization?',
            data.is_submitter_in_charge
        ),
        (
            'Are you collaborating/partnering with other student organizations',
            data.is_multi_org_collab
        ),
        ('Does the event have content that is religious', data.is_religious),
        ('Will money be exchanged', data.is_money_exchanged),
        (
            'students, faculty or staff, will your event guests, participants, vendors, etc. need to park on campus?',
            data.is_parking_needed
        ),
        ('Do you plan to serve food at your event?', data.is_serving_food),
        (
            'Do you plan to have alcohol be served/consumed during this event?',
            data.is_serving_alcohol
        ),
        (
            'Is this event being held inside or outside?',
            data.inside_or_outside
        ),
    ]

    for search, option in to_click:
        click(search, option)

    select(
        'What facility/space do you want to reserve', data.facility_or_space
    )
    select('What space/room are you requesting', data.requested_room)

    text(
        "If you don't see the room you want, write it in here.",
        data.room_if_unlisted
    )

    select(
        'Please select the space setup needed for your event',
        data.requested_setup
    )

    click(
        'Do you need any additional equipment available from Conference Services?',
        data.need_additional_equipment
    )

    agrees = xpath(
        driver, '//label[text()="I agree" or text()="I agee"]/../input'
    )
    for agree in agrees:
        agree.click()


def submit_form(driver: WebDriver):
    xpath(driver, '//button[@id="submit-form-button"]')[0].click()


def submit_draft(driver: WebDriver):
    xpath(driver, '//button[contains(@class,"dropdown-toggle")]')[0].click()
    xpath(driver, '//a[text()="Save as Draft"]')[0].click()


def submit_preview(driver: WebDriver):
    xpath(driver, '//button[contains(@class,"dropdown-toggle")]')[0].click()
    xpath(driver, '//a[text()="Preview Response"]')[0].click()


def show_submission_menu(driver: WebDriver):
    print()
    print('Submission Actions:')
    print()
    print('1. Submit for approval')
    print('2. Preview Response')
    print('3. Save as Draft')
    print()
    choice = input('Choice (leave blank to skip): ').strip()

    match choice:
        case '1':
            submit_form(driver)
        case '2':
            submit_preview(driver)
        case '3':
            submit_draft(driver)
        case _:
            pass

    return choice
