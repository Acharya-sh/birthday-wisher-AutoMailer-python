import datetime as dt
import pandas
import smtplib
import os

# Get email credentials from environment variables (GitHub Secrets)
MY_EMAIL = os.environ.get("EMAIL_ADDRESS")
MY_PASSWORD = os.environ.get("EMAIL_PASSWORD")

# Get today's date
today = dt.datetime.now()
today_tuple = (today.month, today.day)

# Get real birthdays CSV from GitHub Secret (PLAIN TEXT)
csv_data = os.environ.get("REAL_BIRTHDAYS_CSV")

# Write secret CSV data to a local file at runtime
if csv_data:
    with open("birthdays.csv", "w") as f:
        f.write(csv_data)

# Read birthdays from CSV
data = pandas.read_csv("birthdays.csv")

# Create a dictionary with (month, day) as key
birthdays_dict = {
    (row["month"], row["day"]): row
    for _, row in data.iterrows()
}

# Check if today matches any birthday
if today_tuple in birthdays_dict:
    person = birthdays_dict[today_tuple]

    # Calculate age
    age = today.year - person["year"]

    # Load and personalize the letter
    with open("letter_templates/letter.txt") as file:
        contents = file.read()
        contents = contents.replace("[NAME]", person["name"])
        contents = contents.replace("[AGE]", str(age))

    # Send email
    with smtplib.SMTP("smtp.gmail.com", 587) as connection:
        connection.starttls()
        connection.login(MY_EMAIL, MY_PASSWORD)
        connection.sendmail(
            from_addr=MY_EMAIL,
            to_addrs=person["email"],
            msg=f"Subject:Happy Birthday \n\n{contents}"
        )
