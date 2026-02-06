import datetime as dt
import pandas as pd
import smtplib
import os
import sys
import pytz
from email.message import EmailMessage

# Get email credentials
MY_EMAIL = os.environ.get("EMAIL_ADDRESS")
MY_PASSWORD = os.environ.get("EMAIL_PASSWORD")
CSV_DATA = os.environ.get("REAL_BIRTHDAYS_CSV")

if not MY_EMAIL or not MY_PASSWORD:
    print("ERROR: EMAIL_ADDRESS or EMAIL_PASSWORD missing")
    sys.exit(1)

if not CSV_DATA:
    print("ERROR: REAL_BIRTHDAYS_CSV missing")
    sys.exit(1)

# ----- FIX 1: Use IST timezone -----
ist = pytz.timezone("Asia/Kolkata")
today = dt.datetime.now(ist)
today_month = today.month
today_day = today.day

print(f"Today (IST): {today_month}-{today_day}")

# Write CSV from secret
with open("birthdays.csv", "w", encoding="utf-8") as f:
    f.write(CSV_DATA)

# Read CSV
data = pd.read_csv("birthdays.csv")

# Match birthdays
matches = data[
    (data["month"] == today_month) &
    (data["day"] == today_day)
]

if matches.empty:
    print("No birthdays today.")
    sys.exit(0)

# Load template
with open("letter_templates/letter.txt", "r", encoding="utf-8") as f:
    template = f.read()

# Send emails
with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login(MY_EMAIL, MY_PASSWORD)

    for _, person in matches.iterrows():
        age = today.year - int(person["year"])

        body = (
            template
            .replace("[NAME]", person["name"])
            .replace("[AGE]", str(age))
        )

        msg = EmailMessage()
        msg["Subject"] = "Happy Birthday"
        msg["From"] = MY_EMAIL
        msg["To"] = person["email"]
        msg.set_content(body, charset="utf-8")

        server.send_message(msg)
        print(f"Email sent to {person['email']}")
