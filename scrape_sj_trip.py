import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import smtplib
import ssl

# Webdriver options configurations
op = webdriver.ChromeOptions()
op.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
op.add_argument("--headless")
op.add_argument("--no-sandbox")
op.add_argument("--disable-dev-sh-usage")
op.add_argument("--disable-gpu")
op.add_argument("--start-maximized")
op.add_argument("--window-size=1920,1080")

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
og_available_amount = 3


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

    # PATH = "C:\\Users\\keiwa\\Documents\\projects\\apps\\sj-trip-watcher\\chromedriver.exe"
    # driver = webdriver.Chrome(executable_path=PATH)

    driver.get("https://www.sj.se/en/home.html#/tidtabell/%25C3%2585re/Stockholm%2520Central/enkel/avgang/20220320-0500/avgang/20220320-1300/BO-25--false///0//")

    try:
        timetable_present = EC.presence_of_element_located(
            (By.XPATH, '//div[@ng-switch-when="SUCCESS"]'))
        WebDriverWait(driver, 5).until(timetable_present)
    except:
        print("Doesn't find table. Exiting function.")
        return

    timetable = driver.find_element_by_xpath(
        '//div[@ng-switch-when="SUCCESS"]')

    timetable_rows = timetable.find_elements_by_xpath(
        '//div[@ng-repeat="timetableRow in sjTimetableModel"]')

    timetable_rows_amount = len(timetable_rows)

    available_amount = 0
    unavailable_amount = 0
    for row in timetable_rows:
        try:
            row.find_element_by_class_name(
                "timetable-unexpanded-price--unavailable")
            unavailable_amount += 1
        except:
            pass

        try:
            row.find_element_by_class_name(
                "timetable-unexpanded-price__wrapper")
            available_amount += 1
        except:
            pass

    if timetable_rows_amount != available_amount + unavailable_amount:
        print("Count was unsuccessful, sending email.")
        send_email(unsuccessful_count)

    if og_available_amount != available_amount:
        print("The available amount has changed, sending email.")
        send_email(available_amount_diff)

    print(
        f'Statistics from this run: {available_amount} available, and {unavailable_amount} unavailable trips.')
    driver.close()


# Main
starttime = time.time()
while True:
    for _ in range(1440):
        trip_scrape()
        print("One check done. Will check again in 1 minute.")
        time.sleep(60.0 - ((time.time() - starttime) % 60.0))

    print("24 hours have past. Sending email...")
    send_email(daily_message)
