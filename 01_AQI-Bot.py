#!/usr/bin/python3.6
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

token = open("TOKEN.txt").read()

with open("Email-Credentials.txt", "r") as file:
    credentials = json.load(file)

# ------------ HELPER FUNCTIONS

def scrapeAQI(CITY="San Francisco"):

    base = "https://api.waqi.info"
    r = requests.get(base + f"/feed/{CITY}/?token={token}")
    return r.json()['data']['aqi']


def defineQuality(AQI):

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


def formatEmail(NAME, CITY="San Francisco"):

    AQI = scrapeAQI(CITY=CITY)
    QUALITY = defineQuality(scrapeAQI(CITY=CITY))

    body = ("""Good morning {},
    <br><br>
    The current Air Quality Index in {}, California is rated <b>{}</b>.
    <br><br>
    This value is considered <b><u>{}</u></b> by the Environmental Protection Agency. For a more thorough breakdown of San Francisco's air quality, please <a href="https://www.iqair.com/us/usa/california/san-francisco" target=_blank><b>see here</b></a>.
    <br> <br>
    Stay safe,
    <br>
    <b>The Bay Area AQI Bot</b>""").format(NAME, CITY, int(AQI), QUALITY)

    return body


def today():
    return datetime.datetime.now().strftime("%x")


def sendEmail(NAME, EMAIL, CITY):

    port = 587
    smtp_server = 'smtp.gmail.com'
    my_address = credentials["Email Address"]
    password = credentials["Password"]
    receiver_address = EMAIL

    body = formatEmail(NAME, CITY=CITY)

    s = smtplib.SMTP(host = smtp_server, port = port)
    s.ehlo()
    s.starttls()
    s.login(user = my_address, password = password)

    msg = MIMEMultipart()
    msg["From"] = "Bay Area AQI Bot"
    msg["To"] = EMAIL
    msg["Subject"] = ("{} AQI: {}".format(CITY, str(today())))
    msg.attach(MIMEText(body, "html"))

    s.sendmail(my_address, receiver_address, msg.as_string())

    s.quit()


# ------------ RIPPER

mailingList = pd.read_csv("Mailing-List.csv")

for index, NAME in enumerate(mailingList["NAME"]):
    ADDRESS = mailingList["EMAIL"][index]
    CITY = mailingList["CITY"][index]

    if str(CITY).lower() == "nan":
        sendEmail(NAME, ADDRESS, "San Francisco")
        print("Contacting {}...".format(NAME))
        sleep(2)

    else:
        sendEmail(NAME, ADDRESS, CITY=CITY)
        print("Contacting {}...".format(NAME))
        sleep(2)

sleep(1)
print("\nAll addresses contacted")
