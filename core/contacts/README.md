# Contacts

This directory provides a versatile `<user.prose_contact>` capture that can be
used to insert names and email addresses using a suffix. The contact list may be
provided through `contacts.csv` in the settings directory, `contacts.json` in
this directory, or both.

Here is an example contacts.json:

```json
[
    {
        "email": "john.doe@example.com",
        "full_name": "Jonathan Doh: Jonathan Doe",
        "nicknames": ["Jon", "Jah Nee: Jonny"]
    },
    ...
]
```

Note that for either full_name or nicknames, pronunciation can be provided via
the standard Talon list format of "[pronunciation]: [name]".

To refer to this contact, you could say:

- Jonathan Doh email -> john.doe@example.com
- Jonathan email -> john.doe@example.com
- Jah Nee email -> john.doe@example.com
- Jah Nee name -> Jonny
- Jonathan Doh name -> Jonathan Doe
- Jon last name -> Doe
- Jon full name -> Jonathan Doe

The CSV format provides only email and full name functionality:

```csv
Name,Email
John Doe,jon.doe@example.com
Jane Doe,jane.doe@example.com
```

The advantage of the CSV format is that it is easily exported. For example, to
export from Gmail, go to https://contacts.google.com/, then click "Frequently
contacted", then "Export". Then run:

```bash
cat contacts.csv | python -c "import csv; import sys; w=csv.writer(sys.stdout); [w.writerow([row['First Name'] + ' ' + row['Last Name'], row['E-mail 1 - Value']]) for row in csv.DictReader(sys.stdin)]"
```

If both the CSV and JSON are present, they will be merged based on email
addresses. This makes it easy to use an exported CSV and maintain nicknames in
the JSON.
