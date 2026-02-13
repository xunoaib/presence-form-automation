from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class EventForm:
    start_time: str
    end_time: str
    host: str
    event_name: str
    about_html: str
    location: str
    contact_person: str
    is_virtual: str
    tags: list[str]
    contact_email: str
    contact_phone: str
    attendance_goal: str
    need_access_beforehand: str
    estimated_attendance: str
    agency_account: str
    after_2pm_or_weekend: str
    hired_speaker: str
    agency_account_number: str
    payment_expenses_source: str
    event_creator_source: str
    is_submitter_in_charge: str
    is_multi_org_collab: str
    is_religious: str
    is_money_exchanged: str
    is_parking_needed: str
    is_serving_food: str
    is_serving_alcohol: str
    inside_or_outside: str
    facility_or_space: str
    requested_room: str
    room_if_unlisted: str
    requested_setup: str
    need_additional_equipment: str
    event_notes_html: str
    budget: str
    cost: str
    rsvp_link: str
    cover_image_file_path: str
    on_or_off_campus: str

    @classmethod
    def from_yaml(
        cls,
        yaml_path: str | Path,
        overrides: dict[str, Any] | None = None,
    ):
        yaml_path = Path(yaml_path)

        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f) or {}

        if overrides:
            config.update(overrides)

        for k, v in config.items():
            if isinstance(v, bool):
                config[k] = 'Yes' if v else 'No'

        return cls(**config)
