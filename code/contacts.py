from talon import Context, Module

from .user_settings import get_list_from_csv

mod = Module()
ctx = Context()

mod.list("contact_emails", desc="contact email addresses")
mod.list("contact_full_names", desc="contact full names")

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


ctx.lists["user.contact_emails"] = create_name_to_email_dict()
ctx.lists["user.contact_full_names"] = create_name_to_full_name_dict()


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
