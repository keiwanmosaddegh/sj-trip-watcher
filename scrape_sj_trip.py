import os
from selenium import webdriver
import time
import smtplib
import ssl

# Webdriver options configurations
op = webdriver.ChromeOptions()
op.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
op.add_argument("--headless")
op.add_argument("--no-sandbox")
op.add_argument("--disable-dev-sh-usage")

# Email configurations
port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = os.environ.get("SENDER_EMAIL")
receiver_email = os.environ.get("RECEIVER_EMAIL")
password = os.environ.get("SENDER_PASSWORD")

# Email messages
unsuccessful_count = """\
Subject: [SJ Trip Watcher] Unsuccessful Count Alert

The script was unfortunately not able to label all rows, leaving resulting in:
timeTableRowsAmount != availableAmount + unavailableAmount

Link:
https://www.sj.se/en/home.html#/tidtabell/%25C3%2585re/Stockholm%2520Central/enkel/avgang/20220320-0500/avgang/20220320-1300/BO-25--false///0//
"""
daily_message = """\
Subject: [SJ Trip Watcher] Daily alive notice

This is a daily check. Nothing more, nothing less. Just ignore me, and have an amazing day.
"""
available_amount_diff = """\
Subject: [SJ Trip Watcher] ALERT! New Amount Of Available Trips Detected!

The amount of available trips have diverged from the original (3).

This might mean that there's either a new available trip,
or that another trip is fully booked. 

Link:
https://www.sj.se/en/home.html#/tidtabell/%25C3%2585re/Stockholm%2520Central/enkel/avgang/20220320-0500/avgang/20220320-1300/BO-25--false///0//
"""

# Original values
ogAvailableAmount = 3


def send_email(custom_message):
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, custom_message)


def trip_scrape():
    driver = webdriver.Chrome(
        executable_path=os.environ.get('CHROMEDRIVER_PATH'),
        options=op
    )

    driver.get("https://www.sj.se/en/home.html#/tidtabell/%25C3%2585re/Stockholm%2520Central/enkel/avgang/20220320-0500/avgang/20220320-1300/BO-25--false///0//")

    timeTable = driver.find_element_by_xpath(
        '//div[@ng-switch-when="SUCCESS"]')

    timeTableRows = timeTable.find_elements_by_xpath(
        '//div[@ng-repeat="timetableRow in sjTimetableModel"]')

    timeTableRowsAmount = len(timeTableRows)

    availableAmount = 0
    unavailableAmount = 0
    for row in timeTableRows:
        try:
            row.find_element_by_class_name(
                "timetable-unexpanded-price--unavailable")
            unavailableAmount += 1
        except:
            pass

        try:
            row.find_element_by_class_name(
                "timetable-unexpanded-price__wrapper")
            availableAmount += 1
        except:
            pass

    if timeTableRowsAmount != availableAmount + unavailableAmount:
        send_email(unsuccessful_count)

    if ogAvailableAmount != availableAmount:
        send_email(available_amount_diff)

    driver.close()


# Main
starttime = time.time()
while True:
    for _ in range(1440):
        trip_scrape()
        time.sleep(60.0 - ((time.time() - starttime) % 60.0))

    print("24 hours have past. Sending email...")
    send_email(daily_message)
