# Automated Data Entry for Presence.io Forms

This project automates data entry for a specific Presence.io form using
Selenium, XPath, and a custom YAML data template. It can easily be adapted for
other forms.

# Instructions

- Copy `.env-example` to `.env`
- Copy `example-config.yml` to `config.yml`
- Edit `core.py` to match your form (i.e. XPath patterns, actions, and substitutions)
- Add/remove any desired fields to `eventform.py`

# Configuration

## Environment Variables

- `FORM_URL`: URL of the form to fill out (i.e. `https://yourdomain.presence.io/admin/Event/create`)
- `FIREFOX_BIN_PATH`: Path to Firefox executable (optional) (i.e. `/snap/firefox/current/usr/lib/firefox/firefox`)
- `FIREFOX_PROFILE_PATH`: Path to Firefox profile (i.e. `/home/user/.mozilla/firefox/xxxxxxxx.selenium`)

See `.env-example` for examples.

## Form Data

Form data can be directly passed to an `EventForm` object, or loaded from a
YAML template and overridden as needed.
