# Automated Data Entry for Presence.io Forms

This project automates data entry for a specific Presence.io form using
Selenium, XPath, and a custom YAML data template. It can easily be adapted for
other forms.

# Instructions

- Copy `.env-example` to `.env`
- Copy `example-config.yml` to `config.yml`
- Edit `core.py` to match your form (i.e. XPath patterns, actions, and substitutions)
- Add/remove any desired data fields to `eventform.py`
- Create a new Firefox browser profile for Selenium to use
- In that profile, log in to your presence.io subdomain
- Run `uv run main.py`

# Configuration

## Environment Variables

- `FORM_URL`: URL of the form to visit and fill out.
- `FIREFOX_PROFILE_PATH`: Path to Firefox profile directory.
- `FIREFOX_BIN_PATH`: Path to Firefox executable (optional).

See `.env-example` for examples.

## Form Data

Form data can be directly passed to an `EventForm` object, or loaded from a
YAML template and overridden as needed.

See `example-config.yml` for examples.
