import datetime as dt
import pandas as pd
import smtplib
import os
import sys
from email.message import EmailMessage

# Get email credentials from environment variables (GitHub Secrets)
MY_EMAIL = os.environ.get("EMAIL_ADDRESS")
MY_PASSWORD = os.environ.get("EMAIL_PASSWORD")

if not MY_EMAIL or not MY_PASSWORD:
    print("ERROR: EMAIL_ADDRESS and EMAIL_PASSWORD must be set in environment.")
    sys.exit(1)

# Get today's date
today = dt.datetime.now()
today_month, today_day = today.month, today.day

# Get real birthdays CSV from GitHub Secret (PLAIN TEXT)
csv_data = os.environ.get("REAL_BIRTHDAYS_CSV")

# Write secret CSV data to a local file at runtime (if provided)
if csv_data:
    with open("birthdays.csv", "w", encoding="utf-8", newline="") as f:
        f.write(csv_data)

# Ensure the CSV file exists
if not os.path.exists("birthdays.csv"):
    print("No birthdays.csv found and REAL_BIRTHDAYS_CSV secret not provided. Exiting.")
    sys.exit(0)

# Read birthdays from CSV (expect columns: name, email, year, month, day)
try:
    data = pd.read_csv("birthdays.csv", encoding="utf-8")
except Exception as e:
    print(f"Failed to read birthdays.csv: {e}")
    sys.exit(1)

# Filter rows matching today's month and day (supports multiple people)
matches = data[
    (data.get("month") == today_month) &
    (data.get("day") == today_day)
]

if matches.empty:
    print("No birthdays today.")
    sys.exit(0)

# Load the letter template once (used for all matches)
template_path = os.path.join("letter_templates", "letter.txt")
try:
    with open(template_path, "r", encoding="utf-8") as file:
        template_contents = file.read()
except Exception as e:
    print(f"Failed to read letter template '{template_path}': {e}")
    sys.exit(1)

# Connect to SMTP once and send all emails
try:
    with smtplib.SMTP("smtp.gmail.com", 587) as connection:
        connection.starttls()
        connection.login(MY_EMAIL, MY_PASSWORD)

        for _, person in matches.iterrows():
            try:
                name = str(person.get("name", "")).strip()
                recipient_email = str(person.get("email", "")).strip()
                year_of_birth = person.get("year")

                # Compute age if year is available and numeric
                try:
                    age = today.year - int(year_of_birth)
                except Exception:
                    age = ""

                # Personalize template
                contents = template_contents
                contents = contents.replace("[NAME]", name)
                contents = contents.replace("[AGE]", str(age))

                # Build EmailMessage with UTF-8 charset
                msg = EmailMessage()
                msg["Subject"] = "Happy Birthday"
                msg["From"] = MY_EMAIL
                msg["To"] = recipient_email
                msg.set_content(contents, subtype="plain", charset="utf-8")

                # Send the message
                connection.send_message(msg)
                print(f"Sent birthday email to {recipient_email!s}")

            except Exception as person_err:
                print(f"Failed to send to {person.get('email')}: {person_err}")

except Exception as smtp_err:
    print(f"SMTP error: {smtp_err}")
    sys.exit(1)
