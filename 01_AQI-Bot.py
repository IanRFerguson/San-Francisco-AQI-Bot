#!/usr/bin/env python3.6
# coding: utf-8

# ------------ IMPORTS

import pandas as pd
import requests
import json
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
from time import sleep


# ------------ ENVIRONMENT

token = open("TOKEN.txt").read()                                # Read in token from WAQI API

with open("Email-Credentials.txt", "r") as file:                # Read in email address + password
    credentials = json.load(file)

# ------------ HELPER FUNCTIONS

def scrapeAQI(CITY="San Francisco"):

    """
    Scrapes JSON file from WAQI API
    Returns only the AQI

    Note: Default city is San Francisco, but can be overwritten
    """

    base = "https://api.waqi.info"
    r = requests.get(base + f"/feed/{CITY}/?token={token}")
    return r.json()['data']['aqi']


def defineQuality(AQI):

    """
    Determines how AQI value is rated by EPA
    """

    if 0 < AQI < 50:
        return "good"

    elif 51 < AQI < 100:
        return "moderate"

    elif 101 < AQI < 150:
        return "unhealthy for sensitive groups"

    elif 151 < AQI < 200:
        return "unhealthy"

    elif 201 < AQI < 300:
        return "very unhealthy"

    elif 301 < AQI < 500:
        return "hazardous"

    else:
        return "Error: Invalid AQI"


def formatEmail(NAME):

    """
    Impute relevant end user information into HTML body for email
    """

    body = ("""Good morning {},
    <br><br>
    The current air quality in San Francisco, California is <b>{}</b>.
    <br><br>
    San Francisco's air quality is rated as <b><u>{}</u></b> by the Environmental Protection Agency. For a more thorough breakdown of San Francisco's air quality, please <a href="https://www.iqair.com/us/usa/california/san-francisco" target=_blank><b>see here</b></a>.
    <br> <br>
    Stay safe,
    <br>
    The Bay Area AQI Bot""").format(NAME, int(scrapeAQI()), defineQuality(scrapeAQI()))

    return body


def today():

    """
    Returns current date in longform, for imputation to email subject
    """

    return datetime.datetime.now().strftime("%x")


def sendEmail(NAME, EMAIL):

    """
    Wrap all of the above into an email to folks on mailing list
    """

    # Outgoing email setup
    port = 587
    smtp_server = 'smtp.gmail.com'
    my_address = credentials["Email Address"]
    password = credentials["Password"]
    receiver_address = EMAIL

    # Structure body of email
    body = formatEmail(NAME)

    # Connect to server with credentials
    s = smtplib.SMTP(host = smtp_server, port = port)
    s.ehlo()
    s.starttls()
    s.login(user = my_address, password = password)

    # Structure HTML output
    msg = MIMEMultipart()
    msg["From"] = "Bay Area AQI Bot"
    msg["To"] = EMAIL
    msg["Subject"] = ("San Francisco AQI: {}".format(str(today())))
    msg.attach(MIMEText(body, "html"))

    # Send email + Close server connection
    s.sendmail(my_address, receiver_address, msg.as_string())
    s.quit()


# ------------ RIPPER

mailingList = pd.read_excel("Mailing-List.xlsx")

# Loop through mailing list and send email
for index, NAME in enumerate(mailingList["NAME"]):
    sendEmail(NAME, mailingList["EMAIL"][index])

    print("Contacting {}...".format(NAME))
    sleep(1)

print("\nAll addresses contacted")
