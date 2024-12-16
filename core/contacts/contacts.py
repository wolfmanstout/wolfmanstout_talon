import json
import logging
from dataclasses import dataclass
from pathlib import Path

from talon import Context, Module, actions, resource

from ..user_settings import track_csv_list

mod = Module()
ctx = Context()

mod.list("contact_names", desc="Contact first names, full names, and nicknames.")
mod.list("contact_emails", desc="Maps names to email addresses.")
mod.list("contact_full_names", desc="Maps names to full names.")


@dataclass
class Contact:
    email: str
    full_name: str
    nicknames: list[str]
    pronunciations: dict[str, str]

    @classmethod
    def from_json(cls, contact):
        email = contact.get("email")
        if not email:
            logging.error(f"Skipping contact missing email: {contact}")
            return None

        # Handle full name with potential pronunciation
        full_name_raw = contact.get("full_name", "")
        pronunciations = {}
        if ":" in full_name_raw:
            pronunciation, full_name = [x.strip() for x in full_name_raw.split(":", 1)]
            pron_parts = pronunciation.split()
            name_parts = full_name.split()
            if len(pron_parts) == len(name_parts):
                for pron, name in zip(pron_parts, name_parts):
                    if name in pronunciations and pronunciations[name] != pron:
                        logging.warning(
                            f"Multiple different pronunciations found for '{name}' in "
                            f"{full_name_raw}"
                        )
                    pronunciations[name] = pron
            else:
                logging.error(
                    f"Pronunciation parts don't match name parts for {full_name_raw}"
                )
        else:
            full_name = full_name_raw

        # Handle nicknames with potential pronunciations
        nicknames = []
        for nickname_raw in contact.get("nicknames", []):
            if ":" in nickname_raw:
                pronunciation, nickname = [
                    x.strip() for x in nickname_raw.split(":", 1)
                ]
                if (
                    nickname in pronunciations
                    and pronunciations[nickname] != pronunciation
                ):
                    logging.warning(
                        f"Multiple different pronunciations found for '{nickname}' in "
                        f"contact {email}"
                    )
                pronunciations[nickname] = pronunciation
                nicknames.append(nickname)
            else:
                nicknames.append(nickname_raw)

        return Contact(
            email=email,
            full_name=full_name,
            nicknames=nicknames,
            pronunciations=pronunciations,
        )


csv_contacts: list[Contact] = []
json_contacts: list[Contact] = []


@track_csv_list("contacts.csv", headers=("Name", "Email"))
def on_contacts_csv(values):
    global csv_contacts
    csv_contacts = [
        Contact(email=email, full_name=full_name, nicknames=[], pronunciations={})
        for email, full_name in values.items()
    ]
    reload_contacts()


contacts_json = Path(__file__).parent / "contacts.json"
if not contacts_json.exists():
    contacts_json.write_text("[]")


@resource.watch("contacts.json")
def on_contacts_json(f):
    global json_contacts
    try:
        contacts = json.load(f)
    except Exception:
        logging.exception("Error parsing contacts.json")
        return

    json_contacts = []
    for contact in contacts:
        try:
            parsed_contact = Contact.from_json(contact)
            if parsed_contact:
                json_contacts.append(parsed_contact)
        except Exception:
            logging.exception(f"Error parsing contact: {contact}")
    reload_contacts()


def create_pronunciation_to_name_map(contact):
    result = {}
    if contact.full_name:
        # Add pronunciation mapping for full name
        pron_parts = [
            contact.pronunciations.get(name, name) for name in contact.full_name.split()
        ]
        result[" ".join(pron_parts)] = contact.full_name

        # Add pronunciation mapping for first name only
        first_name = contact.full_name.split()[0]
        result[contact.pronunciations.get(first_name, first_name)] = first_name
    for nickname in contact.nicknames:
        result[contact.pronunciations.get(nickname, nickname)] = nickname
    return result


def reload_contacts():
    # Merge the CSV and JSON contacts
    csv_by_email = {contact.email: contact for contact in csv_contacts}
    json_by_email = {contact.email: contact for contact in json_contacts}
    all_emails = set(csv_by_email.keys()) | set(json_by_email.keys())
    merged_contacts = []
    for email in all_emails:
        csv_contact = csv_by_email.get(email)
        json_contact = json_by_email.get(email)

        if csv_contact and json_contact:
            # Prefer JSON data but use CSV name if JSON name is empty
            full_name = json_contact.full_name or csv_contact.full_name
            merged_contacts.append(
                Contact(
                    email=email,
                    full_name=full_name,
                    nicknames=json_contact.nicknames,
                    pronunciations=json_contact.pronunciations,
                )
            )
        else:
            # Use whichever contact exists
            merged_contacts.append(json_contact or csv_contact)

    contact_names = {}
    contact_emails = {}
    contact_full_names = {}
    for contact in merged_contacts:
        pronunciation_map = create_pronunciation_to_name_map(contact)
        for pronunciation, name in pronunciation_map.items():
            contact_names[pronunciation] = name
            contact_emails[pronunciation] = contact.email
            if contact.full_name:
                contact_full_names[pronunciation] = contact.full_name

    ctx.lists["user.contact_names"] = contact_names
    ctx.lists["user.contact_emails"] = contact_emails
    ctx.lists["user.contact_full_names"] = contact_full_names


# We extend str so this can be used with no changes to the <user.prose> implementation.
class TimestampedString(str):
    def __new__(cls, string: str, start: float, end: float):
        return super().__new__(cls, string)

    def __init__(self, string: str, start: float, end: float):
        super().__init__()
        self.start = start
        self.end = end


@mod.capture(
    rule="{user.contact_names} name",
)
def prose_name(m) -> TimestampedString:
    return TimestampedString(m.contact_names, m[0].start, m[0].end)


@mod.capture(
    rule="{user.contact_names} names",
)
def prose_name_possessive(m) -> TimestampedString:
    if hasattr(m, "contact_name_possessives"):
        return TimestampedString(m.contact_name_possessives, m[0].start, m[0].end)
    else:
        return TimestampedString(
            actions.user.make_name_possessive(m.contact_names), m[0].start, m[0].end
        )


@mod.capture(
    rule="{user.contact_emails} email [address]",
)
def prose_email(m) -> TimestampedString:
    return TimestampedString(m.contact_emails, m[0].start, m[0].end)


@mod.capture(
    rule="{user.contact_emails} (username | L dap)",
)
def prose_username(m) -> TimestampedString:
    return TimestampedString(
        actions.user.username_from_email(m.contact_emails), m[0].start, m[0].end
    )


@mod.capture(
    rule="{user.contact_full_names} full name",
)
def prose_full_name(m) -> TimestampedString:
    return TimestampedString(m.contact_full_names, m[0].start, m[0].end)


@mod.capture(
    rule="{user.contact_full_names} full names",
)
def prose_full_name_possessive(m) -> TimestampedString:
    return TimestampedString(
        actions.user.make_name_possessive(m.contact_full_names), m[0].start, m[0].end
    )


@mod.capture(
    rule="{user.contact_full_names} first name",
)
def prose_first_name(m) -> TimestampedString:
    return TimestampedString(
        actions.user.first_name_from_full_name(m.contact_full_names),
        m[0].start,
        m[0].end,
    )


@mod.capture(
    rule="{user.contact_full_names} first names",
)
def prose_first_name_possessive(m) -> TimestampedString:
    return TimestampedString(
        actions.user.make_name_possessive(
            actions.user.first_name_from_full_name(m.contact_full_names)
        ),
        m[0].start,
        m[0].end,
    )


@mod.capture(
    rule="{user.contact_full_names} last name",
)
def prose_last_name(m) -> TimestampedString:
    return TimestampedString(
        actions.user.last_name_from_full_name(m.contact_full_names),
        m[0].start,
        m[0].end,
    )


@mod.capture(
    rule="{user.contact_full_names} last names",
)
def prose_last_name_possessive(m) -> TimestampedString:
    return TimestampedString(
        actions.user.make_name_possessive(
            actions.user.last_name_from_full_name(m.contact_full_names)
        ),
        m[0].start,
        m[0].end,
    )


@mod.capture(
    rule="(hi | high) {user.contact_names} [name]",
)
def prose_contact_snippet(m) -> TimestampedString:
    return TimestampedString(f"hi {m.contact_names}", m[0].start, m[-1].end)


@mod.capture(
    rule=(
        "<user.prose_name> "
        "| <user.prose_name_possessive> "
        "| <user.prose_email> "
        "| <user.prose_username> "
        "| <user.prose_full_name> "
        "| <user.prose_full_name_possessive> "
        "| <user.prose_first_name> "
        "| <user.prose_first_name_possessive> "
        "| <user.prose_last_name>"
        "| <user.prose_last_name_possessive>"
        "| <user.prose_contact_snippet>"
    ),
)
def prose_contact(m) -> TimestampedString:
    return m[0]


@mod.action_class
class Actions:
    def first_name_from_full_name(full_name: str):
        """Returns the first name from the full name."""
        return full_name.split(" ")[0]

    def last_name_from_full_name(full_name: str):
        """Returns the last name from the full name."""
        return full_name.split(" ")[-1]

    def username_from_email(email: str):
        """Returns the username from the email address."""
        return email.split("@")[0]

    def make_name_possessive(name: str):
        """Returns the possessive version of the name."""
        return f"{name}'s"
