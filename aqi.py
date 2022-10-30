#!/usr/bin/python3.6
import pandas as pd
import requests
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
from time import sleep
from dotenv import load_dotenv


##########


load_dotenv("./.env")

token = os.environ.get("WAQI")
my_address = os.environ.get("MY_ADDRESS")
password = os.environ.get("PASSWORD")


#########


def scrape_aqi(CITY: str="San Francisco"):
    """
    Obtain numeric AQI value from WAQI.info
    Defaults to San Francisco
    """

    base = "https://api.waqi.info"
    r = requests.get(base + f"/feed/{CITY}/?token={token}")
    
    return r.json()['data']['aqi']



def define_quality(AQI: int):
    """
    AQI: Quantiative value from scrape_aqi() function

    Converts quant to qualitative value based on EPA ratings
    """

    # If AQI API is broken (happens sometimes)...
    if AQI == "-":
        return 0

    # If you receive a valid AQI value...
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



def format_email(NAME: str, CITY: str="San Francisco"):
    """
    * NAME: End user's first name
    * CITY: Geographic location of obtained AQI

    If AQI unavailable, script defaults to beta email body
    """

    AQI = scrape_aqi(CITY=CITY)
    QUALITY = define_quality(AQI)

    if QUALITY != 0:

        body = (f"""Good morning {NAME},
        <br><br>
        The current Air Quality Index in {CITY}, California is rated <b>{int(AQI)}</b>.
        <br><br>
        This value is considered <b><u>{QUALITY}</u></b> by the Environmental Protection Agency. For a more thorough breakdown of San Francisco's air quality, please <a href="https://www.iqair.com/us/usa/california/san-francisco" target=_blank><b>see here</b></a>.
        <br> <br>
        Stay safe,
        <br>
        <b>The Bay Area AQI Bot</b>
        <br> <br>
        <a href="mailto:irf229@nyu.edu">Email Me</a> to unsubscribe at any time""")

    else:
        body = (f"""Good morning {NAME},
        <br><br>
        Our API is currently not returning data for {CITY}. Sorry for the inconvenience!
        <br><br>
        If you'd like to check your area's AQI manually <a href="https://www.iqair.com/us/usa/california/san-francisco" target=_blank><b>see here</b></a>.
        <br> <br>
        Stay safe,
        <br>
        <b>The Bay Area AQI Bot</b>
        <br><br>
        <a href="mailto:irf229@nyu.edu">Email Me</a> to unsubscribe at any time
        """)

    return body



def today():
    return datetime.datetime.now().strftime("%x")



def send_email(NAME:str, EMAIL:str, CITY:str):
    """
    * NAME: End user's first name
    * EMAIL: End user's email address
    * CITY: End user's geographic location

    Wraps functions defined above, sends end user email w/ relevant AQI ratings
    """

    port = 587
    smtp_server = 'smtp.gmail.com'
    receiver_address = EMAIL

    ###

    body = format_email(NAME=NAME, CITY=CITY)
    s = smtplib.SMTP(host=smtp_server, port=port)
    s.ehlo()
    s.starttls()
    s.login(user=my_address, password=password)

    ###

    msg = MIMEMultipart()
    msg["From"] = "Bay Area AQI Bot"
    msg["To"] = EMAIL
    msg["Subject"] = ("{} AQI: {}".format(CITY, str(today())))
    msg.attach(MIMEText(body, "html"))

    s.sendmail(my_address, receiver_address, msg.as_string())
    s.quit()


##########


def main():

    mailing_list = pd.read_csv("Mailing-List.csv")

    # Loop through end users in local CSV file
    for index, NAME in enumerate(mailing_list["NAME"]):
        ADDRESS = mailing_list["EMAIL"][index]
        CITY = mailing_list["CITY"][index]

        if str(CITY).lower() == "nan":
            CITY="San Francisco"

        send_email(
            NAME=NAME,
            EMAIL=ADDRESS,
            CITY=CITY)

        print(f"Contacting {NAME}...")
        sleep(2)

    sleep(1)
    print("\nAll addresses contacted")


#########


if __name__ == "__main__":
    main()
