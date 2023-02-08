#!/usr/bin/env python
import os
import asyncio
import smtplib
import logging
from email.message import EmailMessage
from playwright.async_api import async_playwright
from asyncio import sleep
from typing import List

URL = "https://whatson.bfi.org.uk/imax/Online/default.asp"
DELAY_SEC = 1800  # 30 minutes = 60 seconds * 30

logging.basicConfig(filename="ant.log", format='%(asctime)s %(message)s', level=logging.INFO)

async def main():
    email = os.environ.get("OUTLOOK_EMAIL")
    email_password = os.environ.get("OUTLOOK_PASSWORD")
    receivers = os.environ.get("RECEIVERS")

    if not email or not email_password or not receivers:
        print("Either email or password is missing")
        exit(1)

    logging.info("Starting server")
    while True:
        try:
            if await check_if_tickets_are_on_sale():
                logging.info("Tickets are on sale")
                send_email(
                    email,
                    email_password,
                    [email, receivers],
                    "YES! Tickets are on sale, go buy them now!",
                    f"YES! Tickets are on sale now, go buy them immediately!\n\nYou can by them at {URL}",
                )
            else:
                logging.info("Not on sale yet")
                send_email(
                    email,
                    email_password,
                    [receivers],
                    f"Are Ant-man tickets on sale yet?",
                    f"No, they are still not on sale...\n\nYou can check here: {URL}",
                )
        except Exception as e:
            logging.error(str(e))

        await sleep(DELAY_SEC)


async def check_if_tickets_are_on_sale() -> bool:
    async with async_playwright() as p:
        browser_type = p.firefox
        browser = await browser_type.launch()
        page = await browser.new_page()
        await page.goto(URL)
        frame = page.frame_locator("#calendar-widget-frame")
        month = frame.get_by_text("February 2023")
        await sleep(1)

        while not await month.is_visible():
            logging.debug("Feburary not visible")
            button = frame.get_by_title("Next month")
            await button.click()
            await sleep(1)
            frame = page.frame_locator("#calendar-widget-frame")
            month = frame.get_by_text("February 2023")

        day = frame.get_by_text("24")
        isAvailable = await day.get_attribute("class") != None

        await browser.close()

        return isAvailable


def send_email(from_email: str, email_password: str, to_email: List[str], subject: str, content: str):
    msg = EmailMessage()
    msg.set_content(content)
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    server = smtplib.SMTP("smtp-mail.outlook.com", port=587)
    server.ehlo()
    server.starttls()
    server.login(from_email, email_password)
    server.send_message(msg)
    server.quit()


asyncio.run(main())
