import os
from selenium import webdriver
import time
import smtplib, ssl

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
in_stock_message = """\
Subject: SIZE 34 IS IN STOCK!

Good news! Size 34 is in stock! Buy it while it lasts.

Link:
https://www.stories.com/en_sek/clothing/dresses/mini-dresses/product.sheer-leopard-jacquard-mini-dress-black.0793274001.html
"""
hourly_message = """\
Subject: Hourly check (yep we're still up and running, boys)

This is an hourly check. Nothing more, nothing less. Just ignore me, and have an amazing day."""
not_found_message = """\
Subject: Size 34 NOT FOUND...

Size 34 can no longer be found when scraping. Something's broken with something.
Begin by taking a look at the original link and see that it still exists:
https://www.stories.com/en_sek/clothing/dresses/mini-dresses/product.sheer-leopard-jacquard-mini-dress-black.0793274001.html"""


# Send Email
def send_email(custom_message):
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, custom_message)

# Scrape Dress Availability Status
def dress_scrape():
    driver = webdriver.Chrome(executable_path=os.environ.get('CHROMEDRIVER_PATH'), chrome_options=op)
    driver.get("https://www.stories.com/en_sek/clothing/dresses/mini-dresses/product.sheer-leopard-jacquard-mini-dress-black.0793274001.html")
    sizes = driver.find_element_by_id('sizes')

    size_options = sizes.find_elements_by_class_name('size-options')

    size_34_found = False
    for size_option in size_options:
        if (size_option.get_attribute('data-value') == '34'):
            size_34_found = True
            print("Size 34 found!")
            if 'is-sold-out' in size_option.get_attribute('class'):
                print("Size 34 is sold out!")
            else:
                print("Size 34 is in stock! Sending email...")
                send_email(in_stock_message)

    if(not size_34_found):
        print("Could not find size 34. Sending email...")
        send_email(not_found_message)

    driver.close()

# Main
starttime = time.time()
while True:
    dress_scrape()
    time.sleep(3600.0 - ((time.time() - starttime) % 3600.0))
    print("An hour has gone. Sending email...")
    send_email(hourly_message)
