from talon import Context, Module

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
