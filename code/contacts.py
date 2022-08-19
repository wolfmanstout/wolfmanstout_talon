from talon import Context, Module, actions

from .user_settings import get_list_from_csv

mod = Module()
ctx = Context()

mod.list("contact_emails", desc="Maps names to email addresses.")
mod.list("contact_full_names", desc="Maps names to full names.")
mod.list("contact_names", desc="Contact first names and full names.")
mod.list(
    "contact_name_possessives", desc="Contact first name and full name possessives."
)

# To export from Gmail, go to https://contacts.google.com/, then click "Frequently contacted", then
# "Export". Then run `pipx install csvkit` and `csvcut -c 1,31 contacts.csv`.
email_to_full_name = get_list_from_csv(
    "contacts.csv",
    headers=("Name", "Email"),
)
full_name_to_email = {v: k for k, v in email_to_full_name.items()}


def create_name_to_email_dict():
    return {
        name: email
        for full_name, email in full_name_to_email.items()
        for name in full_name.split(" ") + [full_name]
        if name
    }


def create_name_to_full_name_dict():
    return {
        name: full_name
        for full_name in full_name_to_email
        for name in full_name.split(" ") + [full_name]
        if name
    }


def create_contact_names():
    return [
        name
        for full_name in full_name_to_email
        for name in [full_name.split(" ")[0], full_name]
        if name
    ]


ctx.lists["user.contact_emails"] = create_name_to_email_dict()
ctx.lists["user.contact_full_names"] = create_name_to_full_name_dict()
ctx.lists["user.contact_names"] = create_contact_names()
ctx.lists["user.contact_name_possessives"] = [
    f"{name}'s" for name in create_contact_names()
]


# We extend str so this can be used with no changes to the <user.prose> implementation.
class TimestampedString(str):
    def __new__(cls, string: str, start: float, end: float):
        return super().__new__(cls, string)

    def __init__(self, string: str, start: float, end: float):
        super().__init__()
        self.start = start
        self.end = end


@mod.capture(
    rule="{user.contact_names} [name]",
)
def prose_name(m) -> TimestampedString:
    return TimestampedString(m.contact_names, m[0].start, m[0].end)


@mod.capture(
    rule="{user.contact_name_possessives} | {user.contact_names} [names]",
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
